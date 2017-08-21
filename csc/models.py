import random
import re
from collections import defaultdict

import flask_login
import pymongo

import csc.security as security
from csc import login_manager
import csc.exceptions as exceptions

client = pymongo.MongoClient('0.0.0.0', 27017)
db = client['csc']


def underscorize(txt):
    return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', txt).lower()


class MongoDbEntity:
    """ Base class for all the collections in the database """

    def __init__(self, json):
        self.json = json

    def __getattr__(self, item):
        return self.json[item] if item in self.json else None

    def __getitem__(self, name):
        return self.json[name]

    def __contains__(self, a):
        return a in self.json

    def __repr__(self):
        if 'username' in self:
            return '<{} - {} - {}>'.format(str(str(self.__class__)[1:-1]), self._id, self.username)
        return '<{} - {}>'.format(str(str(self.__class__)[1:-1]), self._id)

    @classmethod
    def find(cls, filter=None, projection=None):
        """
        Generic helper for the mongo db find method.
        Each returned object is casted to the correct class depending on the first 4 characters of the _id
        """
        assert not cls is MongoDbEntity and not cls is LoggableUser, \
            'MongoDbEntity.find_one is intended to be called by an instance of a derived ' \
            'class, not directely by a MongoDbEntity instance'

        collection = class2collection[cls]
        if projection:
            p = {}
            if '_id' not in projection:
                p['_id'] = 0
            p.update({k: 1 for k in projection})
        else:
            p = None

        cursor = collection.find(filter, p)
        while True:
            yield cls(cursor.next())

    @classmethod
    def find_one(cls, filter=None, projection=None):
        """
        Generic helper for the mongo db find_one method.
        The returned object is casted to the correct class depending on the first 4 characters of the _id
        """
        assert not cls is MongoDbEntity and not cls is LoggableUser, \
            'MongoDbEntity.find_one is intended to be called by an instance of a derived ' \
            'class, not directely by a MongoDbEntity instance'

        collection = class2collection[cls]
        if projection:
            p = {}
            if not '_id' in projection:
                p['_id'] = 0
            p.update({k: 1 for k in projection})
        else:
            p = None

        doc = collection.find_one(filter, p)
        if doc:
            return cls(doc)

    @classmethod
    def find_text(cls, text, skip, limit):
        """ Text search sorted by textScore """
        assert not cls is MongoDbEntity and not cls is LoggableUser, \
            'MongoDbEntity.find_one is intended to be called by an instance of a derived ' \
            'class, not directely by a MongoDbEntity instance'

        collection = class2collection[cls]
        cursor = (collection
                  .find({'$text': {'$search': text}},
                        {'score': {'$meta': 'textScore'}})
                  .sort([('score', {'$meta': 'textScore'})])
                  .skip(skip)
                  .limit(limit))
        while True:
            doc = cursor.next()
            return_class = id2class[doc['_id'][:4]]
            yield return_class(doc)

    @classmethod
    def get_by_id(cls, id):
        """
        The first 4 characters of the id determine what sub-class to search and return
        (unlike the find<...> methods that are intended to be called as method of the sub-class)
        """
        try:
            prefix = id[:4]
            collection = id2collection[prefix]
            return_class = id2class[id[:4]]

            doc = collection.find_one({'_id': id})
            if doc:
                return return_class(doc)
        except:
            pass

    @classmethod
    def get_by_ids(cls, ids):
        """ find all the objects listed in ids, searching one collection at a time (regardless of the order of ids) """
        id_types = defaultdict(list)
        for i in ids:
            id_types[i[:4]].append(i)

        for id_type in id_types:
            collection = id2collection[id_type]
            return_class = id2class[id_type]
            ids = id_types[id_type]

            cursor = collection.find({'_id': {'$in': ids}})
            while True:
                doc = cursor.next()
                yield return_class(doc)

    @classmethod
    def get_by_id_on_field(cls, field_name, id):
        """
        id can be an id "club-1" or a list of ids ["club-1", "club-3"]
        Example: to find all the users with 'club-3' in the list of clubs:
            User.get_by_id_on_field('clubs', 'club-3')
        """
        cursor = cls.find({field_name: {'$in': id}})
        while True:
            yield cls(next(cursor))

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
        fields = [str(self.json[field_name])
                  for field_name in ['street', 'city', 'zip', 'state']
                  if field_name in self.json]
        return ', '.join(fields)

    @property
    def schools(self):
        if 'school_ids' in self.json:
            return sorted(School.get_by_ids(self.school_ids), key=lambda school: school.name)
        return []

    def set_field_value(self, field_name, value):
        collection = id2collection[self._id[:4]]
        collection.find_one_and_update(
            {'_id': self._id},
            {'$set': {field_name: value}})

    @property
    def to_posts(self):
        """ return the posts addressed to self and to all the clubs etc. of self """
        try:
            recipient_ids = [self.json['_id']]
            try:
                recipient_ids.extend(self.json['club_ids'])
            except KeyError:
                pass
            return Post.get_by_id_on_field('recipient_ids', recipient_ids)
        except Exception as e:
            raise e


class LoggableUser(MongoDbEntity, flask_login.UserMixin):
    """ All the objects that represent members that can login derive this class instead of MongoDbEntity """

    @staticmethod
    def create(username, email, password, member_type):
        """ return the id of the new user/company/host """
        if member_type not in ('user', 'cmpn', 'coho'):
            raise TypeError('Unexpected member type: {}'.format(member_type))

        if LoggableUser.get_by_email(email):
            raise exceptions.DuplicatedEmail

        while True:
            try:
                # TODO the random number is an ugly temporary trick to make unique id
                collection = id2collection[member_type]
                res = collection.insert_one({'_id': '{}-{}'.format(member_type, random.randint(1, 1000000000)),
                                             'username': username,
                                             'email': email,
                                             'password': security.hash_password(password)})
                if (member_type != 'user' and
                        db.user.find_one({'$or': [{'username': username}, {'email': email}]}) or
                                member_type != 'cmpn' and db.competition.find_one(
                            {'$or': [{'username': username}, {'email': email}]}) or member_type != 'coho' and
                    db.competition_host.find_one(
                        {'$or': [{'username': username}, {'email': email}]})):
                    raise pymongo.errors.DuplicateKeyError()

            except pymongo.errors.DuplicateKeyError as e:
                if 'index: username' in e.args[0]:
                    raise exceptions.DuplicatedUserName
                if 'index: email' in e.args[0]:
                    raise exceptions.DuplicatedEmail
                # the duplicated field is the _id, because the random number is duplicated
            else:
                break

        return res.inserted_id

    @staticmethod
    def get_by_email(email):
        """
        Find user, company or competition host by email, starting by user because it
        is the case most of times
        """
        user = User.find_one({'email': email})
        if user:
            return user

        company = Company.find_one({'email': email})
        if company:
            return company

        competition_host = CompetitionHost.find_one({'email': email})
        if competition_host:
            return competition_host

    @staticmethod
    def get_by_username(username):
        """
        Find user, company or competition host by username, starting by user because it
        is the case the 90% of times
        """
        user = User.find_one({'username': username})
        if user:
            return user

        company = Company.find_one({'username': username})
        if company:
            return company

        competition_host = CompetitionHost.find_one({'username': username})
        if competition_host:
            return competition_host

    def get_id(self):
        return self.username

    def set_email_verified(self):
        collection = id2collection[self._id[:4]]
        collection.find_one_and_update(
            {'_id': self._id},
            {'$set': {'email_verified': 1},
             '$unset': {'verify_email_token': ''}})


class Club(MongoDbEntity):
    @property
    def school(self):
        return School(School.find_one({'_id': self.school_id}))


class Company(LoggableUser):
    pass


class Competition(MongoDbEntity):
    def members(self, projection=None):
        return User.find({'competition_ids': self.json['_id']}, projection)


class CompetitionHost(LoggableUser):
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


class User(LoggableUser):
    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_username(user_id)

    @property
    def clubs(self):
        if self._clubs is None:  # all the attirbutes not present in the json document are returned as None
            try:
                self._clubs = sorted(self.get_by_ids(self.club_ids), key=lambda club: club.name)
                for club in self._clubs:
                    try:
                        club.user_data = self.club_data[club._id]
                    except KeyError as e:
                        pass
            except TypeError:
                self._clubs = []

        return self._clubs

    def position_in_club(self, club_id):
        for club in self.clubs:
            if club._id == club_id:
                try:
                    return club.officers[self._id]
                except (TypeError,  # officers does not exist
                        KeyError):  # officers doesn't contain self._id
                    return 'Member'

    @property
    def competitions(self):
        return sorted(Competition.get_by_ids(self.competition_ids), key=lambda competition: competition.name)

    @property
    def school(self):
        try:
            return School.get_by_id(self.school_ids[0])
        except:
            return None

    @property
    def search_box(self):
        try:
            return self.json['search_box']
        except KeyError as e:
            return {'search_value': '',
                    'search_url': 'search/',
                    'search_title': 'Search by School, Person, Club, Company, Competition, State, City'}


id2class = {'club': Club,
            'cmpn': Company,
            'cmpt': Competition,
            'coho': CompetitionHost,
            'post': Post,
            'scho': School,
            'user': User}
id2collection = {'club': db.club,
                 'cmpn': db.company,
                 'cmpt': db.competition,
                 'coho': db.competition_host,
                 'post': db.post,
                 'scho': db.school,
                 'user': db.user}
class2id = {Club: 'club',
            Company: 'cmpn',
            Competition: 'cmpt',
            CompetitionHost: 'coho',
            Post: 'post',
            School: 'scho',
            User: 'user'}
class2collection = {Club: db.club,
                    Company: db.company,
                    Competition: db.competition,
                    CompetitionHost: db.competition_host,
                    Post: db.post,
                    School: db.school,
                    User: db.user}
