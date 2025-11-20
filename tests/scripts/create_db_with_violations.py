#!/usr/bin/env python3
"""
Create a database with DIRECT violations of referential integrity.

Key insight: To get imperfect rules, we need violations that actually break
the discovered rules. E.g., if MATILDA discovers "enrollment → student",
we need an enrollment with a student_id that doesn't exist in student table.
"""
import sqlite3
from pathlib import Path

def create_db_with_direct_violations(db_path: Path):
    """Create database with referential integrity violations."""
    if db_path.exists():
        db_path.unlink()
    
    conn = sqlite3.connect(str(db_path))
    # IMPORTANT: disable foreign key enforcement to allow violations
    conn.execute("PRAGMA foreign_keys = OFF")
    cursor = conn.cursor()
    
    print("Creating database with DIRECT referential integrity violations...")
    
    # Create tables
    cursor.execute('''CREATE TABLE department (
        dept_id INTEGER PRIMARY KEY,
        dept_name TEXT NOT NULL
    )''')
    
    cursor.execute('''CREATE TABLE professor (
        prof_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        dept_id INTEGER,
        FOREIGN KEY(dept_id) REFERENCES department(dept_id)
    )''')
    
    cursor.execute('''CREATE TABLE student (
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        year INTEGER,
        dept_id INTEGER,
        FOREIGN KEY(dept_id) REFERENCES department(dept_id)
    )''')
    
    cursor.execute('''CREATE TABLE course (
        course_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        dept_id INTEGER,
        FOREIGN KEY(dept_id) REFERENCES department(dept_id)
    )''')
    
    cursor.execute('''CREATE TABLE enrollment (
        enrollment_id INTEGER PRIMARY KEY,
        student_id INTEGER,
        course_id INTEGER,
        FOREIGN KEY(student_id) REFERENCES student(student_id),
        FOREIGN KEY(course_id) REFERENCES course(course_id)
    )''')
    
    cursor.execute('''CREATE TABLE advisor (
        advisor_id INTEGER PRIMARY KEY,
        prof_id INTEGER,
        student_id INTEGER,
        FOREIGN KEY(prof_id) REFERENCES professor(prof_id),
        FOREIGN KEY(student_id) REFERENCES student(student_id)
    )''')
    
    # Insert data
    
    # 2 departments
    cursor.executemany('INSERT INTO department VALUES (?, ?)', [
        (1, 'CS'),
        (2, 'Math'),
    ])
    
    # 10 professors: 5 CS, 5 Math
    professors = []
    for dept in range(1, 3):
        for p in range(1, 6):
            prof_id = (dept - 1) * 5 + p
            professors.append((prof_id, f'Prof_Dept{dept}_{p}', dept))
    cursor.executemany('INSERT INTO professor VALUES (?, ?, ?)', professors)
    
    # 50 real students (will add fake ones later)
    students = []
    for dept in range(1, 3):
        for s in range(1, 26):
            student_id = (dept - 1) * 25 + s
            students.append((student_id, f'Student_{dept}_{s}', 1 + (s % 4), dept))
    cursor.executemany('INSERT INTO student VALUES (?, ?, ?, ?)', students)
    
    # 10 courses: 5 CS, 5 Math
    courses = []
    for dept in range(1, 3):
        for c in range(1, 6):
            course_id = (dept - 1) * 5 + c
            courses.append((course_id, f'Course_Dept{dept}_{c}', dept))
    cursor.executemany('INSERT INTO course VALUES (?, ?, ?)', courses)
    
    # 95 enrollments from REAL students (96/100 = 0.96 if 4 students missing)
    enrollments = []
    enrollment_id = 1
    for student_id in range(1, 51):
        # Skip 4 students
        if student_id in [10, 20, 30, 40]:
            continue
        
        # Each student takes 2-4 courses
        for course_id in range(1, 1 + (student_id % 4)):
            enrollments.append((enrollment_id, student_id, course_id))
            enrollment_id += 1
    
    # Add enrollments from FAKE students (that don't exist in student table)
    # These are the VIOLATIONS
    # Add 5 enrollments from non-existent students
    for fake_student_id in [999, 998, 997, 996, 995]:
        for c in range(1, 3):
            enrollments.append((enrollment_id, fake_student_id, c))
            enrollment_id += 1
    
    cursor.executemany('INSERT INTO enrollment VALUES (?, ?, ?)', enrollments)
    
    # 45 advisor relationships (90% coverage)
    advisors = []
    advisor_id = 1
    for student_id in range(1, 51):
        # Skip some students
        if student_id % 10 == 0:
            continue
        
        prof_id = ((student_id - 1) % 10) + 1
        advisors.append((advisor_id, prof_id, student_id))
        advisor_id += 1
    
    # Add advisor relationships from FAKE students
    for fake_student_id in [999, 998, 997]:
        advisors.append((advisor_id, 1, fake_student_id))
        advisor_id += 1
    
    cursor.executemany('INSERT INTO advisor VALUES (?, ?, ?)', advisors)
    
    conn.commit()
    conn.close()
    
    print(f"\n✓ Database with direct violations created!")
    print(f"\nStatistics:")
    print(f"  - Real students: 50")
    print(f"  - Students in enrollment table: 51 (46 real + 5 fake)")
    print(f"  - Professors: 10")
    print(f"  - Courses: 10")
    print(f"  - Enrollments: {len(enrollments)}")
    print(f"  - Advisor relationships: {len(advisors)}")
    
    print(f"\nVIOLATIONS (should cause < 1.0 metrics):")
    print(f"  ✗ Rule 'enrollment → student' has 5/51 violations (90.2% accuracy)")
    print(f"  ✗ Rule 'advisor → student' has 3/48 violations (93.75% accuracy)")

def main():
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    db_path = data_dir / "university.db"
    create_db_with_direct_violations(db_path)
    print(f"\nDatabase: {db_path}")

if __name__ == "__main__":
    main()
