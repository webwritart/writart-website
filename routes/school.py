from flask import Blueprint, render_template
from flask_login import current_user


school = Blueprint('school', __name__, static_folder='static', template_folder='templates')


@school.route('/')
def home():
    return render_template('courses.html', logged_in=current_user.is_authenticated)


@school.route('/classroom')
def classroom():
    all_recorded_video_urls = []
    vid_caption_list = []
    if current_user.is_authenticated:
        ws_list = current_user.participated
        ws_list.reverse()
        all_ws = ws_list
        for i in all_ws:
            nm = i.name
            topic = i.topic
            vid_list = [i.yt_p1_id, i.yt_p2_id, i.yt_p3_id, i.yt_p4_id]
            for n in range(len(vid_list)):
                if vid_list[n]:
                    part = f"Part-{n + 1}"
                    caption = f'{nm}-{topic} | {part}'
                    all_recorded_video_urls.append(vid_list[n])
                    vid_caption_list.append(caption)

    video_count = len(all_recorded_video_urls)

    return render_template('classroom.html', yt_vid_id_list=all_recorded_video_urls,
                           vid_caption_list=vid_caption_list, video_count=video_count,
                           logged_in=current_user.is_authenticated)