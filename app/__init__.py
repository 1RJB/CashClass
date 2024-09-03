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


def create_sample_flashcards():
    sample_flashcards = [
        {"question": "What is a budget?", "answer": "A plan for managing income and expenses.", "category": "Finance"},
        {"question": "What is interest?", "answer": "The cost of borrowing money or the return on invested money.", "category": "Finance"},
        {"question": "What is a savings account?", "answer": "A bank account that earns interest on the money deposited.", "category": "Banking"},
    ]

    for card in sample_flashcards:
        new_card = Flashcard(
            question=card['question'],
            answer=card['answer'],
            category=card['category'],
            user_id="testuser@example.com"  # Replace with appropriate user_id
        )
        db.session.add(new_card)
    db.session.commit()
    click.echo("Sample flashcards added successfully!")
