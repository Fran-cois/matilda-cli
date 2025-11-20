"""
Integration tests for AlchemyUtility with real databases.
"""

import pytest
import os
from pathlib import Path
import sys

# Add the fixtures to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "fixtures"))

from test_databases import university_db, employee_db, retail_db
from matilda_cli.database.alchemy_utility import AlchemyUtility


class TestAlchemyUtilityWithRealDB:
    """Test AlchemyUtility with real test databases."""
    
    def test_university_db_connection(self, university_db, tmp_path):
        """Test connecting to university database."""
        db_url, db_path = university_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db:
            # Test basic connection
            assert db.base_name == "university"
            
            # Test table retrieval
            tables = db.get_table_names()
            assert set(tables) == {'students', 'courses', 'enrollments'}
            
            # Test attribute retrieval
            student_attrs = db.get_attribute_names('students')
            assert set(student_attrs) == {'id', 'name', 'email'}
            
            # Test attribute domain
            id_domain = db.get_attribute_domain('students', 'id')
            assert 'INTEGER' in id_domain or 'INT' in id_domain
            
            # Test key detection
            is_key = db.get_attribute_is_key('students', 'id')
            assert is_key is True
    
    def test_employee_db_structure(self, employee_db, tmp_path):
        """Test employee database structure."""
        db_url, db_path = employee_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db:
            tables = db.get_table_names()
            assert set(tables) == {'departments', 'employees', 'projects', 'assignments'}
            
            # Check foreign keys
            emp_attrs = db.get_attribute_names('employees')
            assert 'dept_id' in emp_attrs
            
            # Check data loading
            assert db.tables_data is not None
            assert 'employees' in db.tables_data
            assert len(db.tables_data['employees']['rows']) == 5
    
    def test_retail_db_queries(self, retail_db, tmp_path):
        """Test retail database queries."""
        db_url, db_path = retail_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db:
            # Test table names
            tables = db.get_table_names()
            assert 'customers' in tables
            assert 'orders' in tables
            assert 'products' in tables
            assert 'order_items' in tables
            
            # Test data extraction
            customers_data = db.tables_data['customers']
            assert len(customers_data['rows']) == 4
            assert 'customer_id' in customers_data['columns']
    
    def test_foreign_key_detection(self, university_db, tmp_path):
        """Test foreign key detection."""
        db_url, db_path = university_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=False
        ) as db:
            # Check if foreign keys are correctly identified
            # enrollments.student_id -> students.id
            is_fk = db.are_foreign_keys('enrollments', 'student_id', 'students', 'id')
            assert is_fk is True
            
            # Check non-foreign key
            is_fk = db.are_foreign_keys('students', 'name', 'courses', 'title')
            assert is_fk is False
    
    def test_csv_export(self, university_db, tmp_path):
        """Test CSV export functionality."""
        db_url, db_path = university_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=True,
            create_tsv=False,
            get_data=False
        ) as db:
            # Check if CSV files were created
            csv_dir = tmp_path / "university" / "csv"
            assert csv_dir.exists()
            
            students_csv = csv_dir / "students.csv"
            assert students_csv.exists()
            
            # Verify CSV content
            with open(students_csv, 'r') as f:
                lines = f.readlines()
                assert len(lines) > 0  # Header + data
    
    def test_threshold_check(self, employee_db, tmp_path):
        """Test threshold checking for attribute compatibility."""
        db_url, db_path = employee_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db:
            # Test with proper join_conditions format:
            # (table1, occurrence1, attr1, table2, occurrence2, attr2)
            join_conditions = [('employees', 0, 'dept_id', 'departments', 0, 'dept_id')]
            result = db.check_threshold(
                join_conditions=join_conditions,
                disjoint_semantics=False,
                distinct=False,
                count_over=None,
                threshold=1
            )
            # Result is the count
            assert isinstance(result, int)
    
    def test_join_row_count(self, university_db, tmp_path):
        """Test join row count calculation."""
        db_url, db_path = university_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=False
        ) as db:
            # Count join between students and enrollments
            # Format: (table1, occurrence1, attr1, table2, occurrence2, attr2)
            join_conditions = [('students', 0, 'id', 'enrollments', 0, 'student_id')]
            count = db.get_join_row_count(
                join_conditions=join_conditions,
                disjoint_semantics=False,
                distinct=False
            )
            assert count >= 0
            # We know there are 10 enrollments
            assert count <= 10
    
    def test_table_data_extraction(self, retail_db, tmp_path):
        """Test data extraction from tables."""
        db_url, db_path = retail_db
        
        with AlchemyUtility(
            db_url,
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=True
        ) as db:
            # Test that data was extracted
            assert db.tables_data is not None
            assert 'customers' in db.tables_data
            customer_data = db.tables_data['customers']
            assert 'rows' in customer_data
            assert len(customer_data['rows']) == 4
    
    def test_multiple_databases_sequential(self, tmp_path):
        """Test handling multiple databases sequentially."""
        from test_databases import TestDatabaseFactory
        
        # Create multiple databases
        db1_path = tmp_path / "db1.db"
        db2_path = tmp_path / "db2.db"
        
        TestDatabaseFactory.create_simple_university_db(str(db1_path))
        TestDatabaseFactory.create_employee_department_db(str(db2_path))
        
        # Test first database
        with AlchemyUtility(
            f"sqlite:///{db1_path}",
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=False
        ) as db1:
            tables1 = db1.get_table_names()
            assert 'students' in tables1
        
        # Test second database
        with AlchemyUtility(
            f"sqlite:///{db2_path}",
            database_path=str(tmp_path),
            create_index=False,
            create_csv=False,
            create_tsv=False,
            get_data=False
        ) as db2:
            tables2 = db2.get_table_names()
            assert 'employees' in tables2
            assert 'students' not in tables2
