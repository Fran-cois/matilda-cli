#!/usr/bin/env python3
"""
MATILDA CLI - Command-line interface for MATILDA rule discovery.
"""
import argparse
import csv
import datetime
import logging
import shutil
import signal
import sqlite3
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from matilda_cli.__version__ import __version__
from typing import List, Optional

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

try:
    import mlflow

    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

from matilda_cli.algorithms.matilda import MATILDA
from matilda_cli.database.alchemy_utility import AlchemyUtility
from matilda_cli.utils.config_loader import load_config
from matilda_cli.utils.logging_utils import configure_global_logger
from matilda_cli.utils.monitor import ResourceMonitor
from matilda_cli.utils.rules import RuleIO

# Initialize Rich console
console = Console()


def print_banner():
    """Display the MATILDA ASCII art banner."""
def print_banner():
    """Display the MATILDA ASCII art banner."""
    banner = """
[bold cyan]╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   ███╗   ███╗ █████╗ ████████╗██╗██╗     ██████╗  █████╗        ║
║   ████╗ ████║██╔══██╗╚══██╔══╝██║██║     ██╔══██╗██╔══██╗       ║
║   ██╔████╔██║███████║   ██║   ██║██║     ██║  ██║███████║       ║
║   ██║╚██╔╝██║██╔══██║   ██║   ██║██║     ██║  ██║██╔══██║       ║
║   ██║ ╚═╝ ██║██║  ██║   ██║   ██║███████╗██████╔╝██║  ██║       ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝       ║
║                                                                   ║
║        [bold yellow]Mining Approximate Tuple-Generating Dependencies[/]         ║
║                    [dim]in Large Databases[/]                             ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝[/]
    """
    console.print(banner)
    console.print()


def create_demo_database(demo_type: str, output_path: Path) -> None:
    """Create a demo database using the university data.
    
    For both perfect_database and imperfect_database, we use the test database
    which is designed to produce TGD rules for MATILDA to discover.
    
    Args:
        demo_type: Type of demo ('perfect_database' or 'imperfect_database')
        output_path: Path where to create the database
    """
    from pathlib import Path
    import shutil
    from rich.console import Console
    
    console = Console()
    
    # Use the test database which is designed to generate rules
    project_root = Path(__file__).parent.parent
    source_db = project_root / 'tests' / 'data' / 'university.db'
    
    if not source_db.exists():
        # If test database doesn't exist, create it
        console.print("[yellow]⚠ Test database not found, creating it...[/]")
        import subprocess
        create_script = project_root / 'tests' / 'scripts' / 'create_db_with_violations.py'
        if create_script.exists():
            subprocess.run([sys.executable, str(create_script)], check=True)
        else:
            raise FileNotFoundError(f"Cannot create demo database: {create_script} not found")
        
        if not source_db.exists():
            raise FileNotFoundError(f"Failed to create test database at {source_db}")
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Remove existing database if it exists
    if output_path.exists():
        output_path.unlink()
    
    with console.status(f"[bold cyan]Creating {demo_type} database...", spinner="dots"):
        # Simply copy the test database which already has the right structure
        # Both perfect and imperfect use the same database as it's designed for demonstrations
        shutil.copy2(source_db, output_path)
    
    console.print(f"[green]✓ Demo database created: {output_path}[/]")
    
    # Show info about the database
    import sqlite3
    with sqlite3.connect(str(output_path)) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM student")
        student_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM enrollment")
        enrollment_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM advisor")
        advisor_count = cursor.fetchone()[0]
    
    console.print(f"[cyan]ℹ Database contains: {student_count} students, {enrollment_count} enrollments, {advisor_count} advisors[/]")


@contextmanager
def mlflow_run_context(use_mlflow: bool, config: dict):
    """Context manager to handle MLflow runs."""
    if use_mlflow:
        mlflow_tracking_uri = config.get("mlflow", {}).get("tracking_uri", "http://localhost:5000")
        mlflow_experiment = config.get("mlflow", {}).get("experiment_name", "MATILDA Discovery")
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment(mlflow_experiment)

    console.print(banner)
    console.print()


@contextmanager
def mlflow_run_context(use_mlflow: bool, config: dict):
    """Context manager to handle MLflow runs."""
    if use_mlflow:
        mlflow_tracking_uri = config.get("mlflow", {}).get("tracking_uri", "http://localhost:5000")
        mlflow_experiment = config.get("mlflow", {}).get("experiment_name", "MATILDA Discovery")
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment(mlflow_experiment)
        mlflow.start_run()
        try:
            yield
        finally:
            mlflow.end_run()
    else:
        yield


def display_config_panel(config: dict, database_name: str, database_path: Path):
    """Display configuration in a beautiful panel."""
    config_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="yellow")

    config_table.add_row("🗄️  Database", f"{database_name}")
    config_table.add_row("📁 Path", f"{database_path}")
    config_table.add_row(
        "🎯 Min Occurrence", f"{config.get('algorithm', {}).get('nb_occurrence', 3)}"
    )
    config_table.add_row("📊 Max Tables", f"{config.get('algorithm', {}).get('max_table', 3)}")
    config_table.add_row("🔢 Max Variables", f"{config.get('algorithm', {}).get('max_vars', 6)}")
    config_table.add_row(
        "💾 Memory Limit", f"{config.get('monitor', {}).get('memory_threshold', 15)} GB"
    )
    config_table.add_row("⏱️  Timeout", f"{config.get('monitor', {}).get('timeout', 3600)} seconds")

    mlflow_status = (
        "✅ Enabled"
        if config.get("mlflow", {}).get("use", False) and MLFLOW_AVAILABLE
        else "❌ Disabled"
    )
    config_table.add_row("📈 MLflow", mlflow_status)

    console.print(
        Panel(
            config_table,
            title="[bold blue]⚙️  Configuration[/]",
            border_style="blue",
            padding=(1, 2),
        )
    )
    console.print()


def initialize_directories(results_dir: Path, log_dir: Path) -> None:
    """Ensure that results and logs directories exist."""
    results_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)


class DatabaseProcessor:
    """Handles database rule discovery and result logging."""

    def __init__(
        self,
        database_name: Path,
        database_path: Path,
        results_dir: Path,
        logger: logging.Logger,
        use_mlflow: bool = False,
        config: dict = None,
    ):
        self.database_name = database_name
        self.database_path = database_path
        self.results_dir = results_dir
        self.logger = logger
        self.use_mlflow = use_mlflow
        self.config = config or {}

    def discover_rules(self) -> int:
        """Run the MATILDA rule discovery algorithm."""
        db_file_path = self.database_path / self.database_name
        db_uri = f"sqlite:///{db_file_path}"

        try:
            self.logger.info(f"Using database URI: {db_uri}")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:

                # Initialize database
                task1 = progress.add_task("[cyan]Initializing database connection...", total=100)
                with AlchemyUtility(
                    db_uri, 
                    database_path=str(self.database_path), 
                    create_index=False,
                    create_csv=False,
                    create_tsv=False,
                    get_data=True
                ) as db_util:
                    progress.update(task1, advance=100)

                    # Initialize MATILDA
                    task2 = progress.add_task("[cyan]Initializing MATILDA algorithm...", total=100)
                    
                    # Get algorithm settings from config
                    algorithm_settings = self.config.get('algorithm', {})
                    settings = {
                        'nb_occurrence': algorithm_settings.get('nb_occurrence', 3),
                        'max_table': algorithm_settings.get('max_table', 3),
                        'max_vars': algorithm_settings.get('max_vars', 6),
                    }
                    
                    algo = MATILDA(db_util, settings=settings)
                    rules = []
                    progress.update(task2, advance=100)

                    # Discover rules
                    task3 = progress.add_task("[yellow]Discovering rules...", total=None)
                    self.logger.debug("Starting MATILDA rule discovery...")

                    for rule in algo.discover_rules(results_dir=str(self.results_dir)):
                        self.logger.info(f"Discovered rule: {rule}")
                        rules.append(rule)

                    progress.update(task3, completed=True)

                    # Save results
                    task4 = progress.add_task("[green]Saving results...", total=100)
                    json_file_name = f"MATILDA_{self.database_name.stem}_results.json"
                    result_path = self.results_dir / json_file_name

                    self.logger.debug(f"Saving rules to {result_path}")
                    number_of_rules = RuleIO.save_rules_to_json(rules, result_path)
                    progress.update(task4, advance=100)

                console.print()
                console.print(
                    Panel(
                        f"[bold green]✓[/] Successfully discovered [bold yellow]{number_of_rules}[/] rules!",
                        border_style="green",
                        padding=(1, 2),
                    )
                )
                console.print()

                self.logger.info(f"Discovered {number_of_rules} rules.")
                top_rules = sorted(rules, key=lambda x: -x.accuracy)[:5]
                self.generate_report(number_of_rules, result_path, top_rules)

                if self.use_mlflow:
                    mlflow.log_param("algorithm", "MATILDA")
                    mlflow.log_param("database", self.database_name.name)
                    mlflow.log_metric("number_of_rules", number_of_rules)

                return number_of_rules

        except Exception as e:
            console.print(f"\n[bold red]✗ Error:[/] {e}\n", style="red")
            self.logger.error(f"An error occurred during rule discovery: {e}", exc_info=True)
            if self.use_mlflow:
                mlflow.log_param("error", str(e))
            raise

    def clean_up(self, temp_dirs: Optional[List[Path]] = None) -> None:
        """Clean up temporary directories."""
        temp_dirs = temp_dirs or [
            self.database_path / "prolog_tmp",
            self.database_path / "MATILDA_temp",
        ]
        for directory in temp_dirs:
            if directory.exists() and directory.is_dir():
                shutil.rmtree(directory)
                self.logger.info(f"Cleaned up temporary directory: {directory}")

    def generate_report(self, number_of_rules: int, result_path: Path, top_rules: List) -> None:
        """Generate a report of the run and display top rules in a beautiful table."""

        # Display top rules in Rich table
        if top_rules:
            console.print(Panel("[bold cyan]Top 5 Rules by Accuracy[/]", border_style="cyan"))

            rules_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
            rules_table.add_column("Rank", style="cyan", justify="center", width=6)
            rules_table.add_column("Rule", style="white", width=50)
            rules_table.add_column("Support", style="green", justify="right", width=10)
            rules_table.add_column("Confidence", style="yellow", justify="right", width=12)

            for idx, rule in enumerate(top_rules, start=1):
                rule_desc = rule.display.replace("\n", " ")[:50]
                rules_table.add_row(
                    f"#{idx}", rule_desc, f"{rule.accuracy:.3f}", f"{rule.confidence:.3f}"
                )

            console.print(rules_table)
            console.print()

        # Generate markdown report
        report_content = f"""
# MATILDA Run Report

**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Database:** {self.database_name.name}
**Number of Rules Discovered:** {number_of_rules}
**Results Path:** {result_path}

## Summary
- **Algorithm:** MATILDA
- **Database:** {self.database_name.name}
- **Number of Rules Discovered:** {number_of_rules}
- **Results Path:** {result_path}

## Top 5 Best Rules
Below are the top-5 best rules discovered based on their accuracy:

| Rank | Rule Description | Support  | Confidence |
|------|------------------|----------|------------|
"""

        for idx, rule in enumerate(top_rules, start=1):
            rule_desc = rule.display.replace("\n", " ").replace("|", "\\|")
            report_content += (
                f"| {idx} | {rule_desc} | {rule.accuracy:.3f} | {rule.confidence:.3f} |\n"
            )

        report_content += """

## Details
The rule discovery process was completed successfully. The discovered rules have been saved to the specified results path.
"""

        report_file_name = f"report_MATILDA_{self.database_name.stem}.md"
        report_path = self.results_dir / report_file_name

        with report_path.open("w") as report_file:
            report_file.write(report_content)

        self.logger.info(f"Generated report: {report_path}")

        console.print(
            Panel(
                f"📄 Report saved to: [cyan]{report_path}[/]\n"
                f"📊 Results saved to: [cyan]{result_path}[/]",
                title="[bold green]Files Generated[/]",
                border_style="green",
            )
        )
        console.print()

        if self.use_mlflow:
            mlflow.log_artifact(str(report_path))
            self.logger.info("Logged report as MLflow artifact.")


def setup_signal_handlers(monitor: ResourceMonitor, logger: logging.Logger) -> None:
    """Set up signal handlers for graceful shutdown."""

    def handle_signal(signum, frame):
        console.print("\n[yellow]⚠️  Shutting down gracefully...[/]")
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        monitor.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments with Rich styling."""
    parser = argparse.ArgumentParser(
        description="🔍 MATILDA - Mining Approximate Tuple-Generating Dependencies in Large Databases",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  matilda                                  Run with default config.yaml
  matilda -c custom.yaml                   Run with custom configuration
  matilda --demo perfect_database          Run with perfect university database
  matilda --demo imperfect_database        Run with imperfect university database
  matilda --version                        Show version information

For more information: https://github.com/Fran-cois/MATILDA
        """,
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Path to the configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--demo",
        choices=["perfect_database", "imperfect_database"],
        help="Run with demo database (perfect_database or imperfect_database using the university schema)",
    )
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"MATILDA CLI {__version__}"
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point of the script."""
    args = parse_arguments()

    # Display banner
    print_banner()

    # Load configuration
    with console.status("[bold cyan]Loading configuration...", spinner="dots"):
        config = load_config(args.config)

    # Extract configuration with defaults
    threshold = config.get("monitor", {}).get("memory_threshold", 15 * 1024 * 1024 * 1024)  # 15GB
    timeout = config.get("monitor", {}).get("timeout", 3600)  # 1 hour
    database_path = Path(config.get("database", {}).get("path", "data/"))
    database_name = Path(config.get("database", {}).get("name", "database.db"))
    log_dir = Path(config.get("logging", {}).get("log_dir", "logs/"))
    results_dir = Path(config.get("results", {}).get("output_dir", "results/"))

    # Handle demo mode
    if args.demo:
        demo_db_name = f"university_{args.demo}.db"
        database_path = Path("data/")
        database_name = Path(demo_db_name)
        demo_db_path = database_path / database_name
        
        # Override config for demo mode to enable rule discovery
        if "algorithm" not in config:
            config["algorithm"] = {}
        config["algorithm"]["nb_occurrence"] = 2  # Lower threshold for small databases
        config["algorithm"]["max_table"] = 2
        config["algorithm"]["max_vars"] = 6
        
        # Create demo database if it doesn't exist
        if not demo_db_path.exists():
            try:
                create_demo_database(args.demo, demo_db_path)
            except Exception as e:
                console.print(f"[red]✗ Failed to create demo database: {str(e)}[/]")
                sys.exit(1)
        else:
            console.print(f"[cyan]ℹ Using existing demo database: {demo_db_path}[/]")

    # Display configuration
    display_config_panel(config, database_name.name, database_path)

    # Initialize directories
    with console.status("[bold cyan]Initializing directories...", spinner="dots"):
        initialize_directories(results_dir, log_dir)

    # Configure logger
    logger = configure_global_logger(log_dir)

    # Determine MLflow usage
    use_mlflow = False
    if MLFLOW_AVAILABLE:
        use_mlflow = config.get("mlflow", {}).get("use", False)
        if use_mlflow:
            logger.info("MLflow is enabled.")
            console.print("[green]✓[/] MLflow is enabled\n")
    else:
        if config.get("mlflow", {}).get("use", False):
            logger.warning("MLflow is not available. Proceeding without MLflow.")
            console.print("[yellow]⚠[/] MLflow requested but not available\n")
            use_mlflow = False

    # Initialize Resource Monitor
    monitor = ResourceMonitor(threshold, timeout)
    monitor_thread = threading.Thread(target=monitor.monitor, daemon=True)
    monitor_thread.start()
    logger.debug("Resource monitor started.")

    # Setup signal handlers for graceful shutdown
    setup_signal_handlers(monitor, logger)

    # Initialize DatabaseProcessor
    processor = DatabaseProcessor(
        database_name=database_name,
        database_path=database_path,
        results_dir=results_dir,
        logger=logger,
        use_mlflow=use_mlflow,
        config=config,
    )

    console.print(Panel("[bold cyan]Starting MATILDA Discovery Process[/]", border_style="cyan"))
    console.print()
    logger.info("Starting MATILDA rule discovery process.")

    try:
        with mlflow_run_context(use_mlflow, config):
            if use_mlflow:
                logger.info("MLflow run started.")

            number_of_rules = processor.discover_rules()

            with console.status("[bold cyan]Cleaning up...", spinner="dots"):
                processor.clean_up()

            console.print(
                Panel(
                    f"[bold green]✓ Process completed successfully![/]\n\n"
                    f"[cyan]Total rules discovered:[/] [bold yellow]{number_of_rules}[/]",
                    title="[bold green]Success[/]",
                    border_style="green",
                    padding=(1, 2),
                )
            )
            logger.info("Process completed successfully.")

    except Exception as e:
        console.print(
            Panel(
                f"[bold red]✗ An error occurred:[/]\n\n{str(e)}",
                title="[bold red]Error[/]",
                border_style="red",
                padding=(1, 2),
            )
        )
        logger.error("An error occurred during the rule discovery process.", exc_info=True)
        sys.exit(1)
    finally:
        if use_mlflow and mlflow.active_run():
            mlflow.end_run()
            logger.info("MLflow run ended.")


if __name__ == "__main__":
    main()
