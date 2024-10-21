import pytest
import json
from flask import Flask
from views.menu import menu_bp, get_db_connection  # Import the connection function

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(menu_bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

# Ensure the database is properly set up for testing
@pytest.fixture(autouse=True)
def setup_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS Items (item_id INTEGER PRIMARY KEY AUTOINCREMENT, hotel_id INTEGER, name TEXT, description TEXT, price REAL);')
    cursor.execute('INSERT INTO Items (hotel_id, name, description, price) VALUES (1, "Test Item", "Test Description", 9.99);')  # Setup initial item
    conn.commit()
    conn.close()

def test_get_items(client):
    response = client.get('/menu')
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_add_item_success(client):
    data = {
        'hotel_id': 1,
        'name': 'Test Item 2',
        'description': 'Test Description 2',
        'price': 19.99
    }
    response = client.post('/menu/add', json=data)
    assert response.status_code == 201
    assert response.json['message'] == 'Item added successfully!'

def test_add_item_missing_data(client):
    data = {
        'hotel_id': 1,
        'name': 'Test Item'
    }
    response = client.post('/menu/add', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Missing data'

def test_update_item_success(client):
    data = {
        'item_id': 1,  # Assuming this ID exists
        'hotel_id': 1,
        'name': 'Updated Item',
        'description': 'Updated Description',
        'price': 19.99
    }
    response = client.post('/menu/update', json=data)
    assert response.status_code == 200
    assert response.json['message'] == 'Item updated successfully!'

def test_update_item_missing_data(client):
    data = {
        'item_id': 1,
        'hotel_id': 1,
        'name': 'Updated Item'
    }
    response = client.post('/menu/update', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Missing data'



def test_delete_item_missing_id(client):
    data = {}
    response = client.post('/menu/delete', json=data)
    assert response.status_code == 400
    assert response.json['error'] == 'Missing item_id'

def test_delete_item_not_found(client):
    data = {
        'item_id': 9999
    }
    response = client.post('/menu/delete', json=data)
    assert response.status_code == 404
    assert response.json['error'] == 'Item not found'


