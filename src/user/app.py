import sqlite3
import uuid
import datetime
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db_connection():
    db_folder = os.path.join(os.path.dirname(__file__), 'db')
    if not os.path.exists(db_folder):
        os.makedirs(db_folder)
    
    conn = sqlite3.connect(os.path.join(db_folder, 'users.db'))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()


@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
        conn.commit()
        conn.close()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user_role = "customer"
    user_email = username

    if username == "admin" and password == "111111":
        user_role = "admin"
        user_email = "admin@system.com"
    
    else:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        user_role = "customer"
        user_email = user['email']

    token = str(uuid.uuid4()) 

    conn = get_db_connection()
    conn.execute('INSERT INTO tokens (token, email, role) VALUES (?, ?, ?)', (token, user_email, user_role))
    conn.commit()
    conn.close()
    
    return jsonify({
        "token": token,
        "role": user_role,
        "email": user_email
    })

@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    token = request.args.get('token')
    
    conn = get_db_connection()
    session = conn.execute('SELECT * FROM tokens WHERE token = ?', (token,)).fetchone()
    conn.close()

    if session:
        return jsonify({
            "valid": True,
            "email": session['email'],
            "role": session['role']
        })
    else:
        return jsonify({"valid": False}), 401

if __name__ == '__main__':
    print("User Service (Auth) running on port 5004...")
    app.run(debug=True, port=5004)