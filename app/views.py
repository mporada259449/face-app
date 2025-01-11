from flask import Blueprint, render_template, session, redirect, flash, url_for, request
from werkzeug.utils import secure_filename
from .logging import log_event
import requests
import os
import uuid
views = Blueprint('views', __name__) 

UPLOAD_FLODER='/home/dev/face-app/mnt/images/'
ALLOWED_EXTENSIONS=['.jpg', 'png', 'jpeg',]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/')
def hello():
    return render_template('main-page.html')

@views.route('/compare_images', methods=['POST'])
def compare_images():
    if not request.files:
        flash('No file was provided')
        redirect(request.url)

    if session.get('subdir', False):
        subdir = session['subdir']
    else:
        subdir = uuid.uuid4().hex
        session['subdir'] = subdir
    
    if not os.path.exists(os.path.join(UPLOAD_FLODER, subdir)):
        os.mkdir(os.path.join(UPLOAD_FLODER, subdir))

    for key, file in request.files.items():
        print(key, file.filename)
        if file.filename == '':
            flash('No selected file')
            redirect(request.url)
        if file and allowed_file(file.filename):
            _, extension = os.path.splitext(file.filename)
            filename = secure_filename(key) + extension
            file.save(os.path.join(UPLOAD_FLODER, subdir, filename))
    
    flash("Files are proccesed by our model")
    return redirect(url_for('views.hello'))