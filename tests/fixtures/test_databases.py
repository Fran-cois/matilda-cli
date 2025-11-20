"""Test database fixtures for MATILDA testing.

This module provides fixtures for creating test databases with various schemas
and data patterns for testing TGD discovery.

Database schemas inspired by:
https://zenodo.org/records/17644035
"""

import sqlite3
from pathlib import Path
from typing import Tuple, Dict
import pytest


class TestDatabaseFactory:
    """Factory for creating test databases with different schemas."""
    
    @staticmethod
    def create_simple_university_db(db_path: str) -> None:
        """
        Create a simple university database with students, courses, and enrollments.
        
        Schema:
        - students(id, name, email)
        - courses(id, title, credits)
        - enrollments(student_id, course_id, grade)
        
        Contains simple functional dependencies and join dependencies.
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE courses (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                credits INTEGER NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE enrollments (
                student_id INTEGER,
                course_id INTEGER,
                grade TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (course_id) REFERENCES courses(id)
            )
        """)
        
        # Insert sample data
        students_data = [
            (1, 'Alice Smith', 'alice@university.edu'),
            (2, 'Bob Johnson', 'bob@university.edu'),
            (3, 'Charlie Brown', 'charlie@university.edu'),
            (4, 'Diana Prince', 'diana@university.edu'),
            (5, 'Eve Wilson', 'eve@university.edu'),
        ]
        cursor.executemany("INSERT INTO students VALUES (?, ?, ?)", students_data)
        
        courses_data = [
            (101, 'Database Systems', 3),
            (102, 'Algorithms', 4),
            (103, 'Machine Learning', 3),
            (104, 'Software Engineering', 3),
        ]
        cursor.executemany("INSERT INTO courses VALUES (?, ?, ?)", courses_data)
        
        enrollments_data = [
            (1, 101, 'A'),
            (1, 102, 'B'),
            (2, 101, 'A'),
            (2, 103, 'B'),
            (3, 102, 'A'),
            (3, 103, 'A'),
            (4, 101, 'B'),
            (4, 104, 'A'),
            (5, 102, 'C'),
            (5, 103, 'B'),
        ]
        cursor.executemany("INSERT INTO enrollments VALUES (?, ?, ?)", enrollments_data)
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def create_employee_department_db(db_path: str) -> None:
        """
        Create an employee-department database.
        
        Schema:
        - departments(dept_id, dept_name, location)
        - employees(emp_id, name, salary, dept_id)
        - projects(proj_id, proj_name, budget)
        - assignments(emp_id, proj_id, hours)
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE departments (
                dept_id INTEGER PRIMARY KEY,
                dept_name TEXT NOT NULL,
                location TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE employees (
                emp_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                salary INTEGER NOT NULL,
                dept_id INTEGER,
                FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE projects (
                proj_id INTEGER PRIMARY KEY,
                proj_name TEXT NOT NULL,
                budget INTEGER NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE assignments (
                emp_id INTEGER,
                proj_id INTEGER,
                hours INTEGER,
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                FOREIGN KEY (proj_id) REFERENCES projects(proj_id)
            )
        """)
        
        # Insert data
        departments_data = [
            (1, 'Engineering', 'Building A'),
            (2, 'Sales', 'Building B'),
            (3, 'HR', 'Building C'),
        ]
        cursor.executemany("INSERT INTO departments VALUES (?, ?, ?)", departments_data)
        
        employees_data = [
            (101, 'John Doe', 75000, 1),
            (102, 'Jane Smith', 80000, 1),
            (103, 'Mike Wilson', 65000, 2),
            (104, 'Sarah Davis', 70000, 2),
            (105, 'Tom Brown', 60000, 3),
        ]
        cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?)", employees_data)
        
        projects_data = [
            (1, 'Project Alpha', 100000),
            (2, 'Project Beta', 150000),
            (3, 'Project Gamma', 80000),
        ]
        cursor.executemany("INSERT INTO projects VALUES (?, ?, ?)", projects_data)
        
        assignments_data = [
            (101, 1, 40),
            (101, 2, 20),
            (102, 1, 30),
            (103, 2, 25),
            (104, 3, 35),
        ]
        cursor.executemany("INSERT INTO assignments VALUES (?, ?, ?)", assignments_data)
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def create_retail_db(db_path: str) -> None:
        """
        Create a retail database with customers, orders, and products.
        
        Schema:
        - customers(customer_id, name, city, country)
        - products(product_id, product_name, category, price)
        - orders(order_id, customer_id, order_date)
        - order_items(order_id, product_id, quantity)
        """
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE customers (
                customer_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                city TEXT NOT NULL,
                country TEXT NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE products (
                product_id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL
            )
        """)
        
        cursor.execute("""
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                order_date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE order_items (
                order_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            )
        """)
        
        # Insert data
        customers_data = [
            (1, 'Alice Johnson', 'New York', 'USA'),
            (2, 'Bob Martin', 'London', 'UK'),
            (3, 'Charlie Lee', 'Paris', 'France'),
            (4, 'Diana Ross', 'Berlin', 'Germany'),
        ]
        cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers_data)
        
        products_data = [
            (1, 'Laptop', 'Electronics', 999.99),
            (2, 'Mouse', 'Electronics', 29.99),
            (3, 'Keyboard', 'Electronics', 79.99),
            (4, 'Chair', 'Furniture', 199.99),
            (5, 'Desk', 'Furniture', 399.99),
        ]
        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products_data)
        
        orders_data = [
            (1, 1, '2025-01-15'),
            (2, 1, '2025-02-20'),
            (3, 2, '2025-01-18'),
            (4, 3, '2025-03-10'),
            (5, 4, '2025-02-25'),
        ]
        cursor.executemany("INSERT INTO orders VALUES (?, ?, ?)", orders_data)
        
        order_items_data = [
            (1, 1, 1),
            (1, 2, 2),
            (2, 3, 1),
            (3, 1, 1),
            (3, 4, 2),
            (4, 5, 1),
            (5, 2, 3),
        ]
        cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?)", order_items_data)
        
        conn.commit()
        conn.close()


@pytest.fixture
def university_db(tmp_path: Path) -> Tuple[str, Path]:
    """Create a temporary university database for testing."""
    db_path = tmp_path / "university.db"
    TestDatabaseFactory.create_simple_university_db(str(db_path))
    return f"sqlite:///{db_path}", db_path


@pytest.fixture
def employee_db(tmp_path: Path) -> Tuple[str, Path]:
    """Create a temporary employee-department database for testing."""
    db_path = tmp_path / "employee.db"
    TestDatabaseFactory.create_employee_department_db(str(db_path))
    return f"sqlite:///{db_path}", db_path


@pytest.fixture
def retail_db(tmp_path: Path) -> Tuple[str, Path]:
    """Create a temporary retail database for testing."""
    db_path = tmp_path / "retail.db"
    TestDatabaseFactory.create_retail_db(str(db_path))
    return f"sqlite:///{db_path}", db_path


@pytest.fixture
def all_test_databases(tmp_path: Path) -> Dict[str, Tuple[str, Path]]:
    """Create all test databases and return their paths."""
    databases: Dict[str, Tuple[str, Path]] = {}
    
    # University DB
    uni_path = tmp_path / "university.db"
    TestDatabaseFactory.create_simple_university_db(str(uni_path))
    databases['university'] = (f"sqlite:///{uni_path}", uni_path)
    
    # Employee DB
    emp_path = tmp_path / "employee.db"
    TestDatabaseFactory.create_employee_department_db(str(emp_path))
    databases['employee'] = (f"sqlite:///{emp_path}", emp_path)
    
    # Retail DB
    retail_path = tmp_path / "retail.db"
    TestDatabaseFactory.create_retail_db(str(retail_path))
    databases['retail'] = (f"sqlite:///{retail_path}", retail_path)
    
    return databases
