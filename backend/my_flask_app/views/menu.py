from flask import Blueprint, jsonify, request
import sqlite3

menu_bp = Blueprint('menu', __name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('HTRMS.db')
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

@menu_bp.route('/menu')
def getItems():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Items;')
        rows = cursor.fetchall()  
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    items = [dict(row) for row in rows]
    
    return jsonify(items)

@menu_bp.route('/menu/add', methods=['POST'])
def addItem():
    data = request.get_json()
    hotel_id = data.get('hotel_id')
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')

    # Validate the input data
    if not hotel_id or not name or price is None:
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Insert the new item
        cursor.execute('''
        INSERT INTO Items (hotel_id, name, description, price) VALUES (?, ?, ?, ?);
        ''', (hotel_id, name, description, price))
        
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Item added successfully!'}), 201

@menu_bp.route('/menu/update', methods=['POST'])   
def update_item():
    # Get data from the request
    item_id = request.json.get('item_id')
    hotel_id = request.json.get('hotel_id')
    name = request.json.get('name')
    description = request.json.get('description')
    price = request.json.get('price')

    # Check if the required data is present
    if not item_id or not hotel_id or not name or price is None:
        return jsonify({'error': 'Missing data'}), 400

    # Connect to the database
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Update the item in the database where item_id matches
        cursor.execute('''
            UPDATE Items 
            SET hotel_id = ?, name = ?, description = ?, price = ?
            WHERE item_id = ?;
        ''', (hotel_id, name, description, price, item_id))
        
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Item updated successfully!'}), 200

@menu_bp.route('/menu/delete', methods=['POST'])
def delete_item():
    # Get item_id from the request
    item_id = request.json.get('item_id')

    # Check if the item_id is provided
    if not item_id:
        return jsonify({'error': 'Missing item_id'}), 400

    # Connect to the database
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        # Delete the item from the database where item_id matches
        cursor.execute('''
            DELETE FROM Items 
            WHERE item_id = ?;
        ''', (item_id,))
        
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Item not found'}), 404
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Item deleted successfully!'}), 200
