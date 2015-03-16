import json
from flask import request, Blueprint
from flask import render_template
from flask import jsonify
from flask.views import MethodView
from models import getRecommendations
from user.models import User, MovieRating
from movies.models import Movie, get_genre


recommend = Blueprint("recommend", __name__)

class RecommendView(MethodView):

    def json_decode(self, data, *args, **kwargs):
          return json.loads(data, *args, **kwargs)

    def get(self):
        data = request.args
        orig_user = User.objects.get(facebook_id=data.get("user_id"))
        friends = orig_user.friends

        movies = orig_user.movies
        data_structure = { orig_user.name: {}}
        for _m in movies:
            _each_m = _m.movie_id
            if _m.ratings:
                data_structure[orig_user.name][_each_m.title] = _m.ratings

        for f in friends:
            _obj = User.objects.get(facebook_id=int(f))

            movies = _obj.movies
            data_structure[_obj.name] = {}
            genre_arr = []
            for _m in movies:
                _each_m = _m.movie_id
                if _m.ratings:
                    data_structure[_obj.name][_each_m.title] = _m.ratings
                genre_arr.extend(_each_m.genre)

        #data_structure[_obj.name]["genre"] = orig_user.genre

        ret = getRecommendations(data_structure, orig_user.name)
        print ret
        return jsonify({"movies_rated": data_structure})

recommend.add_url_rule("/recommend", view_func=RecommendView.as_view('recommend'))
