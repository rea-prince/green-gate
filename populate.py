import sqlite3
from faker import Faker
from werkzeug.security import generate_password_hash
import random

# Faker setup (Philippines locale)
fake = Faker('en_PH')

# Connect to DB
conn = sqlite3.connect('enrollment.db')
cursor = conn.cursor()

# -----------------------
# Helper: Generate DLSU-style ID number
# Format: YYNNNNN (Year + 5 random digits)
# -----------------------
def generate_dlsu_id(existing_ids):
    while True:
        year = str(random.randint(19, 25)).zfill(2)  # 2019-2025
        number = str(random.randint(0, 99999)).zfill(5)
        student_id = int(year + number)
        if student_id not in existing_ids:
            existing_ids.add(student_id)
            return student_id

# -----------------------
# Populate Users
# -----------------------
roles = ["student", "faculty", "admin"]
existing_ids = set()
users_data = []

for _ in range(30):  # 30 random users
    role = random.choices(roles, weights=[0.7, 0.2, 0.1])[0]  # mostly students
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = f"{first_name.lower()}.{last_name.lower()}@dlsu.edu.ph"
    username = f"{first_name.lower()}_{last_name.lower()}"
    password_hash = generate_password_hash("password123")
    user_id = generate_dlsu_id(existing_ids)
    users_data.append((user_id, username, password_hash, role, first_name, last_name, email))

cursor.executemany("""
INSERT INTO users (id, username, password_hash, role, first_name, last_name, email)
VALUES (?, ?, ?, ?, ?, ?, ?)
""", users_data)

# -----------------------
# Populate Courses
# -----------------------
courses = [
    ("CCPROG1", "Computer Programming 1", "Introduction to programming concepts", 3, 40, "Mon 9-11AM"),
    ("CCPROG2", "Computer Programming 2", "Intermediate programming concepts", 3, 40, "Tue 1-3PM"),
    ("CCDSALG", "Data Structures & Algorithms", "In-depth study of data structures", 3, 35, "Wed 10AM-12PM"),
    ("CCDBSYS", "Database Systems", "Relational database concepts", 3, 35, "Thu 9-11AM"),
    ("CCNETWK", "Computer Networks", "Network fundamentals and protocols", 3, 30, "Fri 1-3PM")
]

cursor.executemany("""
INSERT INTO courses (course_code, title, description, credits, max_students, schedule)
VALUES (?, ?, ?, ?, ?, ?)
""", courses)

# -----------------------
# Populate Enrollments (only students)
# -----------------------
student_ids = [u[0] for u in users_data if u[3] == "student"]
course_ids = [row[0] for row in cursor.execute("SELECT id FROM courses").fetchall()]

enrollments = []
for student_id in student_ids:
    num_courses = random.randint(1, 3)  # each student enrolls in 1-3 courses
    chosen_courses = random.sample(course_ids, num_courses)
    for course_id in chosen_courses:
        enrollments.append((student_id, course_id, "enrolled"))

cursor.executemany("""
INSERT INTO enrollments (student_id, course_id, status)
VALUES (?, ?, ?)
""", enrollments)

# Commit changes
conn.commit()
conn.close()

print("Database populated successfully!")
