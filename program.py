import CreateDatabase
import output

# TODO make this automatic every week


def main():
    #TODO write this in such a way that it only does the webscraping when the information in the database is old. 
    # db_programinfo, db_metainfo = CreateDatabase.main()
    # db_metainfo = output.quality_control_dbs(db_programinfo, db_metainfo)
    # output.print_database(db_programinfo, db_metainfo)
    #
    # db_programinfo_json = output.remove_arrow_objects_in_programinfo(db_programinfo)
    # output.db_to_json(db_programinfo_json, db_metainfo)




    db_programinfo, db_metainfo = output.json_to_db()
    db_programinfo = output.insert_arrow_objects_in_programinfo(db_programinfo)
    db_metainfo = output.quality_control_dbs(db_programinfo, db_metainfo)
    output.print_database(db_programinfo, db_metainfo)


if __name__ == '__main__':
    main()