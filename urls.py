from application import BaseApp
from user.handler import user
from movies.handlers import movies

class Urls(BaseApp):
    def attach_urls(self):
        self.app.register_blueprint(user)
        self.app.register_blueprint(movies)
