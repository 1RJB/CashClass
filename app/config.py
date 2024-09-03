import os
class Config:
    SECRET_KEY = "Th3W@yT0Financ1alLit3racy"
    DATABASE_NAME='invest.db'
    SQLALCHEMY_DATABASE_URI='sqlite:///'+DATABASE_NAME
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")