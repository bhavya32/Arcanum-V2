from flask import Flask
from application.config import Config
from application.database import db, login_manager

app = Flask(__name__, template_folder="templates")
app.config.from_object(Config)
app.secret_key = 'your_secret_key_here'
db.init_app(app)
login_manager.init_app(app)
app.app_context().push()

from application.controllers import *

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=8080)
