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
        assert response.status_code == 200
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

    def test_invalid_current_user(self):
        response = requests.get('http://localhost:5000/current_user')
        assert response.status_code == 401
