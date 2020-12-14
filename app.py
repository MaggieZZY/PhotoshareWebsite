######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Craig Einstein <einstein@bu.edu>

# Ziyao Zhang
# U46618591

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
#import flask.ext.login as flask_login
import flask_login
#for image uploading
from werkzeug import secure_filename
import os, base64

import operator


mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Nihao123456789!' #CHANGE THIS TO YOUR MYSQL PASSWORD
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users") 
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users") 
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
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
			<h1>Login Page</h1>
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file
			# redirect me to menu.html
			# url for: can takes in keyword argument into the function(?)

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out') 

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html') 

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register/", methods=['GET'])
def register():
	return render_template('improved_register.html', supress='True')  

@app.route("/register/", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
                print email
		password=request.form.get('password')
		firstname = request.form.get('firstname')
		lastname = request.form.get('lastname')
		dob = request.form.get('birthday')
		gender = request.form.get('gender')
		hometown = request.form.get('hometown')
		bio = request.form.get('bio')

	except:
		print "couldn't find all tokens" #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	
	imgfile=None

	try: 
		imgfile = request.files['photo']
	except:
		print "error"
	print imgfile

	cursor = conn.cursor()
	test =  isEmailUnique(email)

	if test:


		if imgfile is None:
			cursor.execute("SELECT imgdata FROM Pictures WHERE user_id = '{0}'".format('1'))
			data = cursor.fetchone()[0]
		else: 
			data = base64.standard_b64encode(imgfile.read())

		print cursor.execute("INSERT INTO Users (email, password, firstname, lastname, dob, gender, hometown, bio, profilepic) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}','{8}')".format(email, password, firstname, lastname, dob, gender, hometown, bio, data))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('menu.html', name=email, message='Account Created!', profilepic=data)
	else:
		print "couldn't find all tokens (duplicate email)"
		return flask.redirect(flask.url_for('register', token="Email already exists"))


		# url for in a function 

# def getUsersPhotos(uid):
# 	cursor = conn.cursor()
# 	cursor.execute("SELECT picture_id, imgdata, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
# 	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]


def getAlbumsPhotos(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, imgdata, caption FROM Pictures WHERE album_id = '{0}'".format(album_id))
	return cursor.fetchall() #NOTE list of tuples



def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id, name, doc FROM Albums WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(album_id, name, doc), ...]

def getUsersFriends(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT user2_id FROM is_Friend WHERE user1_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples


def getPhotosTags(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT description FROM TaggedWith WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchall() #NOTE list of tuples, [(desciption1,), (description2,), ...]

def getPhotosComments(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT comment_id, user_id, picture_id, txt, comment_date FROM Comments WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchall() #NOTE list of tuples, [(commment_id, user_id, picture_id, txt, comment_date), (...),...]


def getPhotosLikes(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, picture_id FROM Likes WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchall() #NOTE list of tuples



def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def getUserIdFromPhotoId(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id FROM Pictures WHERE picture_id = '{0}'".format(photo_id))
	return cursor.fetchone()[0]


def getUserNameFromId(user_id):
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname FROM Users WHERE user_id = '{0}'".format(user_id))
	return cursor.fetchone()[0]


def getAlbumIdFromName(name):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id  FROM Albums WHERE name = '{0}'".format(name))
	return cursor.fetchone()[0]


def getPhotoFromId(photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, album_id, imgdata, caption FROM Pictures WHERE picture_id = '{0}'".format(photo_id))
	ret = cursor.fetchall()
	if ret != ():
		return ret[0]
	else:
		print("Nothing found")



def hasAlreadyLiked(photo_id, user_id):
	cursor = conn.cursor()
	if cursor.execute("SELECT picture_id, user_id FROM Likes WHERE picture_id = '{0}' AND user_id = '{1}'".format(photo_id, user_id)):
		return True
	else:
		return False


def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)): 
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/menu')
# @flask_login.login_required # line 116
def protected():
	try:
		uid =  getUserIdFromEmail(flask_login.current_user.id)
	except:
		uid ='2'
	cursor = conn.cursor()
	cursor.execute("SELECT profilepic FROM Users WHERE user_id = '{0}'".format(uid))
	profilepic = cursor.fetchone()[0]
	return render_template("menu.html", profilepic=profilepic)


#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1) in ALLOWED_EXTENSIONS



@app.route('/profile', methods = ['GET'])
@flask_login.login_required
def view_profile():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT email, password, firstname, lastname, dob, gender, hometown, bio, profilepic FROM Users WHERE user_id = '{0}'".format(uid))
	myProfile = cursor.fetchall()
	return render_template("profile.html", profile=myProfile)



@app.route('/profile', methods = ['POST'])
@flask_login.login_required
def change_profile_pic():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	imgfile = request.files['photo']
	data = base64.standard_b64encode(imgfile.read())
	cursor = conn.cursor()
	cursor.execute("UPDATE Users SET profilepic = '{0}' WHERE user_id = '{1}'".format(data, uid))
	conn.commit()
	cursor.execute("SELECT email, password, firstname, lastname, dob, gender, hometown, bio, profilepic FROM Users WHERE user_id = '{0}'".format(uid))
	myProfile = cursor.fetchall()
	return render_template("profile.html", profile=myProfile)




@app.route('/createalbum', methods = ['GET'])
@flask_login.login_required
def create_album():
	return render_template("createalbum.html")


@app.route('/createalbum', methods = ['POST'])
@flask_login.login_required
def create_new_album():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	album_name = request.form.get('album_name')
	doc = request.form.get('doc')
	cursor = conn.cursor()
	cursor.execute("INSERT INTO Albums (user_id, name, doc) VALUES ('{0}', '{1}', '{2}' )".format(uid, album_name, doc))
	conn.commit()
	myAlbums = getUsersAlbums(uid)
 	return render_template("albums.html", name=flask_login.current_user.id, message='New Album Created!', albums=myAlbums )


@app.route('/viewalbums', methods = ['GET']) 
@flask_login.login_required
def view_albums():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	myAlbums = getUsersAlbums(uid) # [(album_id, name, doc),..]
	return render_template("albums.html", message="Here are all of your albums", name=flask_login.current_user.id, albums=myAlbums )


@app.route('/viewalbums/<album_id>', methods = ['GET']) # album_id here is album[0] in albums.html
@flask_login.login_required
def view_photos_in_album(album_id):
	myPhotos = getAlbumsPhotos(album_id)
	return render_template("photos.html", message="Photos in this album", albumid=album_id, photos=myPhotos, canedit=True)



@app.route('/deletealbum/<album_id>')
@flask_login.login_required
def delete_album(album_id):
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Albums WHERE album_id =('{0}')".format(album_id))
	conn.commit()
	myAlbums = getUsersAlbums(uid)
	return render_template("albums.html", message="Album deleted", albums=myAlbums)



@app.route('/upload/<album_id>', methods=['GET', 'POST']) # album_id here is albumid in photos.html
@flask_login.login_required
def upload_file(album_id):
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		print caption
		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Pictures (album_id, user_id, imgdata, caption) VALUES ('{0}', '{1}', '{2}', '{3}' )".format(album_id, uid, photo_data, caption))
		cursor.execute("UPDATE Users SET contribution = contribution + 1 WHERE user_id = '{0}'".format(uid))
		conn.commit()
		myPhotos = getAlbumsPhotos(album_id)
		return render_template("photos.html", name=flask_login.current_user.id, message='Photo uploaded!', albumid=album_id, photos=myPhotos )
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		# myAlbums = getUsersAlbums(uid)
		return render_template("upload.html", name=flask_login.current_user.id, albumid=album_id)
#end photo uploading code 



@app.route('/deletephoto/<album_id>/<photo_id>')
@flask_login.login_required
def delete_photo(album_id, photo_id):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM Pictures WHERE picture_id ='{0}'".format(photo_id))
	conn.commit()
	myPhotos = getAlbumsPhotos(album_id)
	return render_template("photos.html", message="Photo deleted", photos=myPhotos, albumid=album_id)



@app.route('/viewtags/<album_id>/<photo_id>', methods = ['GET'])
def view_tags(album_id, photo_id):
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)

	except:
		uid = '2'

	myTags = getPhotosTags(photo_id)
	photo_uid = getUserIdFromPhotoId(photo_id)
	if uid == photo_uid:
		return render_template("tags.html", message="Here are the photo's tags", albumid=album_id, photoid=photo_id, tags=myTags, canedit=True)
	else:
		return render_template("tags.html", message="Here are the photo's tags", albumid=album_id, photoid=photo_id, tags=myTags, canedit=False)


@app.route('/addtag/<album_id>/<photo_id>', methods=['GET'])
@flask_login.login_required
def add_tag(album_id, photo_id):
	return render_template("addtag.html", message="Add a tag for this photo", albumid=album_id, photoid=photo_id)


@app.route('/addtag/<album_id>/<photo_id>', methods = ['POST'])
@flask_login.login_required
def add_new_tag(album_id, photo_id):
	tag_name = request.form.get("tag_name")
	cursor = conn.cursor()
	cursor.execute("INSERT INTO TaggedWith (picture_id, description) VALUES ('{0}', '{1}')".format(photo_id, tag_name))
	conn.commit()
	myTags = getPhotosTags(photo_id)
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photo_uid = getUserIdFromPhotoId(photo_id)
	if uid == photo_uid:
		return render_template("tags.html", message="Tag added", albumid=album_id, photoid=photo_id, tags=myTags, canedit=True)
	else:
		return render_template("tags.html", message="Tag added", albumid=album_id, photoid=photo_id, tags=myTags, canedit=False)
	

@app.route('/deletetag/<album_id>/<photo_id>/<description>')
@flask_login.login_required
def delete_tag(album_id, photo_id, description):
	cursor = conn.cursor()
	cursor.execute("DELETE FROM TaggedWith WHERE description ='{0}'".format(description))
	conn.commit()
	myTags = getPhotosTags(photo_id)
	uid = getUserIdFromEmail(flask_login.current_user.id)
	photo_uid = getUserIdFromPhotoId(photo_id)
	if uid == photo_uid:
		return render_template("tags.html", message="Here are the photo's tags", albumid=album_id, photoid=photo_id, tags=myTags, canedit=True)
	else:
		return render_template("tags.html", message="Here are the photo's tags", albumid=album_id, photoid=photo_id, tags=myTags, canedit=False)



@app.route('/viewcomments/<album_id>/<photo_id>', methods = ['GET'])
def view_comments(album_id, photo_id):
	comments = getPhotosComments(photo_id) # list of tuples, [(commment_id, user_id, picture_id, txt, comment_date), (...),...]
	myComments = []
	for i in comments:
		user_name = getUserNameFromId(i[1])
		myComments.append((i[0], user_name, i[2], i[3], i[4]))
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)
		photo_uid = getUserIdFromPhotoId(photo_id)
		if uid == photo_uid:
			return render_template("comments.html", message="Here are the comments for this photo", albumid=album_id, photoid=photo_id, comments=myComments, canedit=False)
		else:
			return render_template("comments.html", message="Here are the comments for this photo", albumid=album_id, photoid=photo_id, comments=myComments, canedit=True)

	except:
		return render_template("comments.html", message="Here are the comments for this photo", albumid=album_id, photoid=photo_id, comments=myComments, canedit=True)


@app.route('/makecomment/<album_id>/<photo_id>', methods = ['GET'])
def make_comment(album_id, photo_id):
	return render_template("makecomment.html", message="Create a comment here", albumid=album_id, photoid=photo_id)



@app.route('/makecomment/<album_id>/<photo_id>', methods = ['POST'])
def make_new_comment(album_id, photo_id):
	text = request.form.get("comment_txt")
	date = request.form.get("comment_date")
	try:
		uid = getUserIdFromEmail(flask_login.current_user.id)

	except:
		uid = '2'

	cursor = conn.cursor()
	cursor.execute("INSERT INTO Comments(user_id, picture_id, txt, comment_date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(uid, photo_id, text, date))
	cursor.execute("UPDATE Users SET contribution = contribution + 1 WHERE user_id = '{0}'".format(uid))
	conn.commit()
	comments = getPhotosComments(photo_id) # list of tuples, [(commment_id, user_id, picture_id, txt, comment_date), (...),...]
	myComments = []
	for i in comments:
		user_name = getUserNameFromId(i[1])
		myComments.append((i[0], user_name, i[2], i[3], i[4]))
	return render_template("comments.html", message="Comment created", albumid=album_id, photoid=photo_id, comments=myComments)


@app.route('/viewlikes/<album_id>/<photo_id>', methods = ['GET'])
@flask_login.login_required
def view_likes(album_id, photo_id):
	cursor = conn.cursor()
	cursor.execute("SELECT COUNT(user_id) FROM Likes WHERE picture_id = '{0}'".format(photo_id))
	number = cursor.fetchone()[0]
	print number
	myLikes = getPhotosLikes(photo_id) # [(user_id, picture_id), (user_id, picture_id),...]
	user_name = []
	for i in myLikes:
		# print(i[1])
		user_name.append(getUserNameFromId(i[0])) # [(firstname, lastname), (firstname, lastname),...]
	return render_template("likes.html", message="Here are the likes for this photo", albumid=album_id, photoid=photo_id, user_name=user_name, numberoflikes=number)



@app.route('/makelike/<album_id>/<photo_id>', methods = ['POST'])
@flask_login.login_required
def make_new_like(album_id, photo_id):
	uid = getUserIdFromEmail(flask_login.current_user.id)
	if hasAlreadyLiked(photo_id, uid) == False:
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Likes(user_id, picture_id) VALUES ('{0}', '{1}')".format(uid, photo_id))
		conn.commit()
		myLikes = getPhotosLikes(photo_id)
		numberoflikes = len(myLikes) 
		user_name = []
		for i in myLikes:
			user_name.append(getUserNameFromId(i[0]))
		return render_template("likes.html", message="like created", albumid=album_id, photoid=photo_id, user_name=user_name, numberoflikes=numberoflikes)

	else:
		return render_template("likes.html", message="Has already like this photo", albumid=album_id, photoid=photo_id)



@app.route('/viewfriends', methods = ['GET'])
@flask_login.login_required
def friends():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT user2_id FROM is_Friend WHERE user1_id = '{0}'".format(uid))
	myFriends = cursor.fetchall()
	friend_name = []
	for i in myFriends:
		friend_name.append(getUserNameFromId(i[0]))
	return render_template("friends.html", name=flask_login.current_user.id, message="Here's a list of your friends", friends=friend_name)



@app.route('/searchpeople', methods = ['GET']) 
@flask_login.login_required
def add_new_friend():
	return render_template('searchpeople.html')



@app.route('/searchpeople', methods = ['POST'])
@flask_login.login_required
def search_people():
	try:
		email = request.form.get('QUERY')
		cursor = conn.cursor()
		cursor.execute("SELECT user_id, firstname, lastname from Users WHERE email = '{0}'".format(email))
		search_result = cursor.fetchall()
		return render_template("searchpeople.html", name=flask_login.current_user.id, results = search_result)

	except:
		print("Couldn't Find a Match")



@app.route('/addfriend/<uid_friend>')
@flask_login.login_required
def add_friend(uid_friend):
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO is_Friend (user1_id, user2_id) VALUES ('{0}', '{1}')".format(uid, uid_friend))
	conn.commit()
	myFriends = getUsersFriends(uid)
	friend_name = []
	for i in myFriends:
		friend_name.append(getUserNameFromId(i[0]))
	return render_template("friends.html", message="New friend added", friends=friend_name)



@app.route('/viewprofile/<uid_friend>')
@flask_login.login_required
def view_user_profile(uid_friend):
	cursor = conn.cursor()
	cursor.execute("SELECT email, firstname, lastname, dob, gender, hometown, bio, profilepic FROM Users WHERE user_id = '{0}'".format(uid_friend))
	userProfile = cursor.fetchall()
	print(uid_friend)
	return render_template("userprofile.html", profile=userProfile, result=uid_friend)



@app.route('/photosearch', methods = ['GET'])
def photo_search():
	return render_template("photosearch.html", message="Search for all photos by tags", photosearch=True)




@app.route('/photosearch', methods = ['POST']) 
def photo_search_by_tag():
	tag_name = request.form.get("tag_name")
	tagname = tag_name.split(" ")
	idList = []
	allPhotos = []
	for tag in tagname:
		cursor = conn.cursor()
		cursor.execute("SELECT picture_id FROM TaggedWith WHERE description = '{0}'".format(tag))
		photo_tuple = cursor.fetchall() #((id1,),(id2,)..)
		l = []
		for i in photo_tuple:
			l.append(i[0])
		idList.append(l)

	intersection = set(idList[0]).intersection(*idList)
	ret = list(intersection)
	if ret != []:
		for j in ret: # j is photo id
			allPhotos.append(getPhotoFromId(j))
	return render_template("photosearch.html", message="Here are all the photos", photos=allPhotos, canedit=False, photosearch=True)




@app.route('/photosearch/<tag_name>', methods = ['POST']) 
def photo_search_by_given_tag(tag_name):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM TaggedWith WHERE description = '{0}'".format(tag_name))
	photo_tuple = cursor.fetchall() #[(id1,),(id2,)..]
	allPhotos = []
	if photo_tuple != []:
		for i in photo_tuple:
			photo_id = i[0]
			allPhotos.append(getPhotoFromId(photo_id))
	return render_template("photosearch.html", message="Here are the results", photos=allPhotos, canedit=False)



@app.route('/viewtop5', methods = ['GET'])
def view_top_5():
	cursor = conn.cursor()
	cursor.execute("SELECT description, COUNT(picture_id) from TaggedWith GROUP BY description ORDER BY COUNT(picture_id) DESC LIMIT 5")
	toptags = cursor.fetchall() # a list of tuples [(tag, count), (tag, count),...]
	return render_template("viewtop5.html", message="Here are the top 5 tags", tags=toptags)


@app.route('/viewownbytag', methods = ['GET'])
@flask_login.login_required
def view_own_tag():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT description from TaggedWith NATURAL JOIN Pictures WHERE user_id = '{0}'".format(uid))
	tags = cursor.fetchall() # a list of tuples [(tag, count), (tag, count),...]
	return render_template("viewownbytag.html", message="Here are all the tags you have used", tags=tags)



@app.route('/viewownbytag/<tag_name>', methods = ['POST'])
@flask_login.login_required
def view_own_photos_by_tag(tag_name):
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM TaggedWith NATURAL JOIN Pictures WHERE description = '{0}' and user_id = '{1}'".format(tag_name, uid))
	photo_tuple = cursor.fetchall() #[(id1,),(id2,)..]
	myPhotos = []
	if photo_tuple != []:
		for i in photo_tuple:
			photo_id = i[0]
			myPhotos.append(getPhotoFromId(photo_id))
	return render_template("photosearch.html", message="Here are the results", photos=myPhotos, canedit=False)



@app.route('/viewotherbytag/<tag_name>', methods = ['POST'])
@flask_login.login_required
def view_other_photos_by_tag(tag_name):
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM TaggedWith NATURAL JOIN Pictures WHERE description = '{0}' AND user_id != '{1}'".format(tag_name, uid))
	photo_tuple = cursor.fetchall() #[(id1,),(id2,)..]
	myPhotos = []
	if photo_tuple != []:
		for i in photo_tuple:
			photo_id = i[0]
			myPhotos.append(getPhotoFromId(photo_id))
	return render_template("photosearch.html", message="Here are the results", photos=myPhotos, canedit=False)



@app.route('/youmayalsolike')
@flask_login.login_required
def you_may_also_like():
	uid =  getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT DISTINCT description, COUNT(picture_id) From TaggedWith NATURAL JOIN Pictures WHERE user_id = '{0}' GROUP BY description ORDER BY COUNT(picture_id) DESC LIMIT 5".format(uid))
	tags = cursor.fetchall() # a list of tuples [(tag1, count), (tag2, count),...]

	five_tag = []
	for i in tags:
		five_tag.append(i[0])
	print five_tag

	cursor = conn.cursor()
	cursor.execute("SELECT picture_id From Pictures WHERE user_id != '{0}'".format(uid))
	allPhotoId = cursor.fetchall()

	print allPhotoId # ((1,), (5,), (6,), (7,), (10,)...)

	count_dict = {}

	for j in allPhotoId:
		count_dict[j[0]] = 0
		photo_tag = getPhotosTags(j[0]) # ((u'boston',), (u'building',), (u'city',), (u'night',), (u'river',)...
		for k in photo_tag:
			if k[0] in five_tag:
				count_dict[j[0]] += 2
			else:
				count_dict[j[0]] -= 0.01

	print count_dict

	score_dict = sorted(count_dict.items(), key=operator.itemgetter(1), reverse=True)

	# print score_dict

	recommendedPhotos = []
	for l in score_dict:
		if l[1] > 0:
			recommendedPhotos.append(getPhotoFromId(l[0])) 
	return render_template("youmayalsolike.html", message="Here are the photos you may also like", photos=recommendedPhotos)

	


@app.route('/tagrecommendation', methods = ['GET'])
@flask_login.login_required
def enter_tag():
	return render_template("entertag.html", message="Tag recommendation", entertag=True)


@app.route('/tagrecommendation', methods = ['POST'])
@flask_login.login_required
def tag_recommendation():
	tag_name = request.form.get("tag_name")
	tagname = tag_name.split(" ")
	idList = []
	for tag in tagname:
		cursor = conn.cursor()
		cursor.execute("SELECT picture_id FROM TaggedWith WHERE description = '{0}'".format(tag))
		photo_tuple = cursor.fetchall() #((id1,),(id2,)..)
		for i in photo_tuple:
			idList.append(i[0])

	tag_list = []
	if idList != []:
		for j in idList: # j is photo id
			photo_tags = getPhotosTags(j)
			for k in photo_tags:
				tag_list.append(k[0])


	tag_dict = {}
	for a in tag_list:
		if a in tag_dict:
			tag_dict[a] += 1
		else:
			tag_dict[a] = 1


	sorted_dict = sorted(tag_dict.items(), key=operator.itemgetter(1), reverse=True)

	tag_recommendation_list = []

	for b in sorted_dict:
		if b[0] not in tag_recommendation_list and b[0] not in tagname:
			tag_recommendation_list.append(b[0])
				
	return render_template("entertag.html", message="Here are the recommended tags", tags=tag_recommendation_list)



@app.route('/usercontribution', methods = ['GET'])
@flask_login.login_required
def user_contribution():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("SELECT firstname, lastname FROM Users WHERE user_id != '1' AND user_id != '2' ORDER BY contribution DESC LIMIT 10")
	contribution = cursor.fetchall()
	return render_template("usercontribution.html", message="This is the contribution board", usercontribution=contribution)


#default page  
@app.route("/", methods=['GET'])
def hello():
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id, imgdata, caption FROM Pictures WHERE user_id != '1'")
	photos = cursor.fetchall() 
	print(len(photos))
	return render_template('hello.html', message='Welcome to Photoshare', photos=photos)


if __name__ == "__main__":
	#this is invoked when in the shell  you run 
	#$ python app.py 
	app.run(port=5000, debug=True)
