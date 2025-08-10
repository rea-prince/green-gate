import sqlite3
from flask import Flask, redirect, url_for, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash


# connect sqlite3
connection = sqlite3.connect('enrollment.db')
cursor = connection.cursor()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        # check if empty or if id number is a number
        id_number = request.form.get("id_number", "").strip()
        password = request.form.get("password", "")

        # Validate ID number
        if not id_number.isdigit():
            return redirect("/login")

        if not password:
            return redirect("/login")
        
        # query database for user
        user = cursor.execute("SELECT * FROM users WHERE id = ?", (id_number,)).fetchone()
        # hash the password

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
        id_number = request.form.get("id_number").strip()
        username = request.form.get("username").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        user_role = request.form.get("role", "")
        possible_roles = ["student", "faculty", "admin"]

        # validity
        # if any field is blank
        if not id_number or not username or not password or not confirmation or not user_role:
            return redirect("/register")
        # validate ID number
        if not id_number.isdigit():
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
        username_check = cursor.execute("SELECT username FROM users WHERE username = ?", (username)).fetchone()
        if id_check or username_check:
            return render_template("error.html")
        
        # hash password
        password_hash = generate_password_hash(password)
        
        # store in users
        cursor.execute("INSERT INTO users (id, username, password_hash, role) VALUES (?, ?, ?, ?)", (id_number, username, password_hash, user_role))

        # insert to students db
        if user_role == "student":
            cursor.execute("INSERT INTO students (student_id) VALUES (?)", (id_number,))

        # commit insert
        connection.commit()

        # redirect to login page
        return redirect("/login")
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)