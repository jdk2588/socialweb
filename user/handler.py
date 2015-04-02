import json
from flask import request, make_response, Blueprint
from flask import render_template
from flask import jsonify
from flask.views import MethodView
from facebook import Facebook
from models import User, MovieRating
from movies.models import Movie, get_genre
from recommend.models import getRecommendations, transformPrefs, sim_pearson


user = Blueprint("user", __name__)

class UserView(MethodView):

    def json_decode(self, data, *args, **kwargs):
          return json.loads(data, *args, **kwargs)

    def get(self):
        data = request.args
        user_id=data.get("user_id")
        if not user_id:
            return jsonify({"result": "Send user_id of signed in user", "error": 412})

        if data.get("all"):
           all_users = User.objects()

           data_structure = {}

           for _u in all_users:
               if _u.facebook_id == int(user_id):
                   orig_user = _u

               movies = _u.movies
               data_structure[str(_u.pk)] = {}
               for _m in movies:
                    _each_m = _m.movie_id
                    data_structure[str(_u.pk)][_each_m.title] = _m.ratings or 0

           ret = getRecommendations(data_structure, str(orig_user.pk), only_sim=True, similarity=sim_pearson)

           new = []
           for _u in all_users:
               if _u.facebook_id == int(user_id):
                   continue
               _u.sim_score = ret[str(_u.pk)]
               new.append(_u)

           return jsonify({"all_users": new})

        orig_user = User.objects.get(facebook_id=user_id)
        _obj = self.json_decode(orig_user.to_json())
        for i, _m in enumerate(_obj.get("movies")):
            _obj["movies"][i]["title"] = orig_user.movies[i].movie_id.title
            _obj["movies"][i]["_id"] = str(orig_user.movies[i].movie_id.pk)

        return jsonify({"user": _obj})

    def put(self):
        data = self.json_decode(request.data)
        u = User.objects.get(facebook_id=int(data.get("user_id")))
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
            movies_to_rate = data.get("rate")
            if not movies_to_rate:
                #raise Exception("No movie_id to rate")
                return jsonify({"result": "No movie_id to rate", "error": 412})

            if not isinstance(movies_to_rate, list):
                movies_to_rate = [movies_to_rate]

            user_mov = u.movies
            user_genre = u.genre
            found=False
            new_added = []
            already_present = []
            faltu_list = []
            purani_list = []
            for _each_movie in movies_to_rate: 
		m_id = _each_movie.get("movie_id")
		rating = float(_each_movie.get("rating") or 0)
            	for i, _each in enumerate(user_mov):

			if str(_each.movie_id.pk) == m_id:
                            already_present.append({"movie_id": m_id, "ratings": rating})
                            purani_list.append(m_id)
                if m_id not in purani_list and m_id not in faltu_list:
                            faltu_list.append(m_id)
                            new_added.append({"movie_id": m_id, "ratings": rating})


            for i in new_added:
		m = Movie.objects.get(pk=i.get("movie_id"))
		_mr = MovieRating(movie_id=m, ratings=i.get("ratings"))
                _mr.movie_title = _mr.movie_id.title
		tot_num = _mr.movie_id.count * _mr.movie_id.average
		_mr.movie_id.count = _mr.movie_id.count + 1
		_mr.movie_id.average = round((tot_num + i.get("ratings"))/_mr.movie_id.count, 2)
		_mr.movie_id.save()
		user_mov.append(_mr)
		user_genre.extend(m.genre)

            for i in already_present:
               for j, _each in enumerate(u.movies):
                        if str(_each.movie_id.pk) != i.get("movie_id"):
			   continue 
			m = Movie.objects.get(pk=i.get("movie_id"))
			_mr = _each#MovieRating(movie_id=m, ratings=i.get("ratings"))
                        _mr.ratings = i.get("ratings")
                        _mr.movie_title = _mr.movie_id.title
			tot_num = _mr.movie_id.count * _mr.movie_id.average
			_mr.movie_id.count = _mr.movie_id.count + 1
			_mr.movie_id.average = round((tot_num + i.get("ratings"))/_each.movie_id.count, 2)
			_mr.movie_id.save()
                        user_mov[j] = _mr
                        break;
	       user_genre.extend(m.genre)


	    u.genre = list(set(user_genre))

            u.movies = user_mov

            u.save()
            return jsonify({"movies_rated": user_mov})

        elif data.get("genre"):
            genre = data.get("genre") or []

            if not isinstance(genre, list):
                genre = [genre]

            genre.extend(u.genre)
            u.genre = list(set(genre))
            u.save()

            top_movies = Movie.objects(
                __raw__={"genre": {"$in": genre}}).order_by("-count", "-average").limit(20)
            return jsonify({"top_movies": top_movies})


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
        movies = (_fb.get("movies") or {}).get("data") or []
        mov = []
        u_genre = u.genre
        for x in movies:
            m, created_new = Movie.objects.get_or_create(title=x["name"])
            if not created_new:
                _mr = MovieRating(movie_id=m.pk)
                for um in user_movies:
                    _mr.movie_title = m.title
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
            _mr.movie_title = m.title
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
