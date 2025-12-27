# Movie Ticket Booking System

This project is a Microservices-based Movie Ticket Booking System, currently transitioning from a Monolithic architecture. It consists of separate services for Movie Management and Ticket Booking.

## 🛠 Prerequisites

- Python 3.x
- `pip` (Python package manager)

## 🚀 Setup Guide

### 1. Create a Virtual Environment

Open your terminal in the project root directory and run:

```bash
# Linux / MacOS
python3 -m venv venv

# Windows
python -m venv venv
```

### 2. Activate the Virtual Environment

```bash
# Linux / MacOS
source venv/bin/activate
# fish shell
source venv/bin/activate.fish

# Windows (Command Prompt)
virtualenv\Scripts\activate.bat

# Windows (PowerShell)
virtualenv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🏗 Architecture & Services

The system is split into the following microservices:

| Service | Port | Description |
|---------|------|-------------|
| **Movie Service** | `5001` | Manages movie details (Title, Genre, Duration, etc.) |
| **Booking Service** | `5002` | Handles ticket bookings and reservations |

---

## 🧪 Testing

### 1. Automated Integration Tests

We have a built-in test script that sets up the environment, starts both services, runs a sequence of API tests, and verifies the responses.

**To run the automated tests:**

```bash
# Linux / MacOS
export PYTHONPATH=$(pwd)/src && python tests/test_api.py

# Windows (PowerShell) - Set PYTHONPATH first
$env:PYTHONPATH = "$(Get-Location)\src"; python tests/test_api.py
```

*You should see output indicating services starting, requests being made, and JSON responses.*

### 2. Manual Testing

You can also run the services manually and test them using `curl` or Postman.

#### Step 1: Start the Services

You need to open **two separate terminal windows** (one for each service). Don't forget to activate `venv` in both.

**Terminal 1 (Movie Service):**
```bash
# Linux / MacOS
export PYTHONPATH=$(pwd)/src && python src/movie/app.py

# Windows (PowerShell)
$env:PYTHONPATH = "$(Get-Location)\src"; python src/movie/app.py
```

**Terminal 2 (Booking Service):**
```bash
# Linux / MacOS
export PYTHONPATH=$(pwd)/src && python src/booking/app.py

# Windows (PowerShell)
$env:PYTHONPATH = "$(Get-Location)\src"; python src/booking/app.py
```

#### Step 2: Send Requests

**Create a Movie (Movie Service - Port 5001):**
```bash
curl -X POST http://127.0.0.1:5001/api/movies \
     -H "Content-Type: application/json" \
     -d '{
           "title": "Inception",
           "genre": "Sci-Fi",
           "duration": 148,
           "release_date": "2010-07-16"
         }'
```

**Get All Movies:**
```bash
curl http://127.0.0.1:5001/api/movies
```

**Create a Booking (Booking Service - Port 5002):**
```bash
curl -X POST http://127.0.0.1:5002/api/bookings \
     -H "Content-Type: application/json" \
     -d '{
           "user_name": "Alice",
           "showtime_id": "101",
           "seat_number": "A1",
           "price": 12.50
         }'
```

**Get Booking Details:**
```bash
# Replace <booking_id> with the ID returned from the previous step (e.g., 1)
curl http://127.0.0.1:5002/api/bookings/1
```
