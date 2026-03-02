# Architectural Plan: Movie Poster Integration (Updated)

This document tracks the integration of movie posters into the system. Completed phases are marked, and new requirements for asset management have been added.

## ✅ Completed Phases

### 1. Phase 1: Movie Service (The Asset Owner)

The Movie Service now acts as the "Source of Truth" for movie metadata and physical assets.

- **Model:** Added `image_url` to `Movie` class and `to_dict` method.
- **Repository:** Updated SQLite schema to include `image_url TEXT` column and updated CRUD methods.
- **Service:** Updated business logic to handle the new field.
- **App:** Configured Flask to serve static files from `src/movie/resource/static`.

### 2. Phase 2: API Gateway (The Entry Point)

Encapsulation is maintained by routing all asset requests through the Gateway.

- **Proxy:** Added `@app.route('/api/movies/posters/<path:filename>')` to proxy requests to the Movie Service.

### 3. Phase 3: Frontend Implementation (The Presentation Layer)

- **Styling:** Added `.movie-poster` CSS utility for forced aspect-ratio (2:3) and `object-fit: cover`.
- **Pages:** Updated `MoviesPage.js`, `MovieDetailsPage.js`, and `AdminMoviesPage.js` to render posters.

### 4. Phase 4: Data Seeding

- **Script:** Updated `seed_db.py` to populate the database with correct filenames for existing movies.

---

## 🚀 New Phase 5: Asset Management & Fallbacks

To make the system robust and user-friendly, we are adding support for optional images and real-time uploads.

### 1. UI: Emoji Fallback (Conditional Rendering)

Instead of showing a broken image or placeholder, the frontend will detect missing `image_url` data and display the original emoji film style.

- **Logic:**
  - `if (movie.image_url)` -> Show `<img class="movie-poster">`.
  - `else` -> Show `<div class="movie-poster d-flex align-items-center justify-content-center bg-dark text-white"><h1 class="display-1">🎬</h1></div>`.

### 2. Service: Optional Image Support

- **Backend:** Ensure `image_url` remains `NULL` in the database if no image is provided.
- **API:** Update the Movie Service to handle "no-image" payloads gracefully.

### 3. Service: File Upload Endpoint

Enable administrators to upload posters directly to the server.

- **Movie Service (`src/movie/app.py`)**:
  - Add a POST route `/api/movies/upload` that accepts `multipart/form-data`.
  - Save the uploaded file into `src/movie/resource/static/`.
  - Return the saved filename to the frontend.
- **API Gateway (`src/gateway/app.py`)**:
  - Add a proxy route for the upload endpoint.

### 4. Admin UI: File Input

- **AdminMoviesPage.js**:
  - Replace the text input for `image_url` with a File Selection input.
  - When saving a movie, upload the file first, get the filename, and then save the movie record.

---

## 🏗 Architectural Benefits

- **Resilience:** The system looks professional even without data (emoji fallback).
- **Service Autonomy:** The Movie Service manages its own file storage.
- **User Experience:** Admins can manage the visual identity of the theater without touching the filesystem manually.
