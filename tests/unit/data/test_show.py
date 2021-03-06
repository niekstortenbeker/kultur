import arrow
import pytest
from kultur.data.dbsession import DbSession


def test_default_description_end_returns_correct(database_empty, minimal_show):
    # GIVEN a Show object with known description and an initialized database
    minimal_show.description = "Als junger, vielversprechender Anwalt kann sich Bryan Stevenson (Michael B. Jordan) nach seinem Abschluss in Harvard aussuchen, wo er arbeitet. Sein Antrieb ist aber nicht etwa die Möglichkeit, viel Geld zu verdienen, sondern vor allem denen zu helfen, die seine Hilfe ganz besonders brauchen. Er geht nach Alabama, wo er sich an der Seite von Anwältin Eva Ansley (Brie Larson) für zu unrecht Verurteilte einzusetzen - und macht mit einem seiner ersten Fälle gleich Schlagzeilen: Denn Walter McMillian (Jamie Foxx) soll einen grausamen Mord begangen haben, für den er zum Tode verurteilt wurde. Und das obwohl ausreichend Beweise für seine Unschuld vorliegen. Belastet wird der angebliche Täter nur durch die Aussage eines Kriminellen, der auch noch guten Grund hat, zu lügen. Doch Bryan lässt nicht locker und nimmt sich in seinen ersten Berufsjahren zahlreichen Fällen mit geringen Erfolgschancen an, die ihn immer wieder mit offengelegtem Rassismus konfrontieren... (Quelle: Verleih)"  # noqa
    # WHEN the Show is added to the database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN minimal_show.description_end should return the right format
    expectation = " Er geht nach Alabama, wo er sich an der Seite von Anwältin Eva Ansley (Brie Larson) für zu unrecht Verurteilte einzusetzen - und macht mit einem seiner ersten Fälle gleich Schlagzeilen: Denn Walter McMillian (Jamie Foxx) soll einen grausamen Mord begangen haben, für den er zum Tode verurteilt wurde. Und das obwohl ausreichend Beweise für seine Unschuld vorliegen. Belastet wird der angebliche Täter nur durch die Aussage eines Kriminellen, der auch noch guten Grund hat, zu lügen. Doch Bryan lässt nicht locker und nimmt sich in seinen ersten Berufsjahren zahlreichen Fällen mit geringen Erfolgschancen an, die ihn immer wieder mit offengelegtem Rassismus konfrontieren... (Quelle: Verleih)"  # noqa
    assert minimal_show.description_end == expectation


def test_default_description_start_returns_correct_dot(database_empty, minimal_show):
    # GIVEN a Show object with known description and an initialized database
    minimal_show.description = "Als junger, vielversprechender Anwalt kann sich Bryan Stevenson (Michael B. Jordan) nach seinem Abschluss in Harvard aussuchen, wo er arbeitet. Sein Antrieb ist aber nicht etwa die Möglichkeit, viel Geld zu verdienen, sondern vor allem denen zu helfen, die seine Hilfe ganz besonders brauchen. Er geht nach Alabama, wo er sich an der Seite von Anwältin Eva Ansley (Brie Larson) für zu unrecht Verurteilte einzusetzen - und macht mit einem seiner ersten Fälle gleich Schlagzeilen: Denn Walter McMillian (Jamie Foxx) soll einen grausamen Mord begangen haben, für den er zum Tode verurteilt wurde. Und das obwohl ausreichend Beweise für seine Unschuld vorliegen. Belastet wird der angebliche Täter nur durch die Aussage eines Kriminellen, der auch noch guten Grund hat, zu lügen. Doch Bryan lässt nicht locker und nimmt sich in seinen ersten Berufsjahren zahlreichen Fällen mit geringen Erfolgschancen an, die ihn immer wieder mit offengelegtem Rassismus konfrontieren... (Quelle: Verleih)"  # noqa
    # WHEN the Show is added to the database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN minimal_show.description_start should return the right format
    expectation = "Als junger, vielversprechender Anwalt kann sich Bryan Stevenson (Michael B. Jordan) nach seinem Abschluss in Harvard aussuchen, wo er arbeitet. Sein Antrieb ist aber nicht etwa die Möglichkeit, viel Geld zu verdienen, sondern vor allem denen zu helfen, die seine Hilfe ganz besonders brauchen."  # noqa
    assert minimal_show.description_start == expectation


def test_default_description_start_returns_correct_semicolon(
    database_empty, minimal_show
):
    # GIVEN a Show object with known description and an initialized database
    minimal_show.description = "Als junger, vielversprechender Anwalt kann sich Bryan Stevenson (Michael B. Jordan) nach seinem Abschluss in Harvard aussuchen, wo er arbeitet. Sein Antrieb ist aber nicht etwa die Möglichkeit, viel Geld zu verdienen; sondern vor allem denen zu helfen, die seine Hilfe ganz besonders brauchen Er geht nach Alabama wo er sich an der Seite von Anwältin Eva Ansley (Brie Larson) für zu unrecht Verurteilte einzusetzen - und macht mit einem seiner ersten Fälle gleich Schlagzeilen: Denn Walter McMillian (Jamie Foxx) soll einen grausamen Mord begangen haben"  # noqa
    # WHEN the Show is added to the database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN minimal_show.description_start should return the right format
    expectation = "Als junger, vielversprechender Anwalt kann sich Bryan Stevenson (Michael B. Jordan) nach seinem Abschluss in Harvard aussuchen, wo er arbeitet. Sein Antrieb ist aber nicht etwa die Möglichkeit, viel Geld zu verdienen;"  # noqa
    assert minimal_show.description_start == expectation


def test_default_description_start_returns_correct_comma(database_empty, minimal_show):
    # GIVEN a Show object with known description and an initialized database
    minimal_show.description = "Als junger, vielversprechender Anwalt kann sich Bryan Stevenson (Michael B. Jordan) nach seinem Abschluss in Harvard aussuchen, wo er arbeitet. Sein Antrieb ist aber nicht etwa die Möglichkeit, viel Geld zu verdienen, sondern vor allem denen zu helfen, die seine Hilfe ganz besonders brauchen Er geht nach Alabama wo er sich an der Seite von Anwältin Eva Ansley (Brie Larson) für zu unrecht Verurteilte einzusetzen - und macht mit einem seiner ersten Fälle gleich Schlagzeilen: Denn Walter McMillian (Jamie Foxx) soll einen grausamen Mord begangen haben"  # noqa
    # WHEN the Show is added to the database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN minimal_show.description_start should return the right format
    expectation = "Als junger, vielversprechender Anwalt kann sich Bryan Stevenson (Michael B. Jordan) nach seinem Abschluss in Harvard aussuchen, wo er arbeitet. Sein Antrieb ist aber nicht etwa die Möglichkeit, viel Geld zu verdienen, sondern vor allem denen zu helfen,"  # noqa
    assert minimal_show.description_start == expectation


def test_location_name_returns_correct_format(database_empty, minimal_show):
    # GIVEN a Show object with known location and an initialized database
    minimal_show.location = "Cinema Ostertor"
    # WHEN the Show is added to the database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN minimal_show.location_name_url should return the right format
    assert minimal_show.location_name_url == "cinemaostertor"


def test_default_time_returns_correct_format(database_empty, minimal_show):
    # GIVEN a Show object with known time and an initialized database
    date = arrow.get("2020-02-02 20:30").replace(tzinfo="Europe/Berlin")
    minimal_show.date_time = date
    # WHEN the Show is added to the database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN minimal_show.time should return the right format
    assert minimal_show.time == "20:30"


def test_default_time_returns_correct(database_empty, minimal_show):
    # GIVEN a initialized database and a Show object with known date_time
    minimal_show.date_time = arrow.get("2020-02-02T10:30:00").replace(
        tzinfo="Europe/Berlin"
    )
    # WHEN added to database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN Show.time should have the time according to Europe/Berlin timezone
    assert minimal_show.time == "10:30"


def test_default_day_returns_correct_format(database_empty, minimal_show):
    # GIVEN a Show object with known date an initialized database
    date = arrow.get("2020-02-02")
    minimal_show.date_time = date
    # WHEN the show is added to the database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN minimal_show.day should return the right format
    assert minimal_show.day == "SO 2.2."


def test_default_day_returns_correct(database_empty, minimal_show):
    # GIVEN a initialized database and a Show object with known date_time
    minimal_show.date_time = arrow.get("2020-05-05T00:00:00").replace(
        tzinfo="Europe/Berlin"
    )
    # WHEN added to database
    session = DbSession.factory()
    session.add(minimal_show)
    session.commit()
    # THEN Show.time should have the day according to Europe/Berlin timezone
    assert minimal_show.day == "DI 5.5."


def test_false_category_raises(full_show):
    # GIVEN a Show object
    # WHEN Show.category is set to a false string
    # THEN a ValueError should be raised
    with pytest.raises(ValueError):
        full_show.category = "tree"


def test_description_validation(minimal_show):
    # GIVEN a show object
    # WHEN a malformatted description is added
    description = """
    
Im Mai 2015 veröffentlichte Peter\n Wohlleben sein Buch „Das geheime Leben der Bäume“ und stürmte damit sofort die Bestsellerlisten. Wie schafft es ein Buch über Bäume, die Menschen so in den Bann zu ziehen? Vielleicht deswegen, weil es dem Förster aus der Ortschaft Wershofen gelingt, anschaulich wie kein anderer über den deutschen Wald zu schreiben. 

So lässt er die Leser an seiner \nErkenntnis teilhaben, dass Bäume dazu in der Lage sind, miteinander zu kommunizieren. Weiterhin gibt er Waldführungen und hält Lesungen, sodass er den Menschen die außergewöhnlichen Lebewesen näher bringt und seine Leserschar immer weiter anwächst. Seine Leidenschaft hat er zum Beruf gemacht: Angefangen als Beamter in der Landesforstverwaltung Rheinland-Pfalz sprengte er sich bald von den Ketten der Verwaltung frei, stellte zusammen mit der Gemeinde Wershofen einen uralten Buchenwald unter Schutz und gründete eine Waldakademie. Seither reist er durch die Welt, besucht in Schweden den ältesten Baum des Planeten und unterstützt die Demonstranten im Hambacher Forst. Dabei gilt er vielen als Vorbild, denn Peter Wohlleben ist eins bewusst: Wenn es den Bäumen gut geht, werden auch die Menschen überleben.


    """  # noqa
    minimal_show.description = description
    # THEN it should automatically format nicely
    expectation = "Im Mai 2015 veröffentlichte Peter Wohlleben sein Buch „Das geheime Leben der Bäume“ und stürmte damit sofort die Bestsellerlisten.\xa0Wie schafft es ein Buch über Bäume, die Menschen so in den Bann zu ziehen? Vielleicht deswegen, weil es dem Förster aus der Ortschaft Wershofen gelingt, anschaulich wie kein anderer über den deutschen Wald zu schreiben. So lässt er die Leser an seiner Erkenntnis teilhaben, dass Bäume dazu in der Lage sind, miteinander zu kommunizieren. Weiterhin gibt er Waldführungen und hält Lesungen, sodass er den Menschen die außergewöhnlichen Lebewesen näher bringt und seine Leserschar immer weiter anwächst. Seine Leidenschaft hat er zum Beruf gemacht: Angefangen als Beamter in der Landesforstverwaltung Rheinland-Pfalz sprengte er sich bald von den Ketten der Verwaltung frei, stellte zusammen mit der Gemeinde Wershofen einen uralten Buchenwald unter Schutz und gründete eine Waldakademie. Seither reist er durch die Welt, besucht in Schweden den ältesten Baum des Planeten und unterstützt die Demonstranten im Hambacher Forst. Dabei gilt er vielen als Vorbild, denn Peter Wohlleben ist eins bewusst: Wenn es den Bäumen gut geht, werden auch die Menschen überleben."
    assert minimal_show.description == expectation


# def test_description_validation_none(database_empty, minimal_show):
#     # GIVEN a show object
#     # WHEN None is added as description
#     minimal_show.description = None
#     session = DbSession.factory()
#     session.add(minimal_show)
#     session.commit()
#     # THEN it should still store a string
#     assert minimal_show.description == ""
