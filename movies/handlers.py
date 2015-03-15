import json
from flask import request, Blueprint
from flask import render_template
from flask import jsonify
from flask.views import MethodView
from models import Movie


movies = Blueprint("movies", __name__)

class MoviesView(MethodView):

    def json_decode(self, data, *args, **kwargs):
          return json.loads(data, *args, **kwargs)

    def get(self):
        return render_template('about.html')

    #def post(self):
    #    data = self.json_decode(request.data)
    #    access_token = data.get("access_token")
    #    f = Facebook(access_token)
    #    ret = f.profile()

    #    if not ret:
    #        return jsonify({"error": 400, "message": "Error in fetching data from FB. Try Again"})

    #    fb_id = ret.get("id")
    #    u, created_new = User.objects.get_or_create(facebook_id=fb_id)
    #    u.name = ret.get("name")
    #    movies = ret.get("movies").get("data")
    #    mov = [x.get("name") for x in movies]
    #    u.picture = ret.get("picture").get("data").get("url")
    #    u.movies = mov
    #    u.gender = ret.get("gender")
    #    u.save()
    #    return jsonify({"result": u})

    def put(self):
        data = self.json_decode(request.data)
        movie = Movie.objects.get(pk=data.get("_id"))
        pass

movies.add_url_rule("/movies", view_func=MoviesView.as_view('movies'))
