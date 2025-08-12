import sqlite3
import random
from datetime import datetime
from werkzeug.security import generate_password_hash

DB_PATH = "enrollment.db"

def reset_tables():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Drop tables if exist
    cursor.execute("DROP TABLE IF EXISTS carts")
    cursor.execute("DROP TABLE IF EXISTS classes")
    cursor.execute("DROP TABLE IF EXISTS users")

    # Recreate tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'admin', 'faculty')),
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        section TEXT NOT NULL,
        units INTEGER NOT NULL,
        slots INTEGER NOT NULL,
        days TEXT NOT NULL,
        start_time INTEGER NOT NULL,
        end_time INTEGER NOT NULL
    )
    """)

    # After creating classes table
    cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'classes'")
    cursor.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('classes', 1999)")


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS carts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (class_id) REFERENCES classes(id)
    )
    """)

    connection.commit()
    connection.close()

def generate_dlsu_id(entry_year: int):
    # entry_year is a 4-digit year, e.g. 2025
    year_suffix = str(entry_year)[-2:]  # last two digits of the year
    random_part = f"{random.randint(0, 99999):05d}"
    return int(f"1{year_suffix}{random_part}")

def populate_users():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    # Example users to add
    users = [
        # role, first_name, last_name, entry_year
        ("student", "Juan", "Dela Cruz", 2025),
        ("student", "Maria", "Santos", 2024),
        ("faculty", "Anna", "Reyes", 0),    # No entry year needed for faculty/admin
        ("admin", "Jose", "Rizal", 0),
    ]

    for role, first_name, last_name, year in users:
        if role == "student":
            user_id = generate_dlsu_id(year)
        else:
            user_id = None  # Let autoincrement for non-students or generate sequential ID if preferred

        username = f"{first_name.lower()}_{last_name.lower()}"
        email = None
        if role == "student":
            email = f"{username}@dlsu.edu.ph"

        password_hash = generate_password_hash("password123")  # default password for example

        if user_id:
            cursor.execute("""
                INSERT INTO users (id, username, password_hash, role, first_name, last_name, email)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, password_hash, role, first_name, last_name, email))
        else:
            # For admin and faculty, let id autoincrement (pass NULL)
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, first_name, last_name, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (username, password_hash, role, first_name, last_name, email))

    connection.commit()
    connection.close()

def populate_classes():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    classes = [
        ("CS101", "Introduction to Computer Science", "Basics of CS", "A", 3, 40, "MWF", 800, 930),
        ("MATH201", "Calculus I", "Differential calculus", "B", 4, 35, "TTh", 900, 1030),
        ("PHYS150", "General Physics", "Mechanics and Thermodynamics", "A", 4, 30, "MWF", 1100, 1230),
        ("ENG101", "English Literature", "Literature study", "C", 3, 25, "TTh", 1300, 1430),
        ("HIST210", "World History", "History from ancient to modern times", "B", 3, 40, "MWF", 1400, 1530),
        ("BIO110", "Biology Basics", "Intro to Biology", "A", 3, 30, "MWF", 1000, 1130),
        ("CHEM101", "General Chemistry", "Chemistry fundamentals", "B", 4, 35, "TTh", 800, 930),
    ]

    for c in classes:
        cursor.execute("""
            INSERT INTO classes (course_code, title, description, section, units, slots, days, start_time, end_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, c)

    connection.commit()
    connection.close()

def main():
    print("Resetting tables...")
    reset_tables()
    print("Populating users...")
    populate_users()
    print("Populating classes...")
    populate_classes()
    print("Done.")

if __name__ == "__main__":
    main()
