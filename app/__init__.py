from flask import Flask
from .config import Config
# TODO: import flask_sqlalchemy
# TODO: import flask_login
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from os import path
from flask_sqlalchemy import SQLAlchemy
from .utils import usd
from flask.cli import with_appcontext
import click
from .models import db, Flashcard
# TODO: declare sqlalchemy db here
db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    # Custom filter
    app.jinja_env.filters["usd"] = usd
    
    from .models import Users

    with app.app_context():
        # TODO: initialise sqlalchemy db here
        db.init_app(app)
        
        # TODO: create sqlalchemy db file
        if not path.exists(app.config['DATABASE_NAME']):
            db.create_all()
            print('Created Database!')
        
        csrf.init_app(app)


        # TODO: initialise loginmanager
        login_manager = LoginManager()
        login_manager.login_view = 'auth.login'
        login_manager.init_app(app)

        @login_manager.user_loader
        def load_user(id):
            return Users.query.get(id)


        from app.auth import auth
        from app.views import views
        from app.investing import investing

        app.register_blueprint(auth)
        app.register_blueprint(views)
        app.register_blueprint(investing)

    return app
