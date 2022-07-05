from flask import Blueprint, render_template, redirect
from flask_login import login_user, logout_user, login_required

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

import bcrypt
import bson

from handlers import database
from core import User


class SignInForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')  # REMEMBER_COOKIE_DURATION param
    submit = SubmitField('Sign in')


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign up')


bp = Blueprint(
    'login',
    __name__
)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = SignInForm()
    if form.validate_on_submit():
        record = database.users.find_one({
            'email': form.email.data
        })

        if record is not None:
            user = User.from_record(record)
            if user.check_password(form.password.data.encode('utf-8')):
                login_user(user, remember=form.remember_me.data)
                return redirect('/')

        return render_template('auth/login.html',
                               message='There was a problem with your login.',
                               form=form)

    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        record = database.users.find_one({
            'email': form.email.data
        })

        if record is None:
            salt = bcrypt.gensalt()
            hashed_pwd = bcrypt.hashpw(
                form.password.data.encode('utf-8'), salt)
            user = User(
                email=form.email.data,
                password=bson.Binary(hashed_pwd),
                salt=bson.Binary(salt)
            )

            database.users.insert_one(user.to_dict())

            login_user(user)
            return redirect('/')
        else:
            return render_template('auth/register.html',
                                   message='A user with this email already exists!',
                                   form=form)

    return render_template('auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
