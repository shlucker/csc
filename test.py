import pony.orm as ponyorm
import xlrd
from models import db, School, Club, User, JobOffer, Competition, Achievement, Notification, Post, CompetitionHost, \
    Member, Company, Video, Photo, Resume


@ponyorm.db_session
def import_from_excel():
    book = xlrd.open_workbook('test.xlsx')

    sheet = book.sheet_by_name('School')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        city = sheet.cell(r, 1).value
        state = sheet.cell(r, 2).value
        School(name=name, city=city, state=state)

    sheet = book.sheet_by_name('Member')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        major = sheet.cell(r, 1).value
        city = sheet.cell(r, 2).value
        state = sheet.cell(r, 3).value
        school = School.get(name=sheet.cell(r, 4).value)
        email = name.replace(' ', '.') + '@gmail.com'
        Member(name=name, major=major, state=state, city=city, email=email, school=school)

    sheet = book.sheet_by_name('Club')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        school = School.get(name=sheet.cell(r, 1).value)
        president = sheet.cell(r, 2).value
        vicepresident = sheet.cell(r, 3).value
        treasurer = sheet.cell(r, 4).value
        secretary = sheet.cell(r, 5).value
        president = Member.get(name=president) if president else None
        vicepresident = Member.get(name=vicepresident) if vicepresident else None
        treasurer = Member.get(name=treasurer) if treasurer else None
        secretary = Member.get(name=secretary) if secretary else None
        Club(name=name, school=school, president=president, vicepresident=vicepresident, treasurer=treasurer,
             secretary=secretary)

    sheet = book.sheet_by_name('Company')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        city = sheet.cell(r, 1).value
        state = sheet.cell(r, 2).value
        email = name.replace(' ', '.') + '@gmail.com'
        Company(name=name, city=city, state=state, email=email)

    sheet = book.sheet_by_name('CompetitionHost')
    for r in range(1, sheet.nrows):
        name = sheet.cell(r, 0).value
        city = sheet.cell(r, 1).value
        state = sheet.cell(r, 2).value
        email = name.replace(' ', '.') + '@gmail.com'
        CompetitionHost(name=name, city=city, state=state, email=email)


if __name__ == '__main__':
    # ponyorm.sql_debug(True)
    db.bind('sqlite', 'csc.db', create_db=True)
    db.generate_mapping(create_tables=True)
    db.drop_all_tables(with_all_data=True)
    db.create_tables()
    import_from_excel()

    with ponyorm.db_session:
        print('== Get member by name ==')
        u1 = User.get(name='Sade Berney')
        print(u1.name, u1.major, u1.city, u1.state)

        print('== Get members by school ==')
        for s in ponyorm.select(s for s in School):
            if s.members:
                print('Members of school: {}'.format(s.name))
                for m in s.members:
                    print(' ', m.name)
