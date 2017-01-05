import peewee
import datetime
import sys
from inspect import isclass

db = peewee.SqliteDatabase('csc.db', threadlocals=True)


class PeeweeModel(peewee.Model):
    # the following 2 items are defined so Eclipse doesn't complain
    # but they are overwritten by peewee
    DoesNotExist = None
    id = None

    class Meta:
        database = db





class School(PeeweeModel):
    name = peewee.CharField(index=True)
    city = peewee.CharField(index=True)
    state = peewee.CharField(index=True)


class User(PeeweeModel):
    name = peewee.CharField(index=True)
    creation_time = peewee.DateTimeField(default=datetime.datetime.now)
    school = peewee.ForeignKeyField(School, related_name='users')


class Club(PeeweeModel):
    name = peewee.CharField(index=True)


class UserClub(PeeweeModel):
    user = peewee.ForeignKeyField(User)
    club = peewee.ForeignKeyField(Club)


class SchoolClub(PeeweeModel):
    school = peewee.ForeignKeyField(School)
    club = peewee.ForeignKeyField(Club)


class Post(PeeweeModel):
    title = peewee.CharField()
    body = peewee.CharField()
    user = peewee.ForeignKeyField(School, related_name='user_posts')
    club = peewee.ForeignKeyField(School, related_name='club_posts')
    school = peewee.ForeignKeyField(School, related_name='school_posts')


class Attachments(PeeweeModel):
    filename = peewee.CharField()
    post = peewee.ForeignKeyField(Post, related_name='attachments')


def create_tables(drop_existing_tables):
    for name in dir(sys.modules[__name__]):
        cls = globals()[name]
        if isclass(cls) and issubclass(cls, PeeweeModel) and name != 'PeeweeModel':
            if drop_existing_tables:
                cls.drop_table(fail_silently=True)

            cls.create_table(fail_silently=True)


