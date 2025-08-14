# GreenGate Enlistment Portal

## Overview

GreenGate is a university course enlistment portal designed to simplify the process of course enlistment for students. The platform allows users to browse available classes, add courses to a cart, and enlist in courses. GreenGate was built using **Flask**, **SQLite**, and **Bootstrap**. 

## Features
### User Authentication
User authentication begins with the registration and login. I made use of the `werkzeug.security library` to hash the passwords to avoid storing them directly for added security.

- Empty input also triggers a flash messages prompting users to enter required information.
- Invalid ID numbers or incorrect passwords result in an error message being flashed.
- Sessions are cleared upon login to prevent conflicts or unauthorized access.
- Regex syntax was used for email pattern verification.

### Available Courses & Cart Management
Students can view all available courses along with details like course code, title, units, days, times, and enrollment counts. Classes with full capacity are automatically filtered out from the listing.

- Students can add courses to a temporary cart for enlistment.
- Duplicate additions are prevented by checking if a course is already in the cart or if the student is already enlisted.
- Students can see the total units on their cart to help them decide on classes.
- Users can also remove courses from the cart in the same page.
- Python and JavaScript were combined to simplify the user experience. 

### Enlistment Logic
The enlistment process checks in real-time whether a class still has available slots before committing a student’s enlistment.

- Each cart item is verified against the current number of enlisted students.
- Users are notified when one of their classes are full upon trying to enlist.
- Upon successful enlistment, the course is added to the enlistments table, the cart entry is removed, and the class’s enlisted count is incremented.

## Database Schema
The application uses sqlite3 with the following tables:
- **users:** Stores student and faculty information, including hashed passwords.
- **classes:** Contains course details such as code, title, units, schedule, and enrollment limits.
- **carts:** Temporary storage of selected courses before enlistment.
- **enrollments:** Records student enrollments, statuses, and timestamps.
