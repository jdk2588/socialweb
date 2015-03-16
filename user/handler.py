import json
from flask import request, make_response, Blueprint
from flask import render_template
from flask import jsonify
from flask.views import MethodView
from facebook import Facebook
from models import User, MovieRating
from movies.models import Movie, get_genre


user = Blueprint("user", __name__)

class UserView(MethodView):

    def json_decode(self, data, *args, **kwargs):
          return json.loads(data, *args, **kwargs)

    def get(self):
        data = request.args
        orig_user = User.objects.get(facebook_id=data.get("user_id"))
        return jsonify({"user": orig_user})

    def put(self):
        data = self.json_decode(request.data)
        u = User.objects.get(facebook_id=data.get("user_id"))
        if data.get("follow"):
            to_f_id = data.get("follow").get("user_id")
            if not user_id:
                #raise Exception("No user_id to follow")
                return jsonify({"result": "No user_id to follow", "error": 412})

            if user_id == u.pk:
                return jsonify({"result": "Can not follow same user", "error": 412})

            user_fr = u.friends
            user_to_follow = User.objects.get(facebook_id=to_f_id)
            user_fr.append(user_to_follow.pk)
            u.friends=list(set(user_fr))
            u.save()
            return jsonify({"user_followed": user_id})

        elif data.get("rate"):
            m_id = data.get("rate").get("movie_id")
            if not m_id:
                #raise Exception("No movie_id to rate")
                return jsonify({"result": "No movie_id to rate", "error": 412})

            user_mov = u.movies
            user_genre = u.genre
            found=False
            rating = float(data.get("rate").get("rating") or 0)
            for i, _each in enumerate(user_mov):
                if str(_each.movie_id.pk) == m_id:
                    _each.ratings = rating
                    user_mov[i] = _each
                    tot_num = _each.movie_id.count * _each.movie_id.average
                    _each.movie_id.count = _each.movie_id.count + 1
                    _each.movie_id.average = round((tot_num + rating)/_each.movie_id.count, 2)
                    _each.movie_id.save()
                    found=True
                    break

            if not found:
                m = Movie.objects.get(pk=m_id)
                _mr = MovieRating(movie_id=m, ratings=rating)
                tot_num = m.count * m.average
                m.count = m.count + 1
                m.average = round((tot_num + rating)/m.count, 2)
                m.save()
                m.count = m.count+1
                user_mov.append(_mr)
                user_genre.extend(m.genre)
                u.genre = list(set(user_genre))

            u.movies = user_mov

            u.save()
            return jsonify({"movies_rated": user_mov})


    def post(self):
        data = self.json_decode(request.data)
        access_token = data.get("access_token")
        f = Facebook(access_token)
        _fb = f.profile()

        if not _fb:
            return jsonify({
                "error": 400,
                "message": "Error in fetching data from FB. Try Again"
            })

        fb_id = _fb.get("id")
        u, created_new = User.objects.get_or_create(facebook_id=fb_id)
        u.name = _fb.get("name")
        user_movies = u.movies
        movies = _fb.get("movies").get("data")
        mov = []
        u_genre = u.genre
        for x in movies:
            m, created_new = Movie.objects.get_or_create(title=x["name"])
            if not created_new:
                _mr = MovieRating(movie_id=m.pk)
                for um in user_movies:
                    if um.movie_id == m.pk:
                        mov.append(_mr)
                        break
                u_genre.extend(m.genre)
                mov.append(_mr)
                continue

            ret = get_genre(x.get("name"))
            _ret = {}
            if not ret.get("Response") == 'True':
                _mr = MovieRating(movie_id=m.pk)
                for um in user_movies:
                    if um.movie_id == m.pk:
                        mov.append(_mr)
                        break
                u_genre.extend(m.genre)
                mov.append(_mr)
                continue

            genre = str(ret["Genre"])
            votes = ret["imdbVotes"]
            votes = votes.replace(",","")
            genre = genre.split(", ")
            _ret["title"] = str(ret["Title"])
            _ret["genre"] = genre
            _ret["average"] = float(ret["imdbRating"])/2
            _ret["count"] = int(votes)
            m.average = _ret["average"]
            m.title = _ret["title"]
            m.genre = _ret["genre"]
            m.count = _ret["count"]
            m.save()
            _mr = MovieRating()
            _mr.movie_id = m.pk
            mov.append(_mr)
            u_genre.extend(_ret["genre"])

        u.picture = _fb.get("picture").get("data").get("url")
        u.movies = mov
        u.genre = list(set(u_genre))
        u.gender = _fb.get("gender")
        u.save()
        response = make_response(jsonify({"result": u}))
        response.set_cookie('cookie_name',value=fb_id)
        return response

user.add_url_rule("/user", view_func=UserView.as_view('user'))
