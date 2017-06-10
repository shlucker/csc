import re

from pymongo import MongoClient

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
        doc = db.stuff.find_one({'_id': id})
        doc_class = globals()[doc['_tp']]
        return doc_class(doc)

    @classmethod
    def get_by_ids(cls, ids):
        cursor = db.stuff.find({'_id': {'$in': ids}})
        while True:
            doc = cursor.next()
            doc_class = globals()[doc['_tp']]
            yield doc_class(doc)

    @classmethod
    def get_by_id_on_field(cls, field_name, id):
        """
        id can be an id "club 1" or a list of ids ["club 1", "club 3"]
        Example: to find all the users with 'club 3' in the list of clubs:
            User.get_by_id_on_field('club_ids', 'club 3')
        """
        cursor = cls.find({field_name: {'$in': id}})
        while True:
            yield cls(next(cursor))

    @classmethod
    def find_one(cls, filter=None, projection=None):
        """
        If cls is derived from MongoDbEntity then {'_tp': cls.__name__} is added to the filter dictionary
        If cls is MongoDbEntity then '_tp' is not used in the search (searching by '_id' doesn't require the '_tp')
        projection contains the list of fields to return; if None then all the fields are returned
        """
        f = {'_tp': cls.__name__} if cls is not MongoDbEntity else {}
        if filter:
            f.update(filter)

        if projection:
            p = {}
            if not '_id' in projection:
                p['_id'] = 0
            p.update({k: 1 for k in projection})
        else:
            p = None

        doc = db.stuff.find_one(f, p)
        if doc:
            return cls(doc)

    @classmethod
    def find(cls, filter=None, projection=None):
        """
        If cls is derived from MongoDbEntity then {'_tp': cls.__name__} is added to the filter dictionary
        If cls is MongoDbEntity then '_tp' is not used in the search (searching by '_id' doesn't require the '_tp')
        projection contains the list of fields to return; if None then all the fields are returned
        """
        f = {'_tp': cls.__name__} if cls is not MongoDbEntity else {}
        if filter:
            f.update(filter)

        if projection:
            p = {}
            if not '_id' in projection:
                p['_id'] = 0
            p.update({k: 1 for k in projection})
        else:
            p = None

        cursor = db.stuff.find(f, p)
        while True:
            yield cls(cursor.next())

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
        recipient_ids = [self.json['_id']]
        recipient_ids.extend(club_id for club_id in self.json['club_ids'])
        return Post.get_by_id_on_field('recipient_ids', recipient_ids)


class Club(MongoDbEntity):
    @property
    def school(self):
        return School(School.find_one({'_id': self.school_id}))


class Company(MongoDbEntity):
    pass


class Competition(MongoDbEntity):
    def members(self, projection=None):
        return User.find({'competition_ids': self.json['_id']}, projection)


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
        return User.find({'school_ids': self.json['_id']}, projection)

    @property
    def clubs(self):
        return Club.find({'school_id': self.json['_id']})

    @property
    def students(self):
        return User.find({'school_ids': self.json['_id']})


class User(MongoDbEntity):
    @property
    def clubs(self):
        return sorted(self.get_by_ids(self.club_ids), key=lambda club: club.name)

    @property
    def competitions(self):
        return sorted(Competition.get_by_ids(self.competition_ids), key=lambda competition: competition.name)

    @property
    def school(self):
        return School.get_by_id(self.school_ids[0])

    @staticmethod
    def get_by_email(email):
        user = User.find_one({'email': email})
        if user:
            return User(user)
