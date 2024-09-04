from . import db 
from flask_login import UserMixin
from datetime import datetime

class Users(db.Model, UserMixin):
    def get_id(self):
        return self.email
    email = db.Column(db.String(100), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.png')  # Default image
    name = db.Column(db.String(20))
    username = db.Column(db.String(20), nullable=False)
    cash = db.Column(db.Float, nullable=False, default=10000.00)
    expenses = db.relationship('Expenses', backref='users')
    holdings = db.relationship("Holding", backref="users", lazy=True)
    transactions = db.relationship("Transaction", backref="users", lazy=True)


class Holding(db.Model):
    __tablename__ = "holdings"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(5), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.email"), nullable=False)

    def __repr__(self):
        return "<Holding %r>" % self.symbol

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(5), nullable=False)
    shares = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.email"), nullable=False)

    def __repr__(self):
        return "<Transaction %r>" % self.timestamp
    
class Expenses(db.Model):
    expense_id = db.Column(db.Integer, primary_key=True, nullable=False)
    type = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(120), nullable=False)
    date_purchase = db.Column(db.String(10), nullable = False) 
    amount = db.Column(db.Float, nullable = False)
    user = db.Column(db.String(100), db.ForeignKey('users.email'), nullable=False)

class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50), nullable=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.email'))  # Corrected ForeignKey reference

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category
        }

class QuizSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.email'), nullable=False)
    quiz_data = db.Column(db.Text, nullable=False)  # Store the quiz questions and answers as JSON
    score = db.Column(db.Integer, nullable=False)  # Store the user's score
    submitted_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<QuizSubmission {self.id}>'