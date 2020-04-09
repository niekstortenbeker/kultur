import arrow
import pytest
from update.services import parsing


@pytest.mark.parametrize("shift", [30, 9 * 30, -30, -2 * 28])
def test_parse_date_without_year_arrow(shift):
    """
    If the year is removed from a timestamp parse_date_without_year() should guess the
    year correctly and return an arrow object
    shift: number of days from now
    """
    dt_expected = arrow.now("Europe/Berlin").shift(days=+shift)
    dt_before = dt_expected.replace(year=1)
    dt_after = parsing.parse_date_without_year(dt_before)
    assert dt_after == dt_expected


@pytest.mark.parametrize("shift", [30, 9 * 30, -30, -2 * 28])
def test_parse_date_without_year_ints(shift):
    """
    If the year is removed from a timestamp parse_date_without_year() should guess the
    year correctly and return an arrow object
    shift: number of days from now
    """
    dt_expected = (
        arrow.now("Europe/Berlin").shift(days=+shift).replace(second=0, microsecond=0)
    )
    dt_before = dt_expected.replace(year=1)
    dt_after = parsing.parse_date_without_year(
        dt_before.month, dt_before.day, dt_before.hour, dt_before.minute
    )
    assert dt_after == dt_expected


def test_parse_date_without_year_false_type():
    with pytest.raises(TypeError):
        parsing.parse_date_without_year(12, 3, 20)
