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
