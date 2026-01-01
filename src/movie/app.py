import sys
import os
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from movie.business_logic.movie_service import MovieService

app = Flask(__name__)
movie_service = MovieService()

@app.route('/api/movies', methods=['POST'])
def add_movie():
    data = request.json
    try:
        movie_id = movie_service.create_movie(
            title=data['title'],
            genre=data.get('genre', 'Unknown'),
            duration=data['duration'],
            release_date=data.get('release_date', 'TBA')
        )
        return jsonify({"message": "Success", "id": movie_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/showtimes', methods=['POST'])
def add_showtime():
    data = request.json
    try:
        result = movie_service.create_showtime_with_seats(
            movie_id=data['movie_id'],
            start_time=data['start_time'],
            total_seats=data.get('total_seats', 50)
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    print("🎬 Movie/Admin Service running on port 5001...")
    app.run(debug=True, port=5001)