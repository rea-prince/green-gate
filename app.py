import os
import sqlite3
import re
import datetime
from flask import Flask, redirect, url_for, render_template, request, session
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
            return redirect("/register")
        # validate ID number
        if not id_number.isdigit():
            return redirect("/register")
        # validate email address
        if not re.match(email_pattern, email_address):
            return redirect("/register")
        email_check = cursor.execute("SELECT email FROM users WHERE email = ?", (email_address,)).fetchone()
        if email_check:
            return redirect("/register")

        # if password and confirmation don't match
        if password != confirmation:
            return redirect("/register")
        # check user role is valid
        if user_role not in possible_roles:
            return redirect("/register")

        # availability
        # if ID or username are already in db
        id_check = cursor.execute("SELECT id FROM users WHERE id = ?", (id_number,)).fetchone()
        if id_check:
            return render_template("error.html")
        
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
    session.clear()
    if request.method == "POST":
        # input
        id_number = request.form.get("id_number", "").strip()
        password = request.form.get("password", "")

        # check if any field is empty
        if not password or not id_number:
            return redirect("/login")
        
        # check if id number is a number
        if not id_number.isdigit():
            return redirect("/login")

        # query database for user
        user = cursor.execute("SELECT * FROM users WHERE id = ?", (id_number,)).fetchone()

        # check if id number is in database or if password doesn't match
        if user is None or not check_password_hash(user[2], password):
            return redirect("/login")

        # set current session if nothing else
        session["user_id"] = user[0]

        # redirect to home page
        return redirect("/")    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/available_courses", methods=["GET", "POST"])
@login_required
def available_courses():
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

    # adding courses to cart
    if request.method == "POST":
        cart_class_id = request.form.get("add_to_cart")

        # adding to cart
        # check if cart has actual value
        if cart_class_id == None or not cart_class_id.isdigit():
            return render_template("error.html")
        cart_class_id = int(cart_class_id)

        # check if class is full
        if not any(row[0] == int(cart_class_id) for row in classes):
            return render_template("error.html")
        
        # check for duplicates

        # insert into cart
        cursor.execute("INSERT INTO carts (user_id, class_id) VALUES (?, ?)", session["user_id"], cart_class_id)

        # <------------------------------------>
        # removing from cart

        connection.commit()

    # <------------------------------------>
    # rendering cart items ( course id, days, time )
        # get cart items (pull from courses where course id in carts and user id = session[user_id])


    connection.close()

    return render_template("available_courses.html", classes=classes)

@app.route("/my_courses")
@login_required
def my_courses():
    return render_template("my_courses.html")

@app.route("/schedule")
@login_required
def schedule():
    return render_template("schedule.html")




if __name__ == "__main__":
    app.run(debug=True)