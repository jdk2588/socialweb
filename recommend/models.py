import requests
from pymongo import MongoClient
from application import BaseApp

con = BaseApp.access_db()

StringField = con.StringField
FloatField = con.FloatField
IntField = con.IntField
DateTimeField = con.DateTimeField
ListField = con.ListField


def get_genre(movie_name):
    host = "http://www.omdbapi.com/?t=%s" % movie_name
    response = requests.get(host)
    res = {}
    try:
        res = response.json()
    except (ValueError, AttributeError):
        self.logger.error("Problem getting from omdb")
        self.logger.error(response.body)
    finally:
        return res

class Movie(con.Document):
    average = FloatField()
    count = IntField()
    genre = ListField()
    title = StringField()
    int_id = IntField()

    meta = {
        'collection': 'movies_latest',
    }

    def get_movie(self, movie_id, *args, **kwargs):
        movie = Movie.objects.get(pk=movie)
        return movie

    def save(self, *args, **kwargs):
        super(Movie, self).save(*args, **kwargs)

    @staticmethod
    def get_movie_by_title(movie_title, genre):

        conn = MongoClient()
        db = conn["10m"]

        movie = movie_title.split(" ")
        _title = movie[0]
        if len(movie) > 1:
            if movie[0] in ("The", "the", "A", "a"):
                movie.pop()
            _title = movie[0] + " " + movie[1]

        movies = list(db.movies.find({"title":{"$regex":_title}, "genre": {"$in": genre}}))
        return movies
