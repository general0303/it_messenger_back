import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'it-messenger'
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE') or 'mysql+pymysql://petr:byudUJgEG6pkmS20@195.19.44.146:3306/petr'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:pass@localhost:3306/messenger'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'it-messenger'
    UPLOAD_FOLDER = './static/files'
