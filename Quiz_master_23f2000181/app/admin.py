
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models import User, Subject, Chapter, Quiz, Question, Score
from app.models import Subject, Chapter, Quiz, Question
from app import db
from sqlalchemy.orm import joinedload

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
@login_required
def require_admin():
    
    print(f"Checking admin access for user: {current_user.email}, is_admin: {getattr(current_user, 'is_administrator', None)}")
    
    if not getattr(current_user, 'is_administrator', lambda: False)():
        flash('Admin access required', 'danger')
        return redirect(url_for('main.dashboard'))
    
@admin.route('/')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@admin.route('/add-subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Subject name is required', 'danger')
            return redirect(url_for('admin.add_subject'))
            
        new_subject = Subject(name=name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin.add_subject'))
    
    return render_template('admin/add_subject.html')

@admin.route('/add-chapter', methods=['GET', 'POST'])
def add_chapter():
    if request.method == 'POST':
        name = request.form.get('name')
        subject_id = request.form.get('subject_id')
        description = request.form.get('description')
        
        if not all([name, subject_id]):
            flash('Name and subject are required', 'danger')
            return redirect(url_for('admin.add_chapter'))
            
        new_chapter = Chapter(
            name=name,
            subject_id=subject_id,
            description=description
        )
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('admin.add_chapter'))
    
    subjects = Subject.query.all()
    return render_template('admin/add_chapter.html', subjects=subjects)

@admin.route('/upload-quiz', methods=['GET', 'POST'])
def upload_quiz():
    if request.method == 'POST':
        try:
            
            subject_id = request.form.get('subject_id')
            chapter_id = request.form.get('chapter_id')
            quiz_name = request.form.get('quiz_name', '').strip()
            time_duration = request.form.get('time_duration')
            question_count = request.form.get('question_count')
            
            if not all([subject_id, chapter_id, quiz_name, time_duration, question_count]):
                flash('All fields are required', 'danger')
                return redirect(url_for('admin.upload_quiz'))
            
            
            new_quiz = Quiz(
                name=quiz_name,  
                chapter_id=chapter_id,
                time_duration=time_duration
            )
            db.session.add(new_quiz)
            db.session.commit()
            
            
            for i in range(1, int(question_count) + 1):
                question_text = request.form.get(f'question_{i}', '').strip()
                correct_option = request.form.get(f'correct_{i}')
                
                if not question_text or not correct_option:
                    flash(f'Question {i} is incomplete', 'danger')
                    db.session.rollback()
                    return redirect(url_for('admin.upload_quiz'))
                
                question = Question(
                    quiz_id=new_quiz.id,
                    question_statement=question_text,
                    option1=request.form.get(f'option1_{i}', '').strip(),
                    option2=request.form.get(f'option2_{i}', '').strip(),
                    option3=request.form.get(f'option3_{i}', '').strip(),
                    option4=request.form.get(f'option4_{i}', '').strip(),
                    correct_option=correct_option
                )
                db.session.add(question)
            
            db.session.commit()
            flash('Quiz uploaded successfully!', 'success')
            return redirect(url_for('admin.upload_quiz'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('admin.upload_quiz'))
    
    subjects = Subject.query.all()
    return render_template('admin/upload_quiz.html', subjects=subjects)

@admin.route('/get-chapters/<subject_id>')
def get_chapters(subject_id):
    try:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        return jsonify({'chapters': [{'id': c.id, 'name': c.name} for c in chapters]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@admin.route('/manage-users')
def manage_users():
    users = User.query.all()
    return render_template('admin/manage_users.html', users=users)

@admin.route('/view-quizzes')
def view_quizzes():
    quizzes = Quiz.query.options(joinedload(Quiz.chapter)).all()
    return render_template('admin/view_quizzes.html', quizzes=quizzes)

@admin.route('/view-all-scores')
def view_all_scores():
    scores = Score.query.options(
        joinedload(Score.user),
        joinedload(Score.quiz)
    ).all()
    return render_template('admin/view_all_scores.html', scores=scores)