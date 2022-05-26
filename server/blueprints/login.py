from flask import Blueprint, render_template, redirect
from flask_login import login_user, logout_user, login_required

from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

from handlers import database
from core import User


class SignInForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
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
        user = User.from_record(record)

        if user is not None and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')

        return render_template('login.html',
                               message='There was a problem with your login.',
                               form=form)

    return render_template('login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = SignUpForm()
    if form.validate_on_submit():
        record = database.users.find_one({
            'email': form.email.data
        })
        user = User.from_record(record)

        if user is None:
            user = User(email=form.email.data, password=form.password.data)
            database.users.insert_one(user.to_dict())

            login_user(user)
            return redirect('/')
        else:
            return render_template('register.html',
                                    message='A user with this email already exists!',
                                    form=form)

        return redirect('/login')
    return render_template('register.html', form=form)


@login_required
@bp.route('/logout')
def logout():
    logout_user()
    return redirect('/')
