__author__ = "kwhite"

import calendar
import datetime as dt
import random
import re
import time
from datetime import date
from decimal import Decimal
from math import ceil

import pandas as pd
from bs4 import BeautifulSoup
from dateutil.parser import parse
from functional import seq
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


def getOrdersFromDate(driver, theDate, func):
    time.sleep(10)
    calendarButtonElems = driver.find_elements_by_xpath('//div[text()="' + theDate + '"]')
    print(calendarButtonElems)
    soupPayments = []
    for i in calendarButtonElems:
        hourOfOrder = parse(i.text.replace("·", " ")).hour
        print(hourOfOrder)
        if func(hourOfOrder):
            i.click()
            time.sleep(3)
            content = driver.page_source
            soupPayments = soupPayments + [BeautifulSoup(content, features="lxml")]
            driver.find_element_by_class_name("close-button").find_element_by_tag_name("a").click()
            time.sleep(3)
    return soupPayments


def sendKeysOneAtATime(element, phrase):
    for i in phrase:
        element.send_keys(i)
        time.sleep(random.randint(1, 3) / 10)


def scrapeComplex(driver, dateForDay):

    time.sleep(4)
    soupPayments = []
    calendarDate = str(dateForDay.strftime("%m/%d/%Y"))
    nextCalendarDate = str((dateForDay + dt.timedelta(1)).strftime("%m/%d/%Y"))
    print(calendarDate)

    soupPayments = soupPayments + getOrdersFromDate(driver, calendarDate, lambda x: x > 10)
    soupPayments = soupPayments + getOrdersFromDate(driver, nextCalendarDate, lambda x: x < 3)
    non_decimal = re.compile(r"[^\d]+")
    final = seq(soupPayments).reduce(
        lambda v, x: v
        + int(
            non_decimal.sub(
                "",
                x.find("div", string="Payout").findParent().find("div", {"class": "amount"}).text,
            )
        ),
        0,
    )
    print(final / 100)
    return final


def myScraper(dateForDay):
    # dateForDay = date.today() - dt.timedelta(days=1)
    # options = webdriver.ChromeOptions()

    # Path to your chrome profile
    # options.add_argument("user-data-dir=/Users/kwhite/Library/Application Support/Google/Chrome/Default")
    # options.add_extension(
    #     "/usr/local/lib/chromium-browser/extensions/extension_1_29_2_0.crx")

    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(firefox_profile=profile, executable_path="/usr/local/lib/firefox-browser/geckodriver")
    # driver = webdriver.Chrome(options=options, executable_path="/usr/local/lib/chromium-browser/chromedriver")
    driver.get("https://partner.postmates.com/")
    driver.implicitly_wait(10)
    driver.maximize_window()
    driver.refresh()
    time.sleep(1)
    try:
        a = scrapeComplex(driver, dateForDay)
    except Exception as inst:
        raise inst
    finally:
        if driver:
        driver.quit()
    return a


# myScraper(date.today() - dt.timedelta(days=2))
