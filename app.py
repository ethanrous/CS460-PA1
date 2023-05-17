import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import dotenv

# for image uploading
import os
import base64

# For create dates

import dbapi

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'

app.config['MYSQL_DATABASE_USER'] = 'root'

# export dbpassword='SQL_SERVER_PASSWORD', or
dotenv.load_dotenv()
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('dbpassword')
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

dbconnector = dbapi.dbconnector(mysql)
users = dbconnector.getUserList()

no_image_icon = open("no-image-icon.png", 'rb').read()


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
            return flask.redirect(flask.url_for('profile'))  # protected is a function defined in this file

    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


@app.route("/register", methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        try:
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            dob = request.form.get('dob')
            password = request.form.get('password')
        except:
            return flask.redirect(flask.url_for('register'))
        test = dbconnector.isEmailUnique(email)
        if test:
            dbconnector.addNewUser(firstname, lastname, email, dob, password)
            user = User()
            user.id = email
            flask_login.login_user(user)
            uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
            return render_template('hello.html', name=dbconnector.getUserNameFromUserID(uid), message='Account Created!')
        else:
            return flask.redirect(flask.url_for('register_user', supress=False))
    else:
        try:
            request.args['supress']
            supress = None
        except:
            supress = True
        return render_template('register.html', supress=supress)


@app.route("/profile", methods=['GET', 'POST'])
@flask_login.login_required
def profile():
    uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
    users_photos = dbconnector.getUsersPhotos(uid)
    if not (message := request.args.get('message')):
        message = None
    if request.method == 'POST':
        tagsearch = request.form.get('tagsearch')
        users_photos = dbconnector.getUsersPhotos(uid, tagfilter=tagsearch)
        return render_template('profile.html', name=dbconnector.getUserNameFromUserID(uid), photos=users_photos, base64=base64, message=message)
    else:
        return render_template('profile.html', name=dbconnector.getUserNameFromUserID(uid), photos=users_photos, base64=base64, message=message)


@app.route('/albums')
@flask_login.login_required
def albums():
    uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
    users_albums = dbconnector.getUserAlbums(uid)
    for count, album in enumerate(users_albums):
        users_albums[count] = list(album)
        album_photos = dbconnector.getPhotosInAlbum(album[0])
        if album_photos:
            photo_data = album_photos[0][0]
        else:
            photo_data = no_image_icon
        users_albums[count].append(photo_data)
    if not (message := request.args.get('message')):
        message = None
    return render_template('albums.html', name=dbconnector.getUserNameFromUserID(uid), albums=users_albums, base64=base64, message=message)


@app.route('/albums/<album_id>')
@flask_login.login_required
def album(album_id):
    album_photos = dbconnector.getPhotosInAlbum(album_id)
    return render_template('albumpage.html', name="ALBUM_NAME", photos=album_photos, base64=base64)


def photoviewHelper(photo_id):
    photo_data = dbconnector.getPhotoData(photo_id)
    image_tags = dbconnector.getPhotoTags(photo_id)
    is_owner = dbconnector.getUserIdFromEmail(flask_login.current_user.id) == dbconnector.getPhotoOwner(photo_id)
    comments = dbconnector.getPhotoComments(photo_id)
    print(comments)
    return photo_data, image_tags, is_owner, comments


@app.route('/photoview/<photo_id>', methods=['GET', 'POST'])
def photoview(photo_id):
    uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        if comment := request.form.get('comment'):
            dbconnector.addCommentToPhoto(comment=comment, photo_id=photo_id)
            photo_data, image_tags, is_owner, comments = photoviewHelper(photo_id=photo_id)
            return render_template('photoview.html', photo_data=photo_data, image_tags=image_tags, is_owner=is_owner, base64=base64, liked=True, comments=comments)
        if request.form.get('like_button') == 'like':
            dbconnector.likePhoto(uid, photo_id)
            photo_data, image_tags, is_owner, comments = photoviewHelper(photo_id=photo_id)
            return render_template('photoview.html', photo_data=photo_data, image_tags=image_tags, is_owner=is_owner, base64=base64, liked=True, comments=comments)
        if request.form.get('like_button') == 'unlike':
            dbconnector.unlikePhoto(uid, photo_id)
            photo_data, image_tags, is_owner, comments = photoviewHelper(photo_id=photo_id)
            return render_template('photoview.html', photo_data=photo_data, image_tags=image_tags, is_owner=is_owner, base64=base64, liked=False, comments=comments)
        if tag_name := request.form.get('newtagname'):
            if dbconnector.checkTag(tag_name=tag_name):
                dbconnector.addTagToPhoto(tag_name=tag_name, photo_id=photo_id)
                photo_data, image_tags, is_owner, comments = photoviewHelper(photo_id=photo_id)
                return render_template('photoview.html', photo_data=photo_data, image_tags=image_tags, is_owner=is_owner, base64=base64, comments=comments)
            else:
                photo_data, image_tags, is_owner, comments = photoviewHelper(photo_id=photo_id)
                return render_template('photoview.html', photo_data=photo_data, image_tags=image_tags, is_owner=is_owner, base64=base64, tag_fail=True, comments=comments)
    else:
        photo_data, image_tags, is_owner, comments = photoviewHelper(photo_id=photo_id)
        liked = dbconnector.isliked(uid, photo_id)
        return render_template('photoview.html', photo_data=photo_data, image_tags=image_tags, is_owner=is_owner, base64=base64, liked=liked, comments=comments)


@app.route('/tagview/<tagname>', methods=['GET'])
def tagview(tagname):
    tag_data = dbconnector.getPhotosFromTag(tagname)
    return render_template('tagview.html', tag_data=tag_data, base64=base64)


@app.route('/trending', methods=['GET'])
def trending():
    uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
    tag_data = dbconnector.getMostPopularTags()
    return render_template('trending.html', tag_data=tag_data)


@app.route('/photosearch', methods=['GET', 'POST'])
@flask_login.login_required
def photosearch():
    if request.method == 'POST':
        pass
    else:
        tagslist = request.args.get('tagname')
        photos = []
        for tag in tagslist:
            photos.extend(dbconnector.getPhotos(tagfilter=tag))
        return render_template('photosearch.html', photos=photos, base64=base64)


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
        albumName = request.form.get('newalbum')
        if albumName:
            dbconnector.createNewAlbum(albumName, uid)
        else:
            albumName = request.form.get('album')
            if albumName == None:
                albums = dbconnector.getUserAlbums(uid)
                return render_template('upload.html', albums=albums, failedAlbum=True)
        photo_data = imgfile.read()
        album_id = dbconnector.getAlbumIDFromName(albumName, uid)
        dbconnector.addNewPhoto(photo_data, album_id, caption)
        return flask.redirect(flask.url_for('profile', message="Photo Uploaded!"))
    else:
        albums = dbconnector.getUserAlbums(uid)
        for count, album in enumerate(albums):
            albums[count] = album[1]
        return render_template('upload.html', albums=albums)


@app.route('/newalbum', methods=['GET', 'POST'])
@flask_login.login_required
def new_album():
    uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        newAlbumName = request.form.get('newalbum')
        dbconnector.createNewAlbum(newAlbumName, uid)
        return render_template('hello.html', name=dbconnector.getUserNameFromUserID(uid), message='Album Created!')
    else:
        return render_template('newalbum.html')


@app.route('/friends', methods=['GET'])
@flask_login.login_required
def list_friends():
    uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
    user_friends_names = dbconnector.getUserFriendsNames(uid)
    user_friends_emails = dbconnector.getUserFriendsEmails(uid)
    user_friends = []
    for count, friend in enumerate(user_friends_names):
        user_friends.append(f"{friend} ({user_friends_emails[count]})")
    if len(user_friends_names) == 0:
        return render_template('friends.html', nofriends=True)
    else:
        return render_template('friends.html', friends=user_friends)


@app.route('/addfriend', methods=['GET', 'POST'])
@flask_login.login_required
def add_friend():
    uid = dbconnector.getUserIdFromEmail(flask_login.current_user.id)
    if request.method == 'POST':
        newfriendemail = request.form.get('newfriend')
        frienduid = dbconnector.getUserIdFromEmail(newfriendemail)
        dbconnector.addfriend(frienduid, uid)
        return render_template('hello.html', name=dbconnector.getUserNameFromUserID(uid), message='Friend Added!')
    else:
        possible_friends = dbconnector.getPossibleFriends(uid=uid)
        if len(possible_friends) == 0:
            return render_template('addfriend.html', nousers=True)
        else:
            return render_template('addfriend.html', users=possible_friends)

# default page


@app.route("/", methods=['GET', 'POST'])
def hello():
    if request.method == 'POST':
        tagsearch = request.form.get('tagsearch')
        tags_list = tagsearch.split(' ')
        return flask.redirect(flask.url_for('photosearch', tagname=tagsearch))
    else:
        return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
    app.run(port=8000, debug=True)
