from flask import Blueprint, render_template, redirect, flash, url_for, request, json
from werkzeug.utils import secure_filename
from .logging import log_event
import requests
import os
import uuid
views = Blueprint('views', __name__) 

UPLOAD_FLODER='/mnt/images/'
ALLOWED_EXTENSIONS=['jpg', 'png', 'jpeg', 'webp', 'webm', 'mp4', 'avi']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_compare_request(url, files_input, is_video):
    if is_video:
        files = {'image': open(files_input['image2'], 'rb'), 'video': open(files_input['video1'], 'rb')}
        log_event(msg=f"Request was sand to model to compare inputs: {files_input['image2']}, {files_input['video1']}", msg_type='app')
    else:
        files = {'image1': open(files_input['image1'], 'rb'), 'image2': open(files_input['image2'], 'rb')}
        log_event(msg=f"Request was sand to model to compare images: {files_input['image1']}, {files_input['image2']}", msg_type='app')
    result = requests.post(url, files=files)
    result_text = json.loads(result.content.decode()) 
    return result_text


@views.route('/')
def hello():
    return render_template('main-page.html')

@views.route('/compare_media', methods=['POST'])
def compare_images():
    is_video = False
    if not request.files:
        log_event(msg=f'There was an attempt to compere images', msg_type='app')
        flash('No file was provided')
        redirect(request.url)

    subdir = uuid.uuid4().hex
    
    if not os.path.exists(os.path.join(UPLOAD_FLODER, subdir)):
        os.mkdir(os.path.join(UPLOAD_FLODER, subdir))

    saved_files = dict()
    for key, file in request.files.items():
        if file.filename == '' and key == 'image1':
            is_video = True
            continue
        elif file.filename == '':
            continue

        if file and allowed_file(file.filename):
            _, extension = os.path.splitext(file.filename)
            filename = secure_filename(key) + extension
            input_path = os.path.join(UPLOAD_FLODER, subdir, filename)
            file.save(input_path)
            saved_files[key]=input_path
        else:
            flash("Unsupported filetype")
            return redirect(url_for('views.hello'))
    if is_video:
        result = send_compare_request(
            url = 'http://model:5000/faceapp/compare_video',
            files_input=saved_files,
            is_video=is_video)
    else:
        result = send_compare_request(
            url = 'http://model:5000/faceapp/compare',
            files_input=saved_files,
            is_video=is_video)

    if "is_similar" in result:
        if result["is_similar"]:
            flash(f"Similarity_score: {result['similarity_score']}. This is the same person")
        else:
            flash(f"Similarity_score: {result['similarity_score']}. This is not the same person")
        
        log_event(
            msg=f"Files {list(saved_files.values())} were compared with score {result['similarity_score']}",
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
                f"Error occurred while comparing files: {list(saved_files.values())} - "
                f"Status Code: {error_status_code}, Error: {error_message}, Details: {error_details}, "
                f"Correlation ID: {correlation_id}"
            ),
            msg_type="app"
        )
        return redirect(url_for("views.hello"))

    else:
        correlation_id = result.get("correlation_id", "No correlation ID")
        flash("Unexpected response from the comparison service. Correlation ID: {correlation_id}")
        log_event(
            msg=f"Unexpected response for files {list(saved_files.values())}. Response: {result}, Correlation ID: {correlation_id}",
            msg_type="app"
        )
        return redirect(url_for("views.hello"))
