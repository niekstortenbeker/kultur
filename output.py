import arrow


# TODO export to HTML


def print_database(db_programinfo, db_metainfo):
    print_database_header()

    day = arrow.utcnow().day  # necessary to print lines between days
    now = arrow.utcnow()
    week_later = now.shift(weeks=+1).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo='Europe/Berlin')

    for programinfo in db_programinfo:
        if programinfo.datetime > now and programinfo.datetime < week_later:
            if programinfo.datetime.day != day:  # print a day separator
                day = programinfo.datetime.day
                print(''.center(50, '-'))

            if programinfo.location in ['Schauburg', 'Gondel', 'Atlantis']:
                if programinfo.language_version:
                    print_programinfo(programinfo) # only print OMUs and OV, skipping german stuff now
                    # TODO print stuff that is in german original

            elif programinfo.location == 'Cinema Ostertor':
                # only interested in films for which I could retrieve information (not very clean maybe)
                if programinfo.title in db_metainfo:
                    # If any language info is present it's probably not dubbed and I want to see it
                    if db_metainfo[programinfo.title]['language']:
                        print_programinfo(programinfo)
                    # Otherwise if it is made in a german speaking country chances are it's not dubbed
                    elif 'deutschland' in db_metainfo[programinfo.title]['country'].lower():
                        print_programinfo(programinfo)
                    elif 'österreich' in db_metainfo[programinfo.title]['country'].lower():
                        print_programinfo(programinfo)
                    elif 'schweiz' in db_metainfo[programinfo.title]['country'].lower():
                        print_programinfo(programinfo)

            else:
                print_programinfo(programinfo)


def print_database_header():
    print()
    print(''.center(50, '-'))
    print('PROGRAM'.center(50, ' '))
    print(''.center(50, '-'))
    print()


def print_programinfo(programinfo):
    print('{} | {} | {} {} | {} | {} | {}'.format(programinfo.datetime.format('ddd MM-DD HH:mm'),
                                                  programinfo.location.center(15, ' '),
                                                  programinfo.artist,
                                                  programinfo.title,
                                                  programinfo.link_info,
                                                  programinfo.info.replace('\n', '. '),
                                                  programinfo.price))

