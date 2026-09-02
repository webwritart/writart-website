from extensions import db


class YoutubeChannel(db.Model):
    __tablename__ = 'youtube_channel'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    channel_id = db.Column(db.String(100), unique=True)
    channel_name = db.Column(db.String(100), unique=True)
    handle = db.Column(db.String(100), unique=True)
    custom_url = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(100))
    description = db.Column(db.String(500))
    date_time = db.Column(db.String(50))
    videos = db.relationship('YoutubeVideo', backref='youtube_channel', lazy=True)

    def __repr__(self):
        return f"Channel name: {self.channel_name}, handle: {self.handle}, date_time: {self.date_time}"
    

class YoutubeVideo(db.Model):
    __tablename__ = 'youtube_video'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    video_yt_id = db.Column(db.String(100), unique=True)
    title = db.Column(db.String(100)) # auto generated type + serial number eg. short_001
    temp_title = db.Column(db.String(200)) #temporary title eg. Rajasik form of Batuka bhairava explained
    category = db.Column(db.String(50)) # eg tantra, occult, paranormal, tantra story, occult story, paranormal story etc.
    date_time = db.Column(db.String(50))
    status = db.Column(db.String(50)) # eg in-progress, completed, pending
    scheduled_date_time = db.Column(db.String(50))
    channel_id = db.Column(db.Integer, db.ForeignKey('youtube_channel.id'))
    components = db.relationship('YoutubeVideoComponent', backref='youtube_video', lazy=True)

    def __repr__(self):
        return f"Temporary title: {self.temp_title}, category: {self.category}, date_time: {self.date_time}"


class YoutubeVideoComponent(db.Model):
    __tablename__ = 'youtube_video_component'
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    component_type = db.Column(db.String(50)) # eg dialogue_&_narration, image, video, voice_recording, img_vid_instruction, editing_fx, thumbnail, seo, yt_card, upload_time, etc.
    subtype = db.Column(db.String(50)) # e.g. for seo, the subtypes are yt_title, yt_description, yt_keywords
    text = db.Column(db.Text) # text for dialogue_&_narration, img_vid_instruction, and other initial instructions excluding each video, image or any other work feedbacks
    file_path = db.Column(db.String(200)) # path for files like uplaoded images, videos, voice recordings, etc.
    feedback = db.Column(db.String(1000)) # feedback for each video, image or any other work
    approval_status = db.Column(db.String(50)) # eg pending, approved, rejected, revise, etc.
    date_time = db.Column(db.String(50))
    assigned_to_uuid = db.Column(db.String(500))  # uuid of the team member the task is assigned to
    last_assigned = db.Column(db.String(50)) # uuid of the team member who was last assigned this iteration
    scene = db.Column(db.String(50)) # applicable in case of video, eg. 1, 2, 3
    shot = db.Column(db.String(50)) # applicable in case of video, eg. A, B, C etc. | scene and shot together 1-A, 1-B, 2-A, 2-B etc.
    youtube_video_id = db.Column(db.Integer, db.ForeignKey('youtube_video.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    revisions = db.relationship('YoutubeVideoComponentRevision', backref='youtube_video_component')

    def __repr__(self):
        return f"Component type: {self.component_type}, subtype: {self.subtype}, date_time: {self.date_time}"


class YoutubeVideoComponentRevision(db.Model):
    __tablename__ = 'youtube_video_component_revision'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    version = db.Column(db.String(50))
    text = db.Column(db.Text) # applicable in case of revisions.
    file_path = db.Column(db.String(200)) # applicable in case of revisions.
    feedback = db.Column(db.String(1000)) # applicable in case of revisions.
    date_time = db.Column(db.String(50))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    youtube_video_component_id = db.Column(db.Integer, db.ForeignKey('youtube_video_component.id'))

    def __repr__(self):
        return f"Version: {self.version}, date_time: {self.date_time}"