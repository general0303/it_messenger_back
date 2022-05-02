from faker import Faker
import requests
import pytest

fake = Faker()


def get_token():
    return requests.post('http://localhost:5000/login', json={'username': 'user1', 'password': 'user1'}).json()['token']


class TestLogin:
    def test_valid_login(self):
        response = requests.post('http://localhost:5000/login', json={'username': 'user1', 'password': 'user1'})
        assert response.status_code == 200
        assert 'token' in response.json()

    def test_invalid_login(self):
        response = requests.post('http://localhost:5000/login', json={'username': 'user1345', 'password': 'user1'})
        assert response.status_code == 400


class TestRegistration:
    def test_valid_registration(self):
        profile = fake.simple_profile()
        username = profile['username']
        email = profile['mail']
        password = fake.word()
        response = requests.post('http://localhost:5000/registration', json={'username': username, 'email': email,
                                                                             'password': password})
        assert response.status_code == 201
        assert 'token' in response.json()

    def test_invalid_registration(self):
        profile = fake.simple_profile()
        username = 'user1'
        email = profile['mail']
        password = fake.word()
        response = requests.post('http://localhost:5000/registration', json={'username': username, 'email': email,
                                                                             'password': password})
        assert response.status_code == 400


class TestCurrentUser:
    def test_valid_current_user(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/current_user', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 200
        assert 'username', 'email' in response.json()
        assert 'last_seen', 'chats' in response.json()
        assert 'invites' in response.json()
        assert 'avatar' in response.json()

    def test_invalid_current_user(self):
        response = requests.get('http://localhost:5000/current_user')
        assert response.status_code == 401

    def test_valid_put_current_user(self):
        jwt_token = get_token()
        response = requests.put('http://localhost:5000/current_user', headers={'Authorization': f'Bearer {jwt_token}'},
                                data={'username': 'user1'})
        assert response.status_code == 200


class TestChat:
    def test_create(self):
        jwt_token = get_token()
        response = requests.post('http://localhost:5000/chat', headers={'Authorization': f'Bearer {jwt_token}'},
                                data={'name': fake.word()})
        assert response.status_code == 201
        assert 'chat_id' in response.json()

    def test_valid_get(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/chats/1', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 200
        assert 'name' in response.json()
        assert 'image' in response.json()
        assert 'admin' in response.json()

    def test_invalid_get(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/chats/11111111', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 404

    def test_valid_put(self):
        jwt_token = get_token()
        chat_id = requests.post('http://localhost:5000/chat', headers={'Authorization': f'Bearer {jwt_token}'},
                                 data={'name': fake.word()}).json()['chat_id']
        response = requests.put(f'http://localhost:5000/chats/{chat_id}', headers={'Authorization': f'Bearer {jwt_token}'},
                                data={'name': fake.word()})
        assert response.status_code == 200

    def test_invalid_put(self):
        jwt_token = get_token()
        response = requests.put('http://localhost:5000/chats/45',
                                headers={'Authorization': f'Bearer {jwt_token}'},
                                data={'name': fake.word()})
        assert response.status_code == 403

    def test_valid_delete(self):
        jwt_token = get_token()
        chat_id = requests.post('http://localhost:5000/chat', headers={'Authorization': f'Bearer {jwt_token}'},
                                 data={'name': fake.word()}).json()['chat_id']
        response = requests.delete(f'http://localhost:5000/chats/{chat_id}', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 204

    def test_invalid_delete(self):
        jwt_token = get_token()
        response = requests.delete('http://localhost:5000/chats/45',
                                headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 403

    def test_not_found_left(self):
        jwt_token = get_token()
        response = requests.delete('http://localhost:5000/chats/1111111/left',
                                   headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 404

    def test_admin_left(self):
        jwt_token = get_token()
        response = requests.delete('http://localhost:5000/chats/1/left',
                                   headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 400


class TestInvitation:
    def test_valid_create(self):
        token = requests.post('http://localhost:5000/login', json={'username': 'test_user', 'password': 'user'}).json()['token']
        response = requests.post(f'http://localhost:5000/invitation', headers={'Authorization': f'Bearer {token}'},
                                 json={'user_id': 1, 'chat_id': 55})
        assert response.status_code == 201


class TestUserChat:
    def test_valid_user_chat(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/users/1/chats', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 200

    def test_invalid_user_chat(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/users/111111111111/chats', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 404

    def test_valid_chat_users(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/chats/1/users', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 200

    def test_invalid_chat_users(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/chats/111111111/users', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 404


class TestMessage:
    def test_valid_write(self):
        jwt_token = get_token()
        response = requests.post('http://localhost:5000/chats/1/message', headers={'Authorization': f'Bearer {jwt_token}'},
                                json={'body': fake.sentences(nb=1)})
        assert response.status_code == 201
        assert 'message_id' in response.json()

    def test_invalid_write(self):
        jwt_token = get_token()
        response = requests.post('http://localhost:5000/chats/1111111111/message', headers={'Authorization': f'Bearer {jwt_token}'},
                                json={'body': fake.sentences(nb=1)})
        assert response.status_code == 404

    def test_valid_get(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/messages/1', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 200
        assert 'body' in response.json()
        assert 'author' in response.json()
        assert 'timestamp' in response.json()

    def test_invalid_get(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/messages/1111111', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 404

    def test_valid_put(self):
        jwt_token = get_token()
        message_id = requests.post(f'http://localhost:5000/chats/1/message',
                                 headers={'Authorization': f'Bearer {jwt_token}'},
                                 json={'body': fake.sentences(nb=1)}).json()['message_id']
        response = requests.put(f'http://localhost:5000/messages/{message_id}', headers={'Authorization': f'Bearer {jwt_token}'},
                                json={'body': fake.sentences(nb=1)})
        assert response.status_code == 200

    def test_invalid_put(self):
        jwt_token = get_token()
        response = requests.put('http://localhost:5000/messages/111111111', headers={'Authorization': f'Bearer {jwt_token}'},
                                json={'body': fake.sentences(nb=1)})
        assert response.status_code == 404

    def test_valid_delete(self):
        jwt_token = get_token()
        message_id = requests.post(f'http://localhost:5000/chats/1/message',
                                 headers={'Authorization': f'Bearer {jwt_token}'},
                                 json={'body': fake.sentences(nb=1)}).json()['message_id']
        response = requests.delete(f'http://localhost:5000/messages/{message_id}', headers={'Authorization': f'Bearer {jwt_token}'},
                                json={'body': fake.sentences(nb=1)})
        assert response.status_code == 204

    def test_invalid_delete(self):
        jwt_token = get_token()
        response = requests.delete('http://localhost:5000/messages/111111111', headers={'Authorization': f'Bearer {jwt_token}'},
                                json={'body': fake.sentences(nb=1)})
        assert response.status_code == 404

    def test_valid_chat_messages(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/chats/1/messages', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 200

    def test_invalid_chat_messages(self):
        jwt_token = get_token()
        response = requests.get('http://localhost:5000/chats/1111111/messages', headers={'Authorization': f'Bearer {jwt_token}'})
        assert response.status_code == 404


class TestFile:
    def test_valid_image(self):
        response = requests.get('http://localhost:5000/static/chats/2/image.png')
        assert response.status_code == 200

    def test_invalid_image(self):
        response = requests.get('http://localhost:5000/static/chats/2222222/image.png')
        assert response.status_code == 404

    def test_valid_avatar(self):
        response = requests.get('http://localhost:5000/static/users/2/image.png')
        assert response.status_code == 200

    def test_invalid_avatar(self):
        response = requests.get('http://localhost:5000/static/users/2222/image.png')
        assert response.status_code == 404

    def test_valid_file(self):
        response = requests.get('http://localhost:5000/static/chats/4/messages/2/25dad43eeb.py')
        assert response.status_code == 200

    def test_invalid_file(self):
        response = requests.get('http://localhost:5000/static/chats/4444/messages/2/25dad43eeb.py')
        assert response.status_code == 404
