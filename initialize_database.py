import os

DB_NAME = 'csc/database.sqlite'
try:
    os.unlink(DB_NAME)
except FileNotFoundError:
    pass

import pony.orm as orm
import xlrd

import csc.models as models
from csc.security import hash_password


@orm.db_session
def import_from_excel():
    book = xlrd.open_workbook('test.xlsx')

    print('Creating schools')
    sheet = book.sheet_by_name('School')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        city = sheet.cell(r, 1).value
        state = sheet.cell(r, 2).value
        models.School(name=name, city=city, state=state)

    print('Creating administrators')
    sheet = book.sheet_by_name('Administrator')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        email = sheet.cell(r, 1).value
        password = hash_password(sheet.cell(r, 2).value)
        city = sheet.cell(r, 3).value
        state = sheet.cell(r, 4).value
        models.Administrator(name=name, email=email, password=password, state=state, city=city)

    print('Creating members')
    sheet = book.sheet_by_name('Member')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        email = sheet.cell(r, 1).value
        password = hash_password(sheet.cell(r, 2).value)
        major = sheet.cell(r, 3).value
        city = sheet.cell(r, 4).value
        state = sheet.cell(r, 5).value
        school = models.School[int(sheet.cell(r, 6).value)]
        models.Member(name=name, major=major, state=state, city=city, email=email, password=password, school=school)

    print('Creating clubs')
    sheet = book.sheet_by_name('Club')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        school = models.School[int(sheet.cell(r, 1).value)]
        president = models.Member[int(sheet.cell(r, 2).value)] if sheet.cell(r, 2).value else None
        vicepresident = models.Member[int(sheet.cell(r, 3).value)] if sheet.cell(r, 3).value else None
        treasurer = models.Member[int(sheet.cell(r, 4).value)] if sheet.cell(r, 4).value else None
        secretary = models.Member[int(sheet.cell(r, 5).value)] if sheet.cell(r, 5).value else None
        members = [models.Member[i] for i in sheet.cell(r, 6).value.split()]
        models.Club(name=name, school=school, president=president, vicepresident=vicepresident, treasurer=treasurer,
                    secretary=secretary, members=members)

    print('Creating companies')
    sheet = book.sheet_by_name('Company')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        email = sheet.cell(r, 1).value
        password = hash_password(sheet.cell(r, 2).value)
        city = sheet.cell(r, 3).value
        state = sheet.cell(r, 4).value
        models.Company(name=name, email=email, password=password, city=city, state=state)

    print('Creating competition hosts')
    sheet = book.sheet_by_name('CompetitionHost')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        email = sheet.cell(r, 1).value
        password = hash_password(sheet.cell(r, 2).value)
        city = sheet.cell(r, 3).value
        state = sheet.cell(r, 4).value
        models.CompetitionHost(name=name, email=email, password=password, city=city, state=state)

    print('Creating competitions')
    sheet = book.sheet_by_name('Competition')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        description = sheet.cell(r, 1).value
        date = sheet.cell(r, 2).value
        website = sheet.cell(r, 3).value
        clubs = [models.Club[i] for i in sheet.cell(r, 4).value.split()]
        competition_host = models.CompetitionHost[int(sheet.cell(r, 5).value)]
        members = [models.Member[i] for i in sheet.cell(r, 6).value.split()]
        models.Competition(name=name, description=description, date=date, website=website, clubs=clubs,
                           competition_host=competition_host, members=members)

    print('Creating notifications')
    sheet = book.sheet_by_name('Notification')
    for r in range(1, sheet.nrows):
        from_competition = models.Competition[int(sheet.cell(r, 0).value)] if sheet.cell(r, 0).value else None
        from_job_offer = models.JobOffer[int(sheet.cell(r, 1).value)] if sheet.cell(r, 1).value else None
        to_users = [models.Member[i] for i in sheet.cell(r, 2).value.split()]
        to_clubs = [models.Club[i] for i in sheet.cell(r, 3).value.split()]
        date = sheet.cell(r, 4).value
        models.Notification(from_competition=from_competition, from_job_offer=from_job_offer, to_users=to_users,
                    to_clubs=to_clubs, date=date)

    print('Creating posts')
    sheet = book.sheet_by_name('Post')
    for r in range(1, sheet.nrows):
        title = sheet.cell(r, 0).value
        text = sheet.cell(r, 1).value
        date = sheet.cell(r, 2).value
        notification = models.Notification[int(sheet.cell(r, 3).value)]
        models.Post(title=title, text=text, date=date, notification=notification)


# ponyorm.sql_debug(True)
import_from_excel()

with orm.db_session:
    print('== Get member by name ==')
    u1 = models.User.get(name='Sade Berney')
    print(u1.name, u1.major, u1.city, u1.state)

    print('== Get members by school ==')
    for s in orm.select(s for s in models.School):
        if s.members:
            print('Members of school: {}'.format(s.name))
            for m in s.members:
                print(' ', m.name)
        else:
            print('School without members: {}'.format(s.name))

    print('== Get members by competition ==')
    for c in orm.select(c for c in models.Competition):
        if c.members:
            print('Members of competition: {}'.format(c.name))
            for m in c.members:
                print(' ', m.name)
        else:
            print('Competition without members: {}'.format(c.name))

    print('== Get competitions by member ==')
    for m in orm.select(m for m in models.Member if m.competitions):
        print('Competitions of member: {}'.format(m.name))
        for c in m.competitions:
            print(' ', c.name)
