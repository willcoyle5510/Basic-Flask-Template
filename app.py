from flask import *
import sys
import logging
from interfaces.databaseinterface import Database

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10
DATABASE = Database('test.db', log=app.logger)




#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    message = "Please login to continue."
    if request.method == 'POST':
        email = request.form.get('email') #name of the input
        password = request.form.get('password') #name of input
        if email == 'admin' and password == 'admin':
            session['permission'] = 'admin'
            return redirect('/home')
        else:
            message="Invalid credentials. Please try again."
    app.logger.info("Login")
    return render_template('login.html', message=message)

@app.route('/logout')
def logout():
    app.logger.info("Logout")
    session.clear()
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            message = "Passwords do not match."
            return render_template('register.html', message=message)
        else:
            results = DATABASE.ViewQuery("SELECT * FROM users WHERE email = ?", (email,))

    app.logger.info("Register")
    return render_template('register.html')

@app.route('/home')
def home():
    if 'permission' in session:
        if session['permission'] == 'admin':
            return "All glory to the administrator!"
    app.logger.info("Home")
    return "Home"

@app.route('/admin')
def admin():
    app.logger.info("admin")
    return "Admin"

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000