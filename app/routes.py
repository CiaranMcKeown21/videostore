from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, EditAddressForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Address
from werkzeug.urls import url_parse
from datetime import datetime

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
		form.first_name.data = current_user.first_name
		form.last_name.data = current_user.last_name
		form.about_me.data = current_user.about_me
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

@app.route('/games')
@login_required
def games():
	return 'hi'

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    # prevent non-admins from accessing the page
	if not current_user.is_admin:
		return render_template('error403.html', title="Error 403")
	return render_template('admin_dashboard.html', title="Dashboard")

