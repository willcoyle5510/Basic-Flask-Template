from flask import *
import logging
import os
import sqlite3
import sys

from interfaces.databaseinterface import Database
from interfaces.hashing import hash_password, check_password

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10
DATABASE = Database('database/test.db', log=app.logger)

@app.route('/backdoor')
def backdoor():
    results = DATABASE.ViewQuery("SELECT * FROM users")
    return jsonify(results)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'test.sqlite')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'createscript.txt')


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if os.path.exists(DB_PATH):
        return

    connection = sqlite3.connect(DB_PATH)
    try:
        with open(SCHEMA_PATH, 'r', encoding='utf-8') as schema_file:
            connection.executescript(schema_file.read())
    finally:
        connection.close()


init_db()


#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    message = "Please log in to continue."
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        db = Database(DB_PATH)
        user = db.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
        if user and check_password(user[0]['password'], password):
            session['permission'] = user[0].get('permission', 'user')
            session['user_id'] = user[0]['userid']
            return redirect('/home')

        message = "Invalid credentials. Please try again."

    app.logger.info("Login")
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    app.logger.info("Logout")
    session.clear()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = "Create an account below."

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not first_name or not last_name or not email or not password:
            message = "Please fill in all required fields."
            app.logger.info("Registration failed: missing fields")
            return render_template('register.html', message=message)

        db = Database(DB_PATH)
        existing_user = db.ViewQuery("SELECT userid FROM users WHERE email = ?", (email,))
        if existing_user:
            message = "An account with that email already exists."
            return render_template('register.html', message=message)

        hashed_password = hash_password(password)
        success = db.ModifyQuery(
            "INSERT INTO users (firstname, lastname, password, email) VALUES (?, ?, ?, ?)",
            (first_name, last_name, hashed_password, email)
        )

        if success:
            app.logger.info("Register")
            return redirect('/')

        message = "Registration failed. Please try again."

    app.logger.info("Register")
    return render_template('register.html', message=message)


@app.route('/home')
def home():
    if 'permission' in session:
        if session['permission'] == "admin":
            return "All glory to the administrator!"
    app.logger.info("Home")
    return "<b>Home Page</b>"


@app.route('/admin')
def admin():
    app.logger.info("Admin")
    return "<b>Admin Page</b>"


#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
