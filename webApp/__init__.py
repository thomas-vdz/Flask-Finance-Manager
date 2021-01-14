# -*- coding: utf-8 -*-
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login  import LoginManager
from flask_mail import Mail
from webApp.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager= LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'


mail = Mail()


def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)    
    from webApp.users.routes import users
    from webApp.posts.routes import posts
    from webApp.main.routes import main
    from webApp.errors.handlers import errors
    from webApp.mathpractice.routes import mathpractice
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(mathpractice)
    return app           

def reset_database(config_class = Config):
    app = Flask(__name__)
    db.init_app(app)
    db.drop_all()
    db.create_all()

def create_tables(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    db.create_all()
    
    
    
# Use this to create new tables out of application context in spyder in correct folder

'''
from webApp import create_app, db
app = create_app()
app.app_context().push()
db.init_app(app)
db.create_all()
'''    