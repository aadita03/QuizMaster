from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Subject, Quiz, Score
from app import db, login_manager
from flask_login import current_user
import logging
from sqlalchemy.orm import joinedload  
from app.models import Chapter

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/')
def home():
    return render_template('home.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email').strip()
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return redirect(url_for('main.login'))
            
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password')
        
        if not all([full_name, email, username, password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('main.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('main.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
            return redirect(url_for('main.register'))
            
        try:
            new_user = User(
                full_name=full_name,
                email=email,
                username=username,
                password=generate_password_hash(password),
                is_admin=False  
            )
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'danger')
            
    return render_template('register.html')

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_administrator():
        return redirect(url_for('admin.admin_dashboard'))
    return render_template('dashboard.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/subjects')
@login_required
def subjects():
    subjects = Subject.query.all()
    return render_template('subjects.html', subjects=subjects)

@main.route('/quizzes')
@login_required
def quizzes():
    quizzes = Quiz.query.options(
        joinedload(Quiz.chapter).joinedload(Chapter.subject)
    ).all()
    return render_template('quizzes.html', quizzes=quizzes)

@main.route('/scores')
@login_required
def scores():
    scores = Score.query.options(
        joinedload(Score.quiz)
    ).filter_by(user_id=current_user.id).all()
    return render_template('scores.html', scores=scores)