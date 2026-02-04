import sqlite3
import os
import datetime
import random
from werkzeug.security import generate_password_hash

# --- UTILS ---
def get_db_path(service_name, db_name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'src', service_name, 'db', db_name)

def get_connection(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

# --- SEED USERS ---
def seed_users():
    print("Seeding Users...")
    db_path = get_db_path('user', 'users.db')
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Check for 'role' column (Migration)
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'role' not in columns:
        print("  - Migrating: Adding 'role' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'customer'")

    # Tokens table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 1. The Single Admin
    users = [
        ('admin@system.com', '111111', 'admin'),
        ('user@example.com', 'password123', 'customer'), # Keep default test user
    ]

    # 2. Generate 50 Customers
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin"]

    for i in range(50):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
        users.append((email, 'password', 'customer'))
    
    count_new = 0
    for email, password, role in users:
        hashed = generate_password_hash(password)
        try:
            cursor.execute('INSERT INTO users (email, password, role) VALUES (?, ?, ?)', (email, hashed, role))
            count_new += 1
        except sqlite3.IntegrityError:
            pass # Skip if exists

    print(f"  - Processed {len(users)} users (Inserted new: {count_new})")
    conn.commit()
    conn.close()

# --- SEED MOVIES & SHOWTIMES ---
def seed_movies():
    print("Seeding Movies and Showtimes...")
    db_path = get_db_path('movie', 'movies.db')
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Tables
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
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            rows INTEGER NOT NULL,
            seats_per_row INTEGER NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS showtimes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            room_id INTEGER,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            price INTEGER DEFAULT 50000,
            FOREIGN KEY(movie_id) REFERENCES movies(id),
            FOREIGN KEY(room_id) REFERENCES rooms(id)
        )
    ''')

    # Migration Check
    cursor.execute("PRAGMA table_info(showtimes)")
    columns = [info[1] for info in cursor.fetchall()]
    if 'room_id' not in columns:
        cursor.execute("ALTER TABLE showtimes ADD COLUMN room_id INTEGER")
    if 'price' not in columns:
        print("  - Migrating: Adding 'price' column to showtimes table...")
        cursor.execute("ALTER TABLE showtimes ADD COLUMN price INTEGER DEFAULT 50000")

    # --- SEED ROOMS (Fixed Size 9x11) ---
    rooms = [
        ("Standard Hall 1", 9, 11),
        ("Standard Hall 2", 9, 11),
        ("Standard Hall 3", 9, 11),
        ("IMAX Hall 1", 9, 11),
        ("IMAX Hall 2", 9, 11),
        ("IMAX Hall 3", 9, 11),
    ]
    
    room_map = {} # name -> id
    for name, rows, seats in rooms:
        cursor.execute('SELECT id FROM rooms WHERE name = ?', (name,))
        row = cursor.fetchone()
        if not row:
            cursor.execute('INSERT INTO rooms (name, rows, seats_per_row) VALUES (?, ?, ?)', (name, rows, seats))
            print(f"  - Created Room: {name}")
            room_map[name] = cursor.lastrowid
        else:
            room_map[name] = row[0]

    # --- SEED MOVIES (~20) ---
    movies_data = [
        ("Inception", "Sci-Fi", 148, "2010-07-16"),
        ("The Dark Knight", "Action", 152, "2008-07-18"),
        ("Interstellar", "Adventure", 169, "2014-11-07"),
        ("The Matrix", "Sci-Fi", 136, "1999-03-31"),
        ("Avengers: Endgame", "Action", 181, "2019-04-26"),
        ("Parasite", "Drama", 132, "2019-05-30"),
        ("Spirited Away", "Animation", 125, "2001-07-20"),
        ("The Godfather", "Crime", 175, "1972-03-24"),
        ("Pulp Fiction", "Crime", 154, "1994-10-14"),
        ("Forrest Gump", "Drama", 142, "1994-07-06"),
        ("Dune: Part Two", "Sci-Fi", 166, "2024-03-01"),
        ("Oppenheimer", "Biography", 180, "2023-07-21"),
        ("Barbie", "Comedy", 114, "2023-07-21"),
        ("Spider-Man: Across the Spider-Verse", "Animation", 140, "2023-06-02"),
        ("The Shawshank Redemption", "Drama", 142, "1994-09-23"),
        ("Schindler's List", "Biography", 195, "1993-11-30"),
        ("Fight Club", "Drama", 139, "1999-10-15"),
        ("Goodfellas", "Crime", 146, "1990-09-19"),
        ("The Silence of the Lambs", "Thriller", 118, "1991-02-14"),
        ("Seven Samurai", "Action", 207, "1954-04-26")
    ]
    
    today = datetime.date.today()
    created_showtimes = [] # List of (id, price, start_time_str)

    for title, genre, duration, release_date in movies_data:
        cursor.execute('SELECT id FROM movies WHERE title = ?', (title,))
        row = cursor.fetchone()
        if not row:
            cursor.execute('INSERT INTO movies (title, genre, duration, release_date) VALUES (?, ?, ?, ?)',
                           (title, genre, duration, release_date))
            movie_id = cursor.lastrowid
        else:
            movie_id = row[0]
            
        # --- SEED SHOWTIMES (Past & Future) ---
        # Generate schedule for Past 30 Days and Future 7 Days
        cursor.execute('SELECT count(*) FROM showtimes WHERE movie_id = ?', (movie_id,))
        count = cursor.fetchone()[0]
        
        # If we have less than ~100 showtimes for this movie, generate more
        if count < 50: 
            # Range: -30 to +7
            for day_offset in range(-30, 8): 
                current_date = today + datetime.timedelta(days=day_offset)
                
                # 2-3 shows per day per movie
                num_shows = random.randint(2, 3)
                start_hours = sorted(random.sample(range(9, 23), num_shows))
                
                for hour in start_hours:
                    minute = random.choice([0, 15, 30, 45])
                    start_dt = datetime.datetime.combine(current_date, datetime.time(hour, minute))
                    end_dt = start_dt + datetime.timedelta(minutes=duration)
                    
                    # Random Room
                    room_id = random.choice(list(room_map.values()))
                    
                    # Pricing logic
                    base_price = 50000
                    if "IMAX" in [k for k,v in room_map.items() if v == room_id][0]:
                        base_price = 100000
                    elif hour >= 18: # Peak hours
                        base_price = 70000
                    
                    cursor.execute('''
                        INSERT INTO showtimes (movie_id, room_id, start_time, end_time, price)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (movie_id, room_id, start_dt.strftime('%Y-%m-%d %H:%M'), end_dt.strftime('%Y-%m-%d %H:%M'), base_price))
                    
                    created_showtimes.append((cursor.lastrowid, base_price, start_dt.strftime('%Y-%m-%d %H:%M')))

    conn.commit()
    conn.close()
    print(f"  - Generated movies & showtimes (History: 30 days, Future: 7 days)")
    return created_showtimes

# --- SEED BOOKINGS ---
def seed_bookings(showtimes_info):
    # showtimes_info: list of (id, price, start_time)
    print("Seeding Bookings (Large History)...")
    
    # 1. Get Users
    user_db_path = get_db_path('user', 'users.db')
    u_conn = get_connection(user_db_path)
    users = [row['email'] for row in u_conn.execute('SELECT email FROM users WHERE role="customer"').fetchall()]
    u_conn.close()
    
    if not users:
        print("  - No customers found, skipping booking seed.")
        return

    # 2. Setup Booking DB
    bk_db_path = get_db_path('booking', 'booking.db')
    conn = get_connection(bk_db_path)
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            showtime_id INTEGER,
            seat_number TEXT,
            customer_email TEXT,
            amount INTEGER,
            status TEXT DEFAULT 'PENDING_PAYMENT'
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS seats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            showtime_id INTEGER,
            seat_number TEXT,
            status TEXT DEFAULT 'available',
            seat_type TEXT DEFAULT 'STANDARD',
            price_surcharge INTEGER DEFAULT 0,
            UNIQUE(showtime_id, seat_number)
        )
    ''')
    # Check Columns
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(seats)")
    cols = [c[1] for c in cursor.fetchall()]
    if 'seat_type' not in cols: conn.execute("ALTER TABLE seats ADD COLUMN seat_type TEXT DEFAULT 'STANDARD'")
    if 'price_surcharge' not in cols: conn.execute("ALTER TABLE seats ADD COLUMN price_surcharge INTEGER DEFAULT 0")
    conn.commit()

    # 3. Fetch Showtimes if not provided (re-query for safety)
    if not showtimes_info:
        mv_db_path = get_db_path('movie', 'movies.db')
        m_conn = get_connection(mv_db_path)
        # Fetch up to 2000 recent/future showtimes
        rows = m_conn.execute('SELECT id, price, start_time FROM showtimes ORDER BY id DESC LIMIT 2000').fetchall()
        showtimes_info = [(r['id'], r['price'], r['start_time']) for r in rows]
        m_conn.close()

    # 4. Generate ~2500 Bookings
    count = 0
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    
    for _ in range(2500): 
        if not showtimes_info: break
        
        sid, price, start_time = random.choice(showtimes_info)
        email = random.choice(users)
        
        # Determine Status based on date
        # If showtime is in past, it must be 'confirmed' (paid) to make sense for history
        # If future, can be Pending or Confirmed
        is_past = start_time < today_str
        
        if is_past:
            status = 'confirmed'
        else:
            status = random.choice(['confirmed', 'confirmed', 'PENDING_PAYMENT'])

        # Random Seat: Row A-I, Num 1-11
        row = chr(random.randint(65, 73)) # A-I
        num = random.randint(1, 11)
        seat_num = f"{row}{num}"
        
        # Calculate Price
        total_price = price
        seat_type = 'STANDARD'
        surcharge = 0
        
        # VIP Logic
        if row >= 'E' and row <= 'H' and 4 <= num <= 8:
            seat_type = 'VIP'
            surcharge = 20000
            total_price += surcharge
            
        # Check if seat taken in DB
        exist = conn.execute('SELECT 1 FROM seats WHERE showtime_id=? AND seat_number=? AND status="booked"', 
                             (sid, seat_num)).fetchone()
        
        if not exist:
            # 1. Update Seat
            conn.execute('''
                INSERT OR REPLACE INTO seats (showtime_id, seat_number, status, seat_type, price_surcharge)
                VALUES (?, ?, "booked", ?, ?)
            ''', (sid, seat_num, seat_type, surcharge))
            
            # 2. Insert Booking
            conn.execute('''
                INSERT INTO bookings (showtime_id, seat_number, customer_email, amount, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (sid, seat_num, email, total_price, status))
            count += 1

    conn.commit()
    conn.close()
    print(f"  - Created {count} bookings across {len(showtimes_info)} showtimes.")


if __name__ == "__main__":
    seed_users()
    new_showtimes = seed_movies()
    seed_bookings(new_showtimes)
    
    print("\nDatabase seeding completed successfully!")
