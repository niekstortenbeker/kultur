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


def make_current_program(db_programinfo, db_metainfo):
    #TODO I'm not really happy with this function, its not easy to understand
    current_program = []
    day = arrow.utcnow().day  # necessary to identify day separator
    now = arrow.utcnow()
    week_later = now.shift(weeks=+1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Europe/Berlin')
    for programinfo in db_programinfo:
        if now < programinfo['datetime'] < week_later:
            title = programinfo['title']
            if programinfo['datetime'].day != day:  # append a day separator
                day = programinfo['datetime'].day
                current_program.append({'title': 'day_separator', 'day':day}) # TODO maybe this is a bit of a hack

            if programinfo['location'] in ['Schauburg', 'Gondel', 'Atlantis']:
                try:
                    metainfo = db_metainfo[programinfo['location']][title]
                except KeyError:
                    metainfo = ''
                if programinfo['language_version']:  # save OMUs and OV
                    current_program_info = save_programinfo(programinfo, metainfo=metainfo)
                    current_program.append(current_program_info)
                else:  # save what are probably original versions
                    if is_german(title, programinfo['location'], db_metainfo):
                        current_program_info = save_programinfo(programinfo, metainfo=metainfo)
                        current_program.append(current_program_info)

            elif programinfo['location'] == 'Cinema Ostertor':
                try:
                    metainfo = db_metainfo[programinfo['location']][title]
                except KeyError:
                    metainfo = ''
                # If any language info is present it's probably not dubbed and I want to see it
                try:
                    if db_metainfo['Cinema Ostertor'][title]['language']:
                        save_programinfo(programinfo, metainfo)
                except KeyError:
                    pass
                if is_german(title, 'Cinema Ostertor', db_metainfo):
                    current_program_info = save_programinfo(programinfo, metainfo=metainfo)
                    current_program.append(current_program_info)

            else:
                current_program_info = save_programinfo(programinfo)
                current_program.append(current_program_info)
    return current_program


def save_programinfo(programinfo_old, metainfo=None):
    if metainfo:
        programinfo = dict(datetime=programinfo_old['datetime'].format('ddd MM-DD HH:mm'),
                           location=programinfo_old['location'],
                           artist=programinfo_old['artist'],
                           title=programinfo_old['title'],
                           link_info=programinfo_old['link_info'],
                           info=programinfo_old['info'],
                           price=programinfo_old['price'],
                           title_original=metainfo['title_original'],
                           country=metainfo['country'],
                           year=metainfo['year'],
                           genre=metainfo['genre'],
                           duration=metainfo['duration'],
                           director=metainfo['director'],
                           language=metainfo['language'],
                           description=metainfo['description'],
                           img_poster=metainfo['img_poster'],
                           img_screenshot=metainfo['img_screenshot'])
    else:
        programinfo = dict(datetime=programinfo_old['datetime'].format('ddd MM-DD HH:mm'),
                           location=programinfo_old['location'],
                           artist=programinfo_old['artist'],
                           title=programinfo_old['title'],
                           link_info=programinfo_old['link_info'],
                           info=programinfo_old['info'],
                           price=programinfo_old['price'],
                           title_original='',
                           country='',
                           year='',
                           genre='',
                           duration='',
                           director='',
                           language='',
                           description='',
                           img_poster='',
                           img_screenshot='')
    return programinfo


def is_german(title, location_name, db_metainfo):
    try:
        country = db_metainfo[location_name][title]['country'].lower()
        # Otherwise if it is made in a german speaking country chances are it's not dubbed
        if 'deutschland' in country:
            return True
        elif 'österreich' in country:
            return True
        elif 'schweiz' in country:
            return True
        else:
            return False
    except KeyError:
        return False


def print_database_header():
    print()
    print(''.center(100, '-'))
    print('PROGRAM'.center(100, ' '))
    print(''.center(100, '-'))
    print()


def print_program(program):
    for programinfo in program:
        if programinfo['title'] == 'day_separator':
            print(''.center(50, '-'))
        else:
            print('{} | {} | {} {} | {} | {} | {}'.format(programinfo['datetime'],
                                                          programinfo['location'].center(15, ' '),
                                                          programinfo['artist'],
                                                          programinfo['title'],
                                                          programinfo['link_info'],
                                                          programinfo['info'].replace('\n', '. '),
                                                          programinfo['price']))



