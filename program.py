import CreateDatabase
import InputOutput
import click


@click.command()
@click.option('--new/--old', '-n', default=False,
              help='Scrape websites to make a new database. (Otherwise start from old database)')
def main(new):
    print_header()
    if new:
        make_new_database()
    db_programinfo, db_metainfo, scraping_date = prepare_program_from_JSON()
    current_program = InputOutput.make_current_program(db_programinfo, db_metainfo)
    print_program(current_program, scraping_date)


def print_header():
    print(''.center(100, '-'))
    print('Kultur'.center(100, ' '))
    print(''.center(100, '-'))


def prepare_program_from_JSON():
    db_programinfo, db_metainfo, scraping_date = InputOutput.json_to_db()
    db_programinfo = InputOutput.insert_arrow_objects_in_programinfo(db_programinfo)
    return db_programinfo, db_metainfo, scraping_date


def make_new_database():
    db_programinfo, db_metainfo = CreateDatabase.main()
    db_programinfo_json = InputOutput.remove_arrow_objects_in_programinfo(db_programinfo)
    InputOutput.db_to_json(db_programinfo_json, db_metainfo)


def print_program(current_program, scraping_date):
    print(f'\nthis program uses a database made on: {scraping_date}')
    InputOutput.print_program(current_program)


if __name__ == '__main__':
    main()