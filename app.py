import os
import sqlite3
import re
from flask import Flask, redirect, url_for, render_template, request, session, flash, get_flashed_messages
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash



# configure application
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# configure login requirement
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session["user_id"]:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # initialize db
        connection = sqlite3.connect('enrollment.db')
        cursor = connection.cursor()

        # get id number and email
        id_number = request.form.get("id_number").strip()
        email_address = request.form.get("emailaddress").strip()

        # set regex for email
        email_pattern = r"^[^@]+@[^@]+\.[^@]+$"

        # get first and last name
        firstname = request.form.get("firstname").strip()
        lastname = request.form.get("lastname").strip()

        # get password
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        # get user role
        user_role = request.form.get("role", "")
        possible_roles = ["student", "faculty", "admin"]

        # validity
        # if any field is blank
        if not id_number or not email_address or not firstname or not lastname or not password or not confirmation or not user_role:
            flash("Please enter your complete information")
            return redirect("/register")
        # validate ID number
        if not id_number.isdigit():
            flash("Your ID number must be a number")
            return redirect("/register")
        # validate email address
        if not re.match(email_pattern, email_address):
            flash("Your email address is invalid")
            return redirect("/register")
        email_check = cursor.execute("SELECT email FROM users WHERE email = ?", (email_address,)).fetchone()
        if email_check:
            flash("Your email address is already registered")
            return redirect("/register")

        # if password and confirmation don't match
        if password != confirmation:
            flash("Passwords do not match")
            return redirect("/register")
        # check user role is valid
        if user_role not in possible_roles:
            flash("Please select a valid role")
            return redirect("/register")

        # availability
        # if ID or username are already in db
        id_check = cursor.execute("SELECT id FROM users WHERE id = ?", (id_number,)).fetchone()
        if id_check:
            flash("Your ID is already registered")
            return redirect("/register")
        
        # hash password
        password_hash = generate_password_hash(password)
        
        # generate username based on first and last name w/ regex (chat gpt'd)
        safe_firstname = re.sub(r'[^\wÀ-ÖØ-öø-ÿ]+', '', firstname.lower()) 
        safe_lastname = re.sub(r'[^\wÀ-ÖØ-öø-ÿ]+', '', lastname.lower())
        username = f"{safe_firstname}_{safe_lastname}"

        # store in users
        cursor.execute("INSERT INTO users (id, username, password_hash, role, first_name, last_name, email) VALUES (?, ?, ?, ?, ?, ?, ?)", (id_number, username, password_hash, user_role, firstname, lastname, email_address))

        # commit insert
        connection.commit()

        # redirect to login page
        return redirect("/login")
    return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    # initialize db
    connection = sqlite3.connect('enrollment.db')
    cursor = connection.cursor()
    if request.method == "POST":
        # input
        id_number = request.form.get("id_number", "").strip()
        password = request.form.get("password", "")

        # check if any field is empty
        if not password or not id_number:
            flash("Please enter your information")
            return redirect("/login")
        
        # check if id number is a number
        if not id_number.isdigit():
            flash("Please enter a valid ID number")
            return redirect("/login")

        # query database for user
        user = cursor.execute("SELECT * FROM users WHERE id = ?", (id_number,)).fetchone()

        # check if id number is in database or if password doesn't match
        if user is None or not check_password_hash(user[2], password):
            flash("Your password may not match or your ID nubmer is not regsitered")
            return redirect("/login")

        # set current session if nothing else
        session.clear()
        session["user_id"] = user[0]

        # redirect to home page
        return redirect("/")    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/available_classes", methods=["GET", "POST"])
@login_required
def available_classes():
    # initialize db
    connection = sqlite3.connect('enrollment.db')
    cursor = connection.cursor()

    # select courses and enrollements
    # query is from chat gpt
    classes = cursor.execute("""
        SELECT c.id,
               c.course_code,
               c.title, 
               c.description,
               c.section,
               c.units,
               COUNT(e.id) AS enrolled_count,
               c.slots,
               c.days,
               c.start_time,
               c.end_time 
        FROM classes c
        LEFT JOIN enrollments e
               ON c.id = e.class_id AND e.status = 'enrolled'
        GROUP BY c.id
    """).fetchall()

    class_filter = []
    # filter if class is full
    for row in classes:
        if int(row[6]) < int(row[7]):
            class_filter.append(row)
    classes = class_filter

    if request.method == "POST":

        # removing from cart
        if "class_id_remove" in request.form:
            remove_class_id = request.form.get("class_id_remove")
            cursor.execute("DELETE FROM carts WHERE user_id = ? AND class_id = ?", (session["user_id"], remove_class_id))

            connection.commit()
            return redirect("/available_classes")

        # adding to cart
        if "class_id" in request.form:
            cart_class_id = request.form.get("class_id")

            # check if cart has actual value
            if cart_class_id == None or not cart_class_id.isdigit():
                flash("Invalid cart value")
                return redirect("/available_classes")
            cart_class_id = int(cart_class_id)

            # check if class is full
            if not any(row[0] == int(cart_class_id) for row in classes):
                flash("Class is full")
                return redirect("/available_classes")
            
            # check for duplicates
            cart_items = cursor.execute("SELECT 1 FROM carts WHERE class_id = ? AND user_id = ?", (cart_class_id, session["user_id"])).fetchone()
            if cart_items:
                flash("You are already enrolled in this course")
                return redirect("/available_classes")

            # insert into cart
            cursor.execute("INSERT INTO carts (user_id, class_id) VALUES (?, ?)", (session["user_id"], cart_class_id))

            connection.commit()
            return redirect("/available_classes")
    # rendering cart items ( course id, days, time )
    cart = cursor.execute("""
        SELECT course_code, days, start_time, end_time, units, id
        FROM classes WHERE id IN (
            SELECT class_id FROM carts WHERE user_id = ?
        ) 
        """, (session["user_id"],)).fetchall()
    
    total_units = 0

    for item in cart:
        total_units += int(item[4])
        
    connection.close()

    return render_template("available_classes.html", classes=classes, cart=cart, total_units=total_units)

@app.route("/my_cart", methods=["GET", "POST"])
@login_required
def my_cart():
    connection = sqlite3.connect('enrollment.db')
    cursor = connection.cursor()

    if request.method == "POST":
        if "class_id_remove" in request.form:
            remove_class_id = request.form.get("class_id_remove")
            cursor.execute("DELETE FROM carts WHERE user_id = ? AND id = ?", (session["user_id"], remove_class_id))
            connection.commit()
            return redirect("/my_cart")

    # load cart items
    cart_courses = cursor.execute("""
        SELECT c.id,
               c.course_code,
               c.title, 
               c.description,
               c.section,
               c.units,
               COUNT(e.id) AS enrolled_count,
               c.slots,
               c.days,
               c.start_time,
               c.end_time,
               carts.id
        FROM classes c
        LEFT JOIN enrollments e
               ON c.id = e.class_id AND e.status = 'enrolled'
        JOIN carts ON c.id = carts.class_id
        WHERE c.id IN (
            SELECT class_id FROM carts WHERE user_id = ?
        ) 
        GROUP BY c.id
        """, (session["user_id"],)).fetchall()
    
    connection.close()

    return render_template("my_cart.html", cart_courses=cart_courses)

@app.route("/enlist_classes", methods=["GET", "POST"])
@login_required
def enlist_classes():
    connection = sqlite3.connect('enrollment.db')
    cursor = connection.cursor()
    
    if request.method == "POST":
        # put cart items into enrollments
        user_classes = cursor.execute("SELECT class_id FROM carts WHERE user_id = ?", (session["user_id"],)).fetchall()

        # check if any of the classes are full
        full_classes = []

        for class_row in user_classes:
            class_id = class_row[0]
            enrolled_count = cursor.execute("SELECT COUNT(*) FROM enrollments WHERE class_id = ? AND status = 'enrolled'", (class_id,)).fetchone()[0]
            total_slots = cursor.execute("SELECT slots FROM classes WHERE id = ?",(class_id,)).fetchone()[0]
            if enrolled_count >= total_slots:
                full_classes.append(class_id)
        if full_classes:
            flash(f"The following classes are full and cannot be enrolled: full_classes", "danger")
            connection.close()
            return redirect("/available_courses")

        # enroll all classes
        for class_row in user_classes:
            class_id = class_row[0]
            cursor.execute("INSERT INTO enrollments (student_id, class_id, status) VALUES (?, ?, ?)", (session["user_id"], class_id, "enrolled"))

        # remove items from cart
        cursor.execute("DELETE FROM carts WHERE user_id = ?", (session["user_id"],))

        connection.commit()

    connection.close()

    return redirect("/my_classes")


@app.route("/my_classes")
@login_required
def my_classes():
    connection = sqlite3.connect('enrollment.db')
    cursor = connection.cursor()

    user_classes = cursor.execute("""
        SELECT c.id,
               c.course_code,
               c.title, 
               c.description,
               c.section,
               c.units,
               COUNT(e.id) AS enrolled_count,
               c.slots,
               c.days,
               c.start_time,
               c.end_time
        FROM classes c
        LEFT JOIN enrollments e
               ON c.id = e.class_id AND e.status = 'enrolled'
        WHERE e.student_id = ?
        GROUP BY c.id
        """, (session["user_id"],)).fetchall()

    connection.close()

    return render_template("my_classes.html", user_classes=user_classes)


def parse_days(days_str):
    """Convert a compact days string like 'MWF' or 'TTh' into a list of day names"""
    mapping = {"M": "Mon", "T": "Tue", "W": "Wed", "Th": "Thu", "F": "Fri"}
    result = []
    i = 0
    while i < len(days_str):
        if days_str[i] == "T" and i+1 < len(days_str) and days_str[i+1] == "h":
            result.append("Thu")
            i += 2
        else:
            result.append(mapping[days_str[i]])
            i += 1
    return result

if __name__ == "__main__":
    app.run(debug=True)