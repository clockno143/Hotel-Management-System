from flask import Blueprint, jsonify, request
import sqlite3

slot_bp = Blueprint('slot', __name__)

def get_db_connection():
    try:
        conn = sqlite3.connect('HTRMS.db')
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

@slot_bp.route('/slot')
def getSlots():
    conn = get_db_connection()
    if conn is None:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Slots;')
        slots_data = cursor.fetchall()
    except sqlite3.Error as e:
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
    
    return jsonify(result)

@slot_bp.route('/slot/upsert', methods=['POST'])
def upsertSlots():
    data = request.json
    hotel_id = data.get('hotel_id')
    date = data.get('date')
    time = data.get('time')
    noofslots = data.get('noofslots')

    if not hotel_id or not date or not time or noofslots is None:
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    if conn is None:
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
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Slot upsert operation completed successfully!'})

@slot_bp.route('/slot/book', methods=['POST'])
def bookSlot():
    data = request.json
    hotel_id = data.get('hotel_id')
    date = data.get('date')
    time = data.get('time')

    if not hotel_id or not date or not time:
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    if conn is None:
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
            return jsonify({'error': 'No available slots to reduce or invalid slot data'}), 400
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Slot count decreased successfully'}), 200

@slot_bp.route('/slot/delete', methods=['POST'])
def delSlot():
    data = request.json
    hotel_id = data.get('hotel_id')
    date = data.get('date')
    time = data.get('time')

    if not hotel_id or not date or not time:
        return jsonify({'error': 'Missing data'}), 400

    conn = get_db_connection()
    if conn is None:
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
            return jsonify({'error': 'No slots found to delete or invalid slot data'}), 404
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

    return jsonify({'message': 'Slot deleted successfully'}), 200
