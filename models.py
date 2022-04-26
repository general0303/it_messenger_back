"""
модуль models
"""

import pytz
from datetime import datetime
from init import db, jwt
from werkzeug.security import generate_password_hash, check_password_hash


# для русского языка сделать
# ALTER DATABASE messenger CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
# ALTER TABLE user CHANGE username username VARCHAR(191) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
class User(db.Model):
    """
    Таблица пользователя
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    messages = db.relationship('Message', backref='author', lazy='dynamic')
    admin_chats = db.relationship('Chat', backref='admin', lazy='dynamic')
    invitations = db.relationship('Invitation', backref='user', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.now(pytz.timezone('Europe/Moscow')))
    avatar = db.Column(db.String(64), default=None)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        """
        метод установки пароля
        :param password: пароль
        :type password: строка
        :return: ничего не возвращает
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        метод проверки пароля
        :param password: пароль
        :type password: строка
        :return: True или False
        """
        return check_password_hash(self.password, password)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(id=identity['id']).one_or_none()


class Message(db.Model):
    """
    таблица сообщений пользователей
    """
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(pytz.timezone('Europe/Moscow')))
    attachments = db.relationship('Attachment', backref='message', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))

    def __repr__(self):
        return '{}'.format(self.body)


class Invitation(db.Model):
    """
    таблица приглашений пользователей в чаты
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'))


user_chats = db.Table('user_chats',
                      db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                      db.Column('chat_id', db.Integer, db.ForeignKey('chat.id'))
                      )


class Chat(db.Model):
    """
    таблица чатов
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    users = db.relationship('User', secondary=user_chats, backref='chats')
    posts = db.relationship('Message', backref='chat', lazy='dynamic')
    invitations = db.relationship('Invitation', backref='chat', lazy='dynamic')
    image = db.Column(db.String(64), default=None)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(15), index=True)
    path = db.Column(db.String(64), index=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'))
