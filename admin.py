from flask import request, Blueprint
from flask import render_template
from flask.views import MethodView

admin = Blueprint("admin", __name__)

class AdminView(MethodView):

    def get(self):
        pass

admin.add_url_rule("/admin", view_func=AdminView.as_view('admin'))
