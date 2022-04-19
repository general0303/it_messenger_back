# -*- coding: utf-8 -*-
import os
import uuid

from flask import request, jsonify, abort, send_file

from init import db, app
from models import User, Message, Attachment, Invitation, Chat
from datetime import datetime
from flask_jwt_extended import create_access_token, jwt_required, current_user


@app.route('/login', methods=['POST'])
def login():
    username = request.get_json()['username']
    password = request.get_json()['password']
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(400)
    elif user.check_password(password):
        access_token = create_access_token(identity={
            'id': user.id,
        }, expires_delta=False)
        user.last_seen = datetime.now()
        db.session.commit()
        result = {'token': access_token, 'id': user.id}
        return result
    else:
        abort(400)


@app.route('/registration', methods=['POST'])
def registration():
    username = request.get_json()['username']
    email = request.get_json()['email']
    password = request.get_json()['password']
    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    user = User.query.filter_by(username=username).first()
    access_token = create_access_token(identity={
        'id': user.id,
    }, expires_delta=False)
    result = {'token': access_token}
    return result


@app.route('/users/<user_id>', methods=['GET', 'PUT'])
@jwt_required()
def method_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'GET':
        data = {'username': user.username, 'email': user.email, 'last_seen': user.last_seen}
        current_user.last_seen = datetime.now()
        db.session.commit()
        return jsonify(data)
    else:
        username = str(request.form['username'])
        email = str(request.form['email'])
        password = str(request.form['password'])
        user.username = username
        user.email = email
        user.set_password(password)
        current_user.last_seen = datetime.now()
        db.session.commit()
        return 'Updated', 200


@app.route('/current_user')
@jwt_required()
def get_current_user():
    user = current_user
    data = {'username': user.username, 'email': user.email, 'last_seen': user.last_seen,
            'chats': [{'chat_id': chat.id, 'chat_name': chat.name, 'chat_image': chat.image, 'admin':
                {'username': chat.admin.username, 'email': chat.admin.email, 'last_seen': chat.admin.last_seen}}
                      for chat in user.chats]}
    invites = []
    for invite in current_user.invitations:
        chat = Chat.query.get(invite.chat_id)
        invites.append(
            {'invite_id': invite.id, 'chat_id': chat.id, 'chat_name': chat.name, 'chat_image': chat.image, 'admin':
                {'username': chat.admin.username, 'email': chat.admin.email, 'last_seen': chat.admin.last_seen}})
    data['invites'] = invites
    current_user.last_seen = datetime.now()
    db.session.commit()
    return jsonify(data)


@app.route('/chat', methods=['POST'])
@jwt_required()
def create_chat():
    name = request.form['name']
    chat = Chat(name=name)
    chat.users.append(current_user)
    chat.admin = current_user
    db.session.add(chat)
    current_user.last_seen = datetime.now()
    db.session.commit()
    chat = Chat.query.filter_by(name=name).first()
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != "":
            path = os.path.join(app.config['UPLOAD_FOLDER'], f'chats/{chat.id}')
            os.mkdir(path)
            filename = f'image.{file.filename.rsplit(".", 1)[1].lower()}'
            file.save(os.path.join(path, filename))
            chat_image = f'{path}/{filename}'
            chat.image = chat_image[2:].replace(r'\c', '/c')
            db.session.commit()
    return {'chat_id': chat.id}, 201


@app.route('/chats/<chat_id>', methods=['GET'])
@jwt_required()
def get_chat(chat_id):
    chat = Chat.query.get(chat_id)
    data = {'name': chat.name, 'image': chat.image, 'admin':
        {'username': chat.admin.username, 'email': chat.admin.email, 'last_seen': chat.admin.last_seen}}
    current_user.last_seen = datetime.now()
    db.session.commit()
    return jsonify(data)


@app.route('/chats/<chat_id>', methods=['PUT', 'DELETE'])
@jwt_required()
def method_chat(chat_id):
    chat = Chat.query.get(chat_id)
    if current_user != chat.admin:
        current_user.last_seen = datetime.now()
        db.session.commit()
        abort(403)
    if request.method == 'PUT':
        name = str(request.form['name'])
        chat.name = name
        current_user.last_seen = datetime.now()
        db.session.commit()
        return 'Updated', 200
    else:
        db.session.delete(chat)
        current_user.last_seen = datetime.now()
        db.session.commit()
        return 'Deleted', 204


@app.route('/chats/<chat_id>/left', methods=['DELETE'])
@jwt_required()
def left(chat_id):
    chat = Chat.query.get(chat_id)
    if current_user.id == chat.admin.id:
        abort(400)
    current_user.chats.remove(chat)
    db.session.commit()
    return 'deleted', 204


@app.route('/invitation', methods=['POST'])
@jwt_required()
def create_invitation():
    user_id = str(request.form['user_id'])
    chat_id = str(request.form['chat_id'])
    chat = Chat.query.get(chat_id)
    user = User.query.get(user_id)
    invitation = Invitation()
    invitation.user = user
    invitation.chat = chat
    db.session.add(invitation)
    current_user.last_seen = datetime.now()
    db.session.commit()
    return 'Created', 201


@app.route('/accept_the_invitation/<invitation_id>')
@jwt_required()
def accept_the_invitation(invitation_id):
    invitation = Invitation.query.get(int(invitation_id))
    invitation.user.chats.append(invitation.chat)
    db.session.delete(invitation)
    current_user.last_seen = datetime.now()
    db.session.commit()
    return 'Ok', 200


@app.route('/decline_the_invitation/<invitation_id>')
@jwt_required()
def decline_the_invitation(invitation_id):
    invitation = Invitation.query.get(invitation_id)
    db.session.delete(invitation)
    current_user.last_seen = datetime.now()
    db.session.commit()
    return 'Deleted', 200


@app.route('/users/<user_id>/chats')
@jwt_required()
def user_chat(user_id):
    user = User.query.get(user_id)
    data = [{'chat_id': chat.id, 'chat_name': chat.name, 'chat_image': chat.image, 'admin':
        {'username': chat.admin.username, 'email': chat.admin.email, 'last_seen': chat.admin.last_seen}}
            for chat in
            user.chats]
    current_user.last_seen = datetime.now()
    db.session.commit()
    return jsonify(data)


@app.route('/chats/<chat_id>/users')
@jwt_required()
def chat_user(chat_id):
    chat = Chat.query.get(chat_id)
    data = [{'user_id': user.id, 'username': user.username} for user in chat.users]
    current_user.last_seen = datetime.now()
    db.session.commit()
    return jsonify(data)


@app.route('/chats/<chat_id>/message', methods=['POST'])
@jwt_required()
def write_message(chat_id):
    chat = Chat.query.get(chat_id)
    user = current_user
    body = request.get_json()['body']
    message = Message(body=body)
    message.author = user
    message.chat = chat
    message.timestamp = datetime.now()
    db.session.add(message)
    current_user.last_seen = datetime.now()
    db.session.commit()
    return {'message_id': message.id}, 201


@app.route('/messages/<message_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def method_message(message_id):
    message = Message.query.get(message_id)
    if request.method == 'GET':
        data = {'author': {'username': message.author.username}, 'body': message.body, 'timestamp': message.timestamp}
        current_user.last_seen = datetime.now()
        db.session.commit()
        return jsonify(data)
    elif request.method == 'PUT':
        if current_user == message.author:
            body = str(request.form['body'])
            message.body = body
            current_user.last_seen = datetime.now()
            db.session.commit()
        return 'Updated', 200
    else:
        if current_user == message.author:
            db.session.delete(message)
            current_user.last_seen = datetime.now()
            db.session.commit()
        return 'Deleted', 204


@app.route('/chats/<chat_id>/messages')
@jwt_required()
def chat_messages(chat_id):
    chat = Chat.query.get(chat_id)
    data = [{'id': message.id, 'author': {'username': message.author.username}, 'body': message.body,
             'timestamp': message.timestamp, 'attachments': [{'link': attachment.path} for attachment in message.attachments]}
            for message in chat.posts]
    current_user.last_seen = datetime.now()
    db.session.commit()
    return jsonify(data)


@app.route('/static/chats/<chat_id>/image.png')
def image(chat_id):
    path = f'static/files/chats/{chat_id}/image.png'
    return send_file(path, mimetype='image/png')


@app.route('/create_attachment', methods=['POST'])
@jwt_required()
def create_attachment():
    chat_id = str(request.form['chat_id'])
    message = Message(body="")
    message.author = current_user
    message.chat = Chat.query.get(chat_id)
    db.session.add(message)
    db.session.commit()
    print(request.files.getlist('file'))
    if 'file' in request.files:
        for file in request.files.getlist('file'):
            if file.filename != "":
                path = os.path.join(app.config['UPLOAD_FOLDER'], f'chats/{chat_id}/messages')
                if not os.path.exists(path):
                    os.mkdir(path)
                path = os.path.join(app.config['UPLOAD_FOLDER'], f'chats/{chat_id}/messages/{message.id}')
                if not os.path.exists(path):
                    os.mkdir(path)
                filename = f'{uuid.uuid4().hex[0:10]}.{file.filename.rsplit(".", 1)[1].lower()}'
                file.save(os.path.join(path, filename))
                link = f'{path}/{filename}'
                link = link[2:].replace(r'\c', '/c')
                attachment = Attachment(path=link)
                db.session.add(attachment)
                attachment.message = message
            db.session.commit()
    return 'Created', 201


@app.route('/static/chats/<chat_id>/messages/<message_id>/<filename>')
def get_image(chat_id, message_id, filename):
    path = f'static/files/chats/{chat_id}/messages/{message_id}/{filename}'
    return send_file(path)
