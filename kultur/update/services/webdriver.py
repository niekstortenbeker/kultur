"""
helper functions for obtaining source htmls

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
import time
from typing import List

import requests
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

driver: WebDriver


def start_driver():
    """start driver for selenium"""
    print("...  Loading web driver")
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

    print("    ... Get html from the web (requests)")
    response = requests.get(url)
    if response.status_code == 404:
        raise ConnectionError("received a 404")
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

    print("    ... Get html from the web (ajax)")
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, class_name))
    )
    source = driver.page_source
    return source


def get_html_buttons(url, button_classes):
    """
    Obtain source html from a web page where buttons need to be clicked

    Requires driver to be started

    Parameters
    ----------
    url
        url to obtain html from
    button_classes: list
        names of the classes of the button elements to click

    Raises
    ------
    TimeoutException
        when things take too long

    Returns
    -------
    str or None
        source html
    """
    html_buttons = HtmlClickedButtons(url, button_classes)
    source = html_buttons.get()
    return source


class HtmlClickedButtons:
    def __init__(self, url: str, button_classes: List[str]):
        self.url = url
        self.button_classes = button_classes
        self.buttons = None
        self.wait_time = 0.5
        self.wait_max_tries = 20

    def get(self):
        """
        Obtain source html from a web page where buttons need to be clicked
        """
        print("    ... Get html from the web (clicking buttons)")
        driver.get(self.url)
        self._click_buttons()
        source = driver.page_source
        return source

    def _click_buttons(self):
        self._wait_for_buttons()
        self._wait_until_buttons_are_clickable()
        self._set_buttons()  # try again now that all overlays are gone

        for button in self.buttons:
            button.click()

    def _set_buttons(self):
        buttons = []
        for button_class in self.button_classes:
            buttons.extend(driver.find_elements_by_class_name(button_class))
        if buttons:
            self.buttons = buttons
        else:
            self.buttons = None

    def _wait_for_buttons(self):
        """sometimes overlay classes prevent getting buttons"""
        self._set_buttons()
        tries = 0
        while not self.buttons:
            time.sleep(self.wait_time)
            self._set_buttons()
            tries += 1
            if tries > self.wait_max_tries:
                raise TimeoutException

    def _wait_until_buttons_are_clickable(self):
        """sometimes overlay classes prevent clicking"""
        clicking = self._try_clicking(self.buttons[0])
        tries = 0
        while not clicking:
            time.sleep(self.wait_time)
            clicking = self._try_clicking(self.buttons[0])
            tries += 1
            if tries > self.wait_max_tries:
                raise TimeoutException

    # noinspection PyMethodMayBeStatic
    def _try_clicking(self, button: WebElement) -> bool:
        try:
            button.click()
            button.click()  # reset clicked button
            return True
        except ElementClickInterceptedException:
            return False
