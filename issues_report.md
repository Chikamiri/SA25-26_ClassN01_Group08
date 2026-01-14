# Project Issues Report

## 🔴 Critical Issues (Must Fix)

- [x] ### 1. System Stop Script Incompatible with Linux
    - **File:** `src/run_app.py`
    - **Issue:** The script uses `taskkill` (a Windows-specific command) to stop services. `venv` does not abstract OS-level process management commands.
    - **Impact:** On Linux (and macOS), pressing `Ctrl + C` will crash the stop script. The background services (Flask apps on ports 5000-5004) will **remain running**, requiring manual termination via `kill` commands.
    - **Fix Required:** Replace `taskkill` with Python's cross-platform `process.terminate()` or `process.kill()` methods.

- [ ] ### 2. Hardcoded Admin Backdoor
    - **File:** `src/user/app.py`
    - **Issue:** A hardcoded credential check exists: `if username == "admin" and password == "111111":`.
    - **Impact:** This bypasses database authentication. Anyone knowing these credentials has full admin access, regardless of the actual user records in the database.x
**Note: meh kệ cái này đi**

## 🟡 Major Issues (Should Fix)

- [x] ### 3. Database Path Resolution
    - **Files:**
        - `src/booking/persistence/booking_repository.py`
        - `src/movie/persistence/movie_repository.py`
        - `src/user/app.py`
    - **Issue:** Database paths are resolved relative to the file location (e.g., `os.path.join(os.path.dirname(__file__), '..', 'db')`).
    - **Impact:** If the application is started from a directory other than the expected one, it may create new, empty databases or fail to find existing ones. A consistent, absolute path configuration is safer.

- [ ] ### 4. Sensitive Information Leakage
    - **Files:**
        - `src/booking/app.py`
        - `src/movie/app.py`
        - `src/gateway/app.py`
    - **Issue:** API error handlers return raw exception strings directly to the client (`jsonify({"error": str(e)})`).
    - **Impact:** Attackers can see stack traces, internal variable names, or library versions, aiding in further exploitation.

- [ ] ### 5. Brittle Synchronous Service Communication
    - **Files:**
        - `src/payment/app.py`
        - `src/booking/business_logic/booking_service.py`
    - **Issue:** Services use `requests.get()` to make synchronous HTTP calls to other services (e.g., Payment calls Booking).
    - **Impact:** If the downstream service (e.g., Booking) is slow or offline, the calling service (e.g., Payment) will hang or crash. This creates a "domino effect" of failure.

## 🟢 Code Quality & Minor Issues

- [ ] ### 6. Hardcoded API Gateway Key
    - **File:** `src/gateway/app.py`
    - **Issue:** A default API key (`'BO_CHIKA'`) is hardcoded.
    - **Impact:** If the environment variable isn't set, the system defaults to this weak, known key.

- [ ] ### 7. Fragile Import System
    - **Files:** All `app.py` files (Service entry points).
    - **Issue:** The code uses `sys.path.append(...)` to resolve sibling directories.
    - **Impact:** This is non-standard Python practice ("hacky"). It makes testing, linting, and packaging difficult.

- [ ] ### 8. Hardcoded Configuration Strings
    - **Files:** Multiple service files.
    - **Issue:** Service URLs (e.g., `http://127.0.0.1:5001`) and RabbitMQ credentials are repeated as default strings across multiple files.
    - **Impact:** Changing a port or credential requires editing multiple files, increasing the risk of configuration mismatch.