"""
helper functions for obtaining htmls

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
"""

import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.firefox.options import Options


def start_driver():
    """start driver for selenium"""
    print('...  Loading web driver')
    global driver
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("intl.accept_languages", "de")
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, firefox_profile=firefox_profile)


def close_driver():
    """close driver for selenium"""
    driver.quit()


def get_html(url):
    """
    Obtain source html using requests

    Parameters
    ----------
    url: str
        url to obtain html from

    Raises
    ------
    ConnectionError
        when a 404 or requests ConnectionError

    Returns
    -------
    str or None
        source html
    """

    print('    ... Get html from the web (requests)')
    response = requests.get(url)
    if response.status_code == 404:
        raise ConnectionError('received a 404')
    else:
        return response.text


def get_html_ajax(url, class_name):
    """
    Obtain source html from a web page that uses ajax

    ajax causes elements to load after opening the page so requests
    won't work. Therefore use selenium and wait to be ready.
    Requires driver to be started

    Parameters
    ----------
    url: str
        url to obtain html from
    class_name: str
        name of the class of the element that should be loaded before
        the source html is downloaded

    Raises
    ------
    ConnectionError
        when timeout or webdriver exception

    Returns
    -------
    str or None
        source html
    """

    print('    ... Get html from the web (ajax)')
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_name))
    )
    source = driver.page_source
    return source


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

    Raises
    ------
    ConnectionError
        when Timout exception or webdriver exception

    Returns
    -------
    str or None
        source html
    """

    print('    ... Get html from the web (clicking buttons)')
    driver.get(url)
    if overlay_class:
        _wait_for_overlay(overlay_class)
    _click_buttons(button_classes)
    source = driver.page_source
    return source


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

    # todo: these while loops are maybe not great when connection fails
    # first make sure all overlay classes are gone
    # which I don't know by name, hence the messy code
    buttons = _get_buttons(button_classes)
    while not buttons:  # sometimes this still needs more time
        time.sleep(1)
        buttons = _get_buttons(button_classes)
    clicking = _try_clicking(buttons[0])
    while not clicking:  # sometimes there are still overlay classes preventing clicking
        time.sleep(1)
        clicking = _try_clicking(buttons[0])
    _try_clicking(buttons[0])  # reset clicked button
    # second get the buttons again now that all overlays are gone
    buttons = _get_buttons(button_classes)
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
    buttons = []
    for button_class in button_classes:
        buttons.extend(driver.find_elements_by_class_name(button_class))
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
