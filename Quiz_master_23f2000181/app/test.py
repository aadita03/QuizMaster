from app.models import User
admin = User.query.filter_by(email='admin@quizmaster.com').first()
print(admin.is_admin)  