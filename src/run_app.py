import subprocess
import time
import os
import signal
import sys

services = [
    {"name": "Movie Service (Admin)",   "cmd": ["python", "movie/app.py"],   "port": 5001},
    {"name": "Booking Service (Customer)", "cmd": ["python", "booking/app.py"], "port": 5002},
    {"name": "API Gateway",             "cmd": ["python", "gateway/app.py"], "port": 5000},
]

processes = []

def start_services():
    print("Starting the entire system...")
    print("---------------------------------------")
    
    cwd = os.path.dirname(os.path.abspath(__file__))

    for service in services:
        print(f"   - Starting {service['name']}...")
        p = subprocess.Popen(service["cmd"], shell=True, cwd=cwd)
        processes.append(p)
        time.sleep(1)

    print("---------------------------------------")
    print("System is ready!")
    print("Please access: http://127.0.0.1:5000")
    print("Press Ctrl + C to stop all.")

def stop_services():
    print("\n\nStopping the system...")
    for p in processes:
        try:
            subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
        except Exception:
            pass
    print("Exiting...")

if __name__ == "__main__":
    try:
        start_services()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_services()