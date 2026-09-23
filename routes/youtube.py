from flask import Blueprint, render_template, request, redirect, flash, send_file, session, url_for, jsonify
from flask_login import current_user
from extensions import *
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
    youtube_img_creator = db.session.query(Role).filter_by(name='youtube_img_creator').one_or_none()
    youtube_seo_manager = db.session.query(Role).filter_by(name='youtube_seo_manager').one_or_none()
    youtube_admin = db.session.query(Role).filter_by(name='youtube_admin').one_or_none()
    project_dict = {}
    current_scene_shot_tuple = ()
    creatives_upload_scene_no = ''
    creatives_upload_shot_no = ''
    current_creatives_upload_scene_shot_tuple = ()
    current_creatives_upload_scene_shot_data_tuple = ()
    upload_images_form_top_bar_data_tuple = ()

    def get_project_dict_data(data, key, scene_no, shot_no):
        return next(
            (
                shot.get(key)
                for scene in data.get("storyboard_scenes", [])
                if scene.get("scene") == str(scene_no)
                for shot in scene.get("shots", [])
                if shot.get("shot") == shot_no
            ),
            None
        )

    
    if not current_user.is_authenticated:
        return redirect(url_for('account.login'))
    else:
        if youtube_img_creator in current_user.role or youtube_admin in current_user.role or youtube_seo_manager in current_user.role:
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
                    if request.args.get('project_uuid'):
                        current_video_uuid = request.args.get('project_uuid')
                    else:
                        current_video_uuid = [a.value for a in current_user.tools if a.key == 'current_video_uuid'][0]

                    if current_video_uuid:
                        current_video_exists = True
                except Exception as e:
                    p(f"finding current video exist status error : {e}")  # print(e)
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
                        if len([a for a in v.components if a.component_type == 'video_id']) == 0:
                            if v.status == 'pending' or v.status == 'in-progress':
                                if len(v.components) > 0:
                                    default_vid_uuid_name_list.append((v.uuid, v.temp_title))
                    default_vid_uuid_name_list.reverse()
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
                        default_video_dict['stages'] = [a.stage for a in current_video.stages]
                        default_video_dict['scenes'] = [a.scene for a in current_video.storyboard_scenes]
                        project_dict = current_video.to_dict()
                        try:
                            current_scene_no = max([int(a.scene) for a in current_video.storyboard_scenes])
                            all_shot_no_list = [a.shot for a in db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=str(current_scene_no)).scalar().shots]
                            if len(all_shot_no_list) > 0:
                                current_shot_no = chr(ord(max(all_shot_no_list)) + 1)
                            else:
                                current_shot_no = 'A'
                            current_scene_shot_tuple = (current_scene_no, current_shot_no)
                        except Exception as e:
                            p(e)

                        total_shots = 0
                        shots_done = 0
                        total_scenes = 0
                        last_scene_shot = ''
                        for a in current_video.storyboard_scenes:
                            total_scenes += 1
                            for b in a.shots:
                                total_shots += 1
                                if len(b.creatives) != 0:
                                    shots_done += 1
                                last_scene_shot = f"{a.scene}-{b.shot}"
                        upload_images_form_top_bar_data_tuple = (total_scenes, total_shots, shots_done, last_scene_shot)

                        def find_missing_creative(current_video):
                            scene_no_list = [int(a.scene) for a in current_video.storyboard_scenes]
                            if len(scene_no_list) > 0:
                                scene_no_list.sort()
                                for scene in scene_no_list:
                                    scene_obj = db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=str(scene)).scalar()
                                    shot_no_list = [a.shot for a in db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=str(scene)).scalar().shots]
                                    if len(shot_no_list) > 0:
                                        sorted_shot_no_list = sorted(shot_no_list)
                                        for shot in sorted_shot_no_list:
                                            shot_obj = [a for a in scene_obj.shots if a.shot == shot][0]
                                            creative_uploads = [a for a in shot_obj.creatives]

                                            if not creative_uploads:
                                                return (scene, shot)
                        current_creatives_upload_scene_shot_tuple = find_missing_creative(current_video)
                            
                    else:
                        default_video_dict['image_list'] = [a.file_path for a in first_video.components if a.component_type == 'image']
                        default_video_dict['video_list'] = [a.file_path for a in first_video.components if a.component_type == 'video'] 
                        default_video_dict['stages'] = [a.stage for a in first_video.stages]
                        project_dict = first_video.to_dict()
                        try:
                            current_scene_no = max([int(a.scene) for a in first_video.storyboard_scenes])
                            all_shot_no_list = [a.shot for a in db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=str(current_scene_no)).scalar().shots]
                            if len(all_shot_no_list) > 0:
                                current_shot_no = chr(ord(max(all_shot_no_list)) + 1)
                            else:
                                current_shot_no = 'A'
                            current_scene_shot_tuple = (current_scene_no, current_shot_no)
                        except Exception as e:
                            p(e)
                        current_creatives_upload_scene_shot_tuple = find_missing_creative(first_video)
                        
                    if current_video_exists:
                        default_video_dict['temp_title'] = current_video.temp_title
                        try:
                            current_video_yt_title_revisions = [a for a in current_video.components if a.component_type == 'yt_title'][0].revisions
                            if len(current_video_yt_title_revisions) > 0:
                                current_video_yt_last_revision_no = max([float(a.version) for a in current_video_yt_title_revisions])
                                current_video_yt_title = [a.text for a in current_video_yt_title_revisions if a.version == str(current_video_yt_last_revision_no)][0]
                            else:
                                current_video_yt_title = [a.text for a in current_video.components if a.component_type == 'yt_title'][0]
                        except:
                            current_video_yt_title = ''
                        default_video_dict['yt_title'] = current_video_yt_title
                        try:
                            current_video_yt_description_revisions = [a for a in current_video.components if a.component_type == 'yt_description'][0].revisions
                            if len(current_video_yt_description_revisions) > 0:
                                current_video_yt_last_revision_no = max([float(a.version) for a in current_video_yt_description_revisions])
                                current_video_yt_description = [a.text for a in current_video_yt_description_revisions if a.version == str(current_video_yt_last_revision_no)][0]
                            else:
                                current_video_yt_description = [a.text for a in current_video.components if a.component_type == 'yt_description'][0]
                        except:
                            current_video_yt_description = ''
                        default_video_dict['yt_description'] = current_video_yt_description
                        try:
                            current_video_yt_tags_revisions = [a for a in current_video.components if a.component_type == 'yt_tags'][0].revisions
                            if len(current_video_yt_tags_revisions) > 0:
                                current_video_yt_last_revision_no = max([float(a.version) for a in current_video_yt_tags_revisions])
                                current_video_yt_tags = [a.text for a in current_video_yt_tags_revisions if a.version == str(current_video_yt_last_revision_no)][0]
                            else:
                                current_video_yt_tags = [a.text for a in current_video.components if a.component_type == 'yt_tags'][0]
                        except:
                            current_video_yt_tags = ''
                        default_video_dict['yt_tags'] = current_video_yt_tags
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
                            first_video_yt_title_revisions = [a for a in first_video.components if a.component_type == 'yt_title'][0].revisions
                            if len(first_video_yt_title_revisions) > 0:
                                first_video_yt_last_revision_no = max([float(a.version) for a in first_video_yt_title_revisions])
                                first_video_yt_title = [a.text for a in first_video_yt_title_revisions if a.version == str(first_video_yt_last_revision_no)][0]
                            else:
                                first_video_yt_title = [a.text for a in first_video.components if a.component_type == 'yt_title'][0]
                        except:
                            first_video_yt_title = ''

                        default_video_dict['yt_title'] = first_video_yt_title
                        try:
                            first_video_yt_description_revisions = [a for a in first_video.components if a.component_type == 'yt_description'][0].revisions
                            if len(first_video_yt_description_revisions) > 0:
                                first_video_yt_last_revision_no = max([float(a.version) for a in first_video_yt_description_revisions])
                                first_video_yt_description = [a.text for a in first_video_yt_description_revisions if a.version == str(first_video_yt_last_revision_no)][0]
                            else:
                                first_video_yt_description = [a.text for a in first_video.components if a.component_type == 'yt_description'][0]
                        except:
                            first_video_yt_description = ''
                        default_video_dict['yt_description'] = first_video_yt_description
                        try:
                            first_video_yt_tags_revisions = [a for a in first_video.components if a.component_type == 'yt_tags'][0].revisions
                            if len(first_video_yt_tags_revisions) > 0:
                                first_video_yt_last_revision_no = max([float(a.version) for a in first_video_yt_tags_revisions])
                                first_video_yt_tags = [a.text for a in first_video_yt_tags_revisions if a.version == str(first_video_yt_last_revision_no)][0]
                            else:
                                first_video_yt_tags = [a.text for a in first_video.components if a.component_type == 'yt_tags'][0]
                        except:
                            first_video_yt_tags = ''
                        default_video_dict['yt_tags'] = first_video_yt_tags
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
                    if current_creatives_upload_scene_shot_tuple:
                        current_creatives_shot_obj = [a for a in db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=str(current_creatives_upload_scene_shot_tuple[0])).one_or_none().shots if a.shot == current_creatives_upload_scene_shot_tuple[1]][0]
                        current_creatives_shot_img = current_creatives_shot_obj.storyboard_img_path
                        current_creatives_shot_camera_direction = current_creatives_shot_obj.frame_direction
                        current_creatives_shot_direction = current_creatives_shot_obj.creative_direction
                        current_creatives_shot_narration_dialogue = current_creatives_shot_obj.dialogue_narration
                        current_creatives_shot_type = current_creatives_shot_obj.shot_type
                        creatives_list = [(a.media_type, a.media_path) for a in current_creatives_shot_obj.creatives]
                        current_creatives_upload_scene_shot_data_tuple = (current_creatives_upload_scene_shot_tuple[0], 
                                                                          current_creatives_upload_scene_shot_tuple[1], 
                                                                          current_creatives_shot_img, 
                                                                          current_creatives_shot_camera_direction, 
                                                                          current_creatives_shot_direction, 
                                                                          current_creatives_shot_narration_dialogue, 
                                                                          current_creatives_shot_type, 
                                                                          current_creatives_shot_obj.uuid, 
                                                                          creatives_list)
                    else:
                        current_creatives_upload_scene_shot_data_tuple = ()
                else:
                    default_video_dict = {}
            if request.method == 'POST' and request.is_json:
                data = request.get_json()
                if data['type'] == 'get_img_upload_shot_data':
                    video_uuid = data['video_uuid']
                    current_scene = data['current_scene']
                    current_shot = data['current_shot']
                    subtype = data['subtype']
                    scene = None
                    shot = None
                    shot_uuid = None

                    video_obj = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
                    scene_list = [int(a.scene) for a in video_obj.storyboard_scenes]
                    current_scene_obj = db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=current_scene).scalar()
                    current_scene_shot_list = [a.shot for a in current_scene_obj.shots]

                    if subtype == 'next':
                        if chr(ord(current_shot) + 1) in current_scene_shot_list:
                            scene = current_scene
                            shot = chr(ord(current_shot) + 1)
                            try:
                                shot_uuid = [b for b in [a for a in video_obj.storyboard_scenes if a.scene == scene][0].shots if b.shot == shot][0].uuid
                            except Exception as e:
                                p(e)

                        else:
                            if int(current_scene) + 1 in scene_list:
                                scene = str(int(current_scene) + 1)
                                shot = 'A'
                                try:
                                    shot_uuid = [b for b in [a for a in video_obj.storyboard_scenes if a.scene == scene][0].shots if b.shot == 'A'][0].uuid
                                except Exception as e:
                                    p(e)
                            else:
                                return jsonify(message='No more shots')
                                

                    elif subtype == 'previous':
                        if chr(ord(current_shot) - 1) in current_scene_shot_list:
                            scene = current_scene
                            shot = chr(ord(current_shot) - 1)
                            try:
                                shot_uuid = [b for b in [a for a in video_obj.storyboard_scenes if a.scene == scene][0].shots if b.shot == shot][0].uuid
                            except Exception as e:
                                p(e)

                        else:
                            if int(current_scene) - 1 in scene_list:
                                scene = str(int(current_scene) - 1)
                                shot = max([a.shot for a in [a for a in video_obj.storyboard_scenes if a.scene == scene][0].shots])
                                try:
                                    shot_uuid = [b for b in [a for a in video_obj.storyboard_scenes if a.scene == scene][0].shots if b.shot == 'A'][0].uuid
                                except Exception as e:
                                    p(e)
                            else:
                                return jsonify(message='This is the first shot')
                    shot_id = db.session.query(YoutubeVideoStoryboardShot).filter_by(uuid=shot_uuid).scalar().id
                    shot_creatives_list = [(a.media_type, a.media_path) for a in db.session.query(YoutubeVideoCreative).filter_by(youtube_video_shot_id=shot_id).all()]

                    upload_media_next_shot_data_dict = {
                        'video_uuid': video_uuid,
                        'shot_uuid': shot_uuid,
                        'scene': scene,
                        'shot': shot,
                        'shot_storyboard_img': get_project_dict_data(project_dict, "storyboard_img_path", scene, shot),
                        'shot_type': get_project_dict_data(project_dict, "shot_type", scene, shot),
                        'camera_direction': get_project_dict_data(project_dict, "frame_direction", scene, shot),
                        'direction': get_project_dict_data(project_dict, "creative_direction", scene, shot),
                        'narration_dialogue': get_project_dict_data(project_dict, "dialogue_narration", scene, shot),
                        'creatives_list': shot_creatives_list
                    }
                    return jsonify(upload_media_next_shot_data_dict)
                
                if data['type'] == 'save_storyboard_shot':
                    video_uuid = data['video_uuid']
                    video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
                    channel_id = video.channel_id
                    video_id = video.id
                    scene = data['scene']
                    shot = data['shot']
                    shot_type = data['shot_type']
                    camera_direction = data['camera_direction']
                    narration_dialogue = data['narration_dialogue']
                    direction = data['direction']
                    drawing_data = data['drawing_data']

                    if narration_dialogue[-1] == '.':
                        narration_dialogue = '. . . ' + narration_dialogue
                    else:
                        narration_dialogue = '. . . ' + narration_dialogue + '. . .'

                    drawing_data = drawing_data.split(',', 1)[1]
                    drawing_bytes = base64.b64decode(drawing_data)

                    save_base_path = f"./static/files/youtube/{channel_id}/{video_id}/storyboard_images/"
                    os.makedirs(save_base_path, exist_ok=True)
                    file_name = f"{scene}-{shot}.png"
                    file_path = os.path.join(save_base_path, file_name)

                    with open(file_path, 'wb') as f:
                        f.write(drawing_bytes)

                    existing_scene = [a for a in video.storyboard_scenes if a.scene == scene]
                    if len(existing_scene) > 0:
                        existing_scene_object = existing_scene[0]
                    else:
                        scene_uuid = ''
                        existing_scene_uuid = [a.uuid for a in db.session.query(YoutubeVideoStoryboardScene).all()]
                        scene_uuid = create_uuid(existing_scene_uuid, 9)
                        p('created scene uuid')
                        entry = YoutubeVideoStoryboardScene (
                            uuid=scene_uuid,
                            scene=scene,
                            youtube_video_id=video_id
                        )
                        db.session.add(entry)
                        db.session.commit()

                        existing_scene_object = db.session.query(YoutubeVideoStoryboardScene).filter_by(uuid=scene_uuid).scalar()
                    
                    # Save Shot to database
                    shot_uuid = ''
                    existing_shot_uuid_list = [a.uuid for a in db.session.query(YoutubeVideoStoryboardShot).all()]
                    shot_uuid = create_uuid(existing_shot_uuid_list, 9)

                    entry = YoutubeVideoStoryboardShot (
                        uuid=shot_uuid,
                        shot=shot,
                        storyboard_img_path=file_path[1:],
                        dialogue_narration=narration_dialogue,
                        frame_direction=camera_direction,
                        creative_direction=direction,
                        shot_type=shot_type,
                        youtube_video_storyboard_scene_id=existing_scene_object.id
                    )
                    db.session.add(entry)
                    db.session.commit()
                    
                    return jsonify(f"{scene}-{shot} saved successfully!")
                
                if data['type'] == 'get_task_details':
                    task_uuid = data['task_uuid']
                    task = db.session.query(YoutubeVideoComponent).filter_by(uuid=task_uuid).scalar()
                    task_type = task.component_type
                    assigned_to_name = db.session.query(Member).filter_by(uuid=int(task.assigned_to_uuid)).scalar().name
                    try:
                        last_assigned = db.session.query(Member).filter_by(uuid=int(task.last_assigned)).scalar().name
                    except:
                        last_assigned = ''
                    file_path = ''
                    file_text = ''
                    feedback = ''
                    # if task_type == 'image':
                    if len(task.revisions) > 0:
                        last_revision_no = max([float(a.version) for a in task.revisions])
                        file_path = [a.file_path for a in task.revisions if a.version == str(last_revision_no)][0]
                        all_revision_no_descending_order = sorted([float(a.version) for a in task.revisions], reverse=True)
                        run = True
                        count = 0
                        version_count = len(all_revision_no_descending_order)
                        while run:
                            for i in all_revision_no_descending_order:
                                count += 1
                                version_text = [a.text for a in task.revisions if a.version == str(i)][0]
                                if version_text:
                                    file_text = version_text
                                    run = False
                                    break
                                else:
                                    if count == version_count:
                                        run = False                                
                        if not file_text:
                            file_text = task.text

                        feedback_run = True
                        feedback_count = 0
                        while feedback_run:
                            for i in all_revision_no_descending_order:
                                feedback_count += 1
                                feedback_text = [a.feedback for a in task.revisions if a.version == str(i)][0]
                                if feedback_text:
                                    feedback = feedback_text
                                    feedback_run = False
                                    break
                                else:
                                    if feedback_count == version_count:
                                        feedback_run = False
                        if not feedback:
                            feedback = task.feedback
                    else:
                        file_path = task.file_path
                        p(file_path)
                        file_text = task.text
                        feedback = task.feedback
                    task_dict = {
                        'uuid': task.uuid,
                        'component_type': task_type,
                        'temp_title': task.youtube_video.temp_title,
                        'file_path': file_path,
                        'text': file_text,
                        'feedback': feedback,
                        'assigned_to_name': assigned_to_name,
                        'last_assigned': last_assigned,
                    }
                    return jsonify(task_dict=task_dict)
                    
                    # elif task_type == 'video':
                    #     task_dict = {
                    #         'uuid': task.uuid,
                    #         'component_type': task_type,
                    #         'temp_title': task.temp_title,
                    #     }
                    #     return jsonify('success')
                if data['type'] == 'get_seo_task_details':
                    task_uuid = data['task_uuid']
                    task = db.session.query(YoutubeVideo).filter_by(uuid=task_uuid).scalar()
                    try:
                        yt_title = [a.text for a in task.components if a.component_type == 'yt_title'][0]
                    except:
                        yt_title = ''
                    try:
                        yt_description = [a.text for a in task.components if a.comonent_type == 'yt_description'][0]
                    except:
                        yt_description = ''
                    try:
                        yt_tags = [a.text for a in task.components if a.component_type == 'yt_tags'][0]
                    except:
                        yt_tags = ''
                    seo_task_dict = {
                        'uuid': task.uuid,
                        'temp_title': task.temp_title,
                        'yt_title': yt_title,
                        'yt_description': yt_description,
                        'yt_tags': yt_tags
                    }
                    return jsonify(seo_task_dict=seo_task_dict)
                
                if data['type'] == 'select_channel':
                    channel_uuid = data['channel_uuid']
                    video_list = []
                    channel_videos = db.session.query(YoutubeChannel).filter_by(uuid=channel_uuid).scalar().videos
                    for c in channel_videos:
                        video_list.append((c.uuid, c.temp_title))
                    return jsonify(video_list=video_list)
                if data['type'] == 'select_video':
                    current_scene_shot_tuple = ()
                    creatives_upload_scene_no = ''
                    creatives_upload_shot_no = ''
                    current_creatives_upload_scene_shot_tuple = ()
                    current_creatives_upload_scene_shot_data_tuple = ()

                    video_uuid = data['video_uuid']
                    video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
                    video_temp_title = video.temp_title
                    video_components = video.components
                    stages = [a.stage for a in video.stages]
                    vid_dict = {}
                    dialogue_narration = ''
                    voice_recordings = []
                    image_list = []
                    video_list = []
                    storyboard = []
                    img_vid_instruction = ''
                    thumbnail_instruction = ''
                    youtube_card_instruction = ''
                    yt_title = ''
                    yt_description = ''
                    yt_tags = ''
                    video_yt_id = ''
# -------------------------------------------------------- CREATIVES --------------------------------------------------
                    def find_missing_creative(video):
                        scene_no_list = [int(a.scene) for a in video.storyboard_scenes]
                        if len(scene_no_list) > 0:
                            scene_no_list.sort()
                            for scene in scene_no_list:
                                scene_obj = db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=str(scene)).scalar()
                                shot_no_list = [a.shot for a in db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=str(scene)).scalar().shots]
                                if len(shot_no_list) > 0:
                                    sorted_shot_no_list = sorted(shot_no_list)
                                    for shot in sorted_shot_no_list:
                                        shot_obj = [a for a in scene_obj.shots if a.shot == shot][0]
                                        creative_uploads = [a for a in shot_obj.creatives]

                                        if not creative_uploads:
                                            return (scene, shot)
                    current_creatives_upload_scene_shot_tuple = find_missing_creative(video)
                    if current_creatives_upload_scene_shot_tuple:
                        current_creatives_shot_obj = [a for a in db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=current_creatives_upload_scene_shot_tuple[0]).one_or_none().shots if a.shot == current_creatives_upload_scene_shot_tuple[1]][0]
                        current_creatives_shot_img = current_creatives_shot_obj.storyboard_img_path
                        current_creatives_shot_camera_direction = current_creatives_shot_obj.frame_direction
                        current_creatives_shot_direction = current_creatives_shot_obj.creative_direction
                        current_creatives_shot_narration_dialogue = current_creatives_shot_obj.dialogue_narration
                        current_creatives_shot_type = current_creatives_shot_obj.shot_type
                        creatives_list = [(a.media_type, a.media_path) for a in current_creatives_shot_obj.creatives]
                        current_creatives_upload_scene_shot_data_tuple = (current_creatives_upload_scene_shot_tuple[0], 
                                                                            current_creatives_upload_scene_shot_tuple[1], 
                                                                            current_creatives_shot_img, 
                                                                            current_creatives_shot_camera_direction, 
                                                                            current_creatives_shot_direction, 
                                                                            current_creatives_shot_narration_dialogue, 
                                                                            current_creatives_shot_type, 
                                                                            current_creatives_shot_obj.uuid, 
                                                                            creatives_list)
                    else:
                        if len(video.storyboard_scenes) > 0:
                            last_scene = [a.scene for a in video.storyboard_scenes if a.scene == str(max([int(a.scene) for a in video.storyboard_scenes]))][0]
                            last_shot = [a.shot for a in db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=last_scene).one_or_none().shots if a.shot == str(max([int(a.shot) for a in db.session.query(YoutubeVideoStoryboardScene).filter_by(scene=last_scene).one_or_none().shots]))][0]
                            current_creatives_upload_scene_shot_data_tuple = (last_scene, last_shot)
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
                        elif c.component_type == 'yt_title':
                            yt_title_revisions = c.revisions
                            if len(yt_title_revisions) > 0:
                                yt_last_revision_no = max([float(a.version) for a in yt_title_revisions])
                                yt_title = [a.text for a in yt_title_revisions if a.version == str(yt_last_revision_no)][0]
                            else:
                                yt_title = c.text
                        elif c.component_type == 'yt_description':
                            yt_description_revisions = c.revisions
                            if len(yt_description_revisions) > 0:
                                yt_last_revision_no = max([float(a.version) for a in yt_description_revisions])
                                yt_description = [a.text for a in yt_description_revisions if a.version == str(yt_last_revision_no)][0]
                            else:
                                yt_description = c.text
                        elif c.component_type == 'yt_tags':
                            yt_tags_revisions = c.revisions
                            if len(yt_tags_revisions) > 0:
                                yt_last_revision_no = max([float(a.version) for a in yt_tags_revisions])
                                yt_tags = [a.text for a in yt_tags_revisions if a.version == str(yt_last_revision_no)][0]
                            else:
                                yt_tags = c.text
                        elif c.component_type == 'video':
                            video_yt_id = c.file_path
                    vid_dict['video_yt_id'] = video_yt_id
                    vid_dict['temp_title'] = video_temp_title
                    vid_dict['video_uuid'] = video_uuid
                    vid_dict['currentCreativesUploadSceneShotTuple'] = current_creatives_upload_scene_shot_data_tuple
                    total_shots = 0
                    shots_done = 0
                    total_scenes = 0
                    last_scene_shot = ''
                    for a in current_video.storyboard_scenes:
                        total_scenes += 1
                        for b in a.shots:
                            total_shots += 1
                            if len(b.creatives) != 0:
                                shots_done += 1
                            last_scene_shot = f"{a.scene}-{b.shot}"
                    upload_images_form_top_bar_data_tuple = (total_scenes, total_shots, shots_done, last_scene_shot)
                    vid_dict['uploadImageFormTopBarDataTuple'] = upload_images_form_top_bar_data_tuple
                    try:
                        vid_dict['dialogue_narration'] = markdown.markdown(dialogue_narration).replace('\n', '<br>')
                    except:
                        vid_dict['dialogue_narration'] = dialogue_narration
                    vid_dict['voice_recordings'] = voice_recordings
                    vid_dict['storyboard'] = storyboard
                    vid_dict['image_list'] = image_list
                    vid_dict['video_list'] = video_list
                    vid_dict['yt_title'] = yt_title
                    vid_dict['yt_description'] = yt_description
                    vid_dict['yt_tags'] = yt_tags
                    # -------------------------------------- Add progress stages -------------------------------------------
                    vid_dict['stages'] = stages
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
            # ----------------------------------------------------- NOTIFICATION ---------------------------------------------------------------
            all_videos = db.session.query(YoutubeVideo).all()

            if youtube_admin in current_user.role:
                pending_reviews = [(a.uuid, a.youtube_video.temp_title, a.component_type) for a in db.session.query(YoutubeVideoComponent).all() if a.approval_status == 'pending']
            else:
                pending_reviews = []
            
            if youtube_img_creator in current_user.role:
                pending_revisions = [(a.uuid, a.youtube_video.temp_title, a.component_type) for a in db.session.query(YoutubeVideoComponent).filter_by(assigned_to_uuid=str(current_user.uuid)).all() if a.approval_status == 'revision-required']
            else:
                pending_revisions = []

            pending_seo = []
            if youtube_seo_manager in current_user.role or youtube_admin in current_user.role:
                for v in all_videos:
                    if len([a for a in v.components if a.component_type == 'yt_title']) == 0 or len([a for a in v.components if a.component_type == 'yt_description']) == 0 or len([a for a in v.components if a.component_type == 'yt_tags']) == 0:
                        pending_seo.append((v.uuid, v.category, v.temp_title))

            req_scene = [a for a in project_dict['storyboard_scenes'] if a['scene'] == '1']
            # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            current_user_roles = [a.name for a in current_user.role]
            return render_template('youtube.html', current_year=current_year, channels=channels, default_video_dict=default_video_dict, logged_in=current_user.is_authenticated, admin=admin, first_channel=first_channel,
                                current_video_option_list=current_video_option_list, pending_revisions=pending_revisions, pending_reviews=pending_reviews, pending_seo=pending_seo, youtube_img_creator=youtube_img_creator, youtube_seo_manager=youtube_seo_manager, youtube_admin=youtube_admin, current_user_roles=current_user_roles,
                                project_dict=project_dict, current_scene_shot_tuple=current_scene_shot_tuple, current_creatives_upload_scene_shot_data_tuple=current_creatives_upload_scene_shot_data_tuple, upload_images_form_top_bar_data_tuple=upload_images_form_top_bar_data_tuple, current_creatives_upload_scene_shot_tuple=current_creatives_upload_scene_shot_tuple)
        else:
            return render_template('admin_area.html')


@youtube.route('/upload-images-videos', methods=['GET', 'POST'])
def upload_images_videos():
    youtube_admin = db.session.query(Role).filter_by(name='youtube_admin').scalar()
    youtube_img_creator = db.session.query(Role).filter_by(name='youtube_img_creator').scalar()
    youtube_seo_manager = db.session.query(Role).filter_by(name='youtube_seo_manager').scalar()
    if youtube_admin in current_user.role or youtube_img_creator in current_user.role or youtube_seo_manager in current_user.role:
        if request.method == 'POST' and request.form.get('type') == 'upload_images_videos':
            files = request.files.getlist('files')
            shot_uuid = request.form.get('shot_uuid')
            text = request.form.get('text')
            video_uuid = request.form.get('video_uuid')
            scene = request.form.get('scene')
            shot = request.form.get('shot')
            video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
            channel_id = video.youtube_channel.id
            video_id = video.id
            shot_id = db.session.query(YoutubeVideoStoryboardShot).filter_by(uuid=shot_uuid).scalar().id

            

            base_path = f"./static/files/youtube/{channel_id}/{video_id}/creatives/"

            for f in files:
                if f.filename == '':
                    flash('No selected file', 'error')
                    return redirect(request.url)
                mimetype = f.content_type
                if mimetype.startswith('image/'):
                    media_type = 'image'
                elif mimetype.startswith('video/'):
                    media_type = 'video'
                
                file_name_without_extension = f"{scene}-{shot}"
                file_path = save_with_filename_suffix_if_already_exists(base_path, file_name_without_extension, f)[1:]
                existing_uuid_list = [a.uuid for a in db.session.query(YoutubeVideoCreative).all()]
                uuid = create_uuid(existing_uuid_list, 9)
                entry = YoutubeVideoCreative(
                    uuid=uuid,
                    media_type=media_type,
                    media_path=file_path,
                    text=text,
                    status='pending',
                    date_time=datetime.now().replace(microsecond=0),
                    member_id=current_user.id,
                    youtube_video_shot_id=shot_id
                )
                db.session.add(entry)
                db.session.commit()
            total_shots = 0
            shots_done = 0
            total_scenes = 0
            last_scene_shot = ''
            for a in video.storyboard_scenes:
                total_scenes += 1
                for b in a.shots:
                    total_shots += 1
                    if len(b.creatives) != 0:
                        shots_done += 1
                    last_scene_shot = f"{a.scene}-{b.shot}"
            upload_images_form_top_bar_data_tuple = (total_scenes, total_shots, shots_done, last_scene_shot)
            creatives_list = [(a.media_type, a.media_path) for a in db.session.query(YoutubeVideoCreative).filter_by(youtube_video_shot_id=shot_id).all()]
            return jsonify({"creatives_list": creatives_list, "upload_images_form_top_bar_data_tuple": upload_images_form_top_bar_data_tuple})
    else:
        return render_template('admin_area.html')

@youtube.route('/upload-video', methods=['GET', 'POST'])
def upload_video():
    if request.method == 'POST' and request.form.get('type') == 'upload_video':
        video_file = request.files.get('files')
        video_text = request.form.get('text')
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
            shot=shot,
            text=video_text
        )
        db.session.add(entry)
        db.session.commit()

        # send email to Leader -----------------------------------------------------
        subject = f"New video uploaded - {date_time_now}"
        body = f"New video uploaded\n\nVideo: {video_temp_title}\nScene-shot: {scene}-{shot}\nMember: {current_user.name}\nChannel: {channel_name}"
        send_email_studio(subject, ['shwetabhartist@gmail.com'], body, '', {})
        return jsonify('success')


@youtube.route('/add-title-description-tags', methods=['GET', 'POST'])
def add_title_description_tags():
    def add_title(video_uuid, title):
        video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
        yt_title_stage = db.session.query(YoutubeVideoStage).filter_by(stage='yt_title').scalar()
        try:
            existing_yt_title = [a for a in video.components if a.component_type == 'yt_title'][0]
        except:
            existing_yt_title = None
        if title != '' and existing_yt_title != title:
            try:
                if len(existing_yt_title.revisions) > 0:
                    new_revision_no = f"{(max([float(a.version) for a in existing_yt_title.revisions]) + .1):.1f}"
                else:
                    new_revision_no = 1.1

                existing_uuid = [a.uuid for a in db.session.query(YoutubeVideoComponentRevision)]
                uuid = create_uuid(existing_uuid, 9)
                entry = YoutubeVideoComponentRevision(
                    uuid=uuid,
                    version=str(new_revision_no),
                    date_time=date_time_now,
                    text=title,
                    youtube_video_component_id=existing_yt_title.id,
                    member_id=current_user.id,
                )
                db.session.add(entry)
                if yt_title_stage not in video.stages:
                    video.stages.append(yt_title_stage)

            except Exception as e:
                p(e)
                existing_uuid_list = [a.uuid for a in db.session.query(YoutubeVideoComponent)]
                uuid = create_uuid(existing_uuid_list, 9)
                entry = YoutubeVideoComponent(
                    uuid=uuid,
                    component_type='yt_title',
                    text=title,
                    approval_status='pending',
                    date_time=date_time_now,
                    youtube_video_id=video.id,
                    member_id=current_user.id,
                )
                db.session.add(entry)
                if yt_title_stage not in video.stages:
                    video.stages.append(yt_title_stage)
            db.session.commit()
            p('added title')

    def add_description(video_uuid, description):
        video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
        yt_description_stage = db.session.query(YoutubeVideoStage).filter_by(stage='yt_description').scalar()
        if description != '':
            try:
                existing_yt_description = [a for a in video.components if a.component_type == 'yt_description'][0]
                if len(existing_yt_description.revisions) > 0:
                    new_revision_no = f"{(max([float(a.version) for a in existing_yt_description.revisions]) + .1):.1f}"
                else:
                    new_revision_no = 1.1

                existing_uuid = [a.uuid for a in db.session.query(YoutubeVideoComponentRevision)]
                uuid = create_uuid(existing_uuid, 9)
                entry = YoutubeVideoComponentRevision(
                    uuid=uuid,
                    version=str(new_revision_no),
                    date_time=date_time_now,
                    text=description,
                    youtube_video_component_id=existing_yt_description.id,
                    member_id=current_user.id,
                )
                db.session.add(entry)
                if yt_description_stage not in video.stages:
                    video.stages.append(yt_description_stage)

            except Exception as e:
                p(e)
                existing_uuid_list = [a.uuid for a in db.session.query(YoutubeVideoComponent)]
                uuid = create_uuid(existing_uuid_list, 9)
                entry = YoutubeVideoComponent(
                    uuid=uuid,
                    component_type='yt_description',
                    text=description,
                    approval_status='pending',
                    date_time=date_time_now,
                    youtube_video_id=video.id,
                    member_id=current_user.id,
                )
                db.session.add(entry)
                if yt_description_stage not in video.stages:
                    video.stages.append(yt_description_stage)
            db.session.commit()
            p('added description')

    def add_tags(video_uuid, tags):
        video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
        yt_tags_stage = db.session.query(YoutubeVideoStage).filter_by(stage='yt_video_tags').scalar()
        if tags != '':
            try:
                existing_yt_tags = [a for a in video.components if a.component_type == 'yt_tags'][0]
                if len(existing_yt_tags.revisions) > 0:
                    new_revision_no = f"{(max([float(a.version) for a in existing_yt_tags.revisions]) + .1):.1f}"
                else:
                    new_revision_no = 1.1

                existing_uuid = [a.uuid for a in db.session.query(YoutubeVideoComponentRevision)]
                uuid = create_uuid(existing_uuid, 9)
                entry = YoutubeVideoComponentRevision(
                    uuid=uuid,
                    version=str(new_revision_no),
                    date_time=date_time_now,
                    text=tags,
                    youtube_video_component_id=existing_yt_tags.id,
                    member_id=current_user.id,
                )
                db.session.add(entry)
                if yt_tags_stage not in video.stages:
                    video.stages.append(yt_tags_stage)

            except Exception as e:
                p(e)
                existing_uuid_list = [a.uuid for a in db.session.query(YoutubeVideoComponent)]
                uuid = create_uuid(existing_uuid_list, 9)
                entry = YoutubeVideoComponent(
                    uuid=uuid,
                    component_type='yt_tags',
                    text=tags,
                    approval_status='pending',
                    date_time=date_time_now,
                    youtube_video_id=video.id,
                    member_id=current_user.id,
                )
                db.session.add(entry)
                if yt_tags_stage not in video.stages:
                    video.stages.append(yt_tags_stage)
            db.session.commit()
            p('added tags')
    
    # -------------------------------------------------------------------------------------------------------
    if request.method == 'POST' and request.get_json:
        data = request.get_json()
        if data['type'] == 'get-existing-title':
            last_revision_yt_title = ''
            video_uuid = data['video_uuid']
            video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
            existing_yt_title_row_list = [a for a in video.components if a.component_type == 'yt_title']
            if len(existing_yt_title_row_list) > 0:
                existing_yt_title_row = existing_yt_title_row_list[0]
                if len(existing_yt_title_row.revisions) > 0:
                    last_version_no = max([float(a.version) for a in existing_yt_title_row.revisions])
                    last_revision_yt_title = [a.text for a in existing_yt_title_row.revisions if a.version == str(last_version_no)][0]
                else:
                    last_revision_yt_title = existing_yt_title_row.text
            else:
                last_revision_yt_title = ''
            return jsonify(last_revision_yt_title)
        
        if data['type'] == 'get-existing-description':
            last_revision_yt_description = ''
            video_uuid = data['video_uuid']
            video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
            existing_yt_description_row_list = [a for a in video.components if a.component_type == 'yt_description']
            if len(existing_yt_description_row_list) > 0:
                existing_yt_description_row = existing_yt_description_row_list[0]
                if len(existing_yt_description_row.revisions) > 0:
                    last_version_no = max([float(a.version) for a in existing_yt_description_row.revisions])
                    last_revision_yt_description = [a.text for a in existing_yt_description_row.revisions if a.version == str(last_version_no)][0]
                else:
                    last_revision_yt_description = existing_yt_description_row.text
            else:
                last_revision_yt_description = ''
            p(last_revision_yt_description)
            return jsonify(last_revision_yt_description)
        
        if data['type'] == 'get-existing-tags':
            last_revision_yt_tags = ''
            video_uuid = data['video_uuid']
            video = db.session.query(YoutubeVideo).filter_by(uuid=video_uuid).scalar()
            existing_yt_tags_row_list = [a for a in video.components if a.component_type == 'yt_tags']
            if len(existing_yt_tags_row_list) > 0:
                existing_yt_tags_row = existing_yt_tags_row_list[0]
                if len(existing_yt_tags_row.revisions) > 0:
                    last_version_no = max([float(a.version) for a in existing_yt_tags_row.revisions])
                    last_revision_yt_tags = [a.text for a in existing_yt_tags_row.revisions if a.version == str(last_version_no)][0]
                else:
                    last_revision_yt_tags = existing_yt_tags_row.text
            else:
                last_revision_yt_tags = ''
            return jsonify(last_revision_yt_tags)

        # ---------------------------------------------------------------------------------------------
        
        if data['type'] == 'add-title':
            video_uuid = data['video_uuid']
            title = data['title']
            add_title(video_uuid, title)
            return jsonify('success')
        
        if data['type'] == 'add-description':
            video_uuid = data['video_uuid']
            description = data['description']
            add_description(video_uuid, description)
            return jsonify('success')
        
        if data['type'] == 'add-tags':
            video_uuid = data['video_uuid']
            tags = data['tags']
            add_tags(video_uuid, tags)
            return jsonify('success')

        if data['type'] == 'save_seo_tasks':
            video_uuid = data['uuid']
            yt_title = data['yt_title']
            yt_description = data['yt_description']
            yt_tags = data['yt_tags']
            add_title(video_uuid, yt_title)
            add_description(video_uuid, yt_description)
            add_tags(video_uuid, yt_tags)
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
                    image_version_list_decreasing_order = sorted(image_version_list, reverse=True)
                    if len(image_version_list) == 0:
                        file_path = c.file_path
                        file_text = c.text
                        feedback = c.feedback
                        revision_uuid = c.uuid
                    else:
                        last_version = max(image_version_list)
                        file_path = [a.file_path for a in c.revisions if a.version == str(last_version)][0]
                        feedback = [a.feedback for a in c.revisions if a.version == str(last_version)][0]
                        revision_uuid = [a.uuid for a in c.revisions if a.version == str(last_version)][0]
                        run = True
                        count = 0
                        version_count = len(image_version_list_decreasing_order)
                        while run:
                            for v in image_version_list_decreasing_order:
                                count += 1
                                version_text = [a.text for a in c.revisions if a.version == str(v)][0]
                                if version_text:
                                    file_text = version_text
                                    run = False
                                    break
                                else:
                                    if count == version_count:
                                        run = False
                        if file_text == '' or file_text is None:
                            file_text = c.text
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
                    text = ''
                    all_revisions = [(a.uuid, a.version, a.file_path, a.text, a.feedback) for a in row.revisions if len(row.revisions) > 0]
                    revision_list = sorted(all_revisions, key=lambda x: float(x[1]), reverse=True)
                    run_search = True
                    if len(revision_list) != 0:
                        for r in revision_list:
                            if r[3]:
                                text = r[3]
                                break
                                    
                        if not text:
                            text = row.text
                    else:
                        text = row.text
                        
                    video_dict[row.scene][row.shot][row.uuid] = {'file_path': row.file_path, 'text': text, 'feedback': row.feedback,
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


@youtube.route('/project-stage-operations', methods=['GET', 'POST'])
def project_stage_operations():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        if data['type'] == 'show_project_by_stage':
            selected_stage = data['stage']
            all_videos = db.session.query(YoutubeVideo).all()
            selected_video_uuid_name_tuple_list = []
            if selected_stage == 'all-active':
                for v in all_videos:
                    video_stage_list = [a.stage for a in v.stages]
                    if 'archived' not in video_stage_list and 'published' not in video_stage_list:
                        selected_video_uuid_name_tuple_list.append((v.uuid, v.temp_title))
            if selected_stage == 'pre-production':
                for v in all_videos:
                    video_stage_list = [a.stage for a in v.stages]
                    exclusions = ['released', 'scheduled', 'video', 'yt_tags', 'yt_description', 'yt_title', 'yt_card', 'thumbnail']
                    if all(x not in video_stage_list for x in exclusions):
                        selected_video_uuid_name_tuple_list.append((v.uuid, v.temp_title))

            elif selected_stage == 'video-done':
                for v in all_videos:
                    video_stage_list = [a.stage for a in v.stages]
                    if 'video' in video_stage_list and 'archived' not in video_stage_list:
                        selected_video_uuid_name_tuple_list.append((v.uuid, v.temp_title))

            elif selected_stage == 'seo-done':
                for v in all_videos:
                    video_stage_list = [a.stage for a in v.stages]
                    p(video_stage_list)
                    if 'yt_video_tags' in video_stage_list and 'yt_description' in video_stage_list and 'yt_title' in video_stage_list:
                        selected_video_uuid_name_tuple_list.append((v.uuid, v.temp_title))

            elif selected_stage == 'scheduled':
                for v in all_videos:
                    video_stage_list = [a.stage for a in v.stages]
                    if 'scheduled' in video_stage_list:
                        selected_video_uuid_name_tuple_list.append((v.uuid, v.temp_title))

            elif selected_stage == 'ready-for-publish':
                for v in all_videos:
                    video_stage_list = [a.stage for a in v.stages]
                    required_stages = ['video', 'yt_tags', 'yt_description', 'yt_title', 'yt_card', 'thumbnail']
                    if set(required_stages).issubset(set(video_stage_list)):
                        selected_video_uuid_name_tuple_list.append((v.uuid, v.temp_title))
            elif selected_stage == 'published':
                for v in all_videos:
                    video_stage_list = [a.stage for a in v.stages]
                    if 'released' in video_stage_list:
                        selected_video_uuid_name_tuple_list.append((v.uuid, v.temp_title))

            elif selected_stage == 'archived':
                for v in all_videos:
                    video_stage_list = [a.stage for a in v.stages]
                    if 'archived' in video_stage_list:
                        selected_video_uuid_name_tuple_list.append((v.uuid, v.temp_title))
            return jsonify(selected_video_uuid_name_tuple_list)


@youtube.route('/display-ready-videos', methods=['GET', 'POST'])
def display_ready_videos():
    admin = db.session.query(Role).filter_by(name='admin').scalar()

    back_video_uuid = request.args.get('video_uuid')
    published = db.session.query(YoutubeVideoStage).filter_by(stage='published').scalar()
    all_video_ready_projects_shorts = [(a.uuid, a.temp_title, [c.text for c in a.components if c.component_type == 'video_id'][0]) for a in db.session.query(YoutubeVideo).all() if len([b for b in a.components if b.component_type == 'video_id']) > 0 and 'short' in a.category and published not in a.stages]
    all_video_ready_projects_longs = [(a.uuid, a.temp_title, [c.text for c in a.components if c.component_type == 'video_id'][0]) for a in db.session.query(YoutubeVideo).all() if len([b for b in a.components if b.component_type == 'video_id']) > 0 and 'long' in a.category and published not in a.stages]
    shorts_count = len(all_video_ready_projects_shorts)
    longs_count = len(all_video_ready_projects_longs)
    return render_template('display_ready_videos.html', all_video_ready_projects_shorts=all_video_ready_projects_shorts, all_video_ready_projects_longs=all_video_ready_projects_longs, back_video_uuid=back_video_uuid,
                           shorts_count=shorts_count, longs_count=longs_count, admin=admin, logged_in=current_user.is_authenticated, current_year=current_year)