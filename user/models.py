from application import BaseApp

con = BaseApp.access_db()

class User(con.Document):
    #  first_name = StringField()
    #  last_name = StringField()
    name = con.BinaryField()
    #  bio = StringField()
    #  facebook_id = IntField(unique=True)
    #  email = StringField()
    #  gender = StringField(choices=('F', 'M', '?'))
    #  birthday = DateTimeField()
    #  occupation = StringField()
    #  hometown = ReferenceField(City)
    #  currently_in = ReferenceField(City)
    #  location = GeoPointField()
    #  location_modified = DateTimeField()
    #  created = DateTimeField()
    #  modified = DateTimeField()
    #  details = EmbeddedDocumentField(UserDetails)
    #  password = StringField()
    #  picture = StringField()

    meta = {
         'collection': 'users',
    }

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
