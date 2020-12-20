__author__ = "kwhite"

import calendar
import datetime as dt
import re
import time
from datetime import date
from decimal import Decimal
from math import ceil

from bs4 import BeautifulSoup
from dateutil.parser import parse
from functional import seq
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys


def getOrdersFromPagination(driver):
    soupPayments = []
    content = driver.page_source
    soupPayments = soupPayments + [BeautifulSoup(content, features="lxml")]
    while driver.find_elements_by_css_selector("li:last-child > .pagination__button:not(.pagination__button--disabled)"):
        driver.find_elements_by_class_name("pagination__button")[-1].click()
        time.sleep(2)
        content = driver.page_source
        soupPayments = soupPayments + [BeautifulSoup(content, features="lxml")]
    return soupPayments


def getNetPayout(soupPayments, calendarDayOfWeek, calendarMonthAbrev, dateForDay):
    total = 0
    non_decimal = re.compile(r"[^\d]+")
    for i in soupPayments:
        for j in i.select("tbody tr._style_2T0IvR"):
            orderInfo = j.find_all("td")

            orderDate = parse(orderInfo[0].text)
            if (orderDate.day == dateForDay.day and orderDate.hour > 10) or (orderDate.day == (dateForDay + dt.timedelta(days=1)).day and orderDate.hour < 3):
                print(orderInfo[0].text)
                orderPayment = orderInfo[-1]
                print(orderPayment.text)
                if ")" in orderPayment.text:
                    total -= int(non_decimal.sub("", orderPayment.text))
                else:
                    total += int(non_decimal.sub("", orderPayment.text))
    return total


def getToOrdersByDate(driver, calendarDate, calendarMonth):
    calendarInputElem = driver.find_element_by_css_selector("input[placeholder='ll - ll']")
    calendarInputElem.click()
    time.sleep(6)
    calendarButtonElems = driver.find_elements_by_xpath('//div[text()="' + str(int(calendarDate)) + '"]')
    print(calendarButtonElems)
    calendarButtonElem = (
        calendarButtonElems[-1]
        if int(calendarDate) > 23 and driver.find_elements_by_xpath("//h3[text()='" + calendarMonth + " 2020']")
        else calendarButtonElems[0]
    )
    calendarButtonElem.click()
    time.sleep(4)


def scrapeComplex(driver, dateForDay):
    time.sleep(2)
    calendarDate = dateForDay.strftime("%d")
    calendarMonthAbrev = dateForDay.strftime("%b")
    calendarMonth = dateForDay.strftime("%B")
    calendarDayOfWeekAbrev = calendar.day_abbr[dateForDay.weekday()]
    print(
        "Today's date:",
        calendarDate,
        " month: ",
        calendarMonthAbrev,
        " day of week: ",
        calendarDayOfWeekAbrev,
    )
    getToOrdersByDate(driver, calendarDate, calendarMonth)
    soupPayments = getOrdersFromPagination(driver)
    if calendarDayOfWeekAbrev == "Sun":
        nextCalendarDate = (dateForDay + dt.timedelta(days=1)).strftime("%d")
        print(
            "Today's date:",
            nextCalendarDate,
            " month: ",
            calendarMonthAbrev,
            " day of week: ",
            calendarDayOfWeekAbrev,
        )
        getToOrdersByDate(driver, nextCalendarDate, calendarMonth)
        soupPayments += getOrdersFromPagination(driver)

    netPayout = getNetPayout(soupPayments, calendarDayOfWeekAbrev, calendarMonthAbrev, dateForDay)

    print(netPayout / 100)
    return netPayout


def myScraper(dateForDay):
    # dateForDay = date.today() - dt.timedelta(days=1)
    options = webdriver.ChromeOptions()
    # Path to your chrome profile
    options.add_argument("user-data-dir=/Users/kwhite/Library/Application Support/Google/Chrome/Default")
    driver = webdriver.Chrome("/usr/local/lib/chromium-browser/chromedriver", options=options)
    driver.get()
    driver.implicitly_wait(10)
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
