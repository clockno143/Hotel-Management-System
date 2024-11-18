from flask import Flask, render_template
from views.menu import menu_bp
from flask_cors import CORS
from views.slot import slot_bp
from views.user import user_bp
import sqlite3

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    
    return render_template('index.html')


app.register_blueprint(menu_bp)
app.register_blueprint(slot_bp)
app.register_blueprint(user_bp)


if __name__ == '__main__':
    app.run(debug=True)


