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


def getNetPayout(SoupPayment, calendarDayOfWeek, calendarMonthAbrev, calendarDate):
    netPayout = (SoupPayment.find('div', text=calendarDayOfWeek + ", " + calendarMonthAbrev + " " + calendarDate).findParent()
                 .find('div', text="Net Payout").findParent().find('b'))
    return netPayout.text


def scrapeComplex(driver, dateForDay):
    time.sleep(2)
    calendarInputElem = driver.find_element_by_css_selector(
        "input[placeholder='ll - ll']")
    calendarInputElem.click()
    time.sleep(2)
    calendarDate = dateForDay.strftime("%d")
    calendarMonthAbrev = dateForDay.strftime("%b")
    calendarDayOfWeek = calendar.day_abbr[dateForDay.weekday()]
    calendarButtonElems = driver.find_elements_by_xpath(
        '//div[text()="'+str(int(calendarDate))+'"]')
    calendarButtonElem = calendarButtonElems[0] if int(
        calendarDate) > 23 else calendarButtonElems[-1]
    calendarButtonElem.click()
    time.sleep(2)
    content = driver.page_source
    soupPayments1 = BeautifulSoup(content, features="lxml")
    soupPayments2 = ""

    print("Today's date:", calendarDate, " month: ",
          calendarMonthAbrev, " day of week: ", calendarDayOfWeek)
    netPayout = getNetPayout(
        soupPayments1, calendarDayOfWeek, calendarMonthAbrev, calendarDate)
    print(netPayout)

    if soupPayments2 != "":
        netPayout2 = getNetPayout(
            soupPayments2, calendarDayOfWeek, calendarMonthAbrev, calendarDate)
        print(netPayout2)
    return netPayout


def myScraper():
    dateForDay = date.today() - dt.timedelta(days=1)
    options = webdriver.ChromeOptions()
    # Path to your chrome profile
    options.add_argument(
        "user-data-dir=/Users/kwhite/Library/Application Support/Google/Chrome/Default")
    driver = webdriver.Chrome(
        "/usr/local/lib/chromium-browser/chromedriver", options=options)
    driver.get(
        "https://restaurant.uber.com/payments?")
    driver.implicitly_wait(10)
    try:
        a = scrapeComplex(driver, dateForDay)
    except Exception as inst:
        raise inst
    finally:
        driver.quit()
    return a


myScraper()
