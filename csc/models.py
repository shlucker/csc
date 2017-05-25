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

    def image(self, image_type):
        """
        image_type can be:
        - thumbnail for a square logo
        - logo for a wide logo and text
        - cover for a photo
        """
        if 'image' in self.json:
            if image_type == 'thumbnail':
                return '/static/{}-tn.png'.format(self.json['image'])
            if image_type == 'logo':
                return '/static/{}-logo.png'.format(self.json['image'])
            if image_type == 'cover':
                return '/static/{}-cover.jpg'.format(self.json['image'])

    @property
    def address(self):
        fields = [self.json['street'],
                  self.json['city'],
                  str(self.json['zip']),
                  self.json['state']]
        fields = [field for field in fields if field]
        return ', '.join(fields)

    @property
    def schools(self):
        if 'school_ids' in self.json:
            return sorted([School.get_by_id(school_id) for school_id in self.school_ids],
                          key=lambda school: school.name)
        return []

    @property
    def to_posts(self):
        '''return the posts addressed to self and to all the clubs etc. of self'''
        recipient_ids = ['user {}'.format(self.json['_id'])]
        if 'club_ids' in self.json:
            recipient_ids.extend(['club {}'.format(club_id) for club_id in self.json['club_ids']])
        posts = db.posts.find({'recipient_ids': {'$in': recipient_ids}}).sort('date', -1)
        return [Post(n) for n in posts]


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
        return sorted(User(db.users.find({'school_ids': self.json['_id']}, projection)), key=lambda user: user.name)

    @property
    def clubs(self):
        return sorted([Club(club) for club in db.clubs.find({'school_id': self.json['_id']})],
                      key=lambda club: club.name)


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
