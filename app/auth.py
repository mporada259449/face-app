from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from .models import User
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
        flash("Login successful")
        return redirect(url_for('views.hello'))
    else:
        flash('Invalid password or login')
        return redirect(url_for('views.hello'))

@auth.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id')
    session.pop('is_admin')
    flash("You have been logged out")
    return redirect(url_for('views.hello'))