import random
from typing import List, Union

import arrow
from data.show import Show
from update.services.metainfo import MetaInfo
from update.theaters.theaterbase import TheaterBase

Arrow = arrow.arrow.Arrow

fake_data_container = {
    "title": [
        "Enkel f\u00fcr Anf\u00e4nger",
        "Die K\u00e4nguru-Chroniken",
        "Just Mercy",
        "Parasite",
        "Intrige",
        "Emma",
        "La V\u00e9rit\u00e9 - Leben und l\u00fcgen lassen",
        "Little Women",
        "JENSEITS DES SICHTBAREN - HILMA AF KLINT",
        "DAS GEHEIME LEBEN DER B\u00c4UME",
        "FOR SAMA",
        "CRESCENDO \u2013 #MAKEMUSICNOTWAR",
        "Lindenberg! Mach dein Ding!",
        "Shaun das Schaf - Der Film: UFO-Alarm",
        "Sneak Preview (OV mit Untertiteln)",
        "Parasite (kor. OmU)",
        "Cine Mar - Surf Movie Night - Spring Tour 2020",
        "Best of Outdoor 2020",
        "Royal Opera House 2019/20: Fidelio",
        "La V\u00e9rit\u00e9 - Leben und l\u00fcgen lassen",
        "La Propera Pell (Katal. Omengl.UT)",
        "Die rote Zora und ihre Bande",
        "Jakob Lenz",
        "7. Philharmonisches Konzert",
        "Listen",
        "Jugend ohne Gott",
        "BOY",
        "Fr\u00fchlingserwachen",
        "Turritopsis dohrnii",
        "Zimmer frei \u2013 ein feministisches Casting mit B\u00fcrgermeister",
        "\u203aValentin\u2039",
        "\u203aOh My\u2039",
        "\u203aLet\u2019s talk about Sex & Porno\u2039",
        "26. Landesschultheatertreffen Bremen",
        "Die Deutsche Kammerphilharmonie Bremen - 1. Hanse II-Abonnementkonzert - \u00bbUnvollendet genial\u00ab",
        "Biyon Kattilathu - \u00bb... weil jeder Tag besonders ist\u00ab - Tour 2020",
        "Die Unfassbaren - \u00bbComedy-Zauberei &amp; Hypnose\u00ab",
        "Filmabend \u2013 OSCAR\u00ae Shorts 2020 \u2013 Live Action",
    ],
    "category": ["cinema", "music", "stage"],
    "description": [
        "(*) Kom\u00f6die * Deutschland * Regie: Dani Levy;  * Drehbuch: ;\n(*) Darsteller: Dimitrij Schaad, Rosalie Thomass, Volker Zack, Adnan Maral, Tim Seyfi, Oskar Strohecker, Carmen-Maja Antoni, Henry H\u00fcbchen, Bettina Lamprecht, Daniel Zillmann, Marc-Uwe Kling;\nDas K\u00e4nguru zieht bei seinem Nachbarn, dem unterambitionierten Kleink\u00fcnstler Marc-Uwe, ein. Doch kurz darauf rei\u00dft ein rechtspopulistischer Immobilienhai die halbe Nachbarschaft ab, um mitten in Berlin-Kreuzberg das Hauptquartier der internationalen Nationalisten zu bauen. Das findet das K\u00e4nguru gar nicht gut. Es ist n\u00e4mlich Kommunist. (\u00c4h ja, das hatte ich vergessen zu erw\u00e4hnen.) Jedenfalls entwickelt es einen genialen Plan. Und dann noch einen, weil Marc-Uwe den ersten nicht verstanden hat. Und noch einen dritten, weil der zweite nicht funktioniert hat. Den Rest kann man sich ja denken. Vier Nazis, eine Hasenpfote, drei Sportwagen, ein Psychotherapeut, eine Penthouse-Party und am Ende ein gro\u00dfer Anti-Terror-Anschlag, der dem rechten Treiben ein Ende setzen soll. Nach einer wahren Begebenheit. (Quelle: Verleih)",
        "(*) Thriller * S\u00fcdkorea * Regie: Bong Joon Ho;  * Drehbuch: ;\n(*) Darsteller: Song Kang Ho, Lee Sun Kyun, Cho Yeo Jeong, Choi Woo Shik, Park So Dam, Lee Jung Eun, Chang Hyae Jin;\nFamilie Kim ist ganz unten angekommen: Vater, Mutter, Sohn und Tochter hausen in einem gr\u00fcnlich-schummrigen Keller, kriechen f\u00fcr kostenloses W-LAN in jeden Winkel und sind sich f\u00fcr keinen Aushilfsjob zu schade. Erst als der J\u00fcngste eine Anstellung als Nachhilfelehrer in der todschicken Villa der Familie Park antritt, steigen die Kims ein ins Karussell der Klassenk\u00e4mpfe. Mit findigen Tricksereien, bemerkenswertem Talent und gro\u00dfem Mannschaftsgeist gelingt es ihnen, die bisherigen Bediensteten der Familie Park nach und nach loszuwerden. Bald schon sind die Kims unverzichtbar f\u00fcr ihre neuen Herrschaften. Doch dann l\u00f6st ein unerwarteter Zwischenfall eine Kette von Ereignissen aus, die so unvorhersehbar wie unfassbar sind. (Quelle: Verleih)",
        "(*) Drama * USA * Regie: Destin Daniel Cretton;  * Drehbuch: ;\n(*) Darsteller: Michael B. Jordan, Jamie Foxx, Brie Larson;\nAls junger, vielversprechender Anwalt kann sich Bryan Stevenson (Michael B. Jordan) nach seinem Abschluss in Harvard aussuchen, wo er arbeitet. Sein Antrieb ist aber nicht etwa die M\u00f6glichkeit, viel Geld zu verdienen, sondern vor allem denen zu helfen, die seine Hilfe ganz besonders brauchen. Er geht nach Alabama, wo er sich an der Seite von Anw\u00e4ltin Eva Ansley (Brie Larson) f\u00fcr zu unrecht Verurteilte einzusetzen - und macht mit einem seiner ersten F\u00e4lle gleich Schlagzeilen: Denn Walter McMillian (Jamie Foxx) soll einen grausamen Mord begangen haben, f\u00fcr den er zum Tode verurteilt wurde. Und das obwohl ausreichend Beweise f\u00fcr seine Unschuld vorliegen. Belastet wird der angebliche T\u00e4ter nur durch die Aussage eines Kriminellen, der auch noch guten Grund hat, zu l\u00fcgen. Doch Bryan l\u00e4sst nicht locker und nimmt sich in seinen ersten Berufsjahren zahlreichen F\u00e4llen mit geringen Erfolgschancen an, die ihn immer wieder mit offengelegtem Rassismus konfrontieren... (Quelle: Verleih)",
        "Rhonda\nMit authentischen Sixties-Sounds, gro\u00dfen Melodien und markanten Blue-Eyed-Soul-Vibes laden Rhonda aus Hamburg 2014 zum Timetravel-Tanz. Die f\u00fcnf aus Bremen und Hamburg stammenden Musiker Milo Milone (Gesang), Ben Schadow (Gitarre), Jan Fabricius (Bass), Offer Stock (Orgel) und Gunnar Riedel (Schlagzeug) sind in norddeutschen Szene-Kreisen l\u00e4ngst keine Unbekannten mehr, als sie sich im Mai 2013 zusammentun um unter dem Rhonda-Banner alte Soul-Erinnerungen aufzufrischen. Ein Gro\u00dfteil der Band spielte zuvor bereits in mehreren Indie-Bands - darunter auch die Trashmonkeys, die es ihrerseits Anfang der Nullerjahre ins Cramps-Vorprogramm schafften.",
        "Die Cine Mar - Surf Movie Night, nimmt alle Meeress\u00fcchtigen mit um die ganze Welt, ohne dass sie daf\u00fcr den Kinosaal verlassen m\u00fcssen und bietet der Surf-Community Europas ein einzigartiges Event, um sich \u2013 auch w\u00e4hrend man auf die n\u00e4chste Welle wartet \u2013 zusammenzufinden und gemeinsam der Leidenschaft des Surfens zu widmen.",
        "\n\n\n\nIm Mai 2015 ver\u00f6ffentlichte Peter Wohlleben sein Buch \u201eDas geheime Leben der B\u00e4ume\u201c und st\u00fcrmte damit sofort die Bestsellerlisten.\u00a0Wie schafft es ein Buch \u00fcber B\u00e4ume, die Menschen so in den Bann zu ziehen? Vielleicht deswegen, weil es dem F\u00f6rster aus der Ortschaft Wershofen gelingt, anschaulich wie kein anderer \u00fcber den deutschen Wald zu schreiben. So l\u00e4sst er die Leser an seiner Erkenntnis teilhaben, dass B\u00e4ume dazu in der Lage sind, miteinander zu kommunizieren. Weiterhin gibt er Waldf\u00fchrungen und h\u00e4lt Lesungen, sodass er den Menschen die au\u00dfergew\u00f6hnlichen Lebewesen n\u00e4her bringt und seine Leserschar immer weiter anw\u00e4chst. Seine Leidenschaft hat er zum Beruf gemacht: Angefangen als Beamter in der Landesforstverwaltung Rheinland-Pfalz sprengte er sich bald von den Ketten der Verwaltung frei, stellte zusammen mit der Gemeinde Wershofen einen uralten Buchenwald unter Schutz und gr\u00fcndete eine Waldakademie. Seither reist er durch die Welt, besucht in Schweden den \u00e4ltesten Baum des Planeten und unterst\u00fctzt die Demonstranten im Hambacher Forst. Dabei gilt er vielen als Vorbild, denn Peter Wohlleben ist eins bewusst: Wenn es den B\u00e4umen gut geht, werden auch die Menschen \u00fcberleben.\n\n\n\n",
        "In ihrem Dokumentarfilm zeigen die Filmemacher Petra H\u00f6fer und Freddie R\u00f6ckenhaus ein ganz besonderes Land aus einer v\u00f6llig neuen Perspektive: Russland.\u00a0So vielf\u00e4ltig wie das Land, so bunt sind auch die Aufnahmen. Egal ob \u00fcberf\u00fcllte Mega-Citys, wilde Tiere, dann wieder menschenleere Landschaften oder die Transsibirische Eisenbahn, die zwischen dem Sibirien und Wladiwostok pendelt: Alle elf Zeitzonen werden in der Doku bildgewaltig festgehalten und bieten einen einzigartigen Blick auf ein ganz besonderes Land.",
        "Auf der Alpaka-Farm der Familie Gardner schl\u00e4gt ein mysteri\u00f6ser Meteorit ein, der merkw\u00fcrdige Ver\u00e4nderungen mit sich bringt.Kult-Regisseur Richard Stanley (\u201eHardware\u201c) inszeniert die Kurzgeschichte von H.P. Lovecraft (1927) als psychedelisches B-Movie, von den Produzenten von \u201eMandy\u201c, wieder mit Nicolas Cage in der Hauptrolle.",
        "Urauff\u00fchrung / 6+ / von John von D\u00fcffel / nach dem Roman von Kurt Held / Karten f\u00fcr Vormittagsvorstellungen f\u00fcr Schulklassen erhalten Sie beim Service f\u00fcr Schulen und Gruppen unter Tel 0421\u20093653-340, Fax 0421\u20093653-934 oder schulen@theaterbremen.de ",
        "Kammeroper Nr. 2 von Wolfgang Rihm / Text von Michael Fr\u00f6hling frei nach Georg B\u00fcchners Novelle \u201eLenz\u201c / 19 Uhr Einf\u00fchrung / Blauer Sonntag: 20 \u20ac auf allen Pl\u00e4tzen! / ",
        "von dem Hildesheimer Studierenden-Kollektiv taft. / 14+",
        "15+ / nach dem Roman von \u00d6d\u00f6n von Horv\u00e1th / Bremer Schulen Eintritt frei!",
        "Ein Mix aus Jazz, Pop und Weltmusik / Pr\u00e4sentiert vom Kulturforum T\u00fcrkei / Er\u00f6ffnungskonzert der K\u00dcLT\u00dcRALE 2020",
        "ntin\u2039\u00a0 / Graphic Novel-Lesung",
        "\u203aOh My\u2039\u00a0 / Performance f\u00fcr Erwachsene",
        "Veranstaltungskategorien: Kukoon-Format, Workshop",
    ],
    "language_version": ["OmU", "Alternativer Content", "Live", "OV", "OmdU", "OmeU"],
    "dubbed": [True, *[False for _ in range(5)]],
    "url_info": [
        "http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html",
        "http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html",
        "http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html",
        "https://cinema-ostertor.de/programm",
        "http://www.theaterbremen.de/de_DE/kalender/die-rote-zora-und-ihre-bande.16366572",
        "https://theaterbremen.eventim-inhouse.de/webshop/webticket/shop?event=1695#termine",
        "https://schwankhalle.de/spielplan/unverschaemt",
        "https://schwankhalle.de/spielplan/genehr-valentin-780.html",
        "https://www.glocke.de//de/Veranstaltungssuche/01/03/2020/7733/Die-Deutsche-Kammerphilharmonie-Bremen1--Hanse-II-AbonnementkonzertUnvollendet-genial",
        "https://kukoon.de/event/kunst-mit-kids-7/",
    ],
    "url_tickets": [
        "http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Gondel.html",
        "http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Atlantis.html",
        "http://www.bremerfilmkunsttheater.de/Kino_Reservierungen/Schauburg.html",
        "https://cinema-ostertor.de/programm",
        "http://www.theaterbremen.de/de_DE/kalender/die-rote-zora-und-ihre-bande.16366572",
        "https://theaterbremen.eventim-inhouse.de/webshop/webticket/shop?event=1695#termine",
        "https://schwankhalle.de/spielplan/unverschaemt",
        "https://schwankhalle.de/spielplan/genehr-valentin-780.html",
        "https://www.glocke.de//de/Veranstaltungssuche/01/03/2020/7733/Die-Deutsche-Kammerphilharmonie-Bremen1--Hanse-II-AbonnementkonzertUnvollendet-genial",
        "https://kukoon.de/event/kunst-mit-kids-7/",
    ],
}


def get(column: str) -> str:
    """get one random fake item for a column of Show"""
    return random.choice(fake_data_container[column])


def get_value_or_empty(column: str) -> Union[str, None, bool]:
    """get one random fake item for a column of Show, or an empty string, or None"""
    value = random.choice(fake_data_container[column])
    return random.choice([value, value, value, value, "", None])


def get_value_or_none(column: str) -> Union[str, None, bool]:
    """get one random fake item for a column of Show, or an empty string, or None"""
    value = random.choice(fake_data_container[column])
    return random.choice([value, value, None])


def show_date_time(max_days=10) -> Arrow:
    """return a arrow object within the next max_days days rounded to ten minutes"""
    time = random.randrange(
        arrow.now("Europe/Berlin").timestamp,
        arrow.now("Europe/Berlin").shift(days=+max_days).timestamp,
    )
    return arrow.get(time - time % (60 * 15))  # round to ten minutes


def show(location):
    return Show(
        date_time=show_date_time(),
        title=get("title"),
        location=location,
        category=get("category"),
        description=get_value_or_empty("description"),
        language_version=get_value_or_empty("language_version"),
        dubbed=get_value_or_none("dubbed"),
        url_info=get_value_or_empty("url_info"),
        url_tickets=get_value_or_empty("url_tickets"),
    )


def program(location) -> List[Show]:
    """return can be used as a program from TheaterBase.program"""
    if isinstance(location, TheaterBase):
        location = location.name
    elif type(location) != str:
        TypeError("only TheaterBase or str accepted")

    return [show(location) for _ in range(4 * 10)]


def light_program(location) -> List[Show]:
    """return can be used as a program from TheaterBase.program"""
    if isinstance(location, TheaterBase):
        location = location.name
    elif type(location) != str:
        TypeError("only TheaterBase or str accepted")

    return [show(location) for _ in range(2)]


def meta_info():
    meta_info_dict = {}
    for idx in range(0, 10):
        title = fake_data_container["title"][idx]
        meta_info_dict[title] = MetaInfo(
            title=title,
            title_original=title,
            description=get("description"),
            country="USA",
            url_info=get("url_info"),
        )
    return meta_info_dict
