from flask import Blueprint, render_template, session, redirect, flash, url_for, request
views = Blueprint('views', __name__) 

@views.route('/')
def hello():
    return render_template('main-page.html')

@views.route('/compare_images', methods=['POST'])
def compare_images():
    print(len(request.files))
    return render_template('main-page.html')