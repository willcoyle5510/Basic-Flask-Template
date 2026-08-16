from flask import *
import sys
import logging
import hashlib
from interfaces.databaseinterface import Database
from interfaces.hashing import hash_password, check_password

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10
DATABASE = Database('test.db', log=app.logger)


def ensure_database():
    DATABASE.ModifyQuery("""
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            permission TEXT DEFAULT 'user' CHECK (permission in ('user','admin')),
            lastaccess DATE DEFAULT (datetime('now','localtime')),
            status TEXT NULL,
            profilepicture TEXT NULL
        )
    """)

    admin_exists = DATABASE.ViewQuery("SELECT userid FROM users WHERE email = ?", ('admin@admin',))
    if not admin_exists:
        DATABASE.ModifyQuery(
            "INSERT INTO users (email, firstname, lastname, password, permission) VALUES (?, ?, ?, ?, ?)",
            ('admin@admin', 'Peter', 'Whitehouse', hash_password('admin'), 'admin')
        )


ensure_database()


#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password = hashlib.sha256(password.encode()).hexdigest()  # Hash the password before checking

        results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
        if results and check_password(results[0]['password'], password):
            session['userid'] = results[0]['userid']
            session['permission'] = results[0]['permission']
            session['email'] = results[0]['email']
            flash("Login successful!")
            return redirect('/home')

        flash("Invalid credentials. Please try again.")

    app.logger.info("Login")
    return render_template('login.html')

@app.route('/logout')
def logout():
    app.logger.info("Logout")
    session.clear()
    return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash("Passwords do not match.")
        else:
            results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))
            if not results:
                hashed_password = hash_password(password)
                insert_success = DATABASE.ModifyQuery(
                    "INSERT INTO users (email, password, firstname, lastname) VALUES (?, ?, ?, ?)",
                    (email, hashed_password, firstname, lastname)
                )
                if insert_success:
                    flash("Registration successful. Please login.")
                    return redirect('/')
                flash("Registration failed. Please try again.")
            else:
                flash("Email already exists. Please try again.")

    app.logger.info("Register")
    return render_template('register.html')

@app.route('/backdoor')
def backdoor():
    app.logger.info("Backdoor database dump")
    rows = DATABASE.ViewQuery("SELECT userid, firstname, lastname, email, password, permission FROM users")
    return jsonify({'users': rows if rows else []})

@app.route('/hash') #YOU CAN ONLY DO THIS ONCE.
def hashexistingpasswords():
    if 'hashed' in session:
        flash("Passwords have already been hashed.")
        return redirect('/')
    results = DATABASE.ViewQuery("SELECT * FROM users")
    for user in results:
        hashed_password = hashlib.sha256(user['password'].encode()).hexdigest()
        DATABASE.ModifyQuery("UPDATE users SET password = ? WHERE userid = ?", (hashed_password, user['userid']))
    session['hashed'] = True
    return jsonify(results)

@app.route('/home')
def home():
    app.logger.info("Home")
    if 'userid' not in session:
        flash("You must be logged in to access this page.")
        return redirect('/')
    return render_template('home.html')

@app.route('/admin')
def admin():
    app.logger.info("Admin")
    if 'permission' in session:
        if session['permission'] == 'admin':
            results = DATABASE.ViewQuery('Select * from users')
            return render_template('admin.html', users=results)
    flash("You do not have permission to access this page.")
    return redirect('/home')

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000