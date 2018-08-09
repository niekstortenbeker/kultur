import CreateDatabase
import output

# TODO make this automatic every week


def main():
    #TODO use click or argparse with options for new database making
    print_header()

    db_programinfo, db_metainfo = CreateDatabase.main()
    db_metainfo = output.quality_control_dbs(db_programinfo, db_metainfo)
    output.print_database(db_programinfo, db_metainfo)

    db_programinfo_json = output.remove_arrow_objects_in_programinfo(db_programinfo)
    output.db_to_json(db_programinfo_json, db_metainfo)



    # db_programinfo, db_metainfo = output.json_to_db()
    # db_programinfo = output.insert_arrow_objects_in_programinfo(db_programinfo)
    # output.print_database(db_programinfo, db_metainfo)

def print_header():
    print(''.center(70, '-'))
    print('Kultur'.center(70, ' '))
    print(''.center(70, '-'))

if __name__ == '__main__':
    main()