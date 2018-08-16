import CreateDatabase
import InputOutput
import click

# TODO add more help info

@click.command()
@click.option('--new/--old', '-n', default=False,
              help='Scrape websites to make a new database. (Otherwise start from old database)')
def main(new):
    print_header()
    if new:
        start_with_new_database()
    else:
        start_with_old_database()


def start_with_old_database():
    db_programinfo, db_metainfo, scraping_date = InputOutput.json_to_db()
    db_programinfo = InputOutput.insert_arrow_objects_in_programinfo(db_programinfo)
    print(f'this program uses a database made on: {scraping_date}')

    InputOutput.print_database(db_programinfo, db_metainfo)


def start_with_new_database():
    db_programinfo, db_metainfo = CreateDatabase.main()
    InputOutput.print_database(db_programinfo, db_metainfo)

    db_programinfo_json = InputOutput.remove_arrow_objects_in_programinfo(db_programinfo)
    InputOutput.db_to_json(db_programinfo_json, db_metainfo)


def print_header():
    print(''.center(100, '-'))
    print('Kultur'.center(100, ' '))
    print(''.center(100, '-'))

if __name__ == '__main__':
    main()