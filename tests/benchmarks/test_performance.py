"""Benchmark tests for MATILDA performance with test databases.

This module contains performance benchmark tests for the MATILDA algorithm
using various test database schemas.
"""

import pytest
import time
import psutil
import os
from pathlib import Path

from matilda_cli.algorithms.matilda import MATILDA
from matilda_cli.database.alchemy_utility import AlchemyUtility


def _format_benchmark_results(
    title: str,
    rule_count: int,
    duration: float,
    memory_mb: float | None = None
) -> None:
    """Format and print benchmark results.
    
    Args:
        title: Benchmark title
        rule_count: Number of rules discovered
        duration: Duration in seconds
        memory_mb: Optional memory usage in MB
    """
    print(f"\n{'='*50}")
    print(f"Benchmark: {title}")
    print(f"{'='*50}")
    print(f"Rules discovered: {rule_count}")
    print(f"Duration: {duration:.2f} seconds")
    if memory_mb is not None:
        print(f"Memory used: {memory_mb:.2f} MB")
        rules_per_sec = rule_count / duration if duration > 0 else 0
        print(f"Rules/second: {rules_per_sec:.2f}")
    print(f"{'='*50}\n")


class TestMATILDABenchmarks:
    """Benchmark tests for MATILDA performance."""
    
    @pytest.mark.benchmark
    def test_benchmark_university_db(self, university_db, tmp_path):
        """Benchmark MATILDA on university database."""
        db_url, db_path = university_db
        
        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            matilda = MATILDA(database=db_inspector)
            
            rule_count = 0
            for rule in matilda.discover_rules():
                rule_count += 1
                if rule_count >= 20:  # Limit for benchmark
                    break
            
            end_time = time.time()
            end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB
            
            duration = end_time - start_time
            memory_used = end_memory - start_memory
            
            _format_benchmark_results(
                "University Database",
                rule_count,
                duration,
                memory_used
            )
            
            # Assert reasonable performance
            assert duration < 60, "Discovery should complete in less than 60 seconds"
            assert memory_used < 500, "Memory usage should be less than 500 MB"
    
    @pytest.mark.benchmark
    def test_benchmark_employee_db(self, employee_db, tmp_path):
        """Benchmark MATILDA on employee database."""
        db_url, db_path = employee_db
        
        start_time = time.time()
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            matilda = MATILDA(database=db_inspector, settings={'nb_occurrence': 3})
            
            rule_count = 0
            for rule in matilda.discover_rules():
                rule_count += 1
                if rule_count >= 15:
                    break
            
            duration = time.time() - start_time
            
            _format_benchmark_results("Employee Database", rule_count, duration)
            
            assert duration < 60, "Discovery should complete in less than 60 seconds"
    
    @pytest.mark.benchmark
    def test_benchmark_retail_db(self, retail_db, tmp_path):
        """Benchmark MATILDA on retail database."""
        db_url, db_path = retail_db
        
        start_time = time.time()
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            matilda = MATILDA(database=db_inspector)
            
            rule_count = 0
            for rule in matilda.discover_rules():
                rule_count += 1
                if rule_count >= 10:
                    break
            
            duration = time.time() - start_time
            
            _format_benchmark_results("Retail Database", rule_count, duration)
            
            assert duration < 60, "Discovery should complete in less than 60 seconds"
    
    @pytest.mark.benchmark
    def test_database_loading_performance(self, university_db, tmp_path):
        """Benchmark database loading and initialization."""
        db_url, db_path = university_db
        
        start_time = time.time()
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=True,
            create_tsv=False,
            get_data=True
        ) as db_inspector:
            tables = db_inspector.get_table_names()
            
            load_time = time.time() - start_time
            
            print(f"\n{'='*50}")
            print(f"Benchmark: Database Loading")
            print(f"{'='*50}")
            print(f"Tables loaded: {len(tables)}")
            print(f"Load time: {load_time:.2f} seconds")
            print(f"{'='*50}\n")
            
            assert load_time < 10, "Database should load in less than 10 seconds"
    
    @pytest.mark.benchmark
    def test_csv_export_performance(self, employee_db, tmp_path):
        """Benchmark CSV export performance."""
        db_url, db_path = employee_db
        
        start_time = time.time()
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=True,
            create_tsv=False,
            get_data=False
        ) as db_inspector:
            export_time = time.time() - start_time
            
            print(f"\n{'='*50}")
            print(f"Benchmark: CSV Export")
            print(f"{'='*50}")
            print(f"Export time: {export_time:.2f} seconds")
            print(f"{'='*50}\n")
            
            assert export_time < 5, "CSV export should complete in less than 5 seconds"
    
    @pytest.mark.benchmark
    def test_comparative_benchmark(self, all_test_databases, tmp_path):
        """Compare performance across all test databases."""
        results = []
        
        for db_name, (db_url, db_path) in all_test_databases.items():
            start_time = time.time()
            
            with AlchemyUtility(
                db_url,
                database_path=str(tmp_path),
                create_index=False,
                create_csv=False,
                create_tsv=False,
                get_data=True
            ) as db_inspector:
                tables = db_inspector.get_table_names()
                
                matilda = MATILDA(database=db_inspector)
                
                rule_count = 0
                for rule in matilda.discover_rules():
                    rule_count += 1
                    if rule_count >= 5:  # Limit for comparison
                        break
                
                duration = time.time() - start_time
                
                results.append({
                    'database': db_name,
                    'tables': len(tables),
                    'rules': rule_count,
                    'time': duration
                })
        
        # Print comparative results
        print(f"\n{'='*50}")
        print(f"Comparative Benchmark Results")
        print(f"{'='*50}")
        for result in results:
            print(f"{result['database']:12} | Tables: {result['tables']:2} | "
                  f"Rules: {result['rules']:3} | Time: {result['time']:6.2f}s")
        print(f"{'='*50}\n")
        
        # All should complete reasonably fast
        for result in results:
            assert result['time'] < 60, f"{result['database']} took too long"
