from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import Subject, Chapter, Quiz, Question
from app import db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
@login_required
def require_admin():
    if not current_user.is_administrator():
        flash('Admin access required', 'danger')
        return redirect(url_for('main.dashboard'))

@admin.route('/upload-quiz', methods=['GET', 'POST'])
def upload_quiz():
    if request.method == 'POST':
        # Get form data
        subject_id = request.form.get('subject_id')
        chapter_id = request.form.get('chapter_id')
        quiz_name = request.form.get('quiz_name')
        time_duration = request.form.get('time_duration')
        
        # Create new quiz
        new_quiz = Quiz(
            chapter_id=chapter_id,
            time_duration=time_duration
        )
        db.session.add(new_quiz)
        db.session.commit()
        
        # Add questions
        for i in range(1, int(request.form.get('question_count')) + 1):
            question = Question(
                quiz_id=new_quiz.id,
                question_statement=request.form.get(f'question_{i}'),
                option1=request.form.get(f'option1_{i}'),
                option2=request.form.get(f'option2_{i}'),
                option3=request.form.get(f'option3_{i}'),
                option4=request.form.get(f'option4_{i}'),
                correct_option=request.form.get(f'correct_{i}')
            )
            db.session.add(question)
        
        db.session.commit()
        flash('Quiz uploaded successfully!', 'success')
        return redirect(url_for('admin.upload_quiz'))
    
    subjects = Subject.query.all()
    return render_template('admin/upload_quiz.html', subjects=subjects)

@admin.route('/get-chapters/<subject_id>')
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return {'chapters': [{'id': c.id, 'name': c.name} for c in chapters]}