import os

DB_NAME = 'csc/database.sqlite'
try:
    os.unlink(DB_NAME)
except FileNotFoundError:
    pass

from pony import orm

import csc.models as models
from csc.security import hash_password


class TestTable:
    def __init__(self, fname):
        self.tables = {}
        sh_name = ''
        headers = None
        headers_are_coming = False
        for row in open(fname, 'r'):
            row = row[:-1]
            if row.startswith('==') and row.endswith('=='):
                sh_name = row[3:-3]
                self.tables[sh_name] = []
                headers_are_coming = True
            elif headers_are_coming:
                headers = [cell.rstrip() for cell in row.split('|')]
                headers_are_coming = False
            elif row:
                self.tables[sh_name].append(
                    {header: cell.rstrip() for (header, cell) in zip(headers, row.split('|'))})

    def __getitem__(self, table_name):
        return self.tables[table_name]

    def n_rows(self, table_name):
        return len(self.tables[table_name])

    def n_columns(self, table_name):
        return len(self.tables[table_name].items()[0])


@orm.db_session
def import_from_excel():
    test_table = TestTable('test.txt')

    print('Creating schools')
    for r in range(test_table.n_rows('School')):
        name = test_table['School'][r]['name']
        city = test_table['School'][r]['city']
        state = test_table['School'][r]['state']
        models.School(name=name, city=city, state=state)

    print('Creating administrators')
    for r in range(test_table.n_rows('Administrator')):
        name = test_table['Administrator'][r]['name']
        email = test_table['Administrator'][r]['email']
        password = hash_password(test_table['Administrator'][r]['password'])
        city = test_table['Administrator'][r]['city']
        state = test_table['Administrator'][r]['state']
        models.Administrator(name=name, email=email, password=password, state=state, city=city)

    print('Creating members')
    for r in range(test_table.n_rows('Member')):
        name = test_table['Member'][r]['name']
        email = test_table['Member'][r]['email']
        password = hash_password(test_table['Member'][r]['password'])
        major = test_table['Member'][r]['major']
        city = test_table['Member'][r]['city']
        state = test_table['Member'][r]['state']
        school = models.School[int(test_table['Member'][r]['school'])]
        models.Member(name=name, major=major, state=state, city=city, email=email, password=password, school=school)

    print('Creating clubs')
    for r in range(test_table.n_rows('Club')):
        name = test_table['Club'][r]['name']
        school = models.School[int(test_table['Club'][r]['school'])]
        president = models.Member[int(test_table['Club'][r]['president'])] if test_table['Club'][r][
            'president'] else None
        vicepresident = models.Member[int(test_table['Club'][r]['vicepresident'])] if test_table['Club'][r][
            'vicepresident'] else None
        treasurer = models.Member[int(test_table['Club'][r]['treasurer'])] if test_table['Club'][r][
            'treasurer'] else None
        secretary = models.Member[int(test_table['Club'][r]['secretary'])] if test_table['Club'][r][
            'secretary'] else None
        members = [models.Member[i] for i in test_table['Club'][r]['members'].split()]
        models.Club(name=name, school=school, president=president, vicepresident=vicepresident, treasurer=treasurer,
                    secretary=secretary, members=members)

    print('Creating companies')
    for r in range(test_table.n_rows('Company')):
        name = test_table['Company'][r]['name']
        email = test_table['Company'][r]['email']
        password = hash_password(test_table['Company'][r]['password'])
        city = test_table['Company'][r]['city']
        state = test_table['Company'][r]['state']
        models.Company(name=name, email=email, password=password, city=city, state=state)

    print('Creating competition hosts')
    for r in range(test_table.n_rows('CompetitionHost')):
        name = test_table['CompetitionHost'][r]['name']
        email = test_table['CompetitionHost'][r]['email']
        password = hash_password(test_table['CompetitionHost'][r]['password'])
        city = test_table['CompetitionHost'][r]['city']
        state = test_table['CompetitionHost'][r]['state']
        models.CompetitionHost(name=name, email=email, password=password, city=city, state=state)

    print('Creating competitions')
    for r in range(test_table.n_rows('Competition')):
        name = test_table['Competition'][r]['name']
        description = test_table['Competition'][r]['description']
        date = test_table['Competition'][r]['date']
        website = test_table['Competition'][r]['website']
        clubs = [models.Club[i] for i in test_table['Competition'][r]['clubs'].split()]
        competition_host = models.CompetitionHost[int(test_table['Competition'][r]['competition_host'])]
        members = [models.Member[i] for i in test_table['Competition'][r]['members'].split()]
        models.Competition(name=name, description=description, date=date, website=website, clubs=clubs,
                           competition_host=competition_host, members=members)

    print('Creating notifications')
    for r in range(test_table.n_rows('Notification')):
        from_competition = models.Competition[int(test_table['Notification'][r]['from_competition'])] if \
            test_table['Notification'][r]['from_competition'] else None
        from_job_offer = models.JobOffer[int(test_table['Notification'][r]['from_job_offer'])] if \
            test_table['Notification'][r]['from_job_offer'] else None
        to_users = [models.Member[i] for i in test_table['Notification'][r]['to_users'].split()]
        to_clubs = [models.Club[i] for i in test_table['Notification'][r]['to_clubs'].split()]
        date = test_table['Notification'][r]['date']
        models.Notification(from_competition=from_competition, from_job_offer=from_job_offer, to_users=to_users,
                            to_clubs=to_clubs, date=date)

    print('Creating posts')
    for r in range(test_table.n_rows('Post')):
        title = test_table['Post'][r]['title']
        text = test_table['Post'][r]['text']
        date = test_table['Post'][r]['date']
        notification = models.Notification[int(test_table['Post'][r]['notification'])]
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
