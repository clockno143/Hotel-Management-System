import pytest
from flask import Flask
from views.slot import slot_bp
from unittest.mock import patch, MagicMock

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(slot_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_slots(client):
    with patch('views.slot.get_db_connection') as mock_conn:
        mock_conn.return_value = None
        response = client.get('/slot')
        assert response.status_code == 500
        assert response.json['error'] == 'Database connection failed'

def test_upsert_slots_success(client):
    with patch('views.slot.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Simulate successful upsert
        data = {
            'hotel_id': 1,
            'date': '2024-10-20',
            'time': '12:00',
            'noofslots': 5
        }
        response = client.post('/slot/upsert', json=data)
        assert response.status_code == 200
        assert response.json['message'] == 'Slot upsert operation completed successfully!'

def test_upsert_slots_missing_data(client):
    data = {
        'hotel_id': 1,
        'date': '2024-10-20'
    }
    response = client.post('/slot/upsert', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Missing data'

def test_book_slot_success(client):
    with patch('views.slot.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Simulate successful booking
        data = {
            'hotel_id': 1,
            'date': '2024-10-20',
            'time': '12:00'
        }
        response = client.post('/slot/book', json=data)
        assert response.status_code == 200
        assert response.json['message'] == 'Slot count decreased successfully'

def test_book_slot_missing_data(client):
    data = {
        'hotel_id': 1
    }
    response = client.post('/slot/book', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Missing data'

def test_book_slot_no_available(client):
    with patch('views.slot.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0  # Simulate no available slots
        data = {
            'hotel_id': 1,
            'date': '2024-10-20',
            'time': '12:00'
        }
        response = client.post('/slot/book', json=data)
        assert response.status_code == 400
        assert response.json['error'] == 'No available slots to reduce or invalid slot data'

def test_delete_slot_success(client):
    with patch('views.slot.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 1  # Simulate successful delete
        data = {
            'hotel_id': 1,
            'date': '2024-10-20',
            'time': '12:00'
        }
        response = client.post('/slot/delete', json=data)
        assert response.status_code == 200
        assert response.json['message'] == 'Slot deleted successfully'

def test_delete_slot_missing_data(client):
    data = {
        'hotel_id': 1
    }
    response = client.post('/slot/delete', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Missing data'

def test_delete_slot_not_found(client):
    with patch('views.slot.get_db_connection') as mock_conn:
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.rowcount = 0  # Simulate slot not found
        data = {
            'hotel_id': 1,
            'date': '2024-10-20',
            'time': '12:00'
        }
        response = client.post('/slot/delete', json=data)
        assert response.status_code == 404
        assert response.json['error'] == 'No slots found to delete or invalid slot data'

def test_get_slots_database_connection_error(client):
    with patch('views.slot.get_db_connection', return_value=None):
        response = client.get('/slot')
        assert response.status_code == 500
        assert response.json['error'] == 'Database connection failed'



