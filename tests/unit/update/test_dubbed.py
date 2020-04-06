import pytest

from data.show import Show
from update.services import dubbed
from update.services.metainfo import MetaInfo


def test_has_language_version():
    """any language version is not dubbed"""
    assert not dubbed.is_dubbed(Show(language_version="OmU"), MetaInfo())


def test_empty_language_version():
    """No language_version or empty MetaInfo should be assigned as dubbed"""
    assert dubbed.is_dubbed(Show(language_version=""), MetaInfo())


@pytest.mark.parametrize('country',
                         ['in Deutschland', '*DEUTSCHLAND', 'ÖSterREICH*', 'schweiz'])
def test_is_country(country):
    """german speaking countries are probably original language"""
    assert not dubbed.is_dubbed(Show(), MetaInfo(country=country))


def test_false_country():
    """other countries and no other info should be dubbed"""
    assert dubbed.is_dubbed(Show(), MetaInfo(country='Die Niederlande, USA'))


def test_original_title_matches():
    meta_info = MetaInfo(country='deutschland', title='bla', title_original='bLa')
    assert not dubbed.is_dubbed(Show(), meta_info)


def test_original_title_doesnt_match():
    meta_info = MetaInfo(country='deutschland', title='bla', title_original='blaH')
    assert dubbed.is_dubbed(Show(), meta_info)
