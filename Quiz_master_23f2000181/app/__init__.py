from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quizmaster.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'aadita03'  # In production, use a stronger key
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    with app.app_context():
        # Register blueprints
        from app.routes import main
        from app.admin import admin
        app.register_blueprint(main)
        app.register_blueprint(admin, url_prefix='/admin')
        
        # Create tables
        db.create_all()
        
        # Add admin user if not exists (safe version)
        try:
            from app.models import User
            from werkzeug.security import generate_password_hash
            
            if not User.query.filter_by(email='admin@quizmaster.com').first():
                admin_user = User(
                    username='admin',
                    email='admin@quizmaster.com',
                    password=generate_password_hash('admin123'),
                    full_name='Admin User',  # Required field
                    qualification='Admin',   # Optional but good to set
                    is_admin=True            # Critical for admin access
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Admin user created successfully!")
            else:
                print("ℹ️ Admin user already exists")
        except Exception as e:
            print(f"❌ Error creating admin user: {str(e)}")
            db.session.rollback()
    
    return app