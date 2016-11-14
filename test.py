from models import create_tables, User, db, State, School, Club, UserClub
import datetime
import random


def create():
    with db.transaction() as _txn:
        create_tables(True)

        s1 = State.create(name='missouri')
        s2 = State.create(name='florida')

        sc1 = School.create(name='MIZ', state=s1)
        sc2 = School.create(name='UWF', state=s2)

        u1 = User.create(name='shlucker', school=sc1)
        u2 = User.create(name='brandon', school=sc1)
        u3 = User.create(name='stefano', school=sc2)

        c1 = Club.create(name='ASME', school=sc1)
        c2 = Club.create(name='3DP', school=sc1)
        c3 = Club.create(name='ASME', school=sc2)

        UserClub.create(user=u1, club=c1)
        UserClub.create(user=u1, club=c2)
        UserClub.create(user=u2, club=c2)
        UserClub.create(user=u2, club=c3)


if __name__ == '__main__':
    create()
    u1 = User.get(User.name == 'shlucker')
    print(u1.name, u1.school.name)

    users = User.select().where(User.name > 'd')
    for u in users:
        print(u.name, u.school.name)
        clubs = Club.select().join(UserClub).join(User).where(User.id==u.id)
        for c in clubs:
            print('Club:', c.name)
