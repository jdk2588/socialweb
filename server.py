import settings
from flask import Flask
from urls import Urls

class Server(Urls):

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(self)

    def __call__(self, *args, **kwargs):
        self.attach_urls()
        self.app.run(host="0.0.0.0", port=9000, *args, **kwargs)

if __name__ == "__main__":
    app = Server()
    app(debug=settings.DEBUG)
