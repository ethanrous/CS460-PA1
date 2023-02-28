CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Tagged_With CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;
DROP TABLE IF EXISTS Has_Photo CASCADE;
DROP TABLE IF EXISTS Likes_Photo CASCADE;
DROP TABLE IF EXISTS Owns_Album CASCADE;
DROP TABLE IF EXISTS Has_Comment CASCADE;
DROP TABLE IF EXISTS Photos CASCADE;
-- DROP TABLE IF EXISTS Pictures CASCADE; -- 
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Commented CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Friends_with CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
	first_name varchar(255),
    last_name varchar(255),
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    dob DATE,
    hometown varchar(255),
    gender varchar(255),
    password varchar(255),
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Friends_with (
	user_1 int4,
    user_2 int4,
    PRIMARY KEY(User_1, User_2),
	FOREIGN KEY (user_1) REFERENCES Users(user_id),
	FOREIGN KEY (user_2) REFERENCES Users(user_id)

);

CREATE TABLE Comments(
	comment_id int4 AUTO_INCREMENT,
    comment_text varchar(255),
    comment_create_date DATE,
    CONSTRAINT coment_pk PRIMARY KEY (comment_id)
);

CREATE TABLE Commented (
	comment_id int4,
    user_id int4,
    PRIMARY KEY(comment_id),
    FOREIGN KEY(user_id) REFERENCES Users(user_id),
    FOREIGN KEY(comment_id) REFERENCES Comments(comment_id)
);
CREATE TABLE Albums (
	album_name VARCHAR(255),
    album_id int4 AUTO_INCREMENT,
    album_create_date DATE,
    PRIMARY KEY(album_id)
);

CREATE TABLE Photos(
	photo_id int4 AUTO_INCREMENT,
    photo_caption VARCHAR(255),
    photo_data longblob,
    album_id int4,
    PRIMARY KEY(photo_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id)
);


/*CREATE TABLE Pictures
(
	
	picture_id int4  AUTO_INCREMENT,
	user_id int4,
	imgdata longblob ,
	caption VARCHAR(255),
	INDEX upid_idx (user_id),
	CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);
*/

CREATE TABLE Has_Comment (
	comment_id int4,
    photo_id int4,
    PRIMARY KEY(comment_id),
    FOREIGN KEY(comment_id) REFERENCES Comments(comment_id),
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id)
);



CREATE TABLE Owns_Album (
	album_id int4,
    user_id int4,
    PRIMARY KEY (album_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Likes_Photo (
	user_id int4,
    photo_id int4,
    PRIMARY KEY (user_id, photo_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id)
);

CREATE TABLE Has_Photo (
	album_id int4,
    photo_id int4,
    PRIMARY KEY (photo_id),
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id)
);

CREATE TABLE Tags (
	tag_name varchar(255),
    PRIMARY KEY(tag_name)
);

CREATE TABLE Tagged_With (
	photo_id int4,
    tag_name varchar(255),
    PRIMARY KEY (photo_id, tag_name),
    FOREIGN KEY (photo_id) REFERENCES Photos (photo_id),
    FOREIGN KEY (tag_name) REFERENCES Tags(tag_name)
);
