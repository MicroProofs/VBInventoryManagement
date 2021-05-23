import datetime as dt
import json
from operator import getitem

import pytz
from functional import seq

from square.client import Client

utc = pytz.utc
eastern = pytz.timezone("US/Eastern")
fmt = "%Y-%m-%d %H:%M:%S"


time_slice_list = [
    ["2020-12-05 10:00:00", "2020-12-05 16:00:00", "2020-12-05 19:00:00", "2020-12-05 21:00:00", "2020-12-06 03:00:00"],
    ["2020-12-06 10:00:00", "2020-12-06 16:00:00", "2020-12-06 19:00:00", "2020-12-06 21:00:00", "2020-12-07 03:00:00"],
    ["2020-12-07 10:00:00", "2020-12-07 16:00:00", "2020-12-07 21:00:00", "2020-12-08 03:00:00"],
    ["2020-12-08 10:00:00", "2020-12-08 16:00:00", "2020-12-08 21:00:00", "2020-12-09 03:00:00"],
    ["2020-12-09 10:00:00", "2020-12-09 15:00:00", "2020-12-09 21:00:00", "2020-12-10 03:00:00"],
    ["2020-12-10 10:00:00", "2020-12-10 16:00:00", "2020-12-10 19:00:00", "2020-12-10 21:00:00", "2020-12-11 03:00:00"],
    ["2020-12-11 10:00:00", "2020-12-11 16:00:00", "2020-12-11 19:00:00", "2020-12-11 21:00:00", "2020-12-12 03:00:00"],
]


def string_to_time(theDate):
    date = dt.datetime.strptime(theDate, fmt)
    date_eastern = eastern.localize(date)
    return date_eastern


def time_converter(theDate):
    date = dt.datetime.strptime(theDate, fmt)
    date_eastern = eastern.localize(date, is_dst=None)
    date_utc = date_eastern.astimezone(utc)
    # print(date_utc.isoformat('T'))
    return date_utc.isoformat("T")


def get_orders(start_time, end_time):

    start_utc = time_converter(start_time)
    end_utc = time_converter(end_time)


    result = client.orders.search_orders(
        body={
            "location_ids": ["K42JEZ5X764DM"],
            "query": {
                "filter": {
                    "state_filter": {"states": ["COMPLETED"]},
                    "date_time_filter": {"closed_at": {"start_at": start_utc, "end_at": end_utc}},
                },
                "sort": {"sort_field": "CLOSED_AT", "sort_order": "ASC"},
            },
            "limit": 1000,
            "return_entries": False,
        }
    )
    if result.is_success():
        return result
    elif result.is_error():
        print(result.errors)


def get_first_key(thing):
    return list(thing.keys())[0]


def get_order_from_ids(ids):
    body = {"order_ids": ids, "location_id": "K42JEZ5X764DM"}

    result = client.orders.batch_retrieve_orders(body=body)
    if result.is_success():
        return seq(result.body["orders"]).map(lambda fg: {fg["id"]: fg["tenders"][0]["type"]}).reduce(lambda x, y: dict(x, **y))
    elif result.is_error():
        print(result.errors)


def split_orders_and_returns(order_array):
    return seq(order_array).reduce(
        lambda ls, x: {
            "square_sales": ls["square_sales"] + [x],
            "square_returns": ls["square_returns"],
        }
        if "tenders" in x
        else {"square_sales": ls["square_sales"], "square_returns": ls["square_returns"] + [x]},
        {"square_sales": list(), "square_returns": list()},
    )


def map_returns_amount_source(return_array):
    return seq(return_array).map(
        lambda x: {
            x["closed_at"]: {
                "return_amount": x["net_amounts"]["total_money"]["amount"],
                "return_source_id": x["returns"][0]["source_order_id"],
            }
        }
    )


def map_returns_amount_tender(return_array, returned_orders):
    return seq(return_array).map(
        lambda x: {get_first_key(x): dict(x[get_first_key(x)], **{"tender": returned_orders[x[get_first_key(x)]["return_source_id"]]})}
    )


def handle_tender(tender, keys):
    try:
        return seq(keys).reduce(getitem, tender)
    except (KeyError, IndexError, TypeError):
        return 0


def map_to_cash_sales(order_array):
    return seq(order_array).map(
        lambda order: {
            order["closed_at"]: seq(order["tenders"])
            .filter(lambda tender: "CASH" == tender["type"])
            .sum(lambda tender: handle_tender(tender, ["amount_money", "amount"]))
        }
    )


def map_to_tips(order_array):
    return seq(order_array).map(
        lambda order: {
            order["closed_at"]: seq(order["tenders"])
            .filter(lambda tender: "CASH" != tender["type"])
            .sum(lambda tender: handle_tender(tender, ["tip_money", "amount"]))
        }
    )


def summation_all_values(order_array):
    return seq(order_array).reduce(lambda x, y: x + list(y.values())[0], 0)


for days in time_slice_list:
    print("Getting one day of times")
    for i in range(0, len(days)):
        if i == len(days) - 1:
            continue
        else:
            s = days[i]
            e = days[i + 1]
            try:
                result = get_orders(s, e)
                # print(json.dumps(split_orders_and_returns(result.body['orders']), indent=2,sort_keys=True))
                # split_list=split_orders_and_returns(result.body['orders'])
                # returns_list=map_returns_amount_source(split_list['square_returns'])
                # print(returns_list)
                # returned_orders=get_order_from_ids(list(seq(returns_list).map(lambda x: list(x.values())[0]['return_source_id'])))
                # print(returned_orders)
                # final_return_map=map_returns_amount_tender(returns_list, returned_orders)
                # print(final_return_map)
                # print(result.body['orders'])
                if "orders" in result.body:
                    all_cash_sales = map_to_cash_sales(result.body["orders"])
                    all_tips = map_to_tips(result.body["orders"])
                else:
                    all_cash_sales = [{0: 0}]
                    all_tips = [{0: 0}]
                print("Tips for " + s + " to " + e + " >>> " + str(summation_all_values(all_tips) / 100.0))
                print("Cash for " + s + " to " + e + " >>> " + str(summation_all_values(all_cash_sales) / 100.0))
                print("\n")
            except Exception as ag:
                print("Couldn't get tips and cash for " + s + " to " + e, ag)
                print("\n")
