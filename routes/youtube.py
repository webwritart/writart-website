from flask import Blueprint, render_template, request, redirect, flash, send_file, session, url_for, jsonify
from flask_login import current_user
from extensions import db, current_year,p
from models.youtube import *
from models.member import *
import pprint as pp
import markdown


youtube = Blueprint('youtube', __name__, static_folder='static', template_folder='templates/youtube')


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
                    first_voice_recording = [a.file_path for a in first_video.components if a.component_type == 'voice_recording'][0]
                    first_img_vid_instruction = [a.text for a in first_video.components if a.component_type == 'img_vid_instruction'][0]
                    first_thumbnail_instruction = [a.text for a in first_video.components if a.component_type == 'thumbnail_instruction'][0]
                    first_youtube_card_instruction = [a.text for a in first_video.components if a.component_type == 'youtube_card_instruction'][0]
                except Exception as e:
                    p(e)
                    first_dialogue_narration = ''
                    first_voice_recording = ''
                    first_img_vid_instruction = ''
                    first_thumbnail_instruction = ''
                    first_youtube_card_instruction = ''
                    
                default_video_dict['vid_uuid_name_list'] = default_vid_uuid_name_list
                default_video_dict['temp_title'] = first_video.temp_title
                try:
                    default_video_dict['dialogue_narration'] = markdown.markdown(first_dialogue_narration).replace('\n', '<br>')
                except:
                    default_video_dict['dialogue_narration'] = first_dialogue_narration
                default_video_dict['voice_recording'] = first_voice_recording
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
                voice_recording = ''
                img_vid_instruction = ''
                thumbnail_instruction = ''
                youtube_card_instruction = ''
                for c in video_components:
                    if c.component_type == 'dialogue_&_narration':
                        dialogue_narration = c.text
                    elif c.component_type == 'voice_recording':
                        voice_recording = c.file_path
                    elif c.component_type == 'img_vid_instruction':
                        img_vid_instruction = c.text
                    elif c.component_type == 'thumbnail_instruction':
                        thumbnail_instruction = c.text
                    elif c.component_type == 'youtube_card_instruction':
                        youtube_card_instruction = c.text
                vid_dict['temp_title'] = video_temp_title
                vid_dict['dialogue_narration'] = markdown.markdown(dialogue_narration).replace('\n', '<br>')
                vid_dict['voice_recording'] = voice_recording
                vid_dict['img_vid_instruction'] = markdown.markdown(img_vid_instruction).replace('\n', '<br>')
                vid_dict['thumbnail_instruction'] = markdown.markdown(thumbnail_instruction).replace('\n', '<br>')
                vid_dict['youtube_card_instruction'] = markdown.markdown(youtube_card_instruction).replace('\n', '<br>')
                return jsonify(vid_dict)
        return render_template('youtube.html', current_year=current_year, channels=channels, default_video_dict=default_video_dict, logged_in=current_user.is_authenticated, admin=admin, first_channel=first_channel.channel_name, first_video=first_video.temp_title)


@youtube.route('/login', methods=['GET', 'POST'])
def login():
    username_list = ['abhijeet', 'shwetabh']
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