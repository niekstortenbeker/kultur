import CreateDatabase
import output

# TODO make this automatic every week


def main():
    db_programinfo, db_metainfo = CreateDatabase.main()
    output.print_database(db_programinfo, db_metainfo)


if __name__ == '__main__':
    main()