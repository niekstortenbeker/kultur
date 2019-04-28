import arrow


def make_current_program(db_programinfo, db_metainfo, last_date):
    """Only save shows from now to last_date, don't show dubbed films, only save relevant info"""
    program_for_printing = []
    now = arrow.utcnow()

    for show in db_programinfo:
        if show['datetime'] < now:
            continue
        elif show['datetime'] > last_date:
            break
        elif is_probably_dubbed_film(show, db_metainfo):
            continue
        else:
            show = save_programinfo_for_printing(show)
            program_for_printing.append(show)

    return program_for_printing


def is_probably_dubbed_film(programinfo, db_metainfo):
    """Return True if programinfo is probably dubbed. Of cinemas with dubbed films, return False if it is explicitely an
    OmU (etc) or if the movie was made in an german speaking country"""
    if not programinfo['location'] in ['Schauburg', 'Gondel', 'Atlantis', 'Cinema Ostertor']:
        return False
    elif film_is_probably_dubbed(db_metainfo, programinfo):
        return True
    else:
        return False


def film_is_probably_dubbed(db_metainfo, programinfo):
    title = programinfo['title']
    if programinfo['language_version']:  # OMUs and OV
        return False
    elif is_german(title, programinfo['location'], db_metainfo):
        return False
    else:
        return True


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


# def has_meta_info(programinfo, db_metainfo):
#     """return True if programinfo has metainfo. So far only metainfos for four cinemas"""
#     if programinfo['location'] in ['Schauburg', 'Gondel', 'Atlantis', 'Cinema Ostertor']:
#         title = programinfo['title']
#         location = programinfo['location']
#         if title in db_metainfo[location]:
#             return True
#         else:
#             return False
#     else:
#         return False


def save_programinfo_for_printing(programinfo_old):
    programinfo = dict(datetime=programinfo_old['datetime'].format('ddd MM-DD HH:mm'),
                       location=programinfo_old['location'].center(15, ' '),
                       artist=programinfo_old['artist'],
                       title=programinfo_old['title'],
                       link_info=programinfo_old['link_info'],
                       info=programinfo_old['info'].replace('\n', '. '),
                       price=programinfo_old['price'],
                       )
    return programinfo


def print_program(program, scraping_date):
    print(f'\nthis program uses a database made on: {scraping_date}')
    print(''.center(50, '-'))
    old_day = program[0]['datetime'][0:3]
    for programinfo in program:
        # print day separator
        day = programinfo['datetime'][0:3]
        if day != old_day:
            print(''.center(50, '-'))
            old_day = day
        # print program
        print('{} | {} | {} {} | {} | {} | {}'.format(programinfo['datetime'],
                                                      programinfo['location'],
                                                      programinfo['artist'],
                                                      programinfo['title'],
                                                      programinfo['link_info'],
                                                      programinfo['info'],
                                                      programinfo['price']))



