from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///quizmaster.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'aadita03'  
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info' 
    
    with app.app_context():
        
        from app.routes import main
        from app.admin import admin
        app.register_blueprint(main)
        app.register_blueprint(admin, url_prefix='/admin')
        
        
        db.create_all()
        
        
        try:
            from app.models import User
            admin_email = os.environ.get('ADMIN_EMAIL') or 'admin@quizmaster.com'
            admin_password = os.environ.get('ADMIN_PASSWORD') or 'admin123'
            
            if not User.query.filter_by(email=admin_email).first():
                admin_user = User(
                    username='admin',
                    email=admin_email,
                    password=generate_password_hash(admin_password),
                    full_name='Admin User',
                    is_admin=True  
                )
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info("Admin user created successfully!")
        except Exception as e:
            app.logger.error(f"Error creating admin user: {str(e)}")
            db.session.rollback()
    
    return app