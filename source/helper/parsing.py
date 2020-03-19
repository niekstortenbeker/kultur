"""
helper functions for parsing html

Functions
---------
parse_date_without_year(*args)
    Guess the year and return arrow object
list_nested_tag(soup_resultset, element_name):
    list soup tags that are hidden in a nested soup ResultSet structure
"""

from itertools import chain
import arrow


def parse_date_without_year(*args):
    """
    Guess the year and return arrow object

    Assumes that dates don't go back more than 2 months (and must in
    that case be in the nearest future). Useful when year is not
    available.

    Parameters
    ----------
    args
        arrow object, or
        month, day, hour, minute: ints

    Returns
    -------
        arrow object
    """

    # if arrow object was supplied
    if len(args) == 1 and isinstance(args[0], arrow.arrow.Arrow):
        date_time = args[0]
        if date_time.year == 1:  # if year not specified in arrow year 1 is used
            year = arrow.now("Europe/Berlin").year  # get current year
            date_time = date_time.replace(year=year)
    # if month, day, hour, minute was supplied
    elif len(args) == 4:
        year = arrow.now("Europe/Berlin").year  # get current year
        date_time = arrow.get(
            year, args[0], args[1], args[2], args[3], tzinfo="Europe/Berlin"
        )
    else:
        raise TypeError(
            "_parse_date_without_year() only accepts arrow objects or month, day, hour, minute"
        )
    if date_time < arrow.now("Europe/Berlin").shift(months=-2):
        return date_time.replace(year=date_time.year + 1)
    else:
        return date_time


def list_nested_tag(soup_resultset, element_name):
    """
    list soup tags that are hidden in a nested soup ResultSet structure

    this approach prevents list within lists as results
    For instance:
    soup = soup.find_all('table')
    elements = list_nested_tag(soup, 'tr')

    Parameters
    ----------
    soup_resultset: bs4.element.ResultSet
        result of a soup.find_all()
    element_name: str
        name of tag to search in the soup result set

    Returns
    -------
    list
        list of bs4.element.Tag that was searched for
    """

    nested_element = [x.find_all(element_name) for x in soup_resultset]
    return list(chain.from_iterable(nested_element))
