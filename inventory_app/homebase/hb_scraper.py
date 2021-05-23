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


def hoursEachDay(cal, hoursDict, soupPayments):
    for i in cal:
        hoursDict[i] = []
        hoursList = soupPayments.select("." + i.lower() + " .data")
        for j in hoursList:
            if (not j.find("div", {"class": "label-role"})) or (
                not "Trainee" in j.find("div", {"class": "label-role"}).text and not "Advert" in j.find("div", {"class": "label-role"}).text
            ):
                timeList = j.find("div", {"class": "time"}).text.strip().split(" - ")
                noDuplicatesTimeList = [lm for lm in timeList if not lm in hoursDict[i]]
                hoursDict[i] = hoursDict[i] + noDuplicatesTimeList

    return hoursDict


def startEndTotalTimes(timeList, dateForDay):

    start_hour = parse(timeList.strip().split(" - ")[0])
    end_hour = parse(timeList.strip().split(" - ")[-1])
    start_time = (
        dt.datetime.combine(dateForDay, start_hour.time()) if start_hour.hour > 3 else dt.datetime.combine(dateForDay + dt.timedelta(days=1), start_hour.time())
    )
    end_time = (
        dt.datetime.combine(dateForDay, end_hour.time()) if end_hour.hour > 3 else dt.datetime.combine(dateForDay + dt.timedelta(days=1), end_hour.time())
    )
    total_hours = (end_time - start_time).total_seconds() / 3600
    return start_hour, end_hour, total_hours


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
    employeeDict = {}
    employeeWeekDict = {}
    hoursDict = hoursEachDay(cal, hoursDict, soupPayments)

    for i in soupPayments.select("tbody.user-body"):
        emp_name = i.select(".name")[0].text.strip()
        employeeDict[emp_name] = []
        for j in cal:
            hoursList = i.select("." + j.lower() + " .cell")
            for n in range(len(hoursList)):
                k = hoursList[n]
                if n > 0:
                    if k.find("div", {"class": "time"}):
                        timeList = k.find("div", {"class": "time"}).text
                        start_hour, end_hour, total_hours = startEndTotalTimes(timeList, dateForDay)
                        if (not k.find("div", {"class": "label-role"})) or (
                            not "Trainee" in k.find("div", {"class": "label-role"}).text and not "Advert" in k.find("div", {"class": "label-role"}).text
                        ):
                            employeeDict[emp_name][-1] = employeeDict[emp_name][-1] + "   :    " + timeList + " trailer" + " hours= " + str(total_hours)
                        else:
                            employeeDict[emp_name][-1] = employeeDict[emp_name][-1] + "   :    " + timeList + " hours= " + str(total_hours)
                    else:
                        employeeDict[emp_name][-1] = employeeDict[emp_name][-1] + "   :    " + "blank"
                else:
                    if k.find("div", {"class": "time"}):
                        timeList = k.find("div", {"class": "time"}).text
                        start_hour, end_hour, total_hours = startEndTotalTimes(timeList, dateForDay)
                        order = start_hour.hour + start_hour.minute / 100
                        if (not k.find("div", {"class": "label-role"})) or (
                            not "Trainee" in k.find("div", {"class": "label-role"}).text and not "Advert" in k.find("div", {"class": "label-role"}).text
            ):
                            employeeDict[emp_name] = employeeDict[emp_name] + [str(order) + ">" + timeList + " trailer" + " hours= " + str(total_hours)]
                        else:
                            employeeDict[emp_name] = employeeDict[emp_name] + ["999>" + timeList + " hours= " + str(total_hours)]
                    else:
                        employeeDict[emp_name] = employeeDict[emp_name] + ["blank"]
    # for i in employeeDict:
    #     print(i + " hours:" + str(employeeDict[i]))
    #     print()

    for i in range(7):
        print(cal[i])
        dayList = []
        for j in employeeDict:
            if "pm" in str(employeeDict[j][i]) or "am" in str(employeeDict[j][i]):
                dayList = dayList + [str(employeeDict[j][i]).split(">")[0] + ">" + j + " hours:  " + str(employeeDict[j][i]).split(">")[-1]]
        [print(i.split(">")[-1]) for i in sorted(dayList)]
        print("\n\n")

    # print(hoursDict)
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
    driver = webdriver.Firefox(firefox_profile=profile, executable_path="/usr/local/lib/firefox-browser/geckodriver")
    driver.get("https://app.joinhomebase.com/schedule_builder")
    driver.implicitly_wait(20)
    time.sleep(1)
    try:
        a = scrapeComplex(driver, date.today() - dt.timedelta(days=8))
    except Exception as inst:
        raise inst
    finally:
        driver.quit()
    return a


myScraper()
