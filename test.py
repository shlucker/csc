import xlrd
from models import create_tables, User, db, School, Club, UserClub



def import_from_excel():
    book = xlrd.open_workbook('test.xlsx')

    sheet = book.sheet_by_name('Schools')
    print(sheet.nrows)
    with db.atomic():
        for r in range(sheet.nrows):
            school_name = sheet.cell(r, 0).value
            city_name = sheet.cell(r, 1).value
            state_name = sheet.cell(r, 2).value
            print(r,school_name,city_name,state_name)
            School.get_or_create(name=school_name, city=city_name, state=state_name)

    sheet = book.sheet_by_name('Clubs')
    with db.atomic():
        for r in range(sheet.nrows):
            club_name = sheet.cell(r, 0).value
            Club.get_or_create(name=club_name)


def clubs_by_user():
    print('== Get all clubs of all users < ste ==')
    users = User.select().where(User.name < 'ste')
    for u in users:
        print(u.name, u.school.name)
        clubs = Club.select().join(UserClub).join(User).where(User.id == u.id)
        for c in clubs:
            print('Club:', c.name)


if __name__ == '__main__':
    create_tables(True)

    import_from_excel()

    print('== Get user by name ==')
    u1 = User.get(User.name == 'shlucker')
    print(u1.name, u1.school.name)

    clubs_by_user()
