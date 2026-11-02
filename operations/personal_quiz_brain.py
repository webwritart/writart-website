from extensions import *
from models.quiz import PersonalQuizChapter


def get_personal_quiz_chapters():
    chapters = [(a.id, a.name) for a in PersonalQuizChapter.query.all()]
    return chapters