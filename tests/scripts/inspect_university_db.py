#!/usr/bin/env python3
"""
Inspect the fake university database.
Shows statistics and sample data from each table.
"""
import sqlite3
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def inspect_database(db_path: Path):
    """Inspect and display database contents."""
    if not db_path.exists():
        console.print(f"[red]Error: Database not found at {db_path}[/]")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    console.print(Panel(
        f"[bold cyan]Database: {db_path.name}[/]\n"
        f"[dim]Location: {db_path}[/]",
        title="[bold]📊 University Database Inspector[/]",
        border_style="cyan"
    ))
    console.print()
    
    # Summary table
    summary = Table(title="Database Summary", box=box.ROUNDED)
    summary.add_column("Table", style="cyan", no_wrap=True)
    summary.add_column("Tuples", justify="right", style="yellow")
    summary.add_column("Columns", justify="right", style="green")
    
    total_tuples = 0
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_tuples += count
        
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        summary.add_row(table, str(count), str(len(columns)))
    
    summary.add_section()
    summary.add_row("[bold]TOTAL[/]", f"[bold]{total_tuples}[/]", "")
    
    console.print(summary)
    console.print()
    
    # Sample data from each table
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        col_names = [col[1] for col in columns]
        
        cursor.execute(f"SELECT * FROM {table} LIMIT 3")
        rows = cursor.fetchall()
        
        if rows:
            data_table = Table(title=f"Sample Data: {table}", box=box.SIMPLE)
            for col_name in col_names:
                data_table.add_column(col_name, style="white")
            
            for row in rows:
                data_table.add_row(*[str(val) for val in row])
            
            console.print(data_table)
            console.print()
    
    # Foreign key relationships
    console.print(Panel(
        "[bold]Foreign Key Relationships:[/]\n\n"
        "• [cyan]student.major_dept_id[/] → department.dept_id\n"
        "• [cyan]professor.dept_id[/] → department.dept_id\n"
        "• [cyan]course.dept_id[/] → department.dept_id\n"
        "• [cyan]enrollment.student_id[/] → student.student_id\n"
        "• [cyan]enrollment.course_id[/] → course.course_id\n"
        "• [cyan]teaches.prof_id[/] → professor.prof_id\n"
        "• [cyan]teaches.course_id[/] → course.course_id\n"
        "• [cyan]advisor.prof_id[/] → professor.prof_id\n"
        "• [cyan]advisor.student_id[/] → student.student_id",
        title="[bold]🔗 Database Schema[/]",
        border_style="blue"
    ))
    
    conn.close()

def main():
    """Run the database inspector."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    db_path = project_root / "data" / "university.db"
    
    inspect_database(db_path)

if __name__ == "__main__":
    main()
