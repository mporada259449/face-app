from flask import Blueprint, render_template, session, redirect, flash, url_for
views = Blueprint('views', __name__) 

@views.route('/')
def hello():
    return render_template('main-page.html')

@views.route('/save_files')
def compare_images():
    pass
