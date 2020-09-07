__author__ = 'kwhite'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
from decimal import Decimal
from math import ceil
from datetime import date
import datetime as dt
import calendar
from dateutil.parser import parse
from functional import seq
import re


def getOrdersFromDate(driver, theDate, func):
    calendarButtonElems = driver.find_elements_by_xpath(
        '//div[text()="'+theDate+'"]')
    print(calendarButtonElems)
    soupPayments = []
    for i in calendarButtonElems:
        hourOfOrder = parse(i.text.replace('·', ' ')).hour
        print(hourOfOrder)
        if func(hourOfOrder):
            i.click()
            time.sleep(3)
            content = driver.page_source
            soupPayments = (soupPayments +
                            [BeautifulSoup(content, features="lxml")])
            driver.find_element_by_class_name('close-button').find_element_by_tag_name('a').click()
    return soupPayments


def scrapeComplex(driver, dateForDay):

    driver.find_element_by_class_name('submit').click()
    time.sleep(2)
    soupPayments = []
    calendarDate = str(dateForDay.strftime("%m/%d/%Y"))
    nextCalendarDate = str(
        (dateForDay + dt.timedelta(1)).strftime("%m/%d/%Y"))
    print(calendarDate)

    soupPayments = soupPayments + \
        getOrdersFromDate(driver, calendarDate, lambda x: x > 10)
    soupPayments = soupPayments + \
        getOrdersFromDate(driver, nextCalendarDate, lambda x: x < 3)
    non_decimal = re.compile(r'[^\d]+')
    final = (seq(soupPayments).reduce(lambda v, x: v+int(non_decimal.sub('',
                                                                           x.find('div', string="Payout").findParent().find('div',  {"class": "amount"}).text)), 0))
    print(final/100)
    return final


def myScraper():
    dateForDay = date.today() - dt.timedelta(days=1)
    options = webdriver.ChromeOptions()
    # Path to your chrome profile
    options.add_argument(
        "user-data-dir=/Users/kwhite/Library/Application Support/Google/Chrome/Default")
    options.add_extension(
        "/usr/local/lib/chromium-browser/extensions/extension_1_29_2_0.crx")
    driver = webdriver.Chrome(
        "/usr/local/lib/chromium-browser/chromedriver", options=options)
    driver.get(
        "https://partner.postmates.com/dashboard/home/deliveries")
    driver.implicitly_wait(10)
    time.sleep(1)
    try:
        # x = 1
        a = scrapeComplex(driver, dateForDay)
    except Exception as inst:
        raise inst
    finally:
        driver.quit()
    return a


myScraper()
