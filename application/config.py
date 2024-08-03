import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLITE_DB_DIR = basedir
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "lms.sqlite3")
    DEBUG = True