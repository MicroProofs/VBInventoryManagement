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

# def getOrdersFromDate(driver, theDate, func):
#     # time.sleep(10)
#     calendarButtonElems = driver.find_elements_by_xpath(
#         '//td[text()="'+theDate+'"]')
#     print(calendarButtonElems)
#     soupPayments = []
#     for i in range(0, len(calendarButtonElems)):
#         item = driver.find_elements_by_xpath(
#             '//td[text()="'+theDate+'"]/..//a[@href]')[i]
#         item.click()
#         time.sleep(2)
#         hourOfOrder = parse(driver.find_elements_by_xpath(
#             '//span[text()="Pickup time:"]/../span')[-1].text).hour
#         print(hourOfOrder)
#         if func(hourOfOrder):
#             content = driver.page_source
#             soupPayments = (soupPayments +
#                             [BeautifulSoup(content, features="lxml")])
#         driver.back()
#     return soupPayments


def sendKeysOneAtATime(element, phrase):
    for i in phrase:
        element.send_keys(i)
        time.sleep(random.randint(1, 10) / 100)


def scrapeComplex(driver, dateForDay):
    soupPayments = []
    time.sleep(2)
    # calendarDate = str(dateForDay.strftime("%-m/%-d/%Y"))

    driver.find_element_by_class_name("js-email-sign-in").click()
    time.sleep(4)
    driver.find_element_by_css_selector(".prev > span").click()
    time.sleep(4)
    content = driver.page_source
    soupPayments = BeautifulSoup(content, features="lxml")
    cal = calendar.day_name[5:7] + calendar.day_name[0:5]
    hoursDict = {}
    finalArray = []
    for i in cal:
        hoursDict[i] = []
        hoursList = soupPayments.select("." + i.lower() + " .data")
        for j in hoursList:
            if (not j.find("div", {"class": "label-role"})) or (
                not "Trainee" in j.find("div", {"class": "label-role"}).text
                and not "Advert" in j.find("div", {"class": "label-role"}).text
            ):
                timeList = j.find("div", {"class": "time"}).text.strip().split(" - ")
                noDuplicatesTimeList = [lm for lm in timeList if not lm in hoursDict[i]]
                hoursDict[i] = hoursDict[i] + noDuplicatesTimeList

    print(hoursDict)
    for k in range(0, 7):
        hoursDict[cal[k]] = sorted(
            [
                dt.datetime.combine(
                    dateForDay + dt.timedelta(days=k if parse(m).hour > 3 else k + 1),
                    parse(m).time(),
                )
                for m in hoursDict[cal[k]]
            ]
        )
        hoursDict[cal[k]][0] = hoursDict[cal[k]][0] - dt.timedelta(hours=1)
        hoursDict[cal[k]][-1] = hoursDict[cal[k]][-1] + dt.timedelta(hours=1)
        finalArray = finalArray + [[a.strftime("%Y-%m-%d %H:%M:%S") for a in hoursDict[cal[k]]]]
    # print(finalArray)
    for g in finalArray:
        print("[", end="")
        for f in range(0, len(g) - 1):
            print("'" + g[f] + ("', " if f < len(g) - 2 else "', '" + g[f + 1] + "'"), end="")
        print("],")
    return finalArray


def myScraper():
    profile = webdriver.FirefoxProfile()
    driver = webdriver.Firefox(
        firefox_profile=profile, executable_path="/usr/local/lib/firefox-browser/geckodriver"
    )
    driver.get("https://app.joinhomebase.com/schedule_builder")
    driver.implicitly_wait(10)
    time.sleep(1)
    try:
        a = scrapeComplex(driver, date.today() - dt.timedelta(days=7))
    except Exception as inst:
        raise inst
    finally:
        driver.quit()
    return a


myScraper()
