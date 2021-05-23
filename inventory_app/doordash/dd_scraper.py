__author__ = "kwhite"

import datetime as dt
import re
import time

from bs4 import BeautifulSoup
from dateutil.parser import parse
from functional import seq
from selenium import webdriver
import random


def sendKeysOneAtATime(element, phrase):
    for i in phrase:
        element.send_keys(i)
        time.sleep(random.randint(1, 3) / 10)


def get_orders_from_date(driver, the_date, func):
    """get orders from date

    Args:
        driver (webdriver): [description]
        the_date (date): [description]
        func (func): [description]

    Returns:
        [BeautifulSoup]: [description]
    """
    time.sleep(4)
    calendar_button_elems = driver.find_elements_by_xpath('//td[text()="' + the_date + '"]')
    print(calendar_button_elems)
    soup_payments = []
    for i in range(0, len(calendar_button_elems)):
        item = driver.find_elements_by_xpath('//td[text()="' + the_date + '"]/..//a')[i]
        item.click()
        time.sleep(3)
        hour_of_order = parse(driver.find_elements_by_xpath('//span[text()="Pickup Time"]/..//span')[-1].text).hour
        print(hour_of_order)
        if func(hour_of_order):
            content = driver.page_source
            soup_payments = soup_payments + [BeautifulSoup(content, features="lxml")]
        driver.find_element_by_css_selector("button[aria-label='Close']").click()
    return soup_payments


def scrape_complex(driver, date_for_day):
    """idk

    Args:
        driver (webdriver): [description]
        date_for_day (date): [description]

    Returns:
        int: [description]
    """
    soup_payments = []
    time.sleep(2)
    calendar_date = str(date_for_day.strftime("%-m/%-d/%Y"))
    next_calendar_date = str((date_for_day + dt.timedelta(1)).strftime("%-m/%-d/%Y"))
    prev_padded_date = str((date_for_day - dt.timedelta(1)).strftime("%m/%d/%Y"))
    next_padded_date = str((date_for_day + dt.timedelta(1)).strftime("%m/%d/%Y"))
    print(calendar_date)
    time.sleep(6)
    # driver.find_element_by_css_selector("button[aria-label='Close']").click()
    calendar_input_start = driver.find_elements_by_class_name("form-control")[0]
    calendar_input_end = driver.find_elements_by_class_name("form-control")[-1]
    calendar_input_start.click()
    calendar_input_start.clear()
    sendKeysOneAtATime(calendar_input_start, prev_padded_date)
    calendar_input_start.click()
    calendar_input_end.click()
    calendar_input_end.clear()
    sendKeysOneAtATime(calendar_input_end, next_padded_date)
    calendar_input_end.click()
    driver.find_element_by_css_selector('button[kind="BUTTON/PRIMARY"').click()
    soup_payments = soup_payments + get_orders_from_date(driver, calendar_date, lambda x: x > 10)
    soup_payments = soup_payments + get_orders_from_date(driver, next_calendar_date, lambda x: x < 3)
    non_decimal = re.compile(r"[^\d]+")
    final = seq(soup_payments).reduce(
        lambda v, x: v
        + int(
            non_decimal.sub(
                "",
                x.find("span", string="Total Payout").findParent().findParent().findAll("span")[-1].text,
            )
        ),
        0,
    )
    print(final / 100)
    return final


def myScraper(date_for_day):
    options = webdriver.ChromeOptions()
    # Path to your chrome profile
    options.add_argument("user-data-dir=/Users/kwhite/Library/Application Support/Google/Chrome/Default")
    driver = webdriver.Chrome("/usr/local/lib/chromium-browser/chromedriver", options=options)
    driver.implicitly_wait(20)
    # time.sleep(1000)
    try:
        mine = scrape_complex(driver, date_for_day)
    except Exception as inst:
        raise inst
    finally:
        if driver:
        driver.quit()
    return mine


# myScraper(date.today() - dt.timedelta(days=1))
