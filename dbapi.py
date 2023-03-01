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
        return cursor.fetchall()[0]

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
            print(f"{name[0]} {name[1]}")
        return formatted_names

    def getUserFriends(self, uid):
        return []
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT UINQUE Users.first_name, Users.last_name FROM Users JOIN Friends_with ON Users.user_id=Friends_with.user_1 OR Users.user_id=Friends_with.user_2 WHERE Friends_with.user_1={uid} OR Friends_with.user_2={uid}")
        names = cursor.fetchall()
        formatted_names = []
        for name in names:
            formatted_names.append(f"{name[0]} {name[1]}")
            print(f"{name[0]} {name[1]}")
        return formatted_names

    def getUsersPhotos(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Photos.photo_data, Photos.photo_id, Photos.photo_caption FROM Photos JOIN Has_Photo ON Photos.photo_id=Has_Photo.photo_id JOIN Albums ON Has_Photo.album_id=Albums.album_id JOIN Owns_Album ON Albums.album_id=Owns_Album.album_id WHERE Owns_Album.user_id='{uid}'")
        return cursor.fetchall()  # NOTE return a list of tuples, [(imgdata, pid, caption), ...]

    def getAlbumIDFromName(self, albumName, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT Albums.album_id FROM Albums JOIN Owns_Album ON Albums.album_id=Owns_Album.album_id WHERE album_name='{albumName}' AND user_id='{uid}'")
        return cursor.fetchone()[0]

    def getUserIdFromEmail(self, email):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT user_id  FROM Users WHERE email = '{email}'")
        return cursor.fetchone()[0]

    def getUserIdFromUsername(self, username):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT user_id  FROM Users WHERE email = '{username}'")
        return cursor.fetchone()[0]

    def getUserPasswordFromEmail(self, email):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT password FROM Users WHERE email = '{email}'")
        return cursor.fetchone()[0]

    def getUserAlbums(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT album_name FROM Albums JOIN Owns_Album ON Owns_Album.album_id=Albums.album_id WHERE user_id={uid}")
        albumsTuple = cursor.fetchall()
        albums = []
        for album in range(len(albumsTuple)):
            albums.append(albumsTuple[album][0])
        return sorted(albums)

    def createNewAlbum(self, albumName, ownerID):
        cursor = self.conn.cursor()
        todayDate = date.today().strftime("%Y-%m-%d")
        cursor.execute(
            f"INSERT INTO Albums (album_name, album_create_date) VALUES ('{albumName}', str_to_date('{todayDate}','%Y-%m-%d'))")
        self.conn.commit()
        newAlbumID = cursor.lastrowid
        print(f"NEWALBUM: {newAlbumID}")
        cursor.execute(f"INSERT INTO Owns_Album (album_id, user_id) VALUES ({newAlbumID}, {ownerID})")
        self.conn.commit()
        return

    def addNewPhoto(self, photo_data, album_id, caption):
        cursor = self.conn.cursor()
        cursor.execute("""INSERT INTO Photos(photo_data, album_id, photo_caption) VALUES (%s, %s, %s)""",
                       (photo_data, album_id, caption))
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
