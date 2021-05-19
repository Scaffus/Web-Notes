import os

class Config(object):
    
    DEBUG = False
    
    TESTING = False
    
    CSRF_ENABLED = True
    
    SECRET_KEY = '16a627a9-a69b-4b07-9836-5b8b32b1fdc0'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    
class ProductionConfig(Config):
    
    DEBUG = False
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class DevelopmentConfig(Config):
    
    ENV='development'
    
    DEVELOPMENT=True
    
    DEBUG=True
    
SQLALCHEMY_DATABASE_URI="sqlite:///development_database.db"