import helper
import program as p
import run
import theater as t


def main():
    print("DOIN' SOME TESTIN'")
    test_one_theater(t.Schwankhalle())
    # test_filmkunst(atlantis=True)
    # test_combined_program(new=True)


def test_one_theater(theater):
    """
    Parameters
    ----------
    theater: theater.Theater()
        e.g. t.Schwankhalle()
    """

    print(f'test {theater}')
    try:
        helper.start_driver()
        temp = theater
        temp.update_program()
        temp.update_meta_info()
        temp.annotate_dubbed_films()
        temp.program.print_next_week()
    finally:
        helper.close_driver()


def test_filmkunst(schauburg=False, gondel=False, atlantis=False):
    if schauburg:
        schauburg = t.Filmkunst(
            name="Schauburg",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/schauburg-kino-bremen/shows/movies?mode=widget",
        )
        test_one_theater(schauburg)
    if gondel:
        gondel = t.Filmkunst(
            name="Gondel",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/gondel-filmtheater-bremen/shows/movies?mode=widget",
        )
        test_one_theater(gondel)
    if atlantis:
        atlantis = t.Filmkunst(
            name="Atlantis",
            url="http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html",
            url_program_scrape="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/shows?mode=widget",
            url_meta="https://www.kinoheld.de/kino-bremen/atlantis-filmtheater-bremen/shows/movies?mode=widget",
        )
        test_one_theater(atlantis)


def test_combined_program(new=False):
    """
    test combined program

    test_combined_program() = similar to "run.py"
    test_combined_program(from_file = False) = similar to "run.py -n"
    But then with printing some extra information

    Parameters
    ----------
    new: bool, optional
        if True scrape new program, if False (default) use from file
    """

    comb_pro = p.CombinedProgram()

    if new:
        comb_pro.update_program()
    else:
        comb_pro.program_from_file()

    # PRINTING INFO
    print("".center(100, "-"))
    print("programs in the separate theater objects".center(100, " "))
    for x in comb_pro.theaters:
        print(f"{x.name}: {x.program}")
    program_separate = [t.program for t in comb_pro.theaters]
    length = [len(x.shows) for x in program_separate]
    print(f"{sum(length)}: length shows in separate theaters")

    print(f"combined program".center(100, " "))
    print(comb_pro.program)
    print(f"{len(comb_pro.program.shows)}: lenghts shows in the combined program")

    print("".center(100, "-"))
    print("and now meta info".center(100, " "))
    for x in comb_pro.theaters:
        print(x.name, x.meta_info)

    print("".center(100, "-"))
    print("and finally test program".center(100, " "))
    run.print_header()
    comb_pro.program.print_next_week()

    print("".center(100, "-"))
    run.print_header()
    comb_pro.program.print_today()


if __name__ == '__main__':
    main()
