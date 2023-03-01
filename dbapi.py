from datetime import date
import datetime


class dbconnector():
    pass

    def __init__(self, mysql):
        self.conn = mysql.connect()

    def getUserList(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT email from Users")
        return cursor.fetchall()

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

    def getUserPasswordFromEmail(self, email):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT password FROM Users WHERE email = '{email}'")
        return cursor.fetchone()[0]

    def getUserAlbums(self, uid):
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT album_name FROM Albums JOIN Owns_Album ON Owns_Album.album_id=Albums.album_id WHERE user_id={uid}")
        albums = cursor.fetchall()
        print(albums)
        return albums

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
        
        return cursor.lastrowid

    def addNewUser(self, firstname, lastname, email, dob, password):
        cursor = self.conn.cursor()
        cursor.execute(
            f"INSERT INTO Users (first_name, last_name, email, dob, password) VALUES ('{firstname}', '{lastname}', '{email}', '{dob}', '{password}')")
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

    def isTagValid(self,tag):
        # Check to see if input tag is in correct format
        tag_list = tag.split(", ")
        for word in tag_list:
            if ' ' in word:
                return False
            
        return True

    def getTaggedWith(self,tag,photoID):
        cursor = self.conn.cursor()
        multipleTags = tag.split(", ")
        for word in multipleTags:
            cursor.execute(f"INSERT INTO Tagged_With (tag_name, photo_id) VALUES ('{word}', '{photoID}') ")
            cursor.execute(f"INSERT INTO Tags (tag_name) ('{word}')")
        return



    def isDOBCorrect(self, dob):
        # Use this to check if DOB format is correct
        try:
            datetime.date.fromisoformat(dob)
            return True
        except ValueError:
            return False
        
