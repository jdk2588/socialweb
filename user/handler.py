from flask import request, Blueprint
from flask import render_template
from flask.views import MethodView
from models import User


user = Blueprint("about", __name__)

class UserView(MethodView):

    def get(self):
        u = User(name = "Jaideep")
        u.save()
        return render_template('about.html')

user.add_url_rule("/", view_func=UserView.as_view('user'))
