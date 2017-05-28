import sys
from pymongo import MongoClient
import re

db = MongoClient()['csc']


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
        """
        id can be an id or a list ["coll_name", id]
        If it is not a list, then the collection is collection_names[cls]
        """
        if isinstance(id, list):
            collection_name, id = id
            obj_class = collection_names[collection_name]
        else:
            obj_class = cls

        return obj_class(db[collection_names[obj_class]].find_one(id))

    @classmethod
    def get_by_ids(cls, ids):
        """
        ids is a list of ids
        Each id can be an id or a list ["coll_name", id]
        If the ids are not lists, then the collection is collection_names[cls]
        One query per collection is executed
        """
        ids_by_class = {}
        for id in ids:
            if isinstance(id, list):
                collection_name, id = id
                obj_class = collection_names[collection_name]
            else:
                obj_class = cls

            try:
                ids_by_class[obj_class].append(id)
            except KeyError:
                ids_by_class[obj_class] = [id]

        objects = []
        for obj_class in ids_by_class:
            json_docs = db[collection_names[obj_class]].find({'_id': {'$in': ids_by_class[obj_class]}})
            objects.extend([obj_class(json_doc) for json_doc in json_docs])

        return objects

    @classmethod
    def get_by_ids_on_field(cls, field_name, id):
        """
        Example: to find all the users with a 5 in the list of clubs:
            User.get_by_ids_on_field('club_ids', 5)
        """
        collection_name = collection_names[cls]
        json_docs = db[collection_name].find({id: {'$in': field_name}})
        return [cls(json_doc for json_doc in json_docs)]

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
            return sorted(School.get_by_ids(self.school_ids), key=lambda school: school.name)
        return []

    @property
    def to_posts(self):
        """return the posts addressed to self and to all the clubs etc. of self"""
        recipient_ids = [('users', self.json['_id'])]
        recipient_ids.extend([('clubs', club_id) for club_id in self.json['club_ids']])
        posts = db.posts.find({'recipient_ids': {'$in': recipient_ids}}).sort('date', -1)
        return [Post(n) for n in posts]


class Club(MongoDbEntity):
    @property
    def school(self):
        return School(db.schools.find_one({'_id': self.school_id}))


class Company(MongoDbEntity):
    pass


class Competition(MongoDbEntity):
    pass


class CompetitionHost(MongoDbEntity):
    pass


class Post(MongoDbEntity):
    @property
    def sender(self):
        return self.get_by_id(self.json['sender_id'])

    @property
    def recipients(self):
        return self.get_by_ids(self.json['recipient_ids'])


class School(MongoDbEntity):
    def members(self, projection=None):
        return sorted(User(db.users.find({'school_ids': self.json['_id']}, projection)), key=lambda user: user.name)

    @property
    def clubs(self):
        return sorted([Club(club) for club in db.clubs.find({'school_id': self.json['_id']})],
                      key=lambda club: club.name)


class User(MongoDbEntity):
    @property
    def clubs(self):
        return sorted(self.get_by_ids(self.club_ids), key=lambda club: club.name)

    @property
    def school(self):
        return School.get_by_id(self.school_ids[0])

    @staticmethod
    def get_by_email(email):
        return User(db.users.find_one({'email': email}))


collection_names = {
    Club: 'clubs',
    Company: 'companies',
    Competition: 'competitions',
    CompetitionHost: 'competition_hosts',
    Post: 'posts',
    School: 'schools',
    User: 'users',
}
collection_names.update(dict((reversed(item) for item in collection_names.items())))
