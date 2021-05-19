from flask import Flask
from .database import database

def create_app():
    
    app = Flask(__name__)
    
    app.config.from_object('config.DevelopmentConfig')
    
    database.init_app(app)
    
    return app

if __name__ == '__main__':
    create_app().run()