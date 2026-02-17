import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import subprocess
import time
import socket
import glob
from tests.base import Colors, SERVICES_CONFIG

def clean_databases():
    print(f"{Colors.YELLOW}[SETUP] Cleaning old database files...{Colors.RESET}")
    root_dir = os.getcwd()
    patterns = [
        os.path.join(root_dir, '*.db*'), 
        os.path.join(root_dir, 'instance', '*.db*'),
        os.path.join(root_dir, 'src', '**', '*.db*')
    ]
    for pattern in patterns:
        for db_file in glob.glob(pattern, recursive=True):
            try:
                os.remove(db_file)
                print(f" -> Deleted: {os.path.basename(db_file)}")
            except: pass

def wait_for_services(timeout=30):
    start = time.time()
    for name, config in SERVICES_CONFIG.items():
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if sock.connect_ex(('127.0.0.1', config['port'])) == 0: 
                    sock.close()
                    break
            except: pass
            if time.time() - start > timeout:
                print(f"{Colors.RED}[ERROR] Service {name} timed out!{Colors.RESET}")
                return False
            time.sleep(0.5)
    return True

def run_suite():
    # 0. Create logs folder
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # 1. Dọn dẹp
    clean_databases()
    
    # 2. Khởi động Services
    print(f"\n{Colors.BOLD}{Colors.HEADER}>>> STARTING SERVICES <<<{Colors.RESET}")
    processes = []
    log_files = []
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
    env['PYTHONUNBUFFERED'] = '1'
    python_exec = sys.executable

    for name, config in SERVICES_CONFIG.items():
        full_path = os.path.join(*config['path'].split('/'))
        print(f" -> Launching {name.upper()}...")
        
        out_log = open(f"logs/{name}_out.log", "w")
        err_log = open(f"logs/{name}_err.log", "w")
        log_files.extend([out_log, err_log])

        p = subprocess.Popen([python_exec, full_path], env=env, stdout=out_log, stderr=err_log)
        processes.append(p)

    # 3. Chờ Services
    print(f" -> {Colors.YELLOW}Waiting 12s for services...{Colors.RESET}")
    time.sleep(12)
    if not wait_for_services():
        for p in processes: p.terminate()
        sys.exit(1)
    
    print(f"{Colors.GREEN}[READY] Services are running.{Colors.RESET}\n")

    # 4. Chạy Test (Theo thứ tự mong muốn)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Load lần lượt để đảm bảo thứ tự User -> Movie -> Booking -> Payment
    suite.addTests(loader.loadTestsFromName('tests.user.test_user'))
    suite.addTests(loader.loadTestsFromName('tests.movie.test_movie'))
    suite.addTests(loader.loadTestsFromName('tests.booking.test_booking'))
    suite.addTests(loader.loadTestsFromName('tests.payment.test_payment'))

    runner = unittest.TextTestRunner(verbosity=2, failfast=False)
    result = runner.run(suite)

    # 5. Dọn dẹp
    print(f"\n{Colors.BOLD}{Colors.HEADER}>>> STOPPING SERVICES <<<{Colors.RESET}")
    for p in processes: p.terminate()
    for f in log_files: f.close()
    
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == '__main__':
    run_suite()