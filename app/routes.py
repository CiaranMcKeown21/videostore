from operator import add
from flask import abort, render_template, flash, redirect, url_for, request
from flask_wtf import form
from app import app, db
from app.forms import AdminFilmForm, AdminShowForm, AdminUserForm, AdminVideoForm, BookingForm, LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, EditAddressForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Film, FilmBooking, GamesBooking, Show, ShowBooking, User, Post, Address, Game
from werkzeug.urls import url_parse
from datetime import date, datetime

import json


@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.utcnow()
		db.session.commit()


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')
		return redirect(url_for('index'))
	page = request.args.get('page', 1, type=int)
	posts = current_user.followed_posts().paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('index', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) if posts.has_prev else None
	return render_template('index.html', title='Home', form=form, posts=posts.items, 
		next_url = next_url, prev_url=prev_url)

@app.route('/explore')
@login_required
def explore():
	page = request.args.get('page', 1, type=int)
	posts = Post.query.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('explore', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) if posts.has_prev else None

	return render_template('index.html', title='Explore',posts=posts.items, next_url= next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if user.is_admin:
			return redirect(url_for('admin_dashboard'))
		if not next_page or url_parse(next_page).netloc != '':
			next_page=url_for('index')
		return redirect(next_page)
		
	return render_template('login.html', title='Sign In', form=form)



@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user=User(username=form.username.data, email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return(redirect(url_for('login')))
	return render_template('register.html', title= 'Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	page = request.args.get('page', 1, type=int)
	posts = user.posts.order_by(Post.timestamp.desc()).paginate(
		page, app.config['POSTS_PER_PAGE'], False)
	next_url = url_for('user', username=user.username, page = posts.next_num) if posts.has_next else None
	prev_url = url_for('user', username=user.username, page = posts.prev_num) if posts.has_prev else None
	form = EmptyForm()
	return render_template('user.html', user=user, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.first_name = form.first_name.data
		current_user.last_name = form.last_name.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.first_name.data = current_user.first_name
		form.last_name.data = current_user.last_name
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/edit_address', methods=['GET', 'POST'])
def edit_address():
	form = EditAddressForm()
	if form.validate_on_submit():
		current_user.city = form.city.data
		current_user.address = form.address.data
		current_user.postal_Code = form.postal_Code.data
		current_user.country = form.country.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_address'))
	elif request.method == 'GET':
		form.city.data = current_user.city
		form.address.data = current_user.address
		form.postal_Code.data = current_user.postal_code
	return render_template('edit_address.html', title='Edit Profile', form=form)
    


@app.route('/follow/<username>', methods = ['POST'])
@login_required
def follow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=username).first()
		if user is None:
			flash('User {} not found.'.format(username))
			return redirect(url_for('index'))
		if user == current_user:
			flash('You cannot follow yourself!')
			return redirect(url_for('user', username=username))
		current_user.follow(user)
		db.session.commit()
		flash('You are following {}!'.format(username))
		return redirect(url_for('user', username=username))
	else:
		return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods = ['POST'])
@login_required
def unfollow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=username).first()
		if user is None:
			flash('User {} not found.'.format(username))
			return redirect(url_for('index'))
		if user == current_user:
			flash('You cannot unfollow yourself!')
			return redirect(url_for('user', username=username))
		current_user.unfollow(user)
		db.session.commit()
		flash('You have stopped following {}'.format(username))
		return redirect(url_for('user', username = username))
	else:
		return redirect(url_for('index'))

@app.route('/posts/<id>', methods=['GET', 'POST'])
@login_required
def update_posts(id):
    form = PostForm()
    #first we need to fetch the post
    post = Post.query.get(id)
    #check that the user is authorised to edit this post
    if post.author == current_user:
        if form.validate_on_submit():
            #then we update the values with the new from the form
            post.body = form.post.data
            db.session.commit()
            flash('Your changes have been saved.')
            return redirect(url_for('index'))
        elif request.method == 'GET':
            form.post.data = post.body
        return render_template('edit_post.html', title='Edit Post', form=form)
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # prevent non-admins from accessing the page
	if not current_user.is_admin:
		return render_template('error403.html', title="Error 403")
	return render_template('admin_dashboard.html', title="Dashboard")

@app.route('/games')
@login_required
def games():
	games = Game.query.all()
	return render_template ('games.html', games=games, title="Games")


def check_admin():
	if not current_user.is_admin:
		abort(403)

#Game View
@app.route('/admin_games', methods=['GET', 'POST'])
@login_required
def list_games():
	check_admin()
	games = Game.query.all()
	return render_template ('admin/games/games.html', games=games, title="Games")

@app.route('/admin_games/add', methods=['GET', 'POST'])
@login_required
def add_game():
	check_admin()
	add_game = True
	form = AdminVideoForm()
	if form.validate_on_submit():
		game = Game(name=form.name.data, description=form.description.data, release_year = form.release_year.data, rating = form.rating.data, loan_status = form.loan_status.data, last_update = datetime.utcnow())

		try:
			db.session.add(game)
			db.session.commit()
			flash('You have successfully added a new game.')
		
		except:
			flash('Error: Game already exists.')
		return redirect(url_for('list_games'))

	return render_template('admin/games/game.html', action="Add", add_game=add_game, form=form, title="Add Game")


@app.route('/admin_games/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_game(id):
	check_admin()
	add_game = False
	game = Game.query.get_or_404(id)
	form = AdminVideoForm(obj=game)
	if form.validate_on_submit():
		game.name = form.name.data
		game.description = form.description.data
		game.release_year = form.release_year.data
		game.rating = form.rating.data
		game.loan_status = form.loan_status.data
		game.last_update = datetime.utcnow()
		db.session.commit()
		flash('You have successfully edited the game.')
		return redirect(url_for('list_games'))
	form.description.data = game.description
	form.name.data = game.name
	return render_template('admin/games/game.html', action="Edit", add_game=add_game, form=form, game=game, title="Edit Game")


@app.route('/admin_games/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_game(id):
	check_admin()
	game = Game.query.get_or_404(id)
	db.session.delete(game)
	db.session.commit()
	flash('You have successfully deleted the game.')
	return redirect(url_for('list_games'))


#User View
@app.route('/admin_users', methods=['GET', 'POST'])
@login_required
def list_users():
	check_admin()
	users = User.query.all()
	return render_template ('admin/users/users.html', users=users, title="Users")

@app.route('/admin_users/add', methods=['GET', 'POST'])
@login_required
def add_user():
	check_admin()
	add_user = True
	form = AdminUserForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, first_name=form.first_name.data, last_name = form.last_name.data, email = form.email.data)

		try:
			db.session.add(user)
			db.session.commit()
			flash('You have successfully added a new user.')
		
		except:
			flash('Error: User already exists.')
		return redirect(url_for('list_users'))

	return render_template('admin/users/user.html', action="Add", add_user=add_user, form=form, title="Add User")


@app.route('/admin_users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
	check_admin()
	add_user = False
	user = User.query.get_or_404(id)
	form = AdminUserForm(obj=user)
	if form.validate_on_submit():
		user.username = form.username.data
		user.first_name = form.first_name.data
		user.last_name = form.last_name.data
		user.email = form.email.data
		user.last_update = datetime.utcnow()
		db.session.commit()
		flash('You have successfully edited the game.')
		return redirect(url_for('list_users'))

	return render_template('admin/users/user.html', action="Edit", add_user=add_user, form=form, user=user, title="Edit Game")


@app.route('/admin_users/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_user(id):
	check_admin()
	user = User.query.get_or_404(id)
	db.session.delete(user)
	db.session.commit()
	flash('You have successfully deleted the user.')
	return redirect(url_for('list_users'))


#Film View

@app.route('/films')
@login_required
def films():
	films = Film.query.all()
	return render_template ('films.html', films=films, title="Films")

@app.route('/admin_films', methods=['GET', 'POST'])
@login_required
def list_films():
	check_admin()
	films = Film.query.all()
	return render_template ('admin/films/films.html', films=films, title="Films")

@app.route('/admin_films/add', methods=['GET', 'POST'])
@login_required
def add_film():
	check_admin()
	add_film = True
	form = AdminFilmForm()
	if form.validate_on_submit():
		film = Film(name=form.name.data, description=form.description.data, release_year = form.release_year.data, rating = form.rating.data, loan_status = form.loan_status.data, last_update = datetime.utcnow())

		try:
			db.session.add(film)
			db.session.commit()
			flash('You have successfully added a new film.')
		
		except:
			flash('Error: Film already exists.')
		return redirect(url_for('list_films'))

	return render_template('admin/films/film.html', action="Add", add_film=add_film, form=form, title="Add Film")


@app.route('/admin_films/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_film(id):
	check_admin()
	add_film = False
	film = Film.query.get_or_404(id)
	form = AdminVideoForm(obj=film)
	if form.validate_on_submit():
		film.name = form.name.data
		film.description = form.description.data
		film.release_year = form.release_year.data
		film.rating = form.rating.data
		film.loan_status = form.loan_status.data
		film.last_update = datetime.utcnow()
		db.session.commit()
		flash('You have successfully edited the film.')
		return redirect(url_for('list_films'))
	form.description.data = film.description
	form.name.data = film.name
	return render_template('admin/films/film.html', action="Edit", add_film=add_film, form=form, film=film, title="Edit Film")


@app.route('/admin_films/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_film(id):
	check_admin()
	film = Film.query.get_or_404(id)
	db.session.delete(film)
	db.session.commit()
	flash('You have successfully deleted the film.')
	return redirect(url_for('list_films'))


#show View


@app.route('/shows')
@login_required
def shows():
	shows = Show.query.all()
	return render_template ('shows.html', shows=shows, title="Shows")

@app.route('/admin_shows', methods=['GET', 'POST'])
@login_required
def list_shows():
	check_admin()
	shows = Show.query.all()
	return render_template ('admin/shows/shows.html', shows=shows, title="Shows")

@app.route('/admin_shows/add', methods=['GET', 'POST'])
@login_required
def add_show():
	check_admin()
	add_show = True
	form = AdminShowForm()
	if form.validate_on_submit():
		show = Show(name=form.name.data, description=form.description.data, release_year = form.release_year.data, rating = form.rating.data, loan_status = form.loan_status.data, last_update = datetime.utcnow())

		try:
			db.session.add(show)
			db.session.commit()
			flash('You have successfully added a new show.')
		
		except:
			flash('Error: Show already exists.')
		return redirect(url_for('list_shows'))

	return render_template('admin/shows/show.html', action="Add", add_show=add_show, form=form, title="Add Show")


@app.route('/admin_shows/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_show(id):
	check_admin()
	add_show = False
	show = Show.query.get_or_404(id)
	form = AdminVideoForm(obj=show)
	if form.validate_on_submit():
		show.name = form.name.data
		show.description = form.description.data
		show.release_year = form.release_year.data
		show.rating = form.rating.data
		show.loan_status = form.loan_status.data
		show.last_update = datetime.utcnow()
		db.session.commit()
		flash('You have successfully edited the show.')
		return redirect(url_for('list_shows'))
	form.description.data = show.description
	form.name.data = show.name
	return render_template('admin/shows/show.html', action="Edit", add_show=add_show, form=form, show=show, title="Edit Show")


@app.route('/admin_shows/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_show(id):
	check_admin()
	show = Show.query.get_or_404(id)
	db.session.delete(show)
	db.session.commit()
	flash('You have successfully deleted the show.')
	return redirect(url_for('list_shows'))


@app.route('/game/loan/<int:id>', methods=['GET', 'POST'])
@login_required
def gameloan(id):
	game_booking = True
	form = BookingForm()
	if form.validate_on_submit():
		game_booking = GamesBooking(fromdate=form.fromdate.data, todate=form.todate.data, req_date = datetime.utcnow(), userid = current_user.id, gameid = id)
		try:
			db.session.add(game_booking)
			db.session.commit()
			flash('You have successfully requested this loan.')
		
		except:
			flash('Error: Booking Error.')
		return redirect(url_for('games'))

	return render_template('loan.html', action="Add", game_booking=game_booking, form=form, title="Request Loan")

@app.route('/film/loan/<int:id>', methods=['GET', 'POST'])
@login_required
def filmloan(id):
	film_booking = True
	form = BookingForm()
	if form.validate_on_submit():
		film_booking = FilmBooking(fromdate=form.fromdate.data, todate=form.todate.data, req_date = datetime.utcnow(), userid = current_user.id, filmid = id)
		try:
			db.session.add(film_booking)
			db.session.commit()
			flash('You have successfully requested this loan.')
		
		except:
			flash('Error: Booking Error.')
		return redirect(url_for('films'))

	return render_template('loan.html', action="Add", film_booking=film_booking, form=form, title="Request Loan")
	
@app.route('/show/loan/<int:id>', methods=['GET', 'POST'])
@login_required
def showloan(id):
	show_booking = True
	form = BookingForm()
	if form.validate_on_submit():
		show_booking = ShowBooking(fromdate=form.fromdate.data, todate=form.todate.data, req_date = datetime.utcnow(), userid = current_user.id, showid = id)
		try:
			db.session.add(show_booking)
			db.session.commit()
			flash('You have successfully requested this loan.')
		
		except:
			flash('Error: Booking Error.')
		return redirect(url_for('shows'))

	return render_template('loan.html', action="Add", show_booking=show_booking, form=form, title="Request Loan")