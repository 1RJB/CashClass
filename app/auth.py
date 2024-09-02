from flask import Blueprint, flash, render_template, request, url_for, redirect
from . import db
from .models import Users
from .forms import SignUp, Login
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)


# TODO: insert root url ('/') codes here

@auth.route('/')
def home():
    if current_user.is_active:
        return render_template("home.html", name_user=current_user.name)
    return render_template("home.html")

@auth.route('/signup', methods=['GET','POST'])
def signup():
    # insert code here
    if current_user.is_active:
        return redirect(url_for("views.show_expenses"))

    form = SignUp(request.form)
    if form.validate_on_submit():
        name = form.name.data.strip() if form.name.data.strip() else ''
        new_user = Users(name=name, email=form.email.data.lower(), password=generate_password_hash(form.password.data))
        db.session.add(new_user)
        db.session.commit()

        flash('Account created!', category='success')
        return redirect(url_for('auth.login'))

    return render_template("signup.html", form=form)


@auth.route('/login', methods=['GET','POST'])
def login():
    # insert code here
    if current_user.is_active:
        return redirect(url_for("views.show_expenses"))

    form = Login(request.form)
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data.lower()).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.show_expenses'))
        
            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('No account with that email address.', category='error')

    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))
