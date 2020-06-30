from kultur.update.theaters.cinemaostertor import CinemaOstertor
from kultur.update.theaters.city46 import City46
from kultur.update.theaters.filmkunst import Atlantis, Gondel, Schauburg
from kultur.update.theaters.glocke import Glocke
from kultur.update.theaters.kukoon import Kukoon
from kultur.update.theaters.schwankhalle import Schwankhalle
from kultur.update.theaters.theaterbremen import TheaterBremen

all_theaters = [
    Schauburg(),
    Gondel(),
    Atlantis(),
    CinemaOstertor(),
    City46(),
    TheaterBremen(),
    Schwankhalle(),
    # Glocke(),
    Kukoon(),
]

# used for testing
all_theaters_not_initialized = [
    Schauburg,
    # Gondel,
    Atlantis,
    CinemaOstertor,
    City46,
    TheaterBremen,
    Schwankhalle,
    Glocke,
    Kukoon,
]

# Get dictionary that can be used for kultur.commands.data.get_location_names
if __name__ == "__main__":
    names = {s.name.replace(" ", "").lower(): s.name for s in all_theaters}
    print(names)
