import sqlite3
import uuid
import datetime
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

def get_db_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_folder = os.path.join(base_dir, 'db')
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
    
    # Migration: Check for role column
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'role' not in columns:
        print("[User Service] Migrating: Adding 'role' column to users table...")
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'customer'")

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

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
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

    conn = get_db_connection()
    # Kiểm tra email hoặc nếu username là 'admin' thì ánh xạ tới admin@system.com
    target_email = username
    if username == "admin":
        target_email = "admin@system.com"
        
    user = conn.execute('SELECT * FROM users WHERE email = ?', (target_email,)).fetchone()
    
    if not user or not check_password_hash(user['password'], password):
        conn.close()
        return jsonify({"error": "Invalid credentials"}), 401
    
    user_role = user['role']
    user_email = user['email']
    conn.close()

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
    app.run(debug=True, port=5004, host='0.0.0.0')