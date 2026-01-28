# Project Issues Report

## 🟢 Code Quality & Minor Issues

- [ ] ### 1. Search Performance (Frontend)
    - **File:** `frontend/src/pages/MoviesPage.js`
    - **Issue:** The search input triggers an API call on every single keystroke (`input` event) without any debounce (delay).
    - **Impact:** Fast typing will flood the backend with requests, potentially causing performance degradation.

- [ ] ### 2. Potential Data Mismatch (Frontend)
    - **File:** `frontend/src/pages/BookingsPage.js`
    - **Issue:** The booking success message expects specific fields (`response.movie`, `response.price`) that may not match the backend response structure exactly.
    - **Impact:** The success message may display "undefined" for the movie title or price.
