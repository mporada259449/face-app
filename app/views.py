from flask import Blueprint, render_template, session, redirect, flash, url_for, request, json
from werkzeug.utils import secure_filename
from .logging import log_event
import requests
import os
import uuid
views = Blueprint('views', __name__) 

UPLOAD_FLODER='/mnt/images/'
ALLOWED_EXTENSIONS=['jpg', 'png', 'jpeg', 'webp']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_compare_request(img_path_1, img_path_2):
    url = 'http://model:5000/faceapp/compare'
    files = {'image1': open(img_path_1, 'rb'), 'image2': open(img_path_2, 'rb')}
    log_event(msg=f'Request was sand to model to compare images: {img_path_1}, {img_path_2}', msg_type='app')
    result = requests.post(url, files=files)
    result_text = json.loads(result.content.decode()) 
    return result_text

@views.route('/')
def hello():
    return render_template('main-page.html')

@views.route('/compare_images', methods=['POST'])
def compare_images():
    if not request.files:
        log_event(msg=f'There was an attempt to compere images', msg_type='app')
        flash('No file was provided')
        redirect(request.url)

    subdir = uuid.uuid4().hex
    
    if not os.path.exists(os.path.join(UPLOAD_FLODER, subdir)):
        os.mkdir(os.path.join(UPLOAD_FLODER, subdir))
    saved_files = []
    for key, file in request.files.items():
        if file.filename == '':
            flash('No selected file')
            log_event(msg=f'There was an attempt to compere images', msg_type='app')
            redirect(request.url)
        if file and allowed_file(file.filename):
            _, extension = os.path.splitext(file.filename)
            filename = secure_filename(key) + extension
            img_path = os.path.join(UPLOAD_FLODER, subdir, filename)
            file.save(img_path)
            saved_files.append(img_path)
        else:
            flash("Unsupported filetype")
            return redirect(url_for('views.hello'))
    
    result = send_compare_request(img_path_1=saved_files[0], img_path_2=saved_files[1])

    if "is_similar" in result:
        if result["is_similar"]:
            flash(f"Similarity_score: {result['similarity_score']}. This is the same person")
        else:
            flash(f"Similarity_score: {result['similarity_score']}. This is not the same person")
        
        log_event(
            msg=f"Files {saved_files[0]}, {saved_files[1]} were compared with score {result['similarity_score']}",
            msg_type="app"
        )
        return redirect(url_for("views.hello"))

    elif "error" in result:
        error_message = result.get("error", "Unknown error")
        error_details = result.get("details", "No additional details provided")
        error_status_code = result.get("status_code", "Unknown status code")
        correlation_id = result.get("correlation_id", "No correlation ID")

        flash(
            f"Error occurred! Status Code: {error_status_code}, Error: {error_message}, "
            f"Details: {error_details}, Correlation ID: {correlation_id}"
        )
        log_event(
            msg=(
                f"Error occurred while comparing files: {saved_files[0]}, {saved_files[1]} - "
                f"Status Code: {error_status_code}, Error: {error_message}, Details: {error_details}, "
                f"Correlation ID: {correlation_id}"
            ),
            msg_type="error"
        )
        return redirect(url_for("views.hello"))

    else:
        correlation_id = result.get("correlation_id", "No correlation ID")
        flash("Unexpected response from the comparison service. Correlation ID: {correlation_id}")
        log_event(
            msg=f"Unexpected response for files {saved_files[0]}, {saved_files[1]}. Response: {result}, Correlation ID: {correlation_id}",
            msg_type="error"
        )
        return redirect(url_for("views.hello"))
