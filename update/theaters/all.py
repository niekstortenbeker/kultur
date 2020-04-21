from update.theaters.cinemaostertor import CinemaOstertor
from update.theaters.city46 import City46
from update.theaters.filmkunst import Atlantis, Gondel, Schauburg
from update.theaters.glocke import Glocke
from update.theaters.kukoon import Kukoon
from update.theaters.schwankhalle import Schwankhalle
from update.theaters.theaterbremen import TheaterBremen

all_theaters = [
    Schauburg(),
    Gondel(),
    Atlantis(),
    CinemaOstertor(),
    City46(),
    TheaterBremen(),
    Schwankhalle(),
    Glocke(),
    Kukoon(),
]

# used for testing
all_theaters_not_initialized = [
    Schauburg,
    Gondel,
    Atlantis,
    CinemaOstertor,
    City46,
    TheaterBremen,
    Schwankhalle,
    Glocke,
    Kukoon,
]
