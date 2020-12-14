

CREATE DATABASE photoshare;
USE photoshare;


CREATE TABLE Users 
(
    user_id int4  AUTO_INCREMENT,
    email varchar(255) NOT NULL UNIQUE,
    password varchar(255) NOT NULL,
    firstname varchar(255) NOT NULL,
    lastname varchar(255) NOT NULL,
    dob DATE NOT NULL,
    gender varchar(255),
    hometown varchar(255),
    bio varchar(255),
    profilepic longblob,
    contribution INTEGER  NOT NULL DEFAULT '0',
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);


INSERT INTO Users (email, password, firstname, lastname, dob) VALUES ('manager@bu.edu', 'manager', 'manager', 'user','2018-11-07');
INSERT INTO Users (email, password, firstname, lastname, dob) VALUES ('anonymous@bu.edu', 'anonymous', 'anonymous', 'user','2018-11-07');



CREATE TABLE Albums
(
  album_id int4  AUTO_INCREMENT,
  user_id int4 NOT NULL,
  name VARCHAR(255),
  doc DATE,
  CONSTRAINT albums_pk PRIMARY KEY (album_id),
  FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);



CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  album_id int4 NOT NULL,
  user_id int4 NOT NULL,
  imgdata longblob,
  caption VARCHAR(255),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id), 
  FOREIGN KEY (album_id) REFERENCES Albums (album_id) ON DELETE CASCADE,
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE is_Friend
(
  user1_id int4,
  user2_id int4,
  CONSTRAINT is_friend_pk PRIMARY KEY (user1_id, user2_id),
  FOREIGN KEY(user1_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(user2_id) REFERENCES Users(user_id) ON DELETE CASCADE
);


CREATE TABLE TaggedWith
(
  picture_id int4  AUTO_INCREMENT,
  description VARCHAR(255),
  CONSTRAINT tagged_with_pk PRIMARY KEY (picture_id, description),
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Comments
(
  comment_id int4  AUTO_INCREMENT,
  user_id int4 NOT NULL,
  picture_id int4 NOT NULL,
  txt VARCHAR(255),
  comment_date DATE,
  CONSTRAINT comments_pk PRIMARY KEY (comment_id),
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);


CREATE TABLE Likes
(
  user_id int4 NOT NULL,
  picture_id int4 NOT NULL,
  CONSTRAINT likes_pk PRIMARY KEY (user_id, picture_id),
  FOREIGN KEY(user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
  FOREIGN KEY(picture_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);



