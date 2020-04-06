import pytest

from update.services import parsing

import arrow


@pytest.mark.parametrize('shift',
                         [30, 9 * 30, -30, -2 * 28])
def test_parse_date_without_year_arrow(shift):
    """
    If the year is removed from a timestamp parse_date_without_year() should guess the
    year correctly and return an arrow object
    shift: number of days from now
    """
    expected_result = arrow.now('Europe/Berlin').shift(days=+shift)
    function_input = expected_result.replace(year=1)
    result = parsing.parse_date_without_year(function_input)
    assert result == expected_result


@pytest.mark.parametrize('shift',
                         [30, 9 * 30, -30, -2 * 28])
def test_parse_date_without_year_ints(shift):
    """
    If the year is removed from a timestamp parse_date_without_year() should guess the
    year correctly and return an arrow object
    shift: number of days from now
    """
    expected_result = arrow.now('Europe/Berlin')\
        .shift(days=+shift)\
        .replace(second=0, microsecond=0)
    dt = expected_result.replace(year=1)
    result = parsing.parse_date_without_year(dt.month, dt.day, dt.hour, dt.minute)
    assert result == expected_result


def test_parse_date_without_year_false_type():
    with pytest.raises(TypeError):
        parsing.parse_date_without_year(12, 3, 20)
