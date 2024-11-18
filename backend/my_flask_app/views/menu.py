from flask import Blueprint, jsonify, request
import sqlite3
import jwt
from functools import wraps
import logging
from bleach import clean

menu_bp = Blueprint('menu', __name__)

# Secret key for JWT encoding/decoding
SECRET_KEY = 'ascxer2W'

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection function

def get_db_connection():
    try:
        conn = sqlite3.connect('HTRMS.db')
        conn.row_factory = sqlite3.Row  # To access columns by name
        logging.info("Database connection established successfully")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

# Token required decorator (Authentication)
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            logging.warning("Token is missing from the request headers")
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            # Assuming token format is 'Bearer <JWT>'
            token = token[7:]  # Remove 'Bearer ' part
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

# Get all menu items
@menu_bp.route('/menu')
def getItems():
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database while fetching menu items")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Items;')
        rows = cursor.fetchall()
        logging.info("Menu items fetched successfully from the database")
    except sqlite3.Error as e:
        logging.error(f"Error fetching menu items: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    items = [dict(row) for row in rows]
    logging.info("Menu items processed successfully")
    return jsonify(items)

# Add a new item to the menu
from bleach import clean

@menu_bp.route('/menu/add', methods=['POST'])
@token_required
def addItem(payload):
    data = request.get_json()

    # Validate and sanitize inputs
    hotel_id = data.get('hotel_id')
    name = clean(data.get('name', '').strip(), strip=True)  # XSS prevention
    description = clean(data.get('description', '').strip(), strip=True)  # XSS prevention
    price = data.get('price')

    if not hotel_id or not isinstance(hotel_id, int) or hotel_id <= 0:
        return jsonify({'error': 'Invalid hotel_id'}), 400
    if not name or len(name) > 100:
        return jsonify({'error': 'Invalid name'}), 400
    if len(description) > 500:
        return jsonify({'error': 'Description too long'}), 400
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        return jsonify({'error': 'Invalid price'}), 400

    # Database connection and parameterized query
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Items (hotel_id, name, description, price) VALUES (?, ?, ?, ?);
        ''', (hotel_id, name, description, price))  # Prevents SQL injection
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': 'Failed to add the item.'}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Item added successfully!'}), 201

# Update an existing item in the menu
from bleach import clean

@menu_bp.route('/menu/update', methods=['POST'])
@token_required
def update_item(payload):
    logging.info("Update item endpoint called.")
    data = request.get_json()

    # Extract and validate inputs
    item_id = data.get('item_id')
    hotel_id = data.get('hotel_id')
    name = clean(data.get('name', '').strip(), strip=True)  # XSS prevention
    description = clean(data.get('description', '').strip(), strip=True)  # XSS prevention
    price = data.get('price')

    if not item_id or not isinstance(item_id, int) or item_id <= 0:
        logging.warning("Invalid or missing item_id in update item request.")
        return jsonify({'error': 'Invalid item_id'}), 400
    if not hotel_id or not isinstance(hotel_id, int) or hotel_id <= 0:
        logging.warning("Invalid or missing hotel_id in update item request.")
        return jsonify({'error': 'Invalid hotel_id'}), 400
    if not name or len(name) > 100:
        logging.warning("Invalid name provided in update item request.")
        return jsonify({'error': 'Name is required and must be under 100 characters.'}), 400
    if len(description) > 500:
        logging.warning("Description exceeds allowed length in update item request.")
        return jsonify({'error': 'Description must be under 500 characters.'}), 400
    if price is None or not isinstance(price, (int, float)) or price <= 0:
        logging.warning("Invalid price provided in update item request.")
        return jsonify({'error': 'Price must be a positive number.'}), 400

    # Database connection
    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database during item update.")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Use parameterized queries to update the item securely
        cursor.execute('''
            UPDATE Items 
            SET hotel_id = ?, name = ?, description = ?, price = ?
            WHERE item_id = ?;
        ''', (hotel_id, name, description, price, item_id))
        conn.commit()
        logging.info(f"Item updated successfully: {name} (item_id: {item_id})")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error during item update: {e}")
        return jsonify({'error': 'Failed to update the item.'}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Item updated successfully!'}), 200


# Delete an item from the menu
@menu_bp.route('/menu/delete', methods=['POST'])
@token_required
def delete_item(payload):
    item_id = request.json.get('item_id')

    if not item_id:
        logging.warning("Missing item_id in the delete item request")
        return jsonify({'error': 'Missing item_id'}), 400

    conn = get_db_connection()
    if conn is None:
        logging.error("Failed to connect to the database during item deletion")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Delete the item from the database
        cursor.execute('''
            DELETE FROM Items 
            WHERE item_id = ?;
        ''', (item_id,))
        conn.commit()

        if cursor.rowcount == 0:
            logging.warning(f"Item not found for deletion (item_id: {item_id})")
            return jsonify({'error': 'Item not found'}), 404

        logging.info(f"Item deleted successfully (item_id: {item_id})")
    except sqlite3.Error as e:
        conn.rollback()
        logging.error(f"Error during item deletion: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Item deleted successfully!'}), 200
