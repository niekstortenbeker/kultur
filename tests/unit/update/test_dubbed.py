import pytest
from data.show import Show
from update.services import dubbed
from update.services.metainfo import MetaInfo


def test_has_language_version():
    """any language version is not dubbed"""
    show = Show(language_version="OmU")
    meta_info = MetaInfo()
    assert not dubbed.is_dubbed(show, meta_info)


def test_empty_language_version():
    """No language_version or empty MetaInfo should be assigned as dubbed"""
    show = Show(language_version="")
    meta_info = MetaInfo()
    assert dubbed.is_dubbed(show, meta_info)


@pytest.mark.parametrize(
    "country", ["in Deutschland", "*DEUTSCHLAND", "ÖSterREICH*", "schweiz"]
)
def test_is_country(country):
    """german speaking countries are probably original language"""
    show = Show()
    meta_info = MetaInfo(country=country)
    assert not dubbed.is_dubbed(show, meta_info)


def test_false_country():
    """other countries and no other info should be dubbed"""
    show = Show()
    meta_info = MetaInfo(country="Die Niederlande, USA")
    assert dubbed.is_dubbed(show, meta_info)


def test_original_title_matches():
    show = Show()
    meta_info = MetaInfo(country="deutschland", title="bla", title_original="bLa")
    assert not dubbed.is_dubbed(show, meta_info)


def test_original_title_doesnt_match():
    show = Show()
    meta_info = MetaInfo(country="deutschland", title="bla", title_original="blaH")
    assert dubbed.is_dubbed(show, meta_info)
