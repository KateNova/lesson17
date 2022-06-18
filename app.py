from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from schemas import MovieSchema, DirectorSchema, GenreSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)


# создаем пространства имен для api
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

# создаем экземпляры класса MovieSchema
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

# создаем экземпляры класса DirectorSchema
director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

# создаем экземпляры класса GenreSchema
genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# создаем модели
class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


# делаем Class Based Views
@movie_ns.route('/')
class MoviesViews(Resource):

    def get(self):
        # добавляем фильтры
        if request.args.get('director_id', None) and request.args.get('genre_id', None):
            all_movies = db.session.query(Movie).\
                filter(Movie.director_id == request.args['director_id'], Movie.genre_id == request.args['genre_id'])
        elif request.args.get('director_id', None):
            all_movies = db.session.query(Movie).filter(Movie.director_id == request.args['director_id'])
        elif request.args.get('genre_id', None):
            all_movies = db.session.query(Movie).filter(Movie.genre_id == request.args['genre_id'])
        else:
            all_movies = db.session.query(Movie).all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        request_movie = request.json
        new_movie = Movie(**request_movie)
        with db.session.begin():
            db.session.add(new_movie)
        return "", 201


@movie_ns.route('/<int:mid>')
class MovieViews(Resource):

    def get(self, mid):
        try:
            movie = Movie.query.filter(Movie.id == mid).one()
            return movie_schema.dump(movie), 200
        except Exception as e:
            return "", 404

    def put(self, mid):
        try:
            with db.session.begin():
                movie = Movie.query.filter(Movie.id == mid).one()
                # запрос фильма по id
                for k, v in request.json.items():
                    setattr(movie, k, v)
                db.session.add(movie)
            return "movie updated successfully", 204
        except Exception as e:
            return e.__str__(), 500

    def delete(self, mid):
        try:
            with db.session.begin():
                movie = Movie.query.filter(Movie.id == mid).one()
                db.session.delete(movie)
            return "movie deleted successfully", 204
        except Exception as e:
            return e.__str__(), 500


@director_ns.route('/')
class DirectorsViews(Resource):

    def get(self):
        all_directors = Director.query.all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        request_director = request.json
        new_director = Director(**request_director)
        with db.session.begin():
            db.session.add(new_director)
        return "", 201


@director_ns.route('/<int:did>')
class DirectorViews(Resource):

    def get(self, did):
        try:
            director = Director.query.filter(Director.id == did).one()
            return director_schema.dump(director), 200
        except Exception as e:
            return "", 404

    def put(self, did):
        try:
            with db.session.begin():
                # запрос на режиссера по id
                director = Director.query.filter(Director.id == did).one()
                for k, v in request.json.items():
                    setattr(director, k, v)
                db.session.add(director)
            return "director updated successfully", 204
        except:
            return jsonify({"content": "Что-то пошло не так"})

    def delete(self, did):
        try:
            with db.session.begin():
                director = Director.query.filter(Director.id == did).one()
                db.session.delete(director)
            return "director deleted successfully", 204
        except:
            return jsonify({"content": "Что-то пошло не так"})


@genre_ns.route('/')
class GenresViews(Resource):

    def get(self):
        all_genres = Genre.query.all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        request_genre = request.json
        new_genre = Genre(**request_genre)
        with db.session.begin():
            db.session.add(new_genre)
        return "", 201


@genre_ns.route('/<int:gid>')
class GenreViews(Resource):

    def get(self, gid):
        try:
            genre = Genre.query.filter(Genre.id == gid).one()
            return genre_schema.dump(genre), 200
        except Exception as e:
            return "", 404

    def put(self, gid):
        try:
            with db.session.begin():
                # запрос жанра по id
                genre = Genre.query.filter(Genre.id == gid).one()
                for k, v in request.json.items():
                    setattr(genre, k, v)
                db.session.add(genre)
            return "genre updated successfully", 204
        except:
            return jsonify({"content": "Что-то пошло не так"})

    def delete(self, gid):
        try:
            with db.session.begin():
                genre = Genre.query.filter(Genre.id == gid).one()
                db.session.delete(genre)
            return "genre deleted successfully", 204
        except:
            return jsonify({"content": "Что-то пошло не так"})


if __name__ == "__main__":
    app.run()
