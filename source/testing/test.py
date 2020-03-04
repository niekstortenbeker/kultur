from helper import webdriver
from program.combinedprogram import CombinedProgram
from theaters.cinemaostertor import CinemaOstertor
import run
import time


def main():
    print("DOIN' SOME TESTIN'")
    test_one_theater(CinemaOstertor())
    # test_combined_program(new=True)
    # run.run(new=True, today=False)
    # run.run(new=False, today=False)
    # run.run(new=False, today=True)


def test_one_theater(theater):
    """
    Parameters
    ----------
    theater: theater.TheaterBase()
        e.g. t.Schwankhalle()
    """

    print(f'\n\ntest {theater}')
    theater.update_program_and_meta_info(start_driver=True)
    print(f'program: {theater.program}')
    print(f'meta: {theater.meta_info}')
    theater.program.print_next_week()


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

    comb_pro = CombinedProgram()

    if new:
        comb_pro._update_program()

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
