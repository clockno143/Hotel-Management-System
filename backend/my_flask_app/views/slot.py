import logging
from flask import Blueprint, jsonify, request
import sqlite3
import jwt
from functools import wraps
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

slot_bp = Blueprint('slot', __name__)

# Flask-Limiter Setup
limiter = Limiter(get_remote_address)

# Secret key for JWT encoding/decoding
SECRET_KEY = 'ascxer2W'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('HTRMS.db')
        conn.row_factory = sqlite3.Row
        logging.info("Database connection established successfully")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

# Token required decorator (Centralized Authentication)
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            logging.warning("Token is missing from the request headers")
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            # Assuming token format is 'Bearer <JWT>'
            token = token[7:]  # Remove the 'Bearer ' part
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            logging.info(f"Token validated for user with role: {payload['role']}")
            if payload['role'] != "admin":
                logging.warning("Invalid access attempt by non-admin user")
                return jsonify({'error': 'Invalid Access'}), 401
        except jwt.ExpiredSignatureError:
            logging.warning("Token has expired")
            return jsonify({'error': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            logging.error("Invalid token received")
            return jsonify({'error': 'Invalid token!'}), 401
        return func(payload, *args, **kwargs)
    return wrapper

# Route to get all slots
@slot_bp.route('/slot')
def getSlots():
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database while fetching slots")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Slots;')
        slots_data = cursor.fetchall()
        logging.info("Slots data fetched successfully from the database")
    except sqlite3.Error as e:
        logging.error(f"Error fetching slots data: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    result = {}
    for row in slots_data:
        row = dict(row)
        if row['date'] in result:
            result[row['date']][row['time']] = row['noofslots']
        else:
            result[row['date']] = {}
            result[row['date']][row['time']] = row['noofslots']

    logging.info("Slots data processed successfully")
    return jsonify(result)

# Route to upsert slot (Insert or Update slot data)
@slot_bp.route('/slot/upsert', methods=['POST'])
@token_required
def upsertSlots(payload):
    data = request.json
    hotel_id = data.get('hotel_id')
    date = data.get('date')
    time = data.get('time')
    noofslots = data.get('noofslots')
    
    if not hotel_id or not date or not time or noofslots is None:
        logging.warning("Missing data in the upsert request")
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database during slot upsert")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        query = '''
        INSERT OR REPLACE INTO Slots (slot_id, hotel_id, date, time, noofslots)
        VALUES (
            (SELECT slot_id FROM Slots WHERE hotel_id = ? AND date = ? AND time = ?),
            ?, ?, ?, ?
        );
        '''
        cursor.execute(query, (hotel_id, date, time, hotel_id, date, time, noofslots))
        conn.commit()
        logging.info(f"Slot upsert operation completed for hotel_id: {hotel_id}, date: {date}, time: {time}")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error during slot upsert: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Slot upsert operation completed successfully!'})

# Rate limiting for booking slot
@limiter.limit("5 per minute")
@slot_bp.route('/slot/book', methods=['POST'])
@token_required
def bookSlot(payload):
    data = request.json
    hotel_id = data.get('hotel_id')
    date = data.get('date')
    time = data.get('time')

    if not hotel_id or not date or not time:
        logging.warning("Missing data in the slot booking request")
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database during slot booking")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        query = '''
        UPDATE Slots
        SET noofslots = noofslots - 1
        WHERE hotel_id = ? AND date = ? AND time = ? AND noofslots > 0;
        '''
        cursor.execute(query, (hotel_id, date, time))
        conn.commit()

        if cursor.rowcount == 0:
            logging.warning(f"No available slots to reduce for hotel_id: {hotel_id}, date: {date}, time: {time}")
            return jsonify({'error': 'No available slots to reduce or invalid slot data'}), 400

        logging.info(f"Slot count decreased for hotel_id: {hotel_id}, date: {date}, time: {time}")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error during slot booking: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Slot count decreased successfully'}), 200

# Route to delete a slot
@slot_bp.route('/slot/delete', methods=['POST'])
@token_required
def delSlot(payload):
    data = request.json
    hotel_id = data.get('hotel_id')
    date = data.get('date')
    time = data.get('time')

    if not hotel_id or not date or not time:
        logging.warning("Missing data in the slot deletion request")
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database during slot deletion")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        query = '''
        DELETE FROM Slots
        WHERE hotel_id = ? AND date = ? AND time = ?;
        '''
        cursor.execute(query, (hotel_id, date, time))
        conn.commit()

        if cursor.rowcount == 0:
            logging.warning(f"No slots found to delete for hotel_id: {hotel_id}, date: {date}, time: {time}")
            return jsonify({'error': 'No slots found to delete or invalid slot data'}), 404

        logging.info(f"Slot deleted successfully for hotel_id: {hotel_id}, date: {date}, time: {time}")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error during slot deletion: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Slot deleted successfully'}), 200
