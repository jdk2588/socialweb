from application import BaseApp
from user.handler import user
from movies.handlers import movies
from recommend.handlers import recommend

class Urls(BaseApp):
    def attach_urls(self):
        self.app.register_blueprint(user)
        self.app.register_blueprint(movies)
        self.app.register_blueprint(recommend)
