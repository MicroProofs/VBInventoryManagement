import datetime as dt

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import twilio_sms as ts
import ubereats.uber_scraper as ue_scraper
from doordash import dd_scraper
from grubhub import gh_scraper
from postmates import pm_scraper


def main():
    try:
        dateForDay = dt.date.today() - dt.timedelta(days=2)
        ue_totals = ue_scraper.myScraper(dateForDay)
        dd_totals = dd_scraper.myScraper(dateForDay)
        pm_totals = pm_scraper.myScraper(dateForDay)
        gh_totals = gh_scraper.myScraper(dateForDay)
        ue = (ue_totals) / 100
        dd = dd_totals / 100
        gh = gh_totals / 100
        pm = pm_totals / 100
        fn_t = (dd_totals + pm_totals + ue_totals + gh_totals) / 100
        output_date = dateForDay.strftime("%Y/%m/%d")
        final = f"Date: {output_date}\nNet Payouts:\n -Uber Eats: ${ue}\n -Postmates: ${pm}\n -Doordash: ${dd}\n -GrubHub: ${gh}\n\nFinal Total: ${fn_t}"
        print(final)
        ts.send_message(final, "+1")
        f = open("delivery_numbers.txt", "a")
        f.write(final)
        f.write("\n\n")
        f.close()
    except Exception as e:
        # ts.send_message("Error occurred when grabbing totals", '+14437590826')
        print(e)


main()
