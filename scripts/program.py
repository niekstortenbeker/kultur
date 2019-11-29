import webscraping, InputOutput
import click
import arrow


@click.command()
@click.option('--new/--old', '-n', default=False,
              help='Scrape websites to make a new database. (Otherwise start from old database)')
@click.option('--today/--week', '-t', default=False,
              help='Only show today')
def main(new, today):
    print_header()
    if new:
        make_new_database()
    db_programinfo, db_metainfo, scraping_date = prepare_program_from_JSON()

    now = arrow.utcnow()
    if today:
        last_date = now.shift(days=+1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Europe/Berlin')
    else:
        last_date = now.shift(weeks=+1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Europe/Berlin')
    current_program = PrintProgram.make_current_program(db_programinfo, db_metainfo, last_date)
    PrintProgram.print_program(current_program, scraping_date)


def print_header():
    print(''.center(100, '-'))
    print('Kultur Factory'.center(100, ' '))
    print(''.center(100, '-'))


def prepare_program_from_JSON():
    db_programinfo, db_metainfo, scraping_date = InputOutput.json_to_db()
    db_programinfo = InputOutput.insert_arrow_objects_in_program(db_programinfo)
    return db_programinfo, db_metainfo, scraping_date


def make_new_database():
    db_programinfo, db_metainfo = CreateDatabase.main()
    db_programinfo_json = InputOutput.remove_arrow_objects_in_program(db_programinfo)
    InputOutput.db_to_json(db_programinfo_json, db_metainfo)


if __name__ == '__main__':
    main()