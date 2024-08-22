from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = 'website/static/img'

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            #app_context(): to ensure that the database operations are performed within the application context.
            db.create_all()
        print('Created Database!') 

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'daisiyan205125'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    print(app.config['SQLALCHEMY_DATABASE_URI'])

    db.init_app(app)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix= '/')
    app.register_blueprint(auth, url_prefix= '/')

    from .models import User, Item, Comment
    
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
