from flask import render_template

class Handlers(object):

    @classmethod
    def about(self):
        return render_template('about.html')

    @classmethod
    def root(self):
        raise NotImplementedError

