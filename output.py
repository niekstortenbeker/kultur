import arrow
import json
from pprint import pprint

# TODO export to HTML
# TODO there is stuff here that should be database handling or something


def remove_arrow_objects_in_programinfo(db_programinfo):
    for programinfo in db_programinfo:
        programinfo['datetime'] = programinfo['datetime'].for_json()
    return db_programinfo

def db_to_json(db_programinfo, db_metainfo):
    with open('db_programinfo.json', 'w') as f:
        json.dump(db_programinfo, f, indent=2)
        print('saved programinfo to JSON')

    with open('db_metainfo.json', 'w') as f:
        json.dump(db_metainfo, f, indent=2)
        print('saved metainfo to JSON')

def json_to_db():
    with open('db_programinfo.json', 'r') as f:
        db_programinfo = json.load(f)

    with open('db_metainfo.json', 'r') as f:
        db_metainfo = json.load(f)
    return db_programinfo, db_metainfo


def insert_arrow_objects_in_programinfo(db_programinfo):
    for programinfo in db_programinfo:
        programinfo['datetime'] = arrow.get(programinfo['datetime'])
    return db_programinfo


# TODO this should probably go somewhere else
def quality_control_dbs(db_programinfo, db_metainfo):
    db_metainfo = check_meta_for_program(db_programinfo, db_metainfo, 'Cinema Ostertor')
    db_metainfo = check_meta_for_program(db_programinfo, db_metainfo, 'Filmkunst')
    return db_metainfo


def check_meta_for_program(db_programinfo, db_metainfo, location):
    # Find the titles that are present in programinfo but not in metainfo ("no_matches")
    program_titles = set([programinfo['title']
                                   for programinfo in db_programinfo
                                   if programinfo['location'] == location])
    meta_titles = list(db_metainfo[location].keys())
    no_matches = find_no_matches_iterables(loop_iterable=program_titles,
                                           search_iterable=meta_titles)
    if no_matches:
        # see if the no_matches can match when ignoring case, if so adjust the db_metainfo
        matches_after_case_change = []
        for no_match in no_matches:
            for meta_title in meta_titles:
                if no_match.lower() == meta_title.lower():
                    matches_after_case_change.append(no_match)
                    metainfo = db_metainfo[location].pop(meta_title)
                    db_metainfo[location][no_match] = metainfo
                    print(f'adjusted show title "{meta_title}" to "{no_match}" in db_metainfo')
        no_matches_after_case_change = find_no_matches_iterables(loop_iterable=no_matches,
                                                                 search_iterable=matches_after_case_change)
        for title in no_matches_after_case_change:
            print(f'no meta data found for the show "{title}" in {location}')
    return db_metainfo

#TODO are there already functions for this?
def find_no_matches_iterables(loop_iterable, search_iterable):
    """loops over one iterable to search if the items are present in the second iterable. If not, append these to a list"""
    no_matches = []
    for title in loop_iterable:
        if title not in search_iterable:
            no_matches.append(title)
    return no_matches



def print_database(db_programinfo, db_metainfo):
    print_database_header()

    day = arrow.utcnow().day  # necessary to print lines between days
    now = arrow.utcnow()
    week_later = now.shift(weeks=+1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Europe/Berlin')
    for programinfo in db_programinfo:
        if programinfo['datetime'] > now and programinfo['datetime'] < week_later:
            if programinfo['datetime'].day != day:  # print a day separator
                day = programinfo['datetime'].day
                print(''.center(50, '-'))

            if programinfo['location'] in ['Schauburg', 'Gondel', 'Atlantis']:
                title = programinfo['title']
                if programinfo['language_version']:
                    print_programinfo(programinfo) # print OMUs and OV
                else:
                    try:
                        country = db_metainfo['Filmkunst'][title]['country'].lower()
                        # Otherwise if it is made in a german speaking country chances are it's not dubbed
                        if 'deutschland' in country:
                            print_programinfo(programinfo)
                        elif 'österreich' in country:
                            print_programinfo(programinfo)
                        elif 'schweiz' in country:
                            print_programinfo(programinfo)
                    except KeyError:
                        print(f'!keyerror for "{title}" in Filmkunst')

            elif programinfo['location'] == 'Cinema Ostertor':
                title = programinfo['title']
                try:
                    country = db_metainfo['Cinema Ostertor'][title]['country'].lower()
                    # If any language info is present it's probably not dubbed and I want to see it
                    if db_metainfo['Cinema Ostertor'][title]['language']:
                        print_programinfo(programinfo)
                    # Otherwise if it is made in a german speaking country chances are it's not dubbed
                    elif 'deutschland' in country:
                        print_programinfo(programinfo)
                    elif 'österreich' in country:
                        print_programinfo(programinfo)
                    elif 'schweiz' in country:
                        print_programinfo(programinfo)
                except KeyError:
                    print(f'!keyerror for "{title}" in Cinema Ostertor')

            else:
                print_programinfo(programinfo)


def print_database_header():
    print()
    print(''.center(50, '-'))
    print('PROGRAM'.center(50, ' '))
    print(''.center(50, '-'))
    print()


def print_programinfo(programinfo):
    print('{} | {} | {} {} | {} | {} | {}'.format(programinfo['datetime'].format('ddd MM-DD HH:mm'),
                                                  programinfo['location'].center(15, ' '),
                                                  programinfo['artist'],
                                                  programinfo['title'],
                                                  programinfo['link_info'],
                                                  programinfo['info'].replace('\n', '. '),
                                                  programinfo['price']))

