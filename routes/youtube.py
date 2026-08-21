from flask import Blueprint, render_template, request, redirect, flash, send_file, session, url_for, jsonify
from flask_login import current_user
from extensions import db, current_year,p
from models.youtube import *
from models.member import *
import pprint as pp
import markdown
from werkzeug.utils import secure_filename
import os, json
from operations.miscellaneous import *
from datetime import datetime



youtube = Blueprint('youtube', __name__, static_folder='static', template_folder='templates/youtube')



date_time_now = datetime.now().replace(microsecond=0)

@youtube.route('/', methods=['GET', 'POST'])
def home():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    if 'youtube_logged_in' not in session or session['youtube_logged_in'] != True:
        return redirect(url_for('youtube.login'))
    else:
        global first_channel, first_video
        channels = []
        default_video_dict = {}
        default_vid_uuid_name_list = []
        all_channels = db.session.query(YoutubeChannel).all()
        for c in all_channels:
            uuid = c.uuid
            name = c.channel_name
            channels.append((uuid, name))
        if len(channels) > 0:
            channel_list_with_pending_videos_and_componenets = [a for a in db.session.query(YoutubeChannel).all() if len([b for b in a.videos if (b.status=='pending' or b.status=='in-progress')]) > 0]
            if len(channel_list_with_pending_videos_and_componenets) > 0:
                for c in channel_list_with_pending_videos_and_componenets:
                    videos = c.videos
                    for v in videos:
                        if len(v.components) > 0:
                            first_video = v
                            first_channel = c
                for v in first_channel.videos:
                    if v.status == 'pending' or v.status == 'in-progress':
                        if len(v.components) > 0:
                            default_vid_uuid_name_list.append((v.uuid, v.temp_title))
                try:
                    first_dialogue_narration = [a.text for a in first_video.components if a.component_type == 'dialogue_&_narration'][0]
                except:
                    first_dialogue_narration = ''
                try:
                    first_img_vid_instruction = [a.text for a in first_video.components if a.component_type == 'img_vid_instruction'][0]
                except:
                    first_img_vid_instruction = ''
                try:
                    first_thumbnail_instruction = [a.text for a in first_video.components if a.component_type == 'thumbnail_instruction'][0]
                except:
                    first_thumbnail_instruction = ''
                try:
                    first_youtube_card_instruction = [a.text for a in first_video.components if a.component_type == 'youtube_card_instruction'][0]
                except:
                    first_youtube_card_instruction = ''
                
                default_image_list = [a.file_path for a in first_video.components if a.component_type == 'image']
                default_video_dict['image_list'] = default_image_list
                default_video_dict['vid_uuid_name_list'] = default_vid_uuid_name_list
                default_video_dict['temp_title'] = first_video.temp_title
                try:
                    default_video_dict['dialogue_narration'] = markdown.markdown(first_dialogue_narration).replace('\n', '<br>')
                except:
                    default_video_dict['dialogue_narration'] = first_dialogue_narration
                try:
                    first_voice_recording_list = []
                    first_voice_recordings = [a.file_path for a in first_video.components if a.component_type == 'voice_recording']
                    for f in first_voice_recordings:
                        first_voice_recording_list.append(f)
                except:
                    first_voice_recording = ''
                default_video_dict['voice_recordings'] = first_voice_recording_list
                default_video_dict['video_uuid'] = first_video.uuid
                try:
                    default_video_dict['img_vid_instruction'] = markdown.markdown(first_img_vid_instruction).replace('\n', '<br>')
                except:
                    default_video_dict['img_vid_instruction'] = first_img_vid_instruction
                try:
                    default_video_dict['thumbnail_instruction'] = markdown.markdown(first_thumbnail_instruction).replace('\n', '<br>')
                except:
                    default_video_dict['thumbnail_instruction'] = first_thumbnail_instruction
                try:
                    default_video_dict['youtube_card_instruction'] = markdown.markdown(first_youtube_card_instruction).replace('\n', '<br>')
                except:
                    default_video_dict['youtube_card_instruction'] = first_youtube_card_instruction
            else:
                default_video_dict = {}
        
        if request.method == 'POST' and request.is_json:
            data = request.get_json()
            if data['type'] == 'select_channel':
                channel_uuid = data['channel_uuid']
                video_list = []
                channel_videos = db.session.query(YoutubeChannel).filter_by(uuid=channel_uuid).scalar().videos
                for c in channel_videos:
                    video_list.append((c.uuid, c.temp_title))
                return jsonify(video_list=video_list)
            if data['type'] == 'select_video':
                video_uuid = data['video_uuid']
                video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
                video_temp_title = video.temp_title
                video_components = video.components
                vid_dict = {}
                dialogue_narration = ''
                voice_recordings = []
                image_list = []
                img_vid_instruction = ''
                thumbnail_instruction = ''
                youtube_card_instruction = ''
                for c in video_components:
                    if c.component_type == 'dialogue_&_narration':
                        dialogue_narration = c.text
                    elif c.component_type == 'image':
                        image_list.append(c.file_path)
                    elif c.component_type == 'voice_recording':
                        voice_recordings.append(c.file_path)
                    elif c.component_type == 'img_vid_instruction':
                        img_vid_instruction = c.text
                    elif c.component_type == 'thumbnail_instruction':
                        thumbnail_instruction = c.text
                    elif c.component_type == 'youtube_card_instruction':
                        youtube_card_instruction = c.text
                vid_dict['temp_title'] = video_temp_title
                vid_dict['video_uuid'] = video_uuid
                try:
                    vid_dict['dialogue_narration'] = markdown.markdown(dialogue_narration).replace('\n', '<br>')
                except:
                    vid_dict['dialogue_narration'] = dialogue_narration
                vid_dict['voice_recordings'] = voice_recordings
                vid_dict['image_list'] = image_list
                try:
                    vid_dict['img_vid_instruction'] = markdown.markdown(img_vid_instruction).replace('\n', '<br>')
                except:
                    vid_dict['img_vid_instruction'] = img_vid_instruction
                try:
                    vid_dict['thumbnail_instruction'] = markdown.markdown(thumbnail_instruction).replace('\n', '<br>')
                except:
                    vid_dict['thumbnail_instruction'] = thumbnail_instruction
                try:
                    vid_dict['youtube_card_instruction'] = markdown.markdown(youtube_card_instruction).replace('\n', '<br>')
                except:
                    vid_dict['youtube_card_instruction'] = youtube_card_instruction
                return jsonify(vid_dict)

        return render_template('youtube.html', current_year=current_year, channels=channels, default_video_dict=default_video_dict, logged_in=current_user.is_authenticated, admin=admin, first_channel=first_channel)


@youtube.route('/upload-images', methods=['GET', 'POST'])
def upload_images():
    if request.method == 'POST' and request.form.get('type') == 'upload_images':
        files = request.files.getlist('files')
        video_uuid = request.form.get('video_uuid')
        video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
        channel_id = video.youtube_channel.id
        video_id = video.id
        base_path = f"./static/files/youtube/{channel_id}/{video_id}/images/"
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        for f in files:
            if f.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)
            filename_base = secure_filename(f.filename)
            save_path = base_path + filename_base
            f.save(save_path)
            existing_uuid_list = [a.uuid for a in db.session.query(YoutubeVideoComponent) if a.component_type == 'image']
            uuid = create_uuid(existing_uuid_list, 9)
            entry = YoutubeVideoComponent(
                uuid=uuid,
                main=True,
                version_list=json.dumps([]),
                version='1.0',
                component_type='image',
                file_path=save_path[1:],
                approval_status='pending',
                date_time=date_time_now,
                youtube_video_id=video_id
            )
            db.session.add(entry)
        db.session.commit()

        return jsonify('success')


@youtube.route('/image-feedback', methods=['GET', 'POST'])
def image_feedback():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    if current_user.is_authenticated and admin in current_user.role:
        is_admin = True
    else:
        is_admin = False
    if not session.get('youtube_logged_in') or session['youtube_logged_in'] != True:
        return redirect(url_for('youtube.login'))
    else:
        video_uuid = request.args.get('video_uuid')
        image_dict = {}
        video_component_list = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar().components
        for c in video_component_list:
            if c.component_type == 'image':
                approval_status = c.approval_status
                if approval_status == 'approved':
                    approval_status_tuple = (c.approval_status, '#2dad31')
                elif approval_status == 'pending':
                    approval_status_tuple = (c.approval_status, "#a87e2a")
                elif approval_status == 'rejected':
                    approval_status_tuple = (c.approval_status, "#606060")
                image_dict[c.uuid] = {
                    'uuid': c.uuid,
                    'file_path': c.file_path,
                    'feedback': c.feedback,
                    'approval_status': approval_status_tuple
                }
        temp_title = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).one_or_none().temp_title
        return render_template('image_feedback.html', logged_in=current_user.is_authenticated, admin=admin, image_dict=image_dict, temp_title=temp_title, is_admin=is_admin)


@youtube.route('/save_audio', methods=['POST'])
def save_audio():
    if not session.get('youtube_logged_in') or session['youtube_logged_in'] != True:
        return redirect(url_for('youtube.login'))
    else:
        if request.method == 'POST' and request.form.get('type') == 'save_audio':
            image_uuid = request.form.get('image_uuid')
            audio = request.files['audio']
            image = db.session.query(YoutubeVideoComponent).filter_by(uuid=image_uuid).scalar()
            video = image.youtube_video
            video_id = video.id
            channel = video.youtube_channel
            channel_id = channel.id

            if audio.filename == '':
                flash('No selected file', 'error')
                return redirect(request.url)
            filename = f"{image_uuid}_feedback.webm"
            save_base_path = f"./static/files/youtube/{channel_id}/{video_id}/image_feedback/"
            if not os.path.exists(save_base_path):
                os.makedirs(save_base_path)
            save_path = save_base_path + filename
            audio.save(save_path)
            image.feedback = save_path[1:]
            db.session.commit()
            return jsonify(success='success')


@youtube.route('/login', methods=['GET', 'POST'])
def login():
    username_list = ['abhijeet', 'shwetabh', 'yash']
    default_password = '@iig974#lon99!'
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in username_list and password == default_password:
            session['youtube_logged_in'] = True
            return redirect(url_for('youtube.home'))
        else:
            flash("Please enter the correct username and password", category="error")
    return render_template('youtube_login.html', logged_in=current_user.is_authenticated)


@youtube.route('/logout', methods=['GET', 'POST'])
def logout():
    session['youtube_logged_in'] = False
    return redirect(url_for('youtube.login'))
    