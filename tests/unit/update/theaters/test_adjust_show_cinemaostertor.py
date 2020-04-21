import arrow
import pytest
from kultur.data.show import Show
from kultur.update.services.metainfo import MetaInfo
from kultur.update.theaters.cinemaostertor import CinemaOstertor


def test_omu_is_not_dubbed(omu_show, omu_meta_info):
    # GIVEN a show with omu and corresponding meta info
    # WHEN _adjust_show() is called
    cinema = CinemaOstertor()
    result = cinema._adjust_show(omu_show, omu_meta_info)
    # THEN show.dubbed should be false
    assert not result.dubbed


def test_omu_added_description(omu_show, omu_meta_info):
    # GIVEN a show and corresponding metainfo with a description
    # WHEN _adjust_show() is called
    cinema = CinemaOstertor()
    result = cinema._adjust_show(omu_show, omu_meta_info)
    # THEN show.description should be added
    assert result.description


def test_omu_added_url(omu_show, omu_meta_info):
    # GIVEN a show and corresponding metainfo with a url_info
    # WHEN _adjust_show() is called
    cinema = CinemaOstertor()
    result = cinema._adjust_show(omu_show, omu_meta_info)
    # THEN show.url_info should have been updated
    assert result.url_info


@pytest.fixture(scope="module")
def omu_show():
    return Show(
        date_time=arrow.now(),
        title="Amazing Grace",
        location="Kino",
        category="cinema",
        language_version="OmU",
    )


@pytest.fixture(scope="module")
def omu_meta_info():
    return MetaInfo(
        title="Amazing Grace",
        description="now there is some text",
        url_info="www.info.com",
    )


def test_dubbed_show_gets_label(dubbed_show, dubbed_meta_info):
    # GIVEN a dubbed show and corresponding metainfo
    # WHEN _adjust_show() is called
    cinema = CinemaOstertor()
    result = cinema._adjust_show(dubbed_show, dubbed_meta_info)
    # THEN show.dubbed should be True
    assert result.dubbed


@pytest.fixture(scope="module")
def dubbed_show():
    return Show(
        date_time=arrow.now(),
        title="Jungle Abenteuern",
        location="Kino",
        category="cinema",
    )


@pytest.fixture()
def dubbed_meta_info():
    return MetaInfo(
        title="Jungle Abenteuern",
        title_original="Jungle Adventures",
        country="USA, deutschland",
    )


def test_german_show_is_not_dubbed(german_show, german_meta_info):
    # GIVEN a dubbed show and corresponding metainfo
    # WHEN _adjust_show() is called
    cinema = CinemaOstertor()
    result = cinema._adjust_show(german_show, german_meta_info)
    # THEN show.dubbed should be True
    assert not result.dubbed


@pytest.fixture(scope="module")
def german_show():
    return Show(
        date_time=arrow.now(), title="Wunder Bär", location="Kino", category="cinema"
    )


@pytest.fixture(scope="module")
def german_meta_info():
    return MetaInfo(
        title="Wunder Bär",
        title_original="Wunder Bär",
        country="deutschland",
        description="some info",
        url_info="www.bla.com",
    )
