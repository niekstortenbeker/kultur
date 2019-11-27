import webscraping
import re

def main():
    print('\nScraping the program web pages')

    p = webscraping.CombinedProgram()
    p.update_program()
    program_db = [show.__dict__ for show in p.program.shows]
    program_db.sort(key=lambda programinfo: programinfo['date_time'])
    webscraping.start_driver()
    filmkunst_meta = create_db_filmkunst()
    ostertor_meta = create_db_cinema_ostertor()
    webscraping.close_driver()
    meta_db = {**ostertor_meta, **filmkunst_meta}
    for cinema in meta_db:
        for show in meta_db[cinema]:
            meta_db[cinema][show] = meta_db[cinema][show].__dict__
    meta_db = quality_control_dbs(program_db, meta_db)

    return program_db, meta_db


def print_header():
    print(''.center(50, '-'))
    print('KULTUR FACTORY'.center(50, ' '))
    print(''.center(50, '-'))



def quality_control_dbs(db_programinfo, db_metainfo):
    """so far only check for shows in programinfo but not in metainfo if there is a case mismatch in the title"""
    print('\n\nPerforming a quality control on the metainfo and programinfo databases')
    db_metainfo = find_and_change_case_errors(db_programinfo, db_metainfo, 'Cinema Ostertor')
    db_metainfo = find_and_change_case_errors(db_programinfo, db_metainfo, 'Schauburg')
    db_metainfo = find_and_change_case_errors(db_programinfo, db_metainfo, 'Atlantis')
    db_metainfo = find_and_change_case_errors(db_programinfo, db_metainfo, 'Gondel')
    return db_metainfo


def find_and_change_case_errors(db_programinfo, db_metainfo, location):
    """for the shows in db_programinfo with no entry in db_metainfo, see if these no matches can be resolved when
    ignoring case. If so, change case of the title db_metainfo to reflect the case in db_programinfo"""
    print(f'\n  working on {location}')

    program_titles = set([programinfo['title']
                          for programinfo in db_programinfo
                          if programinfo['location'] == location])
    meta_titles = set(db_metainfo[location].keys())
    no_matches = program_titles - meta_titles

    if no_matches:
        matches_after_case_change = []

        for no_match in no_matches:
            for meta_title in meta_titles:
                if no_match.lower() == meta_title.lower():
                    adjust_name(db_metainfo, location, matches_after_case_change, meta_title, no_match)
                elif alphanumeric(no_match) == alphanumeric(meta_title):
                    adjust_name(db_metainfo, location, matches_after_case_change, meta_title, no_match)

        no_matches_after_case_change = no_matches - set(matches_after_case_change)

        for title in no_matches_after_case_change:
            print(f'    no meta data found for the show "{title}" in {location}')
    else:
        print("    lookin' good!")
    return db_metainfo


def adjust_name(db_metainfo, location, matches_after_case_change, meta_title, no_match):
    matches_after_case_change.append(no_match)
    metainfo = db_metainfo[location].pop(meta_title)
    db_metainfo[location][no_match] = metainfo
    print(f'    adjusted show title "{meta_title}" to "{no_match}" in db_metainfo')


def alphanumeric(s):
    """convert all adjecent non-alphanumeric characters to a single space, and makes lowercase"""
    s = s.lower()
    return re.sub('[^0-9a-zA-Z]+', ' ', s)

if __name__ == '__main__':
    main()
