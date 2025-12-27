from flask import Flask, request, jsonify
from movie.business_logic.movie_service import MovieService

app = Flask(__name__)
movie_service = MovieService()


@app.route('/api/movies', methods=['POST'])
def create_movie():
    data = request.json
    try:
        movie = movie_service.create_movie(
            title=data.get('title'),
            genre=data.get('genre'),
            duration=data.get('duration'),
            release_date=data.get('release_date')
        )
        return jsonify(movie.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    try:
        movie = movie_service.get_movie_details(movie_id)
        return jsonify(movie.to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.route('/api/movies', methods=['GET'])
def get_movies():
    movies = movie_service.get_all_movies()
    return jsonify([m.to_dict() for m in movies]), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
