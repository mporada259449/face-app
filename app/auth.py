from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from .models import User
from .logging import log_event, get_event
auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return render_template('main-page.html')

    user = User.query.filter_by(username=username).first()

    if user and user.password == password:
        session['user_id'] = user.id 
        session['is_admin'] = user.is_admin
        session['username'] = username
        flash("Login successful")
        log_event(msg=f'Authorization of user {username}', msg_type='auth')
        return redirect(url_for('views.hello'))
    else:
        flash('Invalid password or login')
        log_event(msg=f'Failed authentication for {username}', msg_type='auth')
        return redirect(url_for('views.hello'))

@auth.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id')
    session.pop('is_admin')
    username = session.pop('username')
    flash("You have been logged out")
    log_event(msg=f'User {username} logged out', msg_type='auth')
    return redirect(url_for('views.hello'))