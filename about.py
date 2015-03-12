from flask import request, Blueprint
from flask import render_template
from flask.views import MethodView


about = Blueprint("about", __name__)

class AboutView(MethodView):

    def get(self):
        return render_template('about.html')

about.add_url_rule("/", view_func=AboutView.as_view('about'))
