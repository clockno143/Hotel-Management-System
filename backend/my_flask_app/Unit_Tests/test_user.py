import pytest
import json
from flask import Flask
from views.user import user_bp
import sqlite3
import jwt
import bcrypt
import datetime
SECRET_KEY = 'your_secret_key_here'

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(user_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def setup_database():
    # Create a fresh database for each test
    conn = sqlite3.connect('HTRMS.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT,
            role TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS slotbookings (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            date TEXT,
            time TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            user_id INTEGER,
            items TEXT,
            hotel_id INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Slots (
            id INTEGER PRIMARY KEY,
            date TEXT,
            time TEXT,
            noofslots INTEGER
        )
    ''')
    conn.commit()
    yield
    cursor.execute('DROP TABLE users')
    cursor.execute('DROP TABLE slotbookings')
    cursor.execute('DROP TABLE orders')
    cursor.execute('DROP TABLE Slots')
    conn.commit()
    conn.close()

def create_expired_token(user_id, role):
    return jwt.encode({
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)
    }, 'your_secret_key_here', algorithm='HS256')

def test_signup_success(client, setup_database):
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    response = client.post('/user/signup', json=data)
    assert response.status_code == 201
    assert response.json['message'] == 'User registered successfully'

def test_signup_missing_data(client, setup_database):
    data = {
        'username': 'testuser'
    }
    response = client.post('/user/signup', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Username and password are required'

def test_signup_username_exists(client, setup_database):
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    client.post('/user/signup', json=data)
    response = client.post('/user/signup', json=data)
    assert response.status_code == 409
    assert response.json['error'] == 'Username already exists'

def test_signin_success(client, setup_database):
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    client.post('/user/signup', json=data)
    response = client.post('/user/signin', json=data)
    assert response.status_code == 200
    assert 'token' in response.json
    assert 'role' in response.json

def test_signin_invalid_credentials(client, setup_database):
    data = {
        'username': 'testuser',
        'password': 'wrongpassword'
    }
    response = client.post('/user/signin', json=data)
    assert response.status_code == 401
    assert response.json['error'] == 'Invalid username or password'

def test_signin_missing_data(client, setup_database):
    data = {
        'username': 'testuser'
    }
    response = client.post('/user/signin', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Username and password are required'

def test_book_slot_success(client, setup_database):
    signup_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    client.post('/user/signup', json=signup_data)
    signin_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    token_response = client.post('/user/signin', json=signin_data)
    token = token_response.json['token']

    # Set up initial data for booking slots
    conn = sqlite3.connect('HTRMS.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Slots (date, time, noofslots) VALUES (?, ?, ?)', ('2024-10-20', '12:00', 5))
    conn.commit()
    conn.close()

    data = {
        'date': '2024-10-20',
        'time': '12:00'
    }
    response = client.post('/user/bookslot', json=data, headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 201
    assert response.json['message'] == 'Slot booked successfully!'

def test_book_slot_missing_token(client, setup_database):
    data = {
        'date': '2024-10-20',
        'time': '12:00'
    }
    response = client.post('/user/bookslot', json=data)
    assert response.status_code == 401
    assert response.json['error'] == 'Token is missing!'

def test_book_slot_invalid_token(client, setup_database):
    data = {
        'date': '2024-10-20',
        'time': '12:00'
    }
    response = client.post('/user/bookslot', json=data, headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401
    assert response.json['error'] == 'Invalid token!'

def test_book_slot_token_expired(client):
    # Create a token that is already expired
    expired_token = jwt.encode({
        'user_id': 1,  # This should match a user in your test database
        'role': 'user',
        'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)  # Expired token
    }, SECRET_KEY, algorithm='HS256')

    data = {
        'date': '2024-10-20',
        'time': '12:00'
    }
    response = client.post('/user/bookslot', json=data, headers={'Authorization': 'Bearer ' + expired_token})
    assert response.status_code == 401
    assert response.json['error'] == 'Token has expired!'
    

def test_place_order_success(client, setup_database):
    signup_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    client.post('/user/signup', json=signup_data)
    signin_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    token_response = client.post('/user/signin', json=signin_data)
    token = token_response.json['token']

    order_data = [
        {
            'hotel_id': 1,
            'item_id': 1,
            'qty': 2
        },
        {
            'hotel_id': 1,
            'item_id': 2,
            'qty': 1
        }
    ]
    response = client.post('/user/placeorder', json=order_data, headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 201
    assert 'Orderid:' in response.json['message']

def test_place_order_missing_token(client, setup_database):
    order_data = [
        {
            'hotel_id': 1,
            'item_id': 1,
            'qty': 2
        }
    ]
    response = client.post('/user/placeorder', json=order_data)
    assert response.status_code == 401
    assert response.json['error'] == 'Token is missing!'

def test_place_order_invalid_data(client, setup_database):
    signup_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    client.post('/user/signup', json=signup_data)
    signin_data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    token_response = client.post('/user/signin', json=signin_data)
    token = token_response.json['token']

    order_data = {
        'hotel_id': 1,
        'item_id': 1,
        'qty': 2
    }
    response = client.post('/user/placeorder', json=order_data, headers={'Authorization': 'Bearer ' + token})
    assert response.status_code == 400
    assert response.json['error'] == 'Invalid order data'

