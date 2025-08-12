import sqlite3
import random
from datetime import datetime, timedelta

def reset_and_populate_enrollments():
    connection = sqlite3.connect('enrollment.db')
    cursor = connection.cursor()

    # Clear enrollments table (reset autoincrement as well)
    cursor.execute("DELETE FROM enrollments;")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='enrollments';")
    connection.commit()

    # Get all student user ids
    cursor.execute("SELECT id FROM users WHERE role = 'student';")
    student_ids = [row[0] for row in cursor.fetchall()]

    # Get all class ids
    cursor.execute("SELECT id FROM classes;")
    class_ids = [row[0] for row in cursor.fetchall()]

    statuses = ['enrolled', 'dropped', 'waitlisted']

    enrollments_added = 0

    # For each student, enroll them randomly in 3-5 classes
    for student_id in student_ids:
        selected_classes = random.sample(class_ids, k=min(len(class_ids), random.randint(3, 5)))
        for class_id in selected_classes:
            status = random.choices(statuses, weights=[80, 10, 10])[0]
            random_days_ago = random.randint(0, 60)
            enrolled_at = datetime.now() - timedelta(days=random_days_ago)
            enrolled_at_str = enrolled_at.strftime('%Y-%m-%d %H:%M:%S')

            try:
                cursor.execute("""
                    INSERT INTO enrollments (student_id, class_id, status, enrolled_at)
                    VALUES (?, ?, ?, ?);
                """, (student_id, class_id, status, enrolled_at_str))
                enrollments_added += 1
            except sqlite3.IntegrityError:
                # Skip duplicates if any
                pass

    connection.commit()
    connection.close()

    print(f"Enrollments reset and {enrollments_added} new records added.")

# Run the function
reset_and_populate_enrollments()
