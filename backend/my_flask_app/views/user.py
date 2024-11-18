import logging
from flask import Blueprint, jsonify, request
import sqlite3
import bcrypt
import jwt
import datetime
import json
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

user_bp = Blueprint('user', __name__)
SECRET_KEY = 'ascxer2W'

# Constants for security
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 15  # in minutes

def get_db_connection():
    try:
        logging.info("Attempting to connect to the database...")
        conn = sqlite3.connect('HTRMS.db')
        conn.row_factory = sqlite3.Row
        logging.info("Database connection established.")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def is_account_locked(user):
    logging.debug(f"Checking if account is locked for user_id: {user['user_id']}")
    if user['failed_attempts'] >= MAX_FAILED_ATTEMPTS:
        lockout_time = datetime.datetime.strptime(user['lockout_time'], '%Y-%m-%d %H:%M:%S')
        if (datetime.datetime.now() - lockout_time).total_seconds() / 60 < LOCKOUT_DURATION:
            logging.warning(f"Account locked for user_id: {user['user_id']}")
            return True
    return False

def increment_failed_attempts(conn, user_id):
    logging.warning(f"Incrementing failed attempts for user_id: {user_id}")
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET failed_attempts = failed_attempts + 1, lockout_time = ? WHERE user_id = ?',
                   (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_id))
    conn.commit()

def reset_failed_attempts(conn, user_id):
    logging.info(f"Resetting failed attempts for user_id: {user_id}")
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET failed_attempts = 0, lockout_time = NULL WHERE user_id = ?', (user_id,))
    conn.commit()

def is_password_strong(password):
    logging.debug("Validating password strength.")
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'[0-9]', password):
        return False
    return True

@user_bp.route('/user/signup', methods=['POST'])
def signup():
    logging.info("Signup endpoint called.")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logging.warning("Missing username or password in signup.")
        return jsonify({'error': 'Username and password are required'}), 400

    if not is_password_strong(password):
        logging.warning("Password does not meet complexity requirements.")
        return jsonify({'error': 'Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, and a number.'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password_hash, salt, role, failed_attempts, lockout_time) VALUES (?, ?, ?, ?, 0, NULL)',
                       (username, hashed_password, salt, "user"))
        conn.commit()
        logging.info(f"User {username} registered successfully.")
        return jsonify({'message': 'User registered successfully'}), 201
    except sqlite3.IntegrityError:
        logging.error(f"Signup failed: Username {username} already exists.")
        return jsonify({'error': 'Username already exists'}), 409
    except sqlite3.Error as e:
        logging.error(f"Signup failed: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@user_bp.route('/user/signin', methods=['POST'])
def signin():
    logging.info("Signin endpoint called.")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logging.warning("Missing username or password in signin.")
        return jsonify({'error': 'Username and password are required'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user is None:
            logging.warning(f"Invalid login attempt: Username {username} not found.")
            return jsonify({'error': 'Invalid username or password'}), 401

        if is_account_locked(user):
            logging.warning(f"Login attempt for locked account: {username}.")
            return jsonify({'error': f'Account locked. Try again after {LOCKOUT_DURATION} minutes.'}), 403

        stored_hash = user['password_hash']

        if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            increment_failed_attempts(conn, user['user_id'])
            logging.warning(f"Invalid password attempt for user: {username}.")
            return jsonify({'error': 'Invalid username or password'}), 401

        reset_failed_attempts(conn, user['user_id'])

        token = jwt.encode({
            'user_id': user['user_id'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, SECRET_KEY, algorithm='HS256')

        logging.info(f"User {username} signed in successfully.")
        return jsonify({'token': token, 'role': user['role']}), 200
    except sqlite3.Error as e:
        logging.error(f"Signin failed: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Add similar logging for the other routes as shown above.

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
