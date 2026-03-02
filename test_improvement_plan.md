# Test Improvement Plan

## 1. Objective
Enhance the existing test suite to ensure comprehensive coverage of the microservices architecture, specifically targeting the API Gateway, Notification service, and administrative endpoints that are currently untested.

## 2. Identified Gaps
*   **API Gateway:** Zero test coverage for routing, API Key validation, and JWT authentication logic.
*   **Notification Service:** Zero test coverage for RabbitMQ event consumption and processing.
*   **Administrative Endpoints:** Missing coverage for user management, room management, and internal booking controls.
*   **Integration Strategy:** Current tests bypass the Gateway, failing to verify the system's primary entry point and security layer.

---

## 3. Implementation Phases

### Phase 1: API Gateway Integration Tests
*   **Target:** `src/gateway/app.py`
*   **Action:** Create `tests/gateway/test_gateway.py`.
*   **Test Cases:**
    *   Verify `401 Unauthorized` when the `peko-key` (API Key) is missing or invalid.
    *   Verify `401 Unauthorized` for protected routes when the `Authorization` bearer token is missing.
    *   Verify successful routing and header injection (`X-User-Email`, `X-User-Role`) when valid credentials are provided.
    *   Verify `403 Forbidden` when a `customer` attempts to access `admin` routes (e.g., `GET /api/users`).

### Phase 2: Notification Service Verification
*   **Target:** `src/notification/app.py`
*   **Action:** Implement unit and integration tests.
*   **Test Cases:**
    *   **Unit Tests:** Directly invoke the `callback` function with mock RabbitMQ properties/bodies to verify correct console output for `OrderPlacedEvent`, `INVOICE_PRINT`, etc.
    *   **Integration Tests:** (Requires RabbitMQ) Publish messages to `ticket_events` and `invoice_events` queues and verify the service processes them without crashing.

### Phase 3: Filling Service Coverage Gaps
*   **User Service:**
    *   Add tests for `GET /api/auth/verify` (Token validation).
    *   Add tests for `GET /api/users/me` (Profile retrieval).
    *   Add tests for Admin CRUD: `GET /api/users` and `PUT /api/users/<id>`.
*   **Movie Service:**
    *   Add tests for Room management: `GET /api/rooms` and `GET /api/rooms/<id>`.
*   **Booking Service:**
    *   Add tests for Internal/Admin routes: `GET /api/bookings` (all bookings) and `GET /api/bookings/showtime/<id>/customers`.

### Phase 4: Test Architecture Refactor
*   **Base Class Update (`tests/base.py`):**
    *   Modify `_req` to support routing through Port 5000 (Gateway) by default.
    *   Add helper methods for injecting required Gateway headers (`peko-key`).
*   **Test Runner Update (`tests/test_api.py`):**
    *   Include the Gateway and Notification services in the service startup/shutdown lifecycle.
    *   Update the `wait_for_services` check to include Port 5000.

---

## 4. Success Criteria
1.  All services (including Gateway and Notification) are verified during the `test_api.py` execution.
2.  Every public endpoint defined in `gateway/app.py` has at least one corresponding test case.
3.  Security logic (RBAC and API Keys) is empirically validated.
