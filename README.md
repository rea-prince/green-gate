# GreenGate Enlistment Portal

## Overview

GreenGate is a university course enlistment portal designed to simplify the process of course enlistment for students. The platform allows users to browse available classes, add courses to a cart, and enlist in courses. GreenGate was built using **Flask**, **SQLite**, and **Bootstrap**. 

---
## Features
### User Authentication
User authentication begins with the registration and login features that I implemented from the Finance problem set. I added extra user information fields on the databases as institutions normally request more than just a username and password. Like the finance problem set, I made use of the `werkzeug.security library` to hash the passwords to avoid storing them directly.

- Empty input fields trigger flash messages prompting users to enter required information.
- Invalid ID numbers or incorrect passwords also generate error notifications.
- Sessions are cleared upon login to prevent conflicts or unauthorized access.
- Regex syntax was used for email pattern verification.

### Available Courses & Cart Management
Students can view all available courses along with details like course code, title, units, days, times, and enrollment counts. Classes with full capacity are automatically filtered out from the listing.

- Students can add courses to a temporary cart for enlistment. Duplicate additions are prevented by checking if a course is already in the cart or if the student is already enlisted. I also implemented a way of counting the amount of units a user has on their cart to help them decide on their courses.
- Users can also remove courses from the cart in the same page.
- Had to handle several errors when implementing the page, especially when combining JavaScript on the frontend and Python on the backend just to implement the search functionality. 

---
### Enlistment Logic
The enlistment process checks in real-time whether a class still has available slots before committing a student’s enlistment.

- Each cart item is verified against the current number of enlisted students.
- Users are notified when one of their classes are full upon trying to enlist.
- Upon successful enlistment, the course is added to the enlistments table, the cart entry is removed, and the class’s enlisted count is incremented.

---
## My Bootstrap experience
I initially attempted to design the webpage myself as I didn't make use of bootstrap on week 8. That was until I discovered that I could simply `href` Bootstsrap and copy their preexisting templates for certain tags which made making the website more aesthetically pleasing without having to go through a lot of trouble. After that, I included a free theme I found online to customize Bootstrap.

---
## Technical Challenges & Solutions

To expand on the issues and errors I encountered:
1. A majority of the issues stemmed from error handling, primarily with the `cursor.execute` function not being exactly akin to the `db.execute` that was used in the CS50 workspace. Unlike in CS50, the function needed precursor lines (which I did not exactly understand), and I had a problem with using what the function retrieved to compare to other values.
2. Initially, flash messages for errors during login or enlistment did not appear because templates did not include the proper `get_flashed_messages()` block. 
3. After introducing forms and dynamic tables, the search script stopped working because table cell indices and selectors did not match the updated structure. This was fixed by correctly referencing table cells in the JavaScript loop.
4. I tried my best to include a background image on the home page, but CSS would not cooperate with the scaling. Ultimately, I gave up on it.

---
## Database Schema
The application uses sqlite3 with the following tables:
- **users:** Stores student and faculty information, including hashed passwords.
- **classes:** Contains course details such as code, title, units, schedule, and enrollment limits.
- **carts:** Temporary storage of selected courses before enlistment.
- **enrollments:** Records student enrollments, statuses, and timestamps.

---
## Conclusion
Project Green Gate taught me a lot about implementing different systems with each other. Though initially I tried to make use of JavaScript more, I found that my strength was in back-end solutions. I also went through a lot of stress debugging the error handling of each function, as with each function I implemented, I realized there were more exceptions. Overall, this project was a slap to the face telling me that I need to improve my CSS, JavaScript, and objct-oriented programming in general. I went through many stages of disappointnment and relief, but the mmost important thing I learned was how to solve unique problems that were outside the scope of the course.