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
from operations.messenger import *
from datetime import datetime
from collections import defaultdict



youtube = Blueprint('youtube', __name__, static_folder='static', template_folder='templates/youtube')



date_time_now = datetime.now().replace(microsecond=0)

@youtube.route('/', methods=['GET', 'POST'])
def home():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    if not current_user.is_authenticated:
        return redirect(url_for('account.login'))
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
        # ---------------------------------------------- SELECT CURRENT VIDEO ------------------------------------------------------
        channel = db.session.query(YoutubeChannel).all()[0]
        current_video_option_list = [(v.uuid, v.temp_title) for v in channel.videos]

        # ----------------------------------------------------------------------------------------------------------------------------
        current_video_exists = False
        if len(channels) > 0:
            channel_list_with_pending_videos_and_componenets = [a for a in db.session.query(YoutubeChannel).all() if len([b for b in a.videos if (b.status=='pending' or b.status=='in-progress')]) > 0]

            try:
                current_video_uuid = [a.value for a in current_user.tools if a.key == 'current_video_uuid'][0]
                if current_video_uuid:
                    current_video_exists = True
            except Exception as e:
                p(e)
            if current_video_exists:
                current_video = db.session.query(YoutubeVideo).filter_by(uuid=current_video_uuid).scalar()

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

                default_video_dict['vid_uuid_name_list'] = default_vid_uuid_name_list
                if current_video_exists:
                    default_video_dict['image_list'] = [a.file_path for a in current_video.components if a.component_type == 'image']
                    default_video_dict['video_list'] = [a.file_path for a in current_video.components if a.component_type == 'video']
                else:
                    default_video_dict['image_list'] = [a.file_path for a in first_video.components if a.component_type == 'image']
                    default_video_dict['video_list'] = [a.file_path for a in first_video.components if a.component_type == 'video'] 
                if current_video_exists:
                    default_video_dict['temp_title'] = current_video.temp_title
                    try:
                        default_video_dict['dialogue_narration'] = markdown.markdown([a.text for a in current_video.components if a.component_type == 'dialogue_&_narration'][0]).replace('\n', '<br>')
                    except:
                        default_video_dict['dialogue_narration'] = ''
                    try:
                        default_video_dict['dialogue_narration'] = markdown.markdown([a.text for a in current_video.components if a.component_type == 'dialogue_&_narration'][0]).replace('\n', '<br>')
                    except:
                        default_video_dict['dialogue_narration'] = ''
                    default_video_dict['voice_recordings'] = [a.file_path for a in current_video.components if a.component_type == 'voice_recording']
                    default_video_dict['storyboard'] = [a.file_path for a in current_video.components if a.component_type == 'storyboard']
                    try:
                        default_video_dict['img_vid_instruction'] = markdown.markdown([a.text for a in current_video.components if a.component_type == 'img_vid_instruction'][0]).replace('\n', '<br>')
                    except:
                        default_video_dict['img_vid_instruction'] = ''
                    try:
                        default_video_dict['thumbnail_instruction'] = markdown.markdown([a.text for a in current_video.components if a.component_type == 'thumbnail_instruction'][0]).replace('\n', '<br>')
                    except:
                        default_video_dict['thumbnail_instruction'] = ''
                    try:
                        default_video_dict['youtube_card_instruction'] = markdown.markdown([a.text for a in current_video.components if a.component_type == 'youtube_card_instruction'][0]).replace('\n', '<br>')
                    except:
                        default_video_dict['youtube_card_instruction'] = ''
                    default_video_dict['video_uuid'] = current_video.uuid
                else:
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
                        first_voice_recordings = ''
                    default_video_dict['voice_recordings'] = first_voice_recording_list
                    default_video_dict['storyboard'] = [a.file_path for a in first_video.components if a.component_type == 'storyboard']
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
                video_list = []
                storyboard = []
                img_vid_instruction = ''
                thumbnail_instruction = ''
                youtube_card_instruction = ''
                for c in video_components:
                    if c.component_type == 'dialogue_&_narration':
                        dialogue_narration = c.text
                    elif c.component_type == 'image':
                        image_list.append(c.file_path)
                    elif c.component_type == 'video':
                        video_list.append(c.file_path)
                    elif c.component_type == 'voice_recording':
                        voice_recordings.append(c.file_path)
                    elif c.component_type == 'storyboard':
                        storyboard = c.file_path
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
                vid_dict['storyboard'] = storyboard
                vid_dict['image_list'] = image_list
                vid_dict['video_list'] = video_list
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
            
            if data['type'] == 'select_current_video':
                video_uuid = data['video_uuid']
                stored_current_video_count = len([a for a in current_user.tools if a.key == 'current_video_uuid'])
                if stored_current_video_count > 0:
                    existing_current_video_uuid = [a.value for a in current_user.tools if a.key == 'current_video_uuid'][0]
                    p(existing_current_video_uuid)
                    for c in current_user.tools:
                        if c.key == 'current_video_uuid':
                            c.value = video_uuid
                            db.session.commit()
                else:
                    entry = MemberTools(key='current_video_uuid', value=video_uuid, member_id=current_user.id)
                    db.session.add(entry)
                    db.session.commit()
                return jsonify(success='success')

        return render_template('youtube.html', current_year=current_year, channels=channels, default_video_dict=default_video_dict, logged_in=current_user.is_authenticated, admin=admin, first_channel=first_channel,
                               current_video_option_list=current_video_option_list)


@youtube.route('/upload-images', methods=['GET', 'POST'])
def upload_images():
    if request.method == 'POST' and request.form.get('type') == 'upload_images':
        files = request.files.getlist('files')
        video_uuid = request.form.get('video_uuid')
        image_text = request.form.get('image_text')
        video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
        video_temp_title = video.temp_title
        channel_id = video.youtube_channel.id
        channel_name = db.session.query(YoutubeChannel).filter_by(id=channel_id).scalar().channel_name
        video_id = video.id
        member_name = current_user.name
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
                component_type='image',
                file_path=save_path[1:],
                approval_status='pending',
                date_time=date_time_now,
                youtube_video_id=video_id,
                text=image_text,
                member_id=current_user.id
            )
            db.session.add(entry)
            db.session.commit()

            # send email to Leader -----------------------------------------------------
            subject = f"Image uploaded - {date_time_now}"
            body = f"New image uploaded\n\nVideo: {video_temp_title}\nMember: {member_name}\nChannel: {channel_name}"
            send_email_studio(subject, ['shwetabhartist@gmail.com'], body, '', {})
        return jsonify('success')


@youtube.route('/upload-video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST' and request.form.get('type') == 'upload_video':
        video_file = request.files.get('files')
        video_uuid = request.form.get('video_uuid')
        scene = request.form.get('scene')
        shot = request.form.get('shot').upper()
        video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
        video_temp_title = video.temp_title
        video_id = video.id
        channel_id = video.channel_id
        channel_name = db.session.query(YoutubeChannel).filter_by(id=channel_id).scalar().channel_name

        base_path = f"./static/files/youtube/{channel_id}/{video_id}/videos/"
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        filename_base = secure_filename(video_file.filename)
        save_path = base_path + filename_base
        video_file.save(save_path)
        existing_uuid_list = [a.uuid for a in db.session.query(YoutubeVideo)]
        uuid = create_uuid(existing_uuid_list, 9)
        entry = YoutubeVideoComponent(
            uuid=uuid,
            component_type='video',
            file_path=save_path[1:],
            approval_status='pending',
            date_time=date_time_now,
            youtube_video_id=video_id,
            member_id=current_user.id,
            scene=scene,
            shot=shot
        )
        db.session.add(entry)
        db.session.commit()

        # send email to Leader -----------------------------------------------------
        subject = f"New video uploaded - {date_time_now}"
        body = f"New video uploaded\n\nVideo: {video_temp_title}\nScene-shot: {scene}-{shot}\nMember: {current_user.name}\nChannel: {channel_name}"
        send_email_studio(subject, ['shwetabhartist@gmail.com'], body, '', {})
        return jsonify('success')

@youtube.route('/image-feedback', methods=['GET', 'POST'])
def image_feedback():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    youtube_img_creator = db.session.query(Role).filter_by(name='youtube_img_creator').one_or_none()
    youtube_admin = db.session.query(Role).filter_by(name='youtube_admin').one_or_none()
    if not current_user.is_authenticated:
        return redirect(url_for('account.login'))
    else:
        if youtube_img_creator in current_user.role or youtube_admin in current_user.role:
            video_uuid = request.args.get('video_uuid')
            p(video_uuid)
            image_dict = {}
            video_dict = {}
            video_component_list = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar().components

            groups = defaultdict(list)
            for row in video_component_list:
                groups[row.component_type].append(row)

            groups = dict(groups)
            if 'image' in groups.keys():
                for c in groups['image']:
                    file_path = None
                    file_text = None
                    feedback = None
                    revision_uuid = None
                    image_version_list = [float(a.version) for a in c.revisions if len(c.revisions) > 0]
                    if len(image_version_list) == 0:
                        file_path = c.file_path
                        file_text = c.text
                        feedback = c.feedback
                        revision_uuid = c.uuid
                    else:
                        last_version = max(image_version_list)
                        file_path = [a.file_path for a in c.revisions if a.version == str(last_version)][0]
                        file_text = [a.text for a in c.revisions if a.version == str(last_version)][0]
                        feedback = [a.feedback for a in c.revisions if a.version == str(last_version)][0]
                        revision_uuid = [a.uuid for a in c.revisions if a.version == str(last_version)][0]

                    approval_status_tuple = None
                    approval_status = c.approval_status
                    if approval_status == 'approved':
                        approval_status_tuple = (c.approval_status, '#2dad31')
                    elif approval_status == 'pending':
                        approval_status_tuple = (c.approval_status, "#a87e2a")
                    elif approval_status == 'rejected':
                        approval_status_tuple = (c.approval_status, "#606060")
                    elif approval_status == 'revision-required':
                        approval_status_tuple = (c.approval_status, "#DA1C1C")
                    try:
                        assigned_to_name = db.session.query(Member).filter_by(uuid=c.assigned_to_uuid).one_or_none().name
                    except:
                        assigned_to_name = ''
                    try:
                        assigned_to_uuid = int(c.assigned_to_uuid)
                    except:
                        assigned_to_uuid = None
                    try: 
                        last_assigned_name = db.session.query(Member).filter_by(uuid=c.last_assigned).one_or_none().name
                    except:
                        last_assigned_name = ''
                    image_dict[c.uuid] = {
                        'uuid': c.uuid,
                        'revision_uuid': revision_uuid,
                        'file_path': file_path,
                        'feedback': feedback,
                        'approval_status': approval_status_tuple,
                        'assigned_to_uuid': assigned_to_uuid,
                        'assigned_to_name': assigned_to_name,
                        'last_assigned_name': last_assigned_name,
                        'text': file_text
                    }
            if 'video' in groups.keys():
                video_dict = defaultdict(lambda: defaultdict(dict))
                for row in groups['video']:
                    video_dict[row.scene][row.shot][row.uuid] = {'file_path': row.file_path, 'text': row.text, 'feedback': row.feedback,
                                                                 'approval_status': (row.approval_status, {
                                                                     'approved': '#2dad31',
                                                                     'pending': "#a87e2a",
                                                                     'rejected': "#606060",
                                                                     'revision-required': "#DA1C1C"
                                                                 }.get(row.approval_status, "gray")), 
                                                                 'assigned_to_name': db.session.query(Member).filter_by(uuid=row.assigned_to_uuid).scalar().name if row.assigned_to_uuid else '', 'last_assigned': db.session.query(Member).filter_by(uuid=row.last_assigned).scalar().name if row.last_assigned else '',
                                                                 'assigned_to_uuid': int(row.assigned_to_uuid) if row.assigned_to_uuid else row.assigned_to_uuid,
                                                             'last_revision': [(a.uuid, a.version, a.file_path, a.text, a.feedback) for a in row.revisions if len(row.revisions) > 0 and a.version == str(max([float(b.version) for b in row.revisions]))],
                                                             'all_revisions': [(a.uuid, a.version, a.file_path, a.text, a.feedback) for a in row.revisions if len(row.revisions) > 0],
                                                             'revisions': len([float(a.version) for a in row.revisions if len(row.revisions) > 0])}
                video_dict = dict(video_dict)
                pp.pprint(video_dict)
                
            all_mates = [(a.uuid, a.name) for a in db.session.query(Member).all() if len([b for b in a.role if b.name == 'youtube_img_creator']) > 0]
            temp_title = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).one_or_none().temp_title
        else:
            return render_template('admin_area.html')
        return render_template('image_feedback.html', logged_in=current_user.is_authenticated, admin=admin, image_dict=image_dict, video_dict=video_dict, temp_title=temp_title, youtube_admin=youtube_admin, youtube_img_creator=youtube_img_creator, mates=all_mates)

@youtube.route('/save-revision-img', methods=['POST'])
def save_revision_img():
    if request.method == 'POST' and request.form.get('type') == 'upload_revision_img':
        revised_image = request.files.getlist('revised_images[]')[0]
        revision_image_text = request.form.get('revision_image_text')
        parent_img_uuid = request.form.get('parent_img_uuid')
        parent_image = db.session.query(YoutubeVideoComponent).filter_by(uuid=parent_img_uuid).scalar()
        video_temp_title = parent_image.youtube_video.temp_title
        channel_name = parent_image.youtube_video.youtube_channel.channel_name
        member_name = current_user.name

        base_path = f"./static/files/youtube/{parent_image.youtube_video.youtube_channel.id}/{parent_image.youtube_video.id}/image_revisions/"
        if not os.path.exists(base_path):
            os.makedirs(base_path)

        existing_uuid_list = [a.uuid for a in db.session.query(YoutubeVideoComponentRevision)]
        uuid = create_uuid(existing_uuid_list, 9)
        file_name = revised_image.filename
        save_path = base_path + file_name
        revised_image.save(save_path)

        version_list = [a.version for a in parent_image.revisions]
        if len(version_list) == 0:
            version = str(1.0+.1)
        else:
            version_list_int = [float(i) for i in version_list]
            version = f"{(max(version_list_int)+.1):.1f}"

        entry = YoutubeVideoComponentRevision(
            uuid=uuid,
            version=version,
            file_path=save_path[1:],
            text=revision_image_text,
            date_time=date_time_now,
            youtube_video_component_id=parent_image.id,
            member_id = current_user.id
        )
        db.session.add(entry)
        parent_image.approval_status = 'pending'
        temp_assigned_uuid = parent_image.assigned_to_uuid
        parent_image.assigned_to_uuid = None
        parent_image.last_assigned = temp_assigned_uuid
        db.session.commit()

        # send email to the Project lead ------------------------------------------------
        subject = f"Revised image uploaded - {date_time_now}"
        body = f"New revised image uploaded\n\nMember: {member_name}\nVideo: {video_temp_title}\nChannel: {channel_name}"
        send_email_studio(subject, ['shwetabhartist@gmail.com'], body, '', {})
        return jsonify(success='success')


@youtube.route('/save-revision-video', methods=['POST'])
def save_revision_video():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        if data['type'] == 'get_video_and_revisions_details':
            video_uuid = data['video_uuid']
            video = db.session.query(YoutubeVideoComponent).filter_by(uuid=video_uuid).scalar()
            scene_shot = f"{video.scene}-{video.shot}"
            if len(video.revisions) > 0:
                last_version = [{'file_path': a.file_path, 'version': a.version} for a in video.revisions if a.version == str(max([float(b.version) for b in video.revisions]))][0]
            else:
                last_version = {"file_path": video.file_path, "version": "1.0"}
            return jsonify(scene_shot=scene_shot, last_version=last_version)
    if request.method == 'POST' and request.form.get('type') == 'upload_revision_video':
        parent_video_uuid = request.form.get('parent_video_uuid')
        parent_video = db.session.query(YoutubeVideoComponent).filter_by(uuid=parent_video_uuid).scalar()
        video_revision_file = request.files['video_revision_file']
        file_name = secure_filename(video_revision_file.filename)
        revision_video_text = request.form.get('revision_video_text')
        base_path = f"./static/files/youtube/{parent_video.youtube_video.youtube_channel.id}/{parent_video.youtube_video.id}/video_revisions/"
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        save_path = base_path + file_name
        video_revision_file.save(save_path)

        existing_uuid_list = [a.uuid for a in db.session.query(YoutubeVideoComponentRevision)]
        uuid = create_uuid(existing_uuid_list, 9)
        version_list = [a.version for a in parent_video.revisions]
        if len(version_list) == 0:
            version = str(1.0+.1)
        else:
            version_list_int = [float(i) for i in version_list]
            version = f"{(max(version_list_int)+.1):.1f}"

        entry = YoutubeVideoComponentRevision(
            uuid=uuid,
            version=version,
            file_path=save_path[1:],
            text=revision_video_text,
            date_time=date_time_now,
            youtube_video_component_id=parent_video.id,
            member_id = current_user.id
        )
        db.session.add(entry)
        parent_video.approval_status = 'pending'
        temp_assigned_uuid = parent_video.assigned_to_uuid
        parent_video.assigned_to_uuid = None
        parent_video.last_assigned = temp_assigned_uuid
        db.session.commit()
        return jsonify(success='success')


@youtube.route('/assign-mate', methods=['POST'])
def assign_mate():
    if request.method == 'POST' and request.form.get('type') == 'assign_mate':
        image_uuid = request.form.get('image_uuid')
        mate_uuid = request.form.get('mate_uuid')
        image = db.session.query(YoutubeVideoComponent).filter_by(uuid=image_uuid).scalar()

        if mate_uuid == 'remove-mate':
            image.assigned_to_uuid = None
            image.approval_status = 'pending'
            db.session.commit()
            return jsonify(success='success')
        else:
            mate_name = db.session.query(Member).filter_by(uuid=mate_uuid).scalar().name
            mate_email = db.session.query(Member).filter_by(uuid=mate_uuid).scalar().email
            image.assigned_to_uuid = mate_uuid
            image.approval_status = 'revision-required'
            db.session.commit()
            subject = f'New image assigned to you - {image.youtube_video.temp_title}'
            video_name = make_unicode_bold(image.youtube_video.temp_title)
            body = f"Hi {mate_name},\nYou have been assigned an image for revision.\nVideo name: {video_name}\nHope you'll begin ASAP!" 
            send_email_studio(subject, [mate_email], body, '', {})
            return jsonify(success='success')

    elif request.method == 'POST' and request.form.get('type') == 'assign_mate_video':
        video_uuid = request.form.get('video_uuid')
        mate_uuid = request.form.get('mate_uuid')
        video = db.session.query(YoutubeVideoComponent).filter_by(uuid=video_uuid).scalar()

        if mate_uuid == 'remove-mate':
            video.assigned_to_uuid = None
            video.approval_status = 'pending'
            db.session.commit()
            return jsonify(success='success')
        else:
            mate_name = db.session.query(Member).filter_by(uuid=mate_uuid).scalar().name
            mate_email = db.session.query(Member).filter_by(uuid=mate_uuid).scalar().email
            video.assigned_to_uuid = mate_uuid
            video.approval_status = 'revision-required'
            db.session.commit()
            subject = f'New video-clip assigned to you - {video.youtube_video.temp_title}'
            video_name = make_unicode_bold(video.youtube_video.temp_title)
            body = f"Hi {mate_name},\nYou have been assigned a video-clip for revision.\nVideo name: {video_name}\nHope you'll begin ASAP!" 
            send_email_studio(subject, [mate_email], body, '', {})
            return jsonify(success='success')


@youtube.route('/submit-status', methods=['POST'])
def submit_status():
    if request.method == 'POST' and request.form.get('type') == 'submit_approval_status':
        image_uuid = request.form.get('image_uuid')
        approval_status = request.form.get('approval_status')
        image = db.session.query(YoutubeVideoComponent).filter_by(uuid=image_uuid).scalar()
        image.approval_status = approval_status
        db.session.commit()
        return jsonify(success='success')
    elif request.method == 'POST' and request.form.get('type') == 'submit_video_approval_status':
        video_uuid = request.form.get('video_uuid')
        approval_status = request.form.get('approval_status')
        video = db.session.query(YoutubeVideoComponent).filter_by(uuid=video_uuid).scalar()
        video.approval_status = approval_status
        db.session.commit()
        return jsonify(success='success')
    
@youtube.route('/save_audio', methods=['POST'])
def save_audio():
    if request.method == 'POST' and request.form.get('type') == 'save_audio':
        image_uuid = request.form.get('image_uuid')
        revision_uuid = request.form.get('revision_uuid')
        kind = None
        if image_uuid == revision_uuid:
            kind = 'main_image'
        else:
            kind = 'revision_image'
        audio = request.files['audio']
        image = db.session.query(YoutubeVideoComponent).filter_by(uuid=image_uuid).scalar()
        video = image.youtube_video
        video_id = video.id
        channel = video.youtube_channel
        channel_id = channel.id

        if audio.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        filename = f"{revision_uuid}_feedback.webm"
        save_base_path = f"./static/files/youtube/{channel_id}/{video_id}/image_feedback/"
        if not os.path.exists(save_base_path):
            os.makedirs(save_base_path)
        save_path = save_base_path + filename
        audio.save(save_path)
        if kind == 'main_image':
            image.feedback = save_path[1:]
        elif kind == 'revision_image':
            db.session.query(YoutubeVideoComponentRevision).filter_by(uuid=revision_uuid).scalar().feedback = save_path[1:]
        db.session.commit()
        return jsonify(success='success')
    if request.method == 'POST' and request.form.get('type') == 'save_video_audio':
        audio = request.files['audio']
        video_uuid = request.form.get('video_uuid')
        kind = None
        video = db.session.query(YoutubeVideoComponent).filter_by(uuid=video_uuid).scalar()
        last_revision_uuid = [a.uuid for a in video.revisions if len(video.revisions) > 0 and a.version == max([a.version for a in video.revisions])][0] if len(video.revisions) > 0 else video_uuid
        if video_uuid == last_revision_uuid:
            kind = 'main_video'
        else:
            kind = 'revision_video'
        video_id = video.youtube_video.id
        channel = video.youtube_video.youtube_channel
        channel_id = channel.id

        if audio.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
        filename = f"{last_revision_uuid}_feedback.webm"
        save_base_path = f"./static/files/youtube/{channel_id}/{video_id}/video_feedback/"
        if not os.path.exists(save_base_path):
            os.makedirs(save_base_path)
        save_path = save_base_path + filename
        audio.save(save_path)
        if kind == 'main_video':
            video.feedback = save_path[1:]
        elif kind == 'revision_video':
            db.session.query(YoutubeVideoComponentRevision).filter_by(uuid=last_revision_uuid).scalar().feedback = save_path[1:]
        db.session.commit()
        return jsonify(success='success')
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        if data['type'] == 'get_all_videos_details':
            video_uuid = data['video_uuid']
            video = db.session.query(YoutubeVideoComponent).filter_by(uuid=video_uuid).scalar()
            main_and_revision_list = []
            main_video_tuple = (video.file_path, 'Main')
            main_and_revision_list.append(main_video_tuple)
            if len(video.revisions) > 0:
                for revision in video.revisions:
                    revision_tuple = (revision.file_path, revision.version)
                    main_and_revision_list.append(revision_tuple)
            scene_shot = f"{video.scene}-{video.shot}"
            return jsonify(video_list=main_and_revision_list, scene_shot=scene_shot)

    