import requests
import sys
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


def start_driver():
    global driver
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference("intl.accept_languages", 'de')
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, firefox_profile=firefox_profile)


def close_driver():
    driver.quit()


def get_html_from_web(url):
    print('    ...loading webpage (requests)')
    try:
        response = requests.get(url)
        if response.status_code == 404:
            print('    tried but failed to retrieve html from: ', url)
            return None
        else:
            print('    Retrieved html from: ', url)
            return response.text
    except requests.exceptions.ConnectionError as e:
        print("    Error! Connection error: {}".format(e))
        print('    the script is aborted')
        sys.exit(1)


def get_html_from_web_ajax(url, class_name):
    """Get page source code from a web page that uses ajax to load elements of the page one at a time.
     Selenium will wait for the element with the class name 'class_name' to load before getting the page source"""
    print('    ...loading webpage (selenium)')
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        source = driver.page_source
    except TimeoutException:
        print("    Error! Selenium Timeout: {}".format(url))
        print('    tried but failed to retrieve html from: ', url)
        return None
    except WebDriverException as e:
        print("    Error! Selenium Exception. {}".format(str(e)))
        print('    tried but failed to retrieve html from: ', url)
        return None
    print('    Retrieved html from: ', url)
    return source


# TODO write the below functions more general
def get_meta_html(url):
    """I need to click some buttons to get all the info in the html. It should wait for the overlay to be gone."""
    print('    ...loading webpage meta kinoheld (selenium)')
    driver.get(url)
    wait_for_overlay()
    source = click_buttons(url)
    return source


def click_buttons(url):
    """click two button types: one if there is also a trailer, one if there is only info without a trailer"""
    buttons = get_buttons()
    while not buttons:  # sometimes this still needs more time
        time.sleep(1)
        buttons = get_buttons()
    clicking = try_clicking(buttons[0])
    while not clicking:  # sometimes there are still overlay classes preventing clicking
        time.sleep(1)
        clicking = try_clicking(buttons[0])
    del buttons[0]
    for button in buttons:
        button.click()
    source = driver.page_source
    print('    Retrieved html from: ', url)
    return source


def get_buttons():
    button_classes = ['ui-button.ui-corners-bottom-left.ui-ripple.ui-button--secondary.u-flex-grow-1',
                      'ui-button.ui-corners-bottom.ui-ripple.ui-button--secondary.u-flex-grow-1']
    buttons = driver.find_elements_by_class_name(button_classes[0])
    buttons.extend(driver.find_elements_by_class_name(button_classes[1]))
    if buttons:
        return buttons
    else:
        return None


def wait_for_overlay():
    try:
        wait = WebDriverWait(driver, 10)
        overlay_class = "overlay-container"
        wait.until_not(EC.visibility_of_element_located((By.CLASS_NAME, overlay_class)))
        return True
    except WebDriverException:
        return False


def try_clicking(button):
    try:
        button.click()
        return True
    except ElementClickInterceptedException:
        return False


def parse_date_without_year(*args):
    """Guess the year and return arrow object.
    Assumes that dates don't go back more than 2 months. Useful when year
    is not available. accepts either an arrow object, or arguments for
    month, day, hour and minute."""
    # if arrow object was supplied
    if len(args) == 1 and isinstance(args[0], arrow.arrow.Arrow):
        date_time = args[0]
        if date_time.year == 1:  # if year not specified in arrow year 1 is used
            year = arrow.now('Europe/Berlin').year  # get current year
            date_time = date_time.replace(year=year)
    # if month, day, hour, minute was supplied
    elif len(args) == 4:
        year = arrow.now('Europe/Berlin').year  # get current year
        date_time = arrow.get(year, args[0], args[1],
                              args[2], args[3],
                              tzinfo="Europe/Berlin")
    else:
        raise TypeError("_parse_date_without_year() only accepts arrow objects or month, day, hour, minute")
    if date_time < arrow.now("Europe/Berlin").shift(months=-2):
        return date_time.replace(year=date_time.year + 1)
    else:
        return date_time
