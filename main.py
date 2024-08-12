from flask import Flask
from application import workers
from application.config import Config
from application.database import db
from application.cache_setup import cache
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = 'your_secret_key_here'
db.init_app(app)
cache.init_app(app)

app.app_context().push()
celery = workers.celery
celery.conf.update(broker_url="redis://localhost:6379/1", result_backend="redis://localhost:6379/2")
celery.Task = workers.ContextTask
from application.controllers import *

if __name__ == '__main__':
  app.run(host='0.0.0.0',port=8080)
