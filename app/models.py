from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5

followers = db.Table('followers',
	db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

show_requests = db.Table('show_requests',
 db.Column('requester_id', db.Integer, db.ForeignKey('user.id')),
 db.Column('requested_id', db.Integer, db.ForeignKey('show.id'))
)

@login.user_loader
def load_user(id):
	return User.query.get(int(id));

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), index=True, unique=True)
	first_name = db.Column(db.String(64))
	last_name = db.Column(db.String(64))
	email = db.Column(db.String(120), index=True, unique=True)
	password_hash = db.Column(db.String(128))
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	about_me = db.Column(db.String(140))
	last_seen = db.Column(db.DateTime, default= datetime.utcnow)
	Address_id = db.Column(db.Integer, db.ForeignKey('address.id', ondelete='CASCADE'))
	is_admin = db.Column(db.Boolean, default=False)


	followed = db.relationship(
		'User', 
		secondary=followers,
		primaryjoin = (followers.c.follower_id == id),
		secondaryjoin = (followers.c.followed_id == id),
		backref= db.backref('followers', lazy='dynamic'), 
		lazy='dynamic')

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	def check_password(self, password):
		return check_password_hash(self.password_hash,password)

	def avatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

	def follow(self, user):
		if not self.is_following(user):
			self.followed.append(user)
	def unfollow(self, user):
		if self.is_following(user):
			self.followed.remove(user)
	def is_following(self, user):
		return self.followed.filter(
			followers.c.followed_id == user.id
		).count() > 0

	def followed_posts(self):
		followed = Post.query.join(
			followers, (
				followers.c.followed_id == Post.user_id
				)
			).filter(
				followers.c.follower_id == self.id
			)
		own = Post.query.filter_by(user_id = self.id)
		return followed.union(own).order_by(Post.timestamp.desc())

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	body = db.Column(db.Text)
	timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __repr__(self):
		return '<Post {}>'.format(self.body)

class Address(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	city = db.Column(db.String(50))
	address = db.Column(db.String(50))
	cadress2 = db.Column(db.String(50))
	postal_code = db.Column(db.String(10))
	phone = db.Column(db.String(20))
	country = db.Column(db.String(50))
	last_update = db.Column(db.DateTime, default=datetime.utcnow)
	Username = db.Column(db.String, db.ForeignKey('user.username', ondelete='CASCADE'))


class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	description = db.Column(db.String(250))
	release_year = db.Column(db.Integer)
	rating = db.Column(db.Integer)
	loan_status = db.Column(db.String(150))
	last_update = db.Column(db.DateTime, default=datetime.utcnow)



class Film(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	description = db.Column(db.String(250))
	release_year = db.Column(db.Integer)
	rating = db.Column(db.Integer)
	loan_status = db.Column(db.String(150))
	last_update = db.Column(db.DateTime, default=datetime.utcnow)

class Show(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	description = db.Column(db.String(250))
	release_year = db.Column(db.Integer)
	rating = db.Column(db.Integer)
	loan_status = db.Column(db.String(150))
	last_update = db.Column(db.DateTime, default=datetime.utcnow)
	
 
	requested_show = db.relationship(
 		'Show',
	secondary=show_requests,
	primaryjoin=(show_requests.c.requester_id == id),
	secondaryjoin=(show_requests.c.requested_id == id),
	backref=db.backref('requesters', lazy='dynamic'), 
	lazy='dynamic')

	def request(self, Show):
		if not self.is_requested(Show):
			self.requested_show.append(Show)







class RequestedShow(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	show_id = db.Column(db.Integer, db.ForeignKey('show.id', ondelete='CASCADE'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
	request_date = db.Column(db.DateTime, default=datetime.utcnow)


class GamesBooking(db.Model):
	bookingid = db.Column(db.Integer, primary_key=True, autoincrement=True)
	userid = db.Column(db.Integer, db.ForeignKey('user.id'))
	gameid = db.Column(db.Integer, db.ForeignKey('game.id'))
	fromdate = db.Column(db.DateTime)
	todate = db.Column(db.DateTime)
	caleventid = db.Column(db.String(255))
	req_date = db.Column(db.DateTime)


	def __repr__(self):
			return "<Booking(bookingid='%s', userid='%s', gameid='%s', fromdate='%s', todate='%s')>" % (
				self.bookingid, self.userid, self.gameid, self.fromdate, self.todate
			)

class FilmBooking(db.Model):
    bookingid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    filmid = db.Column(db.Integer, db.ForeignKey('film.id'))
    fromdate = db.Column(db.DateTime)
    todate = db.Column(db.DateTime)
    req_date = db.Column(db.DateTime)

class ShowBooking(db.Model):
    bookingid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    showid = db.Column(db.Integer, db.ForeignKey('show.id'))
    fromdate = db.Column(db.DateTime)
    todate = db.Column(db.DateTime)
    req_date = db.Column(db.DateTime)