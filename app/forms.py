from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, SelectField, FloatField, HiddenField, PasswordField, FileField
from wtforms.fields import EmailField, DateField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional
from flask_wtf.file import FileAllowed
from .models import Users
import re


class Login(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()]) 
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class SignUp(FlaskForm):
    username = StringField('Username*', validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Name', validators=[Optional(), Length(min=2, max=20)]) 
    email = EmailField('Email*', validators=[DataRequired(), Email(message='Invalid Email')])
    image_file = FileField('Profile Picture')  # Optional image file field
    password = PasswordField('Password*', validators=[DataRequired(), Length(min=8, max=24)])
    confirm_password = PasswordField('Confirm Password*', validators=[DataRequired(), EqualTo(fieldname="password", message="Passwords must match")])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError("This email is already in use, please use a different one.")
    def validate_password(self, password):
        return True
        # if not re.fullmatch("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$", password.data):
        #     raise ValidationError("Password needs to contain at least one letter, number, and special character.")
        
        
class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email(message='Invalid Email')])
    password = PasswordField('Password', validators=[Length(min=6, message='Password must be at least 6 characters long')])
    submit = SubmitField('Update Profile')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=20)])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=8)], render_kw={"placeholder": "Leave as is to keep current password"})
    image_file = FileField('Update Profile Picture', validators=[Optional(), FileAllowed(['jpg', 'png'], 'JPG or PNG Image only!')])


Type_of_expense =["Personal", "House", "Transport", "Pets", "Miscellaneous"]


class EditExpense(FlaskForm):
    id = HiddenField('')
    type = SelectField('Type of expense', choices=[(typ, typ) for typ in Type_of_expense])
    description = StringField('Description of the expense.', validators=[DataRequired("Description required")])
    date= DateField('Purchase Date', format='%Y-%m-%d', validators=[DataRequired()])
    amount = FloatField('Amount (S$)', validators=[DataRequired("Invalid amount, input should be a number greater than 0.")])

    def validate_amount (self, amount): 
        if amount.data <= 0: 
            raise ValidationError("Invalid amount, input should be a number greater than 0.")
