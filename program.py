import CreateDatabase
import InputOutput
import click
from flask import Flask, render_template, url_for

app = Flask(__name__)
# TODO add more help info


@click.command()
@click.option('--new/--old', '-n', default=False,
              help='Scrape websites to make a new database. (Otherwise start from old database)')
@click.option('--website/--no-website', '-w', default=False,
              help='make it into a website')
def main(new, website):
    print_header()
    if new:
        scraping_date = 'just now!'
        db_programinfo, db_metainfo = make_new_database()
    else:
        db_programinfo, db_metainfo, scraping_date = use_old_database()
    if website:
        app.run(debug=True)
    else:
        print_program(db_programinfo, db_metainfo, scraping_date)


def print_header():
    print(''.center(100, '-'))
    print('Kultur'.center(100, ' '))
    print(''.center(100, '-'))


def use_old_database():
    db_programinfo, db_metainfo, scraping_date = InputOutput.json_to_db()
    db_programinfo = InputOutput.insert_arrow_objects_in_programinfo(db_programinfo)
    return db_programinfo, db_metainfo, scraping_date


def make_new_database():
    db_programinfo, db_metainfo = CreateDatabase.main()
    db_programinfo_json = InputOutput.remove_arrow_objects_in_programinfo(db_programinfo)
    InputOutput.db_to_json(db_programinfo_json, db_metainfo)
    return db_programinfo, db_metainfo


def print_program(db_programinfo, db_metainfo, scraping_date):
    print(f'this program uses a database made on: {scraping_date}')
    program = InputOutput.make_current_program(db_programinfo, db_metainfo)
    InputOutput.print_program(program)

@app.route("/")
@app.route("/home")
def make_website():
    return render_template('home.html')


if __name__ == '__main__':
    main()