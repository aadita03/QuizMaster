# QuizMaster
A short application of a quiz platform where students login, take up quizzes, check their scores and admins can set those tests
How to run the same
#First set up the virtual environment
	1.python -m venv venv
	2.venv\Scripts\activate 
#Run this to install the requirements
	1.pip install flask flask-sqlalchemy flask-migrate flask-login werkzeug
#Initialize the Database
	1.flask db init
	2.flask db migrate -m "Initial tables"
	3.flask db upgrade
#Run it
	1. python run.py
#Open browser and type this 
	1.http://localhost:5000
