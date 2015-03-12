from application import BaseApp
from user.handler import user

class Urls(BaseApp):
    def attach_urls(self):
        self.app.register_blueprint(user)
