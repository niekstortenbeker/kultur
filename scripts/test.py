import kultur
import helper
import program
import program as pro

# city46 = kultur.City46()
# city46.update_program()

# helper.start_driver()
# try:
# ostertor = webscraping.CinemaOstertor()
# ostertor.update_program()
# ostertor.update_meta_info()
# print(ostertor.meta_info)
# theater_bremen = webscraping.TheaterBremen()
# theater_bremen.update_program()
# filmkunst = webscraping.Filmkunst()
# filmkunst.update_program()
# schwankhalle = webscraping.Schwankhalle()
# schwankhalle.update_program()
# kukoon = webscraping.Kukoon()
# kukoon.update_program()
# glocke = webscraping.Glocke()
# glocke = glocke.update_program()
# finally:
    # helper.close_driver()

p = program.CombinedProgram()
# print(f"program / theater: {[t.program for t in p.theaters]}")
# print(f"combined program: {p.program}")
#
# SELECT ONE OF THE TWO
p.update_program()
# p.program_from_file()
#
# PRINTING INFO
print("".center(100, "-"))
print("programs in the separate theater objects".center(100, " "))
for t in p.theaters:
    print(f"{t.name}: {t.program}")

program = [t.program for t in p.theaters]
length = [len(p.shows) for p in program]
print(f"{sum(length)}: length shows in separate theaters")

print(f"combined program".center(100, " "))
print(p.program)
print(f"{len(p.program.shows)}: lenghts shows in the combined program")

print("".center(100, "-"))
print("and now meta info".center(100, " "))
for t in p.theaters:
    print(t.name, t.meta_info)

print("".center(100, "-"))
print("and finally test program".center(100, " "))
pro.print_header()
p.program.print_next_week()

print("".center(100, "-"))
pro.print_header()
p.program.print_today()
