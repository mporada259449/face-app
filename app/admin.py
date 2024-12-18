from flask import Blueprint, render_template, session, redirect, flash, url_for, request
adminview = Blueprint('admin', __name__) 

@adminview.route('/admin', methods=['GET'])
def admin_page():
    if session.get('is_admin'):
        return render_template('admin.html')
    else:
        flash("You don't have admin permissions")
        return redirect(url_for('views.hello'))
    
@adminview.route('/set_threshold', methods=['POST'])
def set_treshold():
    if not session.get('is_admin'):
        flash("You don't have permissions to do that")
        redirect(url_for('viwes.hello'))
    
    data = request.form
    threshold = data.get('threshold')
    print(f"Threshold will be set to {threshold}")

    #tutaj trzeba to wysłać do modelu

@adminview.route('/logs', methods=['GET'])
def see_logs():
    pass