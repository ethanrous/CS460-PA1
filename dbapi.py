from datetime import date


class dbconnector():
    pass

    def __init__(self, mysql):
        self.conn = mysql.connect()

    def getUserList(self, exclude=None):
        cursor = self.conn.cursor()
        if exclude:
            cursor.execute(f"SELECT email from Users WHERE NOT user_id={exclude}")
        else:
            cursor.execute(f"SELECT email from Users")
        users_list = list(cursor.fetchall())
        if len(users_list) > 0:
            for count, value in enumerate(users_list):
                users_list[count] = value[0]
            return users_list
        else:
            return []

    def getAllUsersNames(self, exclude=None):
        cursor = self.conn.cursor()
        if exclude:
            cursor.execute(f"SELECT first_name, last_name from Users WHERE NOT user_id={exclude}")
        else:
            cursor.execute(f"SELECT first_name, last_name from Users")
        names = cursor.fetchall()
        formatted_names = []
        for name in names:
            formatted_names.append(f"{name[0]} {name[1]}")
        return formatted_names

    def getAllUsersEmails(self, exclude=None):
        cursor = self.conn.cursor()
        if exclude:
            cursor.execute(f"SELECT email FROM Users WHERE NOT email=\"{exclude}\"")
        else:
            cursor.execute(f"SELECT email FROM Users")
        emails = list(cursor.fetchall())
        for count, email in enumerate(emails):
            emails[count] = email[0]
        return emails

    def getUserFriendsNames(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT DISTINCT Users.first_name, Users.last_name FROM Friends_with JOIN Users ON Friends_with.user_1=Users.user_id OR Friends_with.user_2=Users.user_id WHERE Friends_with.user_1={uid} OR Friends_with.user_2={uid} ")
        names = list(cursor.fetchall())
        for count, name in enumerate(names):
            names[count] = f"{name[0]} {name[1]}"
        return names

    def getUserFriendsEmails(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT DISTINCT Users.email FROM Friends_with JOIN Users ON Friends_with.user_1=Users.user_id OR Friends_with.user_2=Users.user_id WHERE Friends_with.user_1={uid} OR Friends_with.user_2={uid} ")
        emails = list(cursor.fetchall())
        for count, email in enumerate(emails):
            emails[count] = email[0]
        return emails

    def getEmailFromUserID(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT email FROM Users WHERE user_id={uid}")
        return cursor.fetchone()[0]

    def getPossibleFriends(self, uid):
        all_users = self.getAllUsersEmails(exclude=self.getEmailFromUserID(uid=uid))
        user_friends = self.getUserFriendsEmails(uid=uid)
        possible_friends = []
        for user in all_users:
            if user not in user_friends:
                possible_friends.append(user)
        return possible_friends

    def getPhotos(self, tagfilter=None):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Photos.photo_data, Photos.photo_id, Photos.photo_caption FROM Photos")
        photos = list(cursor.fetchall())
        filtered_photos = []
        if tagfilter:
            for photo in photos:
                if tagfilter in self.getPhotoTags(photo[1]):
                    filtered_photos.append(photo)
        else:
            filtered_photos = photos
        return filtered_photos

    def getUsersPhotos(self, uid, tagfilter=None):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Photos.photo_data, Photos.photo_id, Photos.photo_caption, Owns_Album.user_id FROM Photos JOIN Has_Photo ON Photos.photo_id=Has_Photo.photo_id JOIN Owns_Album ON Has_Photo.album_id=Owns_Album.album_id WHERE Owns_Album.user_id='{uid}'")
        photos = list(cursor.fetchall())
        filtered_photos = []
        if tagfilter:
            for photo in photos:
                if tagfilter in self.getPhotoTags(photo[1]):
                    filtered_photos.append(photo)
        else:
            filtered_photos = photos
        return filtered_photos

    def getPhotoData(self, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Photos.photo_data, Photos.photo_caption, Photos.photo_id FROM Photos WHERE photo_id='{photo_id}'")
        return cursor.fetchone()

    def getPhotoTags(self, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT tag_name FROM Tagged_With WHERE photo_id='{photo_id}'")
        return [x[0] for x in cursor.fetchall()]

    def addTagToPhoto(self, tag_name, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Tagged_With (photo_id, tag_name) VALUES('{photo_id}', '{tag_name}')")
        self.conn.commit()
        return

    def checkTag(self, tag_name):
        if ' ' in tag_name:
            return False
        for letter in tag_name:
            if letter.isupper():
                return False
        return True

    def getPhotoOwner(self, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Owns_Album.user_id FROM Has_Photo JOIN Owns_Album ON Has_Photo.album_id=Owns_Album.album_id WHERE Has_Photo.photo_id='{photo_id}'")
        return cursor.fetchone()[0]

    def getAlbumIDFromName(self, albumName, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Albums.album_id FROM Albums JOIN Owns_Album ON Albums.album_id=Owns_Album.album_id WHERE album_name='{albumName}' AND user_id='{uid}'")
        return cursor.fetchone()[0]

    def getUserIdFromEmail(self, email):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT user_id FROM Users WHERE email = '{email}'")
        return cursor.fetchone()[0]

    def getUserIdFromUsername(self, username):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT user_id  FROM Users WHERE email = '{username}'")
        return cursor.fetchone()[0]

    def getUserNameFromUserID(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT first_name, last_name FROM Users WHERE user_id='{uid}'")
        name = cursor.fetchone()
        name = f"{name[0]} {name[1]}"
        return name

    def getUserPasswordFromEmail(self, email):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT password FROM Users WHERE email = '{email}'")
        return cursor.fetchone()[0]

    def getUserAlbums(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Albums.album_id, Albums.album_name FROM Albums JOIN Owns_Album ON Owns_Album.album_id=Albums.album_id WHERE user_id={uid}")
        return sorted(list(cursor.fetchall()))

    def getPhotosInAlbum(self, album_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Photos.photo_data, Photos.photo_id, Photos.photo_caption FROM Albums JOIN Has_Photo ON Albums.album_id=Has_Photo.album_id JOIN Photos ON Has_Photo.photo_id=Photos.photo_id WHERE Albums.album_id={album_id}")
        return cursor.fetchall()

    def createNewAlbum(self, albumName, ownerID):
        cursor = self.conn.cursor()
        todayDate = date.today().strftime("%Y-%m-%d")
        cursor.execute(
            f"INSERT INTO Albums (album_name, album_create_date) VALUES ('{albumName}', str_to_date('{todayDate}','%Y-%m-%d'))")
        self.conn.commit()
        newAlbumID = cursor.lastrowid
        cursor.execute(f"INSERT INTO Owns_Album (album_id, user_id) VALUES ({newAlbumID}, {ownerID})")
        self.conn.commit()
        return

    def addNewPhoto(self, photo_data, album_id, caption):
        cursor = self.conn.cursor()
        cursor.execute("""INSERT INTO Photos(photo_data, album_id, photo_caption) VALUES (%s, %s, %s)""",
                       (photo_data, album_id, caption))
        self.conn.commit()
        photo_id = cursor.lastrowid
        cursor.execute(f"INSERT INTO Has_Photo(album_id, photo_id) VALUES ({album_id}, {photo_id})")
        self.conn.commit()
        return

    def addNewUser(self, firstname, lastname, email, dob, password):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Users (first_name, last_name, email, dob, password) VALUES ('{firstname}', '{lastname}', '{email}', '{dob}', '{password}')")
        self.conn.commit()
        return

    def addfriend(self, uid1, uid2):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Friends_with (user_1, user_2) VALUES ('{uid1}', '{uid2}')")
        self.conn.commit()
        return

    def isEmailUnique(self, email):
        cursor = self.conn.cursor()
        if cursor.execute(f"SELECT email  FROM Users WHERE email = '{email}'"):
            return False
        else:
            return True

    def isliked(self, user_id, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Likes_Photo.photo_id FROM Likes_Photo WHERE Likes_Photo.user_id='{user_id}' AND Likes_Photo.photo_id='{photo_id}'")
        isliked = cursor.fetchone()
        if isliked:
            return True
        else:
            return False

    def likePhoto(self, user_id, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Likes_Photo (user_id, photo_id) VALUES({user_id}, {photo_id})")
        self.conn.commit()
        return

    def unlikePhoto(self, user_id, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"DELETE FROM Likes_Photo WHERE user_id='{user_id}' AND photo_id='{photo_id}'")
        self.conn.commit()
        return

    def getMostPopularTags(self):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT tag_name, COUNT(tag_name) as `occurrence` FROM Tagged_With GROUP BY tag_name ORDER BY occurrence DESC LIMIT 3")
        tag_count = cursor.fetchall()
        return tag_count

    def getPhotosFromTag(self, tagname):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT DISTINCT Photos.photo_data, Photos.photo_id, Photos.photo_caption FROM Photos JOIN Tagged_With ON Photos.photo_id=Tagged_With.photo_id WHERE Tagged_With.tag_name='{tagname}'")
        photos = list(cursor.fetchall())
        return photos

    def addCommentToPhoto(self, comment, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Comments (comment_text) VALUES('{comment}')")
        self.conn.commit()
        comment_id = cursor.lastrowid
        cursor.execute(
            f"INSERT INTO Has_Comment (comment_id, photo_id) VALUES({comment_id}, {photo_id})")
        self.conn.commit()
        return

    def getPhotoComments(self, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Comments.comment_text FROM Has_Comment JOIN Comments ON Has_Comment.comment_id=Comments.comment_id WHERE Has_Comment.photo_id={photo_id}")
        comments = list(cursor.fetchall())
        for count, comment in enumerate(comments):
            comments[count] = comment[0]
        return comments
