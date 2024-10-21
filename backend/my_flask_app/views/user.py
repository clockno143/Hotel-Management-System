from flask import Blueprint, jsonify, request
import sqlite3
import bcrypt
import jwt
import datetime
import json

user_bp = Blueprint('user', __name__)
SECRET_KEY = 'your_secret_key_here'

def get_db_connection():
    try:
        conn = sqlite3.connect('HTRMS.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None


@user_bp.route('/user/signup', methods=['POST'])
def signup():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash, salt, role) VALUES (?, ?, ?, ?)',
                       (username, hashed_password, salt, "user"))
        conn.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username already exists'}), 409
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@user_bp.route('/user/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user is None:
            return jsonify({'error': 'Invalid username or password'}), 401

        stored_hash = user['password_hash']

        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return jsonify({'error': 'Invalid username or password'}), 401

        token = jwt.encode({
            'user_id': user['user_id'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=48)
        }, SECRET_KEY, algorithm='HS256')

        return jsonify({'token': token, 'role': user['role']}), 200
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@user_bp.route('/user/bookslot', methods=['POST'])
def book_slot():
    token = request.headers.get('Authorization')
  
    if not token:
        return jsonify({'error': 'Token is missing!'}), 401

    try:
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token!'}), 401

    data = request.get_json()
    booking_date = data.get('date')
    booking_time = data.get('time')

    if not booking_date or not booking_time:
        return jsonify({'error': 'Booking date and time are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO slotbookings (user_id, date, time) VALUES (?, ?, ?)',
                       (user_id, booking_date, booking_time))
        query = '''
            UPDATE Slots
            SET noofslots = noofslots - 1
            WHERE date = ? AND time = ?;
        '''
        cursor.execute(query, (booking_date, booking_time))
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Slot booked successfully!'}), 201

@user_bp.route('/user/placeorder', methods=['POST'])
def place_order():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Token is missing!'}), 401
    
    try:
        payload = jwt.decode(token[7:], SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired!'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token!'}), 401

    data = request.get_json()
    if not isinstance(data, list) or not all(['hotel_id' in item and 'item_id' in item and 'qty' in item for item in data]):
        return jsonify({'error': 'Invalid order data'}), 400

    items_json = []
    hotel_id = data[0]["hotel_id"]

    for ord in data:
        items_json.append({"user_id": user_id, "item_id": ord["item_id"], "qty": ord["qty"]})

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (user_id, items, hotel_id)
            VALUES (?, ?, ?)
        ''', (user_id, json.dumps(items_json), hotel_id))
        
        conn.commit()
        order_id = cursor.lastrowid
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Order placed successfully! Orderid:' + str(order_id)}), 201
