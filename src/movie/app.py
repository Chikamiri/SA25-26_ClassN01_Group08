import sys
import os
from flask import Flask, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from movie.business_logic.movie_service import MovieService

app = Flask(__name__)
movie_service = MovieService()


@app.route('/api/movies', methods=['POST'])
def create_movie():
    data = request.json
    try:
        input_id = data.get('id')
        
        movie_id = movie_service.add_movie(
            id=input_id,
            title=data['title'], 
            genre=data['genre'], 
            duration=data['duration'], 
            release_date=data['release_date']
        )
        return jsonify({"message": "Movie created successfully", "id": movie_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/movies', methods=['GET'])
def get_movies():
    query = request.args.get('query')
    if query:
        return jsonify(movie_service.search_movies(query)), 200
    return jsonify(movie_service.get_all_movies()), 200

@app.route('/api/movies/<movie_id>', methods=['GET'])
def get_movie_by_id(movie_id):
    movie = movie_service.movie_repo.get_movie(movie_id)
    if movie:
        return jsonify(movie.to_dict()), 200
    return jsonify({"error": "Movie not found"}), 404

@app.route('/api/movies/<movie_id>', methods=['PUT'])
def update_movie(movie_id):
    data = request.json
    try:
        result = movie_service.update_movie(movie_id, data['title'], data['genre'], data['duration'], data['release_date'])
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
    movie_id = request.args.get('movie_id')
    return jsonify(movie_service.get_all_showtimes(movie_id)), 200

@app.route('/api/showtimes/<showtime_id>', methods=['GET'])
def get_showtime_by_id(showtime_id):
    showtime = movie_service.movie_repo.get_showtime(showtime_id)
    if showtime:
        return jsonify(showtime.to_dict()), 200
    return jsonify({"error": "Showtime not found"}), 404

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
    print("Movie Service running on port 5001...")
    app.run(debug=True, port=5001)