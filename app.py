import os
import sqlite3
import re
from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash



# configure application
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():
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
            return render_template("error.html")

        # set current session if nothing else
        session["user_id"] = user[0]

        # redirect to home page
        return redirect("/")    
    return render_template("login.html")

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
            return render_template("error.html")

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


if __name__ == "__main__":
    app.run(debug=True)