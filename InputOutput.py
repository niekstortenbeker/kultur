import arrow
import json
import os
# TODO export to HTML

basepath = os.path.dirname(os.path.abspath(__file__))

def remove_arrow_objects_in_programinfo(db_programinfo):
    for programinfo in db_programinfo:
        programinfo['datetime'] = programinfo['datetime'].for_json()
    return db_programinfo

def db_to_json(db_programinfo, db_metainfo):
    with open(os.path.join(basepath, 'db_programinfo.json'), 'w') as f:
        json.dump(db_programinfo, f, indent=2)
        print('saved programinfo to JSON')

    with open(os.path.join(basepath, 'db_metainfo.json'), 'w') as f:
        json.dump(db_metainfo, f, indent=2)
        print('saved metainfo to JSON')

    with open(os.path.join(basepath, 'scraping_date.txt'), 'w') as f:
        f.write(arrow.now().format())

def json_to_db():
    with open(os.path.join(basepath, 'db_programinfo.json'), 'r') as f:
        db_programinfo = json.load(f)

    with open(os.path.join(basepath, 'db_metainfo.json'), 'r') as f:
        db_metainfo = json.load(f)

    with open(os.path.join(basepath, 'scraping_date.txt'), 'r') as f:
        scraping_date = f.read()
    return db_programinfo, db_metainfo, scraping_date


def insert_arrow_objects_in_programinfo(db_programinfo):
    for programinfo in db_programinfo:
        programinfo['datetime'] = arrow.get(programinfo['datetime'])
    return db_programinfo


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
                if programinfo['language_version']:
                    print_programinfo(programinfo) # print OMUs and OV
                else:
                    if_german_print_programinfo(programinfo, db_metainfo, programinfo['location'])

            elif programinfo['location'] == 'Cinema Ostertor':
                # If any language info is present it's probably not dubbed and I want to see it
                title = programinfo['title']
                try:
                    if db_metainfo['Cinema Ostertor'][title]['language']:
                        print_programinfo(programinfo)
                except KeyError:
                    pass
                if_german_print_programinfo(programinfo, db_metainfo, 'Cinema Ostertor')


            else:
                print_programinfo(programinfo)


def print_database_header():
    print()
    print(''.center(100, '-'))
    print('PROGRAM'.center(100, ' '))
    print(''.center(100, '-'))
    print()


def print_programinfo(programinfo):
    print('{} | {} | {} {} | {} | {} | {}'.format(programinfo['datetime'].format('ddd MM-DD HH:mm'),
                                                  programinfo['location'].center(15, ' '),
                                                  programinfo['artist'],
                                                  programinfo['title'],
                                                  programinfo['link_info'],
                                                  programinfo['info'].replace('\n', '. '),
                                                  programinfo['price']))

def if_german_print_programinfo(programinfo, db_metainfo, location_name):
    title = programinfo['title']
    try:
        country = db_metainfo[location_name][title]['country'].lower()
        # Otherwise if it is made in a german speaking country chances are it's not dubbed
        if 'deutschland' in country:
            print_programinfo(programinfo)
        elif 'österreich' in country:
            print_programinfo(programinfo)
        elif 'schweiz' in country:
            print_programinfo(programinfo)
    except KeyError:
        pass

