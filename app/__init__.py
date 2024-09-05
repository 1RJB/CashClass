from flask import Flask
from .config import Config
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from os import path
from flask_sqlalchemy import SQLAlchemy
from .utils import usd
import os
db = SQLAlchemy()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__,static_folder=os.path.join(os.pardir, 'app/static'),  # Point to the static folder in the root
                template_folder='templates')
    app.config.from_object(config_class)
    # Custom filter
    app.jinja_env.filters["usd"] = usd
    
    from .models import Users

    with app.app_context():
        db.init_app(app)
        
        if not path.exists(app.config['DATABASE_NAME']):
            db.create_all()
            print('Created Database!')
        
        csrf.init_app(app)


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
