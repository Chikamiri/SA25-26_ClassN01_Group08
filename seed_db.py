import sqlite3
import os
from werkzeug.security import generate_password_hash

def get_db_path(service_name, db_name):
    # Sử dụng cấu trúc thư mục thực tế của dự án
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'src', service_name, 'db', db_name)

def seed_users():
    print("Seeding Users...")
    db_path = get_db_path('user', 'users.db')
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Kiểm tra xem cột 'role' đã có chưa (Migration thủ công)
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'role' not in columns:
        print("  - Migrating: Adding 'role' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'customer'")

    # Bảng tokens cho user service
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    users = [
        ('user@example.com', 'password123', 'customer'),
        ('customer@gmail.com', 'customer123', 'customer'),
        ('admin@system.com', '111111', 'admin')
    ]
    
    for email, password, role in users:
        hashed = generate_password_hash(password)
        try:
            cursor.execute('INSERT INTO users (email, password, role) VALUES (?, ?, ?)', (email, hashed, role))
            print(f"  - Created {role}: {email}")
        except sqlite3.IntegrityError:
            print(f"  - User {email} already exists, skipping.")

    conn.commit()
    conn.close()

def seed_movies():
    print("Seeding Movies and Showtimes...")
    db_path = get_db_path('movie', 'movies.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Đảm bảo bảng khớp với MovieRepository
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT NOT NULL,
            duration INTEGER NOT NULL,
            release_date TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS showtimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            price INTEGER DEFAULT 50000,
            FOREIGN KEY(movie_id) REFERENCES movies(id)
        )
    ''')
    
    movies = [
        ("Inception", "Sci-Fi", 148, "2010-07-16"),
        ("The Dark Knight", "Action", 152, "2008-07-18"),
        ("Interstellar", "Adventure", 169, "2014-11-07")
    ]
    
    for title, genre, duration, release_date in movies:
        cursor.execute('SELECT id FROM movies WHERE title = ?', (title,))
        row = cursor.fetchone()
        if not row:
            cursor.execute('INSERT INTO movies (title, genre, duration, release_date) VALUES (?, ?, ?, ?)',
                           (title, genre, duration, release_date))
            movie_id = cursor.lastrowid
            print(f"  - Created movie: {title}")
        else:
            movie_id = row[0]
            print(f"  - Movie {title} already exists.")
            
        # Kiểm tra xem đã có showtime cho phim này chưa
        cursor.execute('SELECT id FROM showtimes WHERE movie_id = ?', (movie_id,))
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO showtimes (movie_id, start_time, end_time, price)
                VALUES (?, ?, ?, ?)
            ''', (movie_id, '2026-02-01 19:00', '2026-02-01 21:30', 80000))
            print(f"    + Created showtime for {title}")
            
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_users()
    seed_movies()
    print("\nDatabase seeding completed successfully!")