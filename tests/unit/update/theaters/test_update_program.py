import pytest
from kultur.update.theaters.all import all_theaters_not_initialized
from tests import fake_data

program = fake_data.program("some theater")
meta_info = fake_data.meta_info()


def stub_scrape_program(self):
    self.program = program


def stub_update_meta_info(self):
    self.meta_info = meta_info


@pytest.mark.parametrize("theater", all_theaters_not_initialized)
def test_program_is_updated(mocker, theater):
    mocker.patch.object(theater, "_scrape_program", new=stub_scrape_program)
    mocker.patch.object(theater, "_update_meta_info", new=stub_update_meta_info)
    result = theater()
    result.update_program()
    assert len(result.program) > 1


@pytest.mark.parametrize("theater", all_theaters_not_initialized)
def test_scrape_program_called(mocker, theater):
    mocker.patch.object(theater, "_scrape_program")
    mocker.patch.object(theater, "_update_meta_info")
    result = theater()
    result.update_program()
    # noinspection PyUnresolvedReferences
    theater._scrape_program.assert_called_once_with()


@pytest.mark.parametrize("theater", all_theaters_not_initialized)
def test_update_meta_info_called(mocker, theater):
    mocker.patch.object(theater, "_scrape_program")
    mocker.patch.object(theater, "_update_meta_info")
    result = theater()
    result.update_program()
    # noinspection PyUnresolvedReferences
    result._update_meta_info.assert_called_once_with()
