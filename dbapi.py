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

    def getUsersPhotos(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Photos.photo_data, Photos.photo_id, Photos.photo_caption, Owns_Album.user_id FROM Photos JOIN Has_Photo ON Photos.photo_id=Has_Photo.photo_id JOIN Owns_Album ON Has_Photo.album_id=Owns_Album.album_id WHERE Owns_Album.user_id='{uid}'")
        return list(cursor.fetchall())

    def getPhotoData(self, photo_id):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Photos.photo_data, Photos.photo_caption FROM Photos WHERE photo_id='{photo_id}'")
        return cursor.fetchone()

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
        # use this to check if a email has already been registered
        cursor = self.conn.cursor()
        if cursor.execute(f"SELECT email  FROM Users WHERE email = '{email}'"):
            # this means there are greater than zero entries with that email
            return False
        else:
            return True
    # end login code
