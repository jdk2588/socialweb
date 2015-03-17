import json
from flask import request, Blueprint
from flask import render_template
from flask import jsonify
from flask.views import MethodView
from models import getRecommendations, transformPrefs
from user.models import User, MovieRating
from movies.models import Movie, get_genre


recommend = Blueprint("recommend", __name__)

class RecommendView(MethodView):

    def json_decode(self, data, *args, **kwargs):
          return json.loads(data, *args, **kwargs)

    def fallback_reco(self):
        data = request.args
        orig_user = User.objects.get(facebook_id=data.get("user_id"))
        friends = orig_user.friends

        movies = orig_user.movies
        data_st = {}
        for _m in movies:
            _each_m = _m.movie_id
            #if _m.ratings:
            data_st[orig_user.name] = {_each_m.title: _m.ratings or 0}

        user_mov = [x.movie_id.pk for x in movies]
        genre = orig_user.genre
        _all_genre = Movie.objects(
            __raw__={
                "genre": {"$in": genre},
                "average": {"$exists": True}}
        ).order_by("-average", "-count")

        data_st["average"] = {}
        for _one in _all_genre:
            data_st["average"][_one.title] = _one.average

        return getRecommendations(data_st, orig_user.name)

    def get(self):
        data = request.args
        orig_user = User.objects.get(facebook_id=data.get("user_id"))
        friends = orig_user.friends

        movies = orig_user.movies
        data_structure = { orig_user.name: {}}
        for _m in movies:
            _each_m = _m.movie_id
            data_structure[orig_user.name][_each_m.title] = _m.ratings or 0

        for f in friends:
            _obj = User.objects.get(facebook_id=int(f))

            movies = _obj.movies
            data_structure[_obj.name] = {}
            genre_arr = []
            for _m in movies:
                _each_m = _m.movie_id
                data_structure[_obj.name][_each_m.title] = _m.ratings or 0
                genre_arr.extend(_each_m.genre)

        #data_structure[_obj.name]["genre"] = orig_user.genre

        ret = getRecommendations(data_structure, orig_user.name)

        if not ret:
            ret = self.fallback_reco()

        return jsonify({"recommended_movies": ret})

recommend.add_url_rule("/recommend", view_func=RecommendView.as_view('recommend'))
