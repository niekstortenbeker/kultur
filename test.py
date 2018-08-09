import CreateDatabase
import webscraping
import output
from pprint import pprint
import click

@click.command()
@click.option('--scrape/--no-scrape', '-s', default=False, help='scrape websites to make a new database. otherwise start from database')
def main(scrape):
    if scrape:
        print('jeej')


if __name__ == '__main__':
    main()