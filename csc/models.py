import csc.model_mixins

from datetime import date
from pony.orm import *


db = Database()


class School(db.Entity, csc.model_mixins.SchoolMixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    clubs = Set('Club')
    city = Required(str)
    state = Required(str)
    members = Set('Member')


class Club(db.Entity, csc.model_mixins.ClubMixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    school = Required(School)
    major = Optional(str)
    competitions = Set('Competition')
    achievements = Set('Achievement')
    to_notifications = Set('Notification')
    members = Set('Member', reverse='clubs')
    photo = Optional('Photo')
    president = Optional('Member', reverse='clubs_president')
    vicepresident = Optional('Member', reverse='clubs_vicepresident')
    treasurer = Optional('Member', reverse='clubs_treasurer')
    secretary = Optional('Member', reverse='clubs_secretary')


class User(db.Entity, csc.model_mixins.UserMixin):
    id = PrimaryKey(int, auto=True)
    email = Required(str)
    password = Required(unicode)
    name = Required(str)
    major = Optional(str)
    notes = Optional(str)
    achievements = Set('Achievement')
    to_notifications = Set('Notification')
    city = Required(str)
    state = Required(str)
    photo = Optional('Photo')


class JobOffer(db.Entity, csc.model_mixins.JobOfferMixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    description = Required(str)
    date = Required(date)
    location = Required(str)
    from_notifications = Set('Notification')
    company = Required('Company')
    members = Set('Member')


class Competition(db.Entity, csc.model_mixins.CompetitionMixin):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    description = Required(str)
    date = Required(date)
    website = Optional(str)
    clubs = Set(Club)
    from_notifications = Set('Notification')
    competition_host = Required('CompetitionHost')
    members = Set('Member')


class Achievement(db.Entity, csc.model_mixins.AchievementMixin):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    description = Required(str)
    date = Required(date)
    club = Optional(Club)
    users = Set(User)


class Notification(db.Entity, csc.model_mixins.NotificationMixin):
    id = PrimaryKey(int, auto=True)
    from_competition = Optional(Competition)
    from_job_offer = Optional(JobOffer)
    to_users = Set(User)
    to_clubs = Set(Club)
    post = Optional('Post')
    date = Required(date)


class Post(db.Entity, csc.model_mixins.PostMixin):
    id = PrimaryKey(int, auto=True)
    notification = Required(Notification)
    title = Required(str)
    text = Required(str)
    date = Required(date)
    video = Optional('Video')
    photos = Set('Photo')


class CompetitionHost(User, csc.model_mixins.CompetitionHostMixin):
    competitions = Set(Competition)


class Member(User, csc.model_mixins.MemberMixin):
    clubs = Set(Club, reverse='members')
    school = Required(School)
    competitions = Set(Competition)
    job_offers = Set(JobOffer)
    clubs_president = Set(Club, reverse='president')
    clubs_vicepresident = Set(Club, reverse='vicepresident')
    clubs_treasurer = Set(Club, reverse='treasurer')
    clubs_secretary = Set(Club, reverse='secretary')
    resume = Optional('Resume')


class Company(User, csc.model_mixins.CompanyMixin):
    job_offers = Set(JobOffer)


class Video(db.Entity, csc.model_mixins.VideoMixin):
    id = PrimaryKey(int, auto=True)
    post = Required(Post)


class Photo(db.Entity, csc.model_mixins.PhotoMixin):
    _table_ = 'Image'
    id = PrimaryKey(int, auto=True)
    user = Optional(User)
    posts = Set(Post)
    club = Optional(Club)


class Resume(db.Entity, csc.model_mixins.ResumeMixin):
    id = PrimaryKey(int, auto=True)
    member = Required(Member)
    text = Required(str)


class Administrator(User, csc.model_mixins.AdministratorMixin):
    pass


db.bind("sqlite", "database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
