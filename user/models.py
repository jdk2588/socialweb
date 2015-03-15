from application import BaseApp
from movies.models import Movie

con = BaseApp.access_db()

StringField = con.StringField
IntField = con.IntField
DateTimeField = con.DateTimeField
ListField = con.ListField
EmbeddedDocumentField = con.EmbeddedDocumentField
EmbeddedDocument = con.EmbeddedDocument
FloatField = con.FloatField
ReferenceField = con.ReferenceField

class MovieRating(EmbeddedDocument):
    movie_id = ReferenceField(Movie)
    ratings = FloatField()

class User(con.Document):
    name = StringField()
    facebook_id = IntField(unique=True)
    gender = StringField(choices=('F', 'M', '?'))
    created = DateTimeField()
    modified = DateTimeField()
    picture = StringField()
    friends = ListField()
    movies = ListField(EmbeddedDocumentField(MovieRating))
    genre = ListField()

    meta = {
        'collection': 'users',
    }

    def get_user(self, user_id, *args, **kwargs):
        user = User.objects.get(pk=user)
        return user

    def get_friends(self, user_id, *args, **kwargs):
        user = User.objects(__raw__={"_id": self.pk})
        return user.get("friends")

    def add_friend(self, user_id, *args, **kwargs):
        user = User.objects(__raw__={"_id": self.pk})
        user_friends = user["friends"]
        user_friends.append(user_id)
        user.save()

        return user.get("friends")

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
