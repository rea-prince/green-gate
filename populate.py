import sqlite3
from faker import Faker
import random

# Setup
fake = Faker()
conn = sqlite3.connect('enrollment.db')
cursor = conn.cursor()

# Populate Users & Students
roles = ['student', 'admin', 'faculty']

for _ in range(10):  # 10 sample users
    username = fake.user_name()
    password_hash = fake.sha256()
    role = 'student'  # keep most as students for testing
    
    cursor.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (?, ?, ?)
    """, (username, password_hash, role))
    
    user_id = cursor.lastrowid
    
    if role == 'student':
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        cursor.execute("""
            INSERT INTO students (user_id, first_name, last_name, email)
            VALUES (?, ?, ?, ?)
        """, (user_id, first_name, last_name, email))

# Populate Courses
for _ in range(5):
    course_code = f"CSE{random.randint(100,499)}"
    title = fake.catch_phrase()
    description = fake.text(max_nb_chars=100)
    credits = random.choice([2, 3, 4])
    max_students = random.randint(20, 50)
    schedule = random.choice(["Mon 9-11AM", "Tue 1-3PM", "Wed 2-4PM"])
    
    cursor.execute("""
        INSERT INTO courses (course_code, title, description, credits, max_students, schedule)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (course_code, title, description, credits, max_students, schedule))

# Populate Enrollments
student_ids = [row[0] for row in cursor.execute("SELECT id FROM students")]
course_ids = [row[0] for row in cursor.execute("SELECT id FROM courses")]

for student_id in student_ids:
    for course_id in random.sample(course_ids, k=random.randint(1, 3)):
        status = 'enrolled'
        cursor.execute("""
            INSERT INTO enrollments (student_id, course_id, status)
            VALUES (?, ?, ?)
        """, (student_id, course_id, status))

# Commit changes
conn.commit()
conn.close()

print("Database populated with random test data!")
