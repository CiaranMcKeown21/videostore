from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, TextAreaField
from wtforms.fields.core import SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app.models import User, Address

class EmptyForm(FlaskForm):
	submit = SubmitField('Submit')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email',validators=[DataRequired(),Email()])
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')
	def validate_email(self, email):
		email = User.query.filter_by(email=email.data).first()
		if email is not None:
			raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	about_me = TextAreaField('About Me', validators=[Length(min=0,max=140)])
	submit = SubmitField('Submit')

class EditAddressForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	city = StringField('city', validators=[DataRequired()])
	address = StringField('Address', validators=[DataRequired()])
	postal_Code = StringField('Post Code', validators=[DataRequired()])
	country = StringField('Country', validators=[DataRequired()])
	submit = SubmitField('Submit')

	

class PostForm(FlaskForm):
	post = TextAreaField('Say something', validators= [
		DataRequired(), Length(min=1, max=140)])
	submit = SubmitField('Submit')

class AdminVideoForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	description = StringField('Description', validators=[DataRequired()])
	release_year = IntegerField('Release Year', validators=[DataRequired()])
	rating = IntegerField('Rating', validators=[DataRequired()])
	loan_status = SelectField('Loan Status', choices=[('Available', 'Available'), ('Out on Loan', 'Out on Loan')])
	submit = SubmitField('Submit')

class AdminFilmForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	description = StringField('Description', validators=[DataRequired()])
	release_year = IntegerField('Release Year', validators=[DataRequired()])
	rating = IntegerField('Rating', validators=[DataRequired()])
	loan_status = SelectField('Loan Status', choices=[('Available', 'Available'), ('Out on Loan', 'Out on Loan')])
	submit = SubmitField('Submit')


class AdminShowForm(FlaskForm):
	name = StringField('Name', validators=[DataRequired()])
	description = StringField('Description', validators=[DataRequired()])
	release_year = IntegerField('Release Year', validators=[DataRequired()])
	rating = IntegerField('Rating', validators=[DataRequired()])
	loan_status = SelectField('Loan Status', choices=[('Available', 'Available'), ('Out on Loan', 'Out on Loan')])
	submit = SubmitField('Submit')


class AdminUserForm(FlaskForm):
	username = StringField('Name', validators=[DataRequired()])
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	email = StringField('E-Mail', validators=[DataRequired()])
	submit = SubmitField('Submit')