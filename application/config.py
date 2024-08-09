import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLITE_DB_DIR = basedir
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "lms.sqlite3")
    DEBUG = True
    CACHE_TYPE = 'RedisCache'
    CACHE_REDIS_HOST = 'localhost' 
    CACHE_REDIS_PORT = 6379
    CACHE_DEFAULT_TIMEOUT = 30
    CACHE_REDIS_DB = 3