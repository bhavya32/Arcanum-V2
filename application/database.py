from flask_sqlalchemy import SQLAlchemy

engine = None
db = SQLAlchemy()

from flask_login import LoginManager
login_manager = LoginManager()