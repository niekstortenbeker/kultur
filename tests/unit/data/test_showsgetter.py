import arrow
import pytest
from kultur.data.dbsession import UninitializedDatabaseError
from kultur.data.show import Show
from kultur.data.showsgetter import ShowsGetter


def test_raises_false_start(database_full):
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        ShowsGetter("", arrow.now())


def test_raises_false_stop(database_full):
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        ShowsGetter(arrow.now(), "")


def test_raises_false_category(database_full):
    with pytest.raises(ValueError):
        ShowsGetter(arrow.now(), arrow.now(), "plant")


def test_raises_false_dubbed(database_full):
    with pytest.raises(TypeError):
        # noinspection PyTypeChecker
        ShowsGetter(arrow.now(), arrow.now(), dubbed="False")


def test_raises_no_database():
    with pytest.raises(UninitializedDatabaseError):
        ShowsGetter(arrow.now(), arrow.now())


def test_get_returns_list(database_full):
    # GIVEN an initialized database
    # WHEN ShowGetter.get() is ran
    sg = ShowsGetter(arrow.now(), arrow.now().shift(days=+1))
    result = sg.get()
    # THEN a list should be returned
    assert type(result) == list


def test_get_returns_shows(database_full):
    # GIVEN an initialized database
    # WHEN ShowGetter.get() is ran
    sg = ShowsGetter(arrow.now(), arrow.now().shift(days=+1))
    result = sg.get()
    # THEN a list with Shows should be returned
    assert type(result[0]) == Show


def test_category_filters_shows(database_full):
    # GIVEN an initialized database
    # WHEN ShowGetter has a category set and .get() is ran
    sg = ShowsGetter(arrow.now(), arrow.now().shift(days=+7), category="cinema")
    result = {show.category for show in sg.get()}
    # THEN no shows from category stage should be returned
    assert "stage" not in result


def test_get_all_categories(database_full):
    # GIVEN an initialized database
    # WHEN ShowGetter category not set and .get() is ran
    sg = ShowsGetter(arrow.now(), arrow.now().shift(days=+7))
    result = {show.category for show in sg.get()}
    # THEN all categories (and onl these) should be obtained
    assert {"cinema", "stage", "music"} == result


def test_dubbed_filters_shows(database_full):
    # GIVEN an initialized database
    # WHEN ShowGetter has dubbed set to True set and .get() is ran
    sg = ShowsGetter(arrow.now(), arrow.now().shift(days=+7), dubbed=True)
    result = {show.dubbed for show in sg.get()}
    # THEN also dubbed films should be retrieved
    assert True in result


def test_dubbed_filters_shows_2(database_full):
    # GIVEN an initialized database
    # WHEN ShowGetter has dubbed not set and .get() is ran
    sg = ShowsGetter(arrow.now(), arrow.now().shift(days=+7))
    result = {show.dubbed for show in sg.get()}
    # THEN also dubbed films should be retrieved
    assert True not in result
