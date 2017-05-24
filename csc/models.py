from pymongo import MongoClient
import re

client = MongoClient()
db = client['csc']


def underscorize(txt):
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', txt).lower()


class MongoDbEntity:
    def __init__(self, json):
        self.json = json

    def __getattr__(self, item):
        return self.json[item] if item in self.json else None

    def __getitem__(self, name):
        return self.json[name]

    def __contains__(self, a):
        return a in self.json

    @classmethod
    def get_by_id(cls, id):
        if isinstance(id, str):
            collection_name, id = id.split()
            if collection_name == 'user':           return User(db.users.find_one(int(id)))
            if collection_name == 'competition':    return Competition(db.competitions.find_one(int(id)))
            if collection_name == 'club':           return Club(db.clubs.find_one(int(id)))
            raise Exception('Unexpected collection name: {}s'.format(collection_name))
        else:
            return cls(db[cls.collection_name + 's'].find_one({'_id': id}))

    @property
    def thumbnail(self):
        if 'image' in self.json:
            return '/static/{}-tn.png'.format(self.json['image'])


class Club(MongoDbEntity):
    collection_name = 'club'

    @property
    def school(self):
        return School(db.schools.find_one({'_id': self.school_id}))


class Company(MongoDbEntity):
    collection_name = 'company'


class Competition(MongoDbEntity):
    collection_name = 'competition'


class CompetitionHost(MongoDbEntity):
    collection_name = 'competition_host'


class Post(MongoDbEntity):
    collection_name = 'post'

    @property
    def sender(self):
        return self.get_by_id(self.json['sender_id'])

    @property
    def recipients(self):
        return [self.get_by_id(recipient_id) for recipient_id in self.json['recipient_ids']]


class School(MongoDbEntity):
    collection_name = 'school'

    def members(self, projection=None):
        return db.users.find({'school_ids': self.json['_id']}, projection)


class User(MongoDbEntity):
    collection_name = 'user'

    @property
    def clubs(self):
        return sorted([Club.get_by_id(club_id) for club_id in self.club_ids], key=lambda club: club.name)

    @property
    def school(self):
        return School(db.schools.find_one({'_id': self.school_ids[0]}))

    @property
    def schools(self):
        return sorted([School.get_by_id(school_id) for school_id in self.school_ids], key=lambda school: school.name)

    @staticmethod
    def get_by_email(email):
        return User(db.users.find_one({'email': email}))

    @property
    def to_posts(self):
        '''return the posts addressed to self and to all the clubs etc. of self'''
        recipient_ids = ['user {}'.format(self.json['_id'])]
        recipient_ids.extend(['club {}'.format(club_id) for club_id in self.json['club_ids']])
        posts = db.posts.find({'recipient_ids': {'$in': recipient_ids}}).sort('date', -1)
        return [Post(n) for n in posts]
