__author__ = 'kwhite'

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


def getEachItem(driver, ele, month):
    pageArray = []
    if(parse(ele.find_elements_by_css_selector('td')[0].text).month == month and not "ERROR" in ele.find_elements_by_css_selector('td')[2].text and not "Appeasement" in ele.find_elements_by_css_selector('td')[1].text):
        ele.click()
        time.sleep(1.3)
        for order_item in driver.find_elements_by_css_selector('.order-detail .order-detail-section')[1].find_elements_by_css_selector('tr._style_2T0IvR'):
            if(order_item.text):
                # print(order_item.text)
                pageArray += [[order_item.find_elements_by_css_selector('td')
                               [0].text, order_item.text]]
        driver.find_element_by_css_selector(
            '.order-detail svg._style_1OXPmY').click()
        time.sleep(1.3)
    return pageArray


def getOrdersFromPagination(driver, month):
    arrayArray = []
    for ele in driver.find_elements_by_class_name("_style_2T0IvR")[1:]:
        arrayArray += getEachItem(driver, ele, month)
    while(driver.find_elements_by_css_selector("li:last-child > .pagination__button:not(.pagination__button--disabled)")):
        driver.find_elements_by_class_name(
            'pagination__button')[-1].click()
        time.sleep(3)
        for ele in driver.find_elements_by_class_name("_style_2T0IvR")[1:]:
            arrayArray += getEachItem(driver, ele, month)
    joinedArray = (seq(arrayArray)
                   .reduce(lambda x, y: x + [y] if y[0] else x[:-1] + [x[-1] + [y[1]]], []))
    return joinedArray


def getNetPayout(soupPayments, calendarDayOfWeek, calendarMonthAbrev, calendarDate):
    total = 0
    non_decimal = re.compile(r'[^\d]+')
    for i in soupPayments:
        for j in i.select('tbody tr._style_2T0IvR'):
            orderInfo = j.find_all('td')

            orderDate = parse(orderInfo[0].text)
            if ((orderDate.day == calendarDate and orderDate.hour > 10) or
                    (orderDate.day == calendarDate+1 and orderDate.hour < 3)):
                print(orderInfo[0].text)
                orderPayment = orderInfo[-1]
                print(orderPayment.text)
                if ")" in orderPayment.text:
                    total -= int(non_decimal.sub('', orderPayment.text))
                else:
                    total += int(non_decimal.sub('', orderPayment.text))
    return total


def getToOrdersByDate(driver, calendarDate, calendarMonth):
    calendarInputElem = driver.find_element_by_css_selector(
        "input[placeholder='ll - ll']")
    calendarInputElem.click()
    time.sleep(4)
    while(not calendarMonth in driver.find_element_by_css_selector("div._style_4kEO6r div h3").text):
        driver.find_element_by_css_selector(
            "div._style_4kEO6r div svg._style_UBVZ6._style_1Jxdph").click()
        time.sleep(1)
    calendarButtonElems = driver.find_elements_by_xpath(
        '//div[text()="'+str(int(calendarDate))+'"]')
    print(calendarButtonElems)
    calendarButtonElem = calendarButtonElems[-1] if int(
        calendarDate) > 23 and driver.find_elements_by_xpath("//h3[text()='"+calendarMonth+" 2020']") else calendarButtonElems[0]
    calendarButtonElem.click()
    time.sleep(4)


def scrapeComplex(driver, dateForDay):
    time.sleep(2)
    calendarDate = dateForDay.strftime("%d")
    calendarMonthAbrev = dateForDay.strftime("%b")
    calendarMonth = dateForDay.strftime("%B")
    calendarDayOfWeekAbrev = calendar.day_abbr[dateForDay.weekday()]
    print("Today's date:", calendarDate, " month: ",
          calendarMonthAbrev, " day of week: ", calendarDayOfWeekAbrev)
    getToOrdersByDate(driver, int(calendarDate), calendarMonth)

    soupPayments = getOrdersFromPagination(driver, dateForDay.month)
    for soup in soupPayments:
        if "1x" in soup[0]:
            print(soup)
    for soup in soupPayments:
        if "2x" in soup[0]:
            print(soup)

    for soup in soupPayments:
        if "3x" in soup[0]:
            print(soup)
    # if calendarDayOfWeekAbrev == "Sun":
    #     getToOrdersByDate(driver, int(calendarDate)+1, calendarMonth)
    #     soupPayments += getOrdersFromPagination(driver)

    # netPayout = getNetPayout(
    #     soupPayments, calendarDayOfWeekAbrev, calendarMonthAbrev, int(calendarDate))

    # print(netPayout/100)
    return 0


def myScraper():
    options = webdriver.ChromeOptions()
    # Path to your chrome profile
    options.add_argument(
        "user-data-dir=/Users/kwhite/Library/Application Support/Google/Chrome/Default")
    driver = webdriver.Chrome(
        "/usr/local/lib/chromium-browser/chromedriver", options=options)
    # profile = webdriver.FirefoxProfile(
    #     '/Users/kwhite/Library/Application Support/Firefox/Profiles/leaxj4k1.default-1493295390185-1570994616071')
    # driver = webdriver.Firefox(
    #     firefox_profile=profile, executable_path="/usr/local/lib/firefox-browser/geckodriver")
    driver.get(
        )
    driver.implicitly_wait(15)
    time.sleep(1)
    try:
        for i in range(1, 32, 7):
            a = scrapeComplex(driver, date(2019, 12, i))
    except Exception as inst:
        raise inst
    finally:
        driver.quit()
    return a


myScraper()
