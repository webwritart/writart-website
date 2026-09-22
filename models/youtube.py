from extensions import db


video_stage = db.Table('video_stage',
    db.Column('youtube_video_id', db.Integer, db.ForeignKey('youtube_video.id')),
    db.Column('youtube_video_stage_id', db.Integer, db.ForeignKey('youtube_video_stage.id'))
    )

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
    storyboard_scenes = db.relationship('YoutubeVideoStoryboardScene', backref='video', lazy=True)
    stages = db.relationship('YoutubeVideoStage', secondary=video_stage, backref='youtube_video', lazy=True)

    def __repr__(self):
        return f"Temporary title: {self.temp_title}, category: {self.category}, date_time: {self.date_time}"

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "video_yt_id": self.video_yt_id,
            "title": self.title,
            "temp_title": self.temp_title,
            "category": self.category,
            "date_time": self.date_time,
            "status": self.status,
            "scheduled_date_time": self.scheduled_date_time,
            "storyboard_scenes": [storyboard_scene.to_dict() for storyboard_scene in self.storyboard_scenes]
        }

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


class YoutubeVideoStage(db.Model):
    __tablename__ = 'youtube_video_stage'

    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.String(50)) # all stages are: dialogue_&_narration, voice_recording, creative_instruction, creatives, video, thumbnail, yt_card, yt_title, yt_description, yt_tags, scheduled, released etc.
    description = db.Column(db.String(100))
    
    def __repr__(self):
        return f"Stage: {self.stage}, date_time: {self.date_time}"


class YoutubeVideoStoryboardScene(db.Model):
    __tablename__ = 'youtube_video_storyboard_scene'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    scene = db.Column(db.String(50))
    description = db.Column(db.String(500))
    youtube_video_id = db.Column(db.Integer, db.ForeignKey('youtube_video.id'))
    shots = db.relationship('YoutubeVideoStoryboardShot', backref='scene', lazy=True)

    def __repr__(self):
        return f"Scene: {self.scene}, Video ID: {self.youtube_video_id}"

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'scene': self.scene,
            'description': self.description,
            'shots': [shot.to_dict() for shot in self.shots]
        }


class YoutubeVideoStoryboardShot(db.Model):
    __tablename__ = 'youtube_video_storyboard_shot'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    shot = db.Column(db.String(50))
    storyboard_img_path = db.Column(db.String(200))
    dialogue_narration = db.Column(db.String(500))
    frame_direction = db.Column(db.String(200))
    creative_direction = db.Column(db.String(500))
    timing = db.Column(db.String(50))
    shot_type = db.Column(db.String(50))  # eg. image, video
    youtube_video_storyboard_scene_id = db.Column(db.Integer, db.ForeignKey('youtube_video_storyboard_scene.id'))
    creatives = db.relationship('YoutubeVideoCreative', backref='shot', lazy=True)

    def __repr__(self):
        return f"Shot: {self.shot}, Scene ID: {self.youtube_video_storyboard_scene_id}"

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'shot': self.shot,
            'storyboard_img_path': self.storyboard_img_path,
            'dialogue_narration': self.dialogue_narration,
            'frame_direction': self.frame_direction,
            'creative_direction': self.creative_direction,
            'timing': self.timing,
            'shot_type': self.shot_type,
            'creatives': [creative.to_dict() for creative in self.creatives]
        }


class YoutubeVideoCreative(db.Model):
    __tablename__ = 'youtube_video_creative'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    media_type = db.Column(db.String(50)) # eg. image, video
    media_path = db.Column(db.String(200))
    text = db.Column(db.String(500))
    status = db.Column(db.String(50)) # eg. pending, approved, rejected, revision-required
    date_time = db.Column(db.String(50))
    feedback = db.Column(db.String(1000))
    assigned_to_uuid = db.Column(db.String(500))  # uuid of the team member the task is assigned to
    last_assigned = db.Column(db.String(50)) # uuid of the team member who was last assigned this iteration
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    revisions = db.relationship('YoutubeVideoCreativeRevision', backref='youtube_video_creative')
    youtube_video_shot_id = db.Column(db.Integer, db.ForeignKey('youtube_video_storyboard_shot.id'))

    def __repr__(self):
        return f"Media type: {self.media_type}, Shot ID: {self.youtube_video_shot_id}"

    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'media_type': self.media_type,
            'media_path': self.media_path,
            'text': self.text,
            'status': self.status,
            'date_time': self.date_time,
            'feedback': self.feedback,
            'assigned_to_uuid': self.assigned_to_uuid,
            'last_assigned': self.last_assigned,
            'member_id': self.member_id,
            'revisions': [revision.to_dict() for revision in self.revisions]
        }


class YoutubeVideoCreativeRevision(db.Model):
    __tablename__ = 'youtube_video_creative_revision'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.Integer, unique=True)
    version = db.Column(db.String(50))
    text = db.Column(db.Text) # applicable in case of revisions.
    file_path = db.Column(db.String(200)) # applicable in case of revisions.
    feedback = db.Column(db.String(1000)) # applicable in case of revisions.
    date_time = db.Column(db.String(50))
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'))
    youtube_video_creative_id = db.Column(db.Integer, db.ForeignKey('youtube_video_creative.id'))

    def __repr__(self):
        return f"Version: {self.version}, date_time: {self.date_time}"