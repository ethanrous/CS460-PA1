CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    First_Name varchar(255),
    Last_Name varchar(255),   
    User_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    Dob DATE,
    Hometown varchar(255),
    Gender varchar(255),
    Password varchar(255),
    CONSTRAINT users_pk PRIMARY KEY (User_id)
);

CREATE TABLE Friends_With(
    User_1 varchar(255),
    User_2 varchar(255),
    PRIMARY KEY (User_1,User_2),
    FOREIGN KEY (User_1) REFERENCES Users(User_id),
    FOREIGN KEY (User_2) REFERENCES Users(User_id)
    -- OR -- 
    -- CONSTRAINT FRIENDS_PK PRIMARY KEY (User_1,User_2)
  
);

CREATE TABLE Comments(
    Comment_id varchar(255) AUTO_INCREMENT,
    Comment_Text varchar(255),
    Comment_Create_Date DATE,
    CONSTRAINT Comment_pk PRIMARY KEY (Comment_id)
);

CREATE TABLE Commented (
    Comment_id varchar(255) AUTO_INCREMENT,
    User_id varchar(255),
    PRIMARY KEY (Comment_id),
    FOREIGN KEY (User_id) REFERENCES Users(User_id),
    FOREIGN KEY (Comment_id) REFERENCES Comments(Comment_id)
);

CREATE TABLE Has_Comment (
    Comment_id varchar(255),
    Photo_id varchar(255),
    PRIMARY KEY (Comment_id),
    FOREIGN KEY (Comment_id) REFERENCES Comments(Comment_id),
	  FOREIGN KEY (Photo_id) REFERENCES Photos(Photo_id)

);

CREATE TABLE Albums(
  	Album_id varchar(255) AUTO_INCREMENT,
    Album_Name varchar(255),
	  album_create_date DATE,
	  PRIMARY KEY (Album_id)

);

CREATE TABLE Owns_Album (
	  Album_id varchar(255),
	  User_id CHAR(10),
	  PRIMARY KEY(Album_id),
	  FOREIGN KEY (Album_id) REFERENCES Albums(Album_id),
	  FOREIGN KEY (User_id) REFERENCES Users(User_id)
);

CREATE TABLE Photos(
    Photo_id varchar(255) AUTO_INCREMENT,
    Caption varchar(255),
    Photo_Data longblob,
    Album_id vharchar(255),
    PRIMARY KEY (Photo_id),
    FOREIGN KEY (Album_id) REFERENCES Albums(Album_id)
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


CREATE TABLE Likes_Photo (
    User_id varchar(255),
	  Photo_id varchar(255),
    PRIMARY KEY (Photo_id, User_id),
    FOREIGN KEY (User_id) REFERENCES Users(User_id)
    FOREIGN KEY (Photo_id) REFERENCES Photos(Photo_id)
);

CREATE TABLE Has_Photo (
    Album_id varchar(255), 
    Photo_id varchar(255), 
    PRIMARY KEY (Photo_id),
    FOREIGN KEY (Album_id) REFERENCES Albums(Album_id), 
    FOREIGN KEY (Photo_id) REFERENCES Photos(Photo_id)
);

CREATE TABLE Tags (
	  Tag_Name VARCHAR(255),
	  PRIMARY KEY (tag_name)
);

CREATE TABLE TaggedWith (
    Photo_id varchar(255), 
    Tag_Name varchar(255),
    PRIMARY KEY (Photo_id, Tag_Name),
    FOREIGN KEY (Photo_id) REFERENCES Photos(Photo_id),
    FOREIGN KEY (Tag_Name) REFERENCES Tags(Tag_Name)
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
