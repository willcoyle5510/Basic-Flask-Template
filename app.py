from flask import *
import sys
import logging

#---CONFIGURE APP---------------------------------------------------
app = Flask(__name__)
logging.basicConfig(filename='logs/flask.log', level=logging.INFO)
sys.tracebacklimit = 10

#---VIEW FUNCTIONS----------------------------------------------------
@app.route('/')
def login():
    app.logger.info("Login")
    return "Login Page"

@app.route('/register')
def register():
    app.logger.info("Register")
    return "Registration Page"

@app.route('/home')
def home():
    app.logger.info("Home")
    return "Home Page"

@app.route('/admin')
def admin():
    app.logger.info("Admin")
    return "Admin Page"

#main method called web server application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) #runs a local server on port 5000
