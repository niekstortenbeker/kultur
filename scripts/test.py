import helper
import program as p
import run
import theater as t


def main():
    print("DOIN' SOME TESTIN'")
    # test_one_theater(t.Schauburg())
    test_combined_program(new=True)


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
        theater.update_program()
        theater.update_meta_info()
        theater.annotate_dubbed_films()
        theater.program.print_next_week()
    finally:
        helper.close_driver()


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
