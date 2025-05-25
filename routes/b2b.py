import os.path

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from operations.messenger import send_email_studio

from models.b2b import VidEditProject
from extensions import db

b2b = Blueprint('b2b', __name__, static_folder='static', template_folder='templates/b2b')


@b2b.route('/', methods=['GET', 'POST'])
def home():
    session['url'] = url_for('b2b.home')
    try:
        current_user_email = current_user.email
    except Exception as e:
        current_user_email = ''
    if 'logged_in' in session:
        if not session['logged_in']:
            return redirect(url_for('account.login'))
        else:
            if current_user_email == 'bipinkrsingh0501@gmail.com':
                if request.method == 'POST':
                    if request.form.get('submit-video-data'):
                        project_name = request.form.get('project_name')
                        raw_video_files = request.files.getlist('raw_video_files')
                        score_vo_files = request.files.getlist('score_vo_files')
                        for r in raw_video_files:
                            if r.filename == '':
                                flash('No selected file', 'error')
                            else:
                                filename = secure_filename(r.filename)
                                raw_vid_path = f'static/files/vid-edit/{current_user.name.split(" ")[0]}-{current_user.uuid}/{project_name}/raw-vid/'
                                if not os.path.exists(raw_vid_path):
                                    os.makedirs(raw_vid_path)
                                r.save(os.path.join(raw_vid_path, filename))
                        for s in score_vo_files:
                            if s.filename == '':
                                flash('No selected file', 'error')
                            else:
                                filename = secure_filename(s.filename)
                                score_vo_path = f'static/files/vid-edit/{current_user.name.split(" ")[0]}-{current_user.uuid}/{project_name}/score-vo/'
                                if not os.path.exists(score_vo_path):
                                    os.makedirs(score_vo_path)
                                s.save(os.path.join(score_vo_path, filename))

                        entry = VidEditProject(
                            name=project_name,
                            models='N/A',
                            animation='N/A',
                            cut='Pending',
                            edit='Pending',
                            vfx='Pending',
                            color='Pending',
                            audio='Pending'
                        )
                        db.session.add(entry)
                        db.session.commit()
                        body = f'New video edit project submitted, Chief!\n\nSubmitted by: {current_user.name}\n\n'
                        send_email_studio('VIDEO EDIT PROJECT SUBMISSION', ['shwetabhartist@gmail.com', 'writartstudios@gmail.com'],
                                          body, '', '')
                        flash('Successfully Submitted!', 'success')
                    if request.form.get('submit-reference'):
                        start_t_min = ''
                        start_t_sec = ''
                        end_t_min = ''
                        end_t_sec = ''
                        project = request.form.get('project')
                        start_time_min = request.form.get('start-min')
                        start_time_sec = request.form.get('start-sec')
                        end_time_min = request.form.get('end-min')
                        end_time_sec = request.form.get('end-sec')
                        ref_files = request.files.getlist('reference_files')
                        if len(start_time_min) < 2:
                            start_t_min = '0' + start_time_min
                        else:
                            start_t_min = start_time_min
                        if len(start_time_sec) < 2:
                            start_t_sec = '0' + start_time_sec
                        else:
                            start_t_sec = start_time_sec
                        if len(end_time_min) < 2:
                            end_t_min = '0' + end_time_min
                        else:
                            end_t_min = end_time_min
                        if len(end_time_sec) < 2:
                            end_t_sec = '0' + end_time_sec
                        else:
                            end_t_sec = end_time_sec
                        start_t_formatted = f'{start_t_min}_{start_t_sec}'
                        end_t_formatted = f'{end_t_min}_{end_t_sec}'
                        folder_name = f'{start_t_formatted}---{end_t_formatted}'
                        ref_path = f'static/files/vid-edit/{current_user.name.split(" ")[0]}-{current_user.uuid}/{project}/{folder_name}/references/'
                        if not os.path.exists(ref_path):
                            os.makedirs(ref_path)
                        for r in ref_files:
                            if r.filename == '':
                                flash('No selected file', 'error')
                            else:
                                filename = secure_filename(r.filename)
                                r.save(os.path.join(ref_path, filename))
                        body = f'Hey Chief!\n\nReference files added for project: {project}\nby {current_user.name}\n'
                        send_email_studio('REFERENCE FILES ADDED', ['shwetabhartist@gmail.com', 'writartstudios@gmail.com'], body, '','')
                        flash('Successfully Submitted!', 'success')
                project_dict = {}
                projects = db.session.query(VidEditProject).all()
                for p in projects:
                    entry = {
                        'id': p.id,
                        'name': p.name
                    }
                    project_dict[p.id] = entry
                return render_template('b2b_home.html', project_dict=project_dict, logged_in=current_user.is_authenticated)
            else:
                return render_template('user_not_allowed.html')
    else:
        return redirect(url_for('account.login'))
