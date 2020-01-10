"""
helper functions for obtaining htmls and parsing html

Functions
---------
start_driver()
    start driver for selenium
close_driver()
    close driver for selenium
get_html(url)
    Obtain source html using requests
get_html_ajax(url, class_name)
    Obtain source html from a web page that uses ajax
get_html_buttons(url, button_classes, overlay_class=None)
    Obtain source html from a web page where buttons need to be clicked
parse_date_without_year(*args)
    Guess the year and return arrow object
"""

import requests
import arrow
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.firefox.options import Options
from itertools import chain


def start_driver():
    """start driver for selenium"""
    global driver
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("intl.accept_languages", "de")
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, firefox_profile=firefox_profile)


def close_driver():
    """close driver for selenium"""
    driver.quit()


# TODO maybe raising exceptions instead of returning None makes more sense
def get_html(url):
    """
    Obtain source html using requests

    Parameters
    ----------
    url: str
        url to obtain html from

    Returns
    -------
    str or None
        source html
    """

    print("    ...loading web page (requests)")
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print("    tried but failed to retrieve html from: ", url)
            return None
        else:
            print("    Retrieved html from: ", url)
            return response.text
    except requests.exceptions.ConnectionError as e:
        print("    Error! Connection error: {}".format(e))
        print("    the script is aborted")
        return None


def get_html_ajax(url, class_name):
    """
    Obtain source html from a web page that uses ajax

    ajax causes elements to load after opening the page so requests
    won't work. Therefore use selenium and wait to be ready.

    Parameters
    ----------
    url: str
        url to obtain html from
    class_name: str
        name of the class of the element that should be loaded before
        the source html is downloaded

    Returns
    -------
    str or None
        source html
    """

    print("    ...loading web page (selenium)")
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_name))
        )
        source = driver.page_source
        print("    Retrieved html from: ", url)
        return source
    except TimeoutException:
        print("    Error! Selenium Timeout: {}".format(url))
        print("    tried but failed to retrieve html from: ", url)
        return None
    except WebDriverException as e:
        print("    Error! Selenium Exception. {}".format(str(e)))
        print("    tried but failed to retrieve html from: ", url)
        return None


def get_html_buttons(url, button_classes, overlay_class=None):
    """
    Obtain source html from a web page where buttons need to be clicked

    Requires driver to be started

    Parameters
    ----------
    url
        url to obtain html from
    button_classes: list
        names of the classes of the button elements to click
    overlay_class: str, optional
        name of the class of an element that should be gone before
        clicking buttons (default is None)

    Returns
    -------
    str or None
        source html
    """

    print("    ...loading web page and clicking buttons (selenium)")
    try:
        driver.get(url)
        if overlay_class:
            _wait_for_overlay(overlay_class)
        _click_buttons(button_classes)
        source = driver.page_source
        print("    Retrieved html from: ", url)
        return source
    except TimeoutException:
        print("    Error! Selenium Timeout: {}".format(url))
        print("    tried but failed to retrieve html from: ", url)
        return None
    except WebDriverException as e:
        print("    Error! Selenium Exception. {}".format(str(e)))
        print("    tried but failed to retrieve html from: ", url)
        return None


def _wait_for_overlay(overlay_class):
    """
    let selenium driver wait until an overlay element is gone

    Requires driver to have gotten a page

    Parameters
    ----------
    overlay_class: str
        name of the class of an element that should be gone

    Returns
    -------
    bool
        True when overlay is gone, False when it's still there after
        10 seconds
    """

    try:
        wait = WebDriverWait(driver, 10)
        wait.until_not(EC.visibility_of_element_located((By.CLASS_NAME, overlay_class)))
        return True
    except WebDriverException:
        return False


def _click_buttons(button_classes):
    """
    let selenium driver click buttons

    Requires driver to have gotten a page

    Parameters
    ----------
    button_classes: list
        names of the classes of the button elements to click
    """

    buttons = _get_buttons(button_classes)
    while not buttons:  # sometimes this still needs more time
        time.sleep(1)
        buttons = _get_buttons(button_classes)
    clicking = _try_clicking(buttons[0])
    while not clicking:  # sometimes there are still overlay classes preventing clicking
        time.sleep(1)
        clicking = _try_clicking(buttons[0])
    del buttons[0]
    for button in buttons:
        button.click()


def _get_buttons(button_classes):
    """
    find button elements by class name

    Parameters
    ----------
    button_classes: list
        class of the button elements to click

    Returns
    -------
    list or None
        list with the buttons
    """

    buttons = driver.find_elements_by_class_name(button_classes[0])
    buttons.extend(driver.find_elements_by_class_name(button_classes[1]))
    if buttons:
        return buttons
    else:
        return None


def _try_clicking(button):
    """
    try clicking buttons

    Parameters
    ----------
    button: selenium object

    Returns
    -------
    bool
        Return True when button was clicked, False when it didn't work
    """

    try:
        button.click()
        return True
    except ElementClickInterceptedException:
        return False


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

