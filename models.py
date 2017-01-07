from datetime import date
from pony.orm import *


db = Database()


class School(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    clubs = Set('Club')
    city = Required(str)
    state = Required(str)
    members = Set('Member')


class Club(db.Entity):
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


class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    email = Required(str)
    major = Optional(str)
    notes = Optional(str)
    achievements = Set('Achievement')
    to_notifications = Set('Notification')
    city = Required(str)
    state = Required(str)
    photo = Optional('Photo')


class JobOffer(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    description = Required(str)
    date = Required(date)
    location = Required(str)
    from_notifications = Set('Notification')
    company = Required('Company')
    members = Set('Member')


class Competition(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Required(str)
    description = Required(str)
    date = Required(date)
    website = Optional(str)
    clubs = Set(Club)
    from_notifications = Set('Notification')
    competition_host = Required('CompetitionHost')
    members = Set('Member')


class Achievement(db.Entity):
    id = PrimaryKey(int, auto=True)
    title = Required(str)
    description = Required(str)
    date = Required(date)
    club = Optional(Club)
    users = Set(User)


class Notification(db.Entity):
    id = PrimaryKey(int, auto=True)
    from_competition = Required(Competition)
    from_job_offer = Required(JobOffer)
    to_users = Set(User)
    to_clubs = Set(Club)
    post = Optional('Post')


class Post(db.Entity):
    id = PrimaryKey(int, auto=True)
    notification = Required(Notification)
    title = Required(str)
    text = Required(str)
    video = Required('Video')
    photos = Set('Photo')


class CompetitionHost(User):
    competitions = Set(Competition)


class Member(User):
    clubs = Set(Club, reverse='members')
    school = Required(School)
    competitions = Set(Competition)
    job_offers = Set(JobOffer)
    clubs_president = Set(Club, reverse='president')
    clubs_vicepresident = Set(Club, reverse='vicepresident')
    clubs_treasurer = Set(Club, reverse='treasurer')
    clubs_secretary = Set(Club, reverse='secretary')
    resume = Optional('Resume')


class Company(User):
    job_offers = Set(JobOffer)


class Video(db.Entity):
    id = PrimaryKey(int, auto=True)
    post = Optional(Post)


class Photo(db.Entity):
    _table_ = 'Image'
    id = PrimaryKey(int, auto=True)
    user = Required(User)
    posts = Set(Post)
    club = Optional(Club)


class Resume(db.Entity):
    id = PrimaryKey(int, auto=True)
    member = Required(Member)
    text = Required(str)
