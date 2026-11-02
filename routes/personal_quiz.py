from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from extensions import *
from operations.personal_quiz_brain import *
from models.member import *
from models.quiz import PersonalQuizChapter, PersonalQuizQuestion


personal_quiz = Blueprint('personal_quiz', __name__, static_folder='static', template_folder='templates/personal_quiz')

@personal_quiz.route('/', methods=['GET', 'POST'])
def home():
    admin = db.session.query(Role).filter_by(name='admin').one_or_none()
    if current_user.is_authenticated and admin in current_user.role:
        chapter_tuple_list = get_personal_quiz_chapters()
        return render_template('personal_quiz.html', current_year=current_year, logged_in=current_user.is_authenticated, chapter_tuple_list=chapter_tuple_list)
    else:
        return redirect(url_for('main.home'))


@personal_quiz.route('/add_chapter', methods=['POST'])
def add_chapter():
    if request.method == 'POST':
        chapter_name = request.form.get('name')
        chapter_category = request.form.get('category')
        chapter_subject = request.form.get('subject')
        chapter_file = request.files['file']

        new_chapter = PersonalQuizChapter(name=chapter_name, category=chapter_category, subject=chapter_subject)
        db.session.add(new_chapter)
        db.session.commit()

        chapter_id = db.session.query(PersonalQuizChapter).filter_by(name=chapter_name).first().id

        if chapter_file:
            file_data = chapter_file.read()

            try:
                content = file_data.decode('utf-8')
            except UnicodeDecodeError:
                content = file_data.decode('cp1252')

            for line in content.splitlines():
                parts = line.strip().split(';', 1)

                if len(parts) != 2:
                    continue

                question_data, answer_data = parts

                entry = PersonalQuizQuestion(
                    question=question_data, 
                    answer=answer_data, 
                    chapter_id=chapter_id
                    )
                db.session.add(entry)
            try:
                # Add all questions
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise e


        return jsonify({'success': 'success', 'message': 'Chapter added successfully.'})


@personal_quiz.route('/load_chapter', methods=['POST'])
def load_chapter():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        chapter_id = data.get('chapter_id')
        chapter_obj = db.session.query(PersonalQuizChapter).filter_by(id=chapter_id).first()
        chapter_name = chapter_obj.name if chapter_obj else "Unknown Chapter"
        top_score = chapter_obj.top_score if chapter_obj else "0"
        question_answer_list = [{'question': a.question,'answer': a.answer} for a in chapter_obj.questions] if chapter_obj else []

        return jsonify({'success': 'success', 'q_a_list': question_answer_list, 'chapter_name': chapter_name, 'top_score': top_score})


@personal_quiz.route('/update_top_score', methods=['POST'])
def update_top_score():
    if request.method == 'POST' and request.is_json:
        data = request.get_json()
        chapter_id = data.get('chapter_id')
        new_score = data.get('new_score')

        chapter_obj = db.session.query(PersonalQuizChapter).filter_by(id=int(chapter_id)).first()
        if chapter_obj:
            chapter_obj.top_score = new_score
            db.session.commit()
            return jsonify({'success': 'success', 'message': 'Top score updated successfully.'})
        else:
            return jsonify({'error': 'error', 'message': 'Chapter not found.'})