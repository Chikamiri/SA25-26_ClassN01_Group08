import sys
import os
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from movie.business_logic.movie_service import MovieService

app = Flask(__name__)
movie_service = MovieService()

@app.route('/api/movies', methods=['GET'])
def get_movies():
    return jsonify(movie_service.get_all_movies()), 200

@app.route('/api/movies/search', methods=['GET'])
def search_movies():
    keyword = request.args.get('query') 
    genre = request.args.get('genre')
    try:
        results = movie_service.search_movies(keyword, genre)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/movies', methods=['POST'])
def add_movie():
    data = request.json
    try:
        input_id = data.get('id') 
        
        id = movie_service.add_movie(
            id=input_id,
            title=data['title'], 
            genre=data.get('genre'), 
            duration=data['duration'], 
            release_date=data.get('release_date')
        )
        return jsonify({"message": "Movie created successfully", "id": id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/movies/<movie_id>', methods=['PUT'])
def update_movie(movie_id):
    data = request.json
    try:
        result = movie_service.update_movie(
            movie_id, 
            data['title'], 
            data.get('genre'), 
            data['duration'], 
            data.get('release_date')
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/movies/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    try:
        result = movie_service.delete_movie(movie_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/showtimes', methods=['GET'])
def get_showtimes():
    return jsonify(movie_service.get_all_showtimes()), 200

@app.route('/api/showtimes', methods=['POST'])
def add_showtime():
    data = request.json
    try:
        input_id = data.get('id')

        result = movie_service.add_showtime(
            id=input_id,
            movie_id=data['movie_id'],
            start_time=data['start_time'],
            end_time=data['end_time'],
            total_seats=data.get('total_seats', 50)
        )
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/showtimes/<showtime_id>', methods=['PUT'])
def update_showtime(showtime_id):
    data = request.json
    try:
        result = movie_service.update_showtime(showtime_id, data['start_time'], data['end_time'])
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/showtimes/<showtime_id>', methods=['DELETE'])
def delete_showtime(showtime_id):
    try:
        result = movie_service.delete_showtime(showtime_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    print("🎬 Movie Service running on port 5001...")
    app.run(debug=True, port=5001)