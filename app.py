######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

# for image uploading
import os
import base64

# For create dates

import dbapi

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!


# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('dbpassword')
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

dbconnector = dbapi.dbconnector(mysql)
users = dbconnector.getUserList()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = dbconnector.getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = dbconnector.getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute(f"SELECT password FROM Users WHERE email = '{email}'")
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    if (data := dbconnector.getUserPasswordFromEmail(email)):
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')

# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier


@app.route("/register", methods=['GET'])
def register():
    try:
        request.args['supress']
        supress = None

    except:
        supress = True
    try:
        request.args['dob_test']
        dob_test = None

    except:
        dob_test = True
    print("here")
    return render_template('register.html', supress=supress, dob_test = dob_test)


@app.route("/register", methods=['POST'])
def register_user():
    try:
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get('email')
        dob = request.form.get('dob')
        password = request.form.get('password')
    except:
        # this prints to shell, end users will not see this (all print statements go to shell)
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))
    email_test = dbconnector.isEmailUnique(email)
    dob_tester = dbconnector.isDOBCorrect(dob)
    if email_test:
        if dob_tester:
            dbconnector.addNewUser(firstname, lastname, email, dob, password)
            user = User()
            user.id = email
            flask_login.login_user(user)
            return render_template('hello.html', name=email, message='Account Created!')
        else:
            print(f"User trying to register has incorrect format for dob")
            return flask.redirect(flask.url_for('register', dob_test=False))
    else:
        print(f"User trying to regester as {email} is not unique")
        return flask.redirect(flask.url_for('register', supress=False))


@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        newAlbumName = request.form.get('newalbum')
        if newAlbumName:
            dbconnector.createNewAlbum(newAlbumName, uid)
        photo_data = imgfile.read()
        album_id = dbconnector.getAlbumIDFromName(newAlbumName, uid)
        dbconnector.addNewPhoto(photo_data, album_id, caption)
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=dbconnector.getUsersPhotos(uid), base64=base64)
    else:
        albums = dbconnector.getUserAlbums(uid)
        return render_template('upload.html', albums=albums)


# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
