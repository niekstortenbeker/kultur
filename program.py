import CreateDatabase
import output
import click

# TODO add more help info

@click.command()
@click.option('--scrape/--no-scrape', '-s', default=False,
              help='Scrape websites to make a fresh database. (Otherwise start from old database)')
def main(scrape):
    print_header()
    if scrape:
        start_with_new_database()
    else:
        start_with_old_database()


def start_with_old_database():
    db_programinfo, db_metainfo, scraping_date = output.json_to_db()
    db_programinfo = output.insert_arrow_objects_in_programinfo(db_programinfo)
    print(f'this program uses a database made on: {scraping_date}')

    output.print_database(db_programinfo, db_metainfo)


def start_with_new_database():
    db_programinfo, db_metainfo = CreateDatabase.main()
    db_metainfo = output.quality_control_dbs(db_programinfo, db_metainfo)

    output.print_database(db_programinfo, db_metainfo)

    db_programinfo_json = output.remove_arrow_objects_in_programinfo(db_programinfo)
    output.db_to_json(db_programinfo_json, db_metainfo)


def print_header():
    print(''.center(70, '-'))
    print('Kultur'.center(70, ' '))
    print(''.center(70, '-'))

if __name__ == '__main__':
    main()