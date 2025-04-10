from flask import Blueprint, render_template, session, redirect, flash, url_for, request
import requests
from .logging import get_event, log_event
adminview = Blueprint('admin', __name__) 

@adminview.route('/admin', methods=['GET'])
def admin_page():
    if session.get('is_admin'):
        return render_template('admin.html')
    else:
        flash("You don't have admin permissions")
        return redirect(url_for('views.hello'))
    
@adminview.route('/set_threshold', methods=['POST'])
def set_threshold():
    if not session.get('is_admin'):
        flash("You don't have permissions to do that")
        return redirect(url_for('views.hello'))
    
    data = request.form
    threshold = data.get('threshold')
    threshold = int(threshold)/100
    
    url = 'http://model:5000/set_threshold'
    json_data = {'threshold': threshold}

    result = requests.post(url, json=json_data, headers={"Content-Type": "application/json"})

    if result.status_code == 200:
        log_event(msg=f'Admin changed the value of threshold to {threshold}', msg_type='admin')
        flash("Success")
        return redirect(url_for('admin.admin_page'))
    else:
        log_event(msg=f'Attempt to set the threshold to {threshold} failed', msg_type='admin')
        flash("Setting threshold failed")
        return redirect(url_for('admin.admin_page'))

@adminview.route('/logs', methods=['POST'])
def see_logs():
    data = request.form
    msg_type = data.get('msg_type')
    events = get_event(msg_type)

    return render_template('admin.html', events=events)
    
    