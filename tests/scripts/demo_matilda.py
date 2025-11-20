#!/usr/bin/env python3
"""
MATILDA Demo - Executes the algorithm and shows logs.
This runs the MATILDA algorithm with actual violation-based metrics.
"""
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import subprocess
import sys
import time
import json

console = Console()

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

def show_database_info(db_path):
    """Show database information."""
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    info_table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    info_table.add_column("Setting", style="cyan")
    info_table.add_column("Value", style="yellow")
    
    info_table.add_row("🗄️  Database", db_path.name)
    info_table.add_row("📁 Path", str(db_path))
    info_table.add_row("📊 Tables", str(len(tables)))
    
    total = 0
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total += cursor.fetchone()[0]
    
    info_table.add_row("📈 Total Tuples", str(total))
    info_table.add_row("🔢 Tables List", ", ".join(tables[:3]) + "...")
    
    conn.close()
    
    console.print(Panel(
        info_table,
        title="[bold blue]📊 Database Information[/]",
        border_style="blue",
        padding=(1, 2)
    ))
    console.print()

def run_matilda(config_file, results_dir):
    """Actually run MATILDA and capture output."""
    
    console.print(Panel(
        "[bold cyan]🚀 Executing MATILDA Algorithm[/]\n"
        "[dim]This will take some time depending on database size...[/]",
        border_style="cyan"
    ))
    console.print()
    
    # Prepare command
    cmd = [
        sys.executable,
        "-m", "matilda_cli",
        "--config", str(config_file)
    ]
    
    console.print(f"[dim]Command: {' '.join(cmd)}[/]\n")
    
    # Run MATILDA
    console.print("[yellow]⏳ Running MATILDA (this may take a minute)...[/]\n")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes max
        )
        
        execution_time = time.time() - start_time
        
        # Show execution results
        if result.returncode == 0:
            console.print(Panel(
                f"[bold green]✓ MATILDA Executed Successfully![/]\n\n"
                f"[cyan]Execution time:[/] {execution_time:.2f}s",
                border_style="green",
                padding=(1, 2)
            ))
            console.print()
            
            # Show logs
            console.print(Panel(
                "[bold]📋 MATILDA Output Log[/]",
                border_style="blue"
            ))
            
            if result.stdout:
                # Truncate if too long
                lines = result.stdout.split('\n')
                if len(lines) > 30:
                    console.print("[dim]" + '\n'.join(lines[:15]) + "[/]")
                    console.print(f"\n[dim]... ({len(lines) - 30} lines omitted) ...[/]\n")
                    console.print("[dim]" + '\n'.join(lines[-15:]) + "[/]")
                else:
                    console.print("[dim]" + result.stdout + "[/]")
            
            console.print()
            
            return True, execution_time
            
        else:
            console.print(Panel(
                f"[bold red]✗ MATILDA Failed![/]\n\n"
                f"[yellow]Error:[/] {result.stderr[:200]}...",
                border_style="red"
            ))
            return False, execution_time
            
    except subprocess.TimeoutExpired:
        console.print(Panel(
            "[bold red]✗ MATILDA Timed Out![/]\n\n"
            "The execution exceeded 5 minutes.",
            border_style="red"
        ))
        return False, 0
    except Exception as e:
        console.print(Panel(
            f"[bold red]✗ Error Running MATILDA![/]\n\n"
            f"[yellow]{str(e)}[/]",
            border_style="red"
        ))
        return False, 0

def show_results(results_dir):
    """Show discovered rules from results."""
    
    # Find result files
    json_files = list(results_dir.glob("*_results.json"))
    md_files = list(results_dir.glob("report_*.md"))
    
    if not json_files:
        console.print("[yellow]⚠ No result files found[/]\n")
        return
    
    console.print(Panel(
        "[bold cyan]📊 Discovered Rules[/]",
        border_style="cyan"
    ))
    
    # Read JSON results
    json_file = json_files[0]
    try:
        with open(json_file) as f:
            data = json.load(f)
        
        # Check if data is a list (direct array) or dict with 'rules' key
        rules = data if isinstance(data, list) else data.get('rules', [])
        
        if rules and len(rules) > 0:
            # Show top 5 rules
            rules_table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
            rules_table.add_column("Rank", style="cyan", justify="center", width=6)
            rules_table.add_column("Rule", style="white", width=60)
            rules_table.add_column("Accuracy\n(Body→Head)", style="green", justify="right", width=12)
            rules_table.add_column("Coverage\n(Head←Body)", style="yellow", justify="right", width=14)
            
            for idx, rule in enumerate(rules[:10], start=1):
                # Get display string directly or construct from body/head
                display = rule.get('display', 'N/A')
                
                # Truncate if too long
                if len(display) > 60:
                    display = display[:57] + "..."
                
                accuracy = f"{rule.get('accuracy', 0):.3f}"
                confidence = f"{rule.get('confidence', 0):.3f}"
                
                rules_table.add_row(f"#{idx}", display, accuracy, confidence)
            
            console.print(rules_table)
            console.print()
            
            # Show summary
            total_rules = len(rules)
            console.print(Panel(
                f"[bold green]✓ Total Rules Discovered:[/] [bold yellow]{total_rules}[/]",
                border_style="green"
            ))
        else:
            console.print("[yellow]⚠ No rules found in results[/]\n")
            
    except Exception as e:
        console.print(f"[red]Error reading results: {e}[/]\n")
    
    console.print()
    
    # Show file locations
    files_table = Table(show_header=False, box=box.SIMPLE)
    files_table.add_column("File", style="cyan")
    files_table.add_column("Path", style="dim")
    
    for f in json_files:
        files_table.add_row("📊 JSON Results", str(f))
    for f in md_files:
        files_table.add_row("📄 Markdown Report", str(f))
    
    console.print(Panel(
        files_table,
        title="[bold]📁 Generated Files[/]",
        border_style="blue"
    ))
    console.print()

def show_logs(log_dir):
    """Show recent log files."""
    log_files = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not log_files:
        console.print("[dim]No log files found[/]\n")
        return
    
    console.print(Panel(
        "[bold]📝 Recent Log Files[/]",
        border_style="yellow"
    ))
    
    for log_file in log_files[:3]:
        size = log_file.stat().st_size
        mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(log_file.stat().st_mtime))
        console.print(f"[cyan]•[/] {log_file.name} [dim]({size} bytes, {mtime})[/]")
    
    console.print()
    
    # Show tail of most recent log
    if log_files:
        console.print(f"[bold]Last 10 lines of {log_files[0].name}:[/]")
        with open(log_files[0]) as f:
            lines = f.readlines()
            for line in lines[-10:]:
                console.print(f"[dim]{line.rstrip()}[/]")
    
    console.print()

def main():
    """Run MATILDA demo."""
    # Set up paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    db_path = project_root / "data" / "university.db"
    config_file = project_root / "config_demo.yaml"
    results_dir = project_root / "results"
    log_dir = project_root / "logs"
    
    # Check if database exists
    if not db_path.exists():
        console.print(Panel(
            "[bold red]Error:[/] Database not found!\n\n"
            "Please run: [cyan]python scripts/generate_fake_university_db.py[/]",
            title="[bold red]❌ Missing Database[/]",
            border_style="red"
        ))
        return
    
    # Print banner
    print_banner()
    
    # Show database info
    show_database_info(db_path)
    
    # Run MATILDA
    success, exec_time = run_matilda(config_file, results_dir)
    
    if success:
        # Show results
        show_results(results_dir)
        
        # Show logs
        if log_dir.exists():
            show_logs(log_dir)
        
        console.print(Panel(
            f"[bold green]🎉 Demo Complete![/]\n\n"
            f"[cyan]Execution time:[/] {exec_time:.2f}s\n"
            f"[cyan]Database:[/] {db_path}\n"
            f"[cyan]Results:[/] {results_dir}",
            title="[bold green]✓ Success[/]",
            border_style="green",
            padding=(1, 2)
        ))
    else:
        console.print(Panel(
            "[bold red]Demo failed - see errors above[/]",
            border_style="red"
        ))

if __name__ == "__main__":
    main()
