import json

from functional import seq
from square.client import Client

 
def get_orders(): 
    client = Client(
        access_token='',
        environment='production',
    )
    
    result = client.orders.search_orders(
        body = {
            "return_entries": False,
            "limit": 1000,
            "location_ids": [
                "K42JEZ5X764DM"
            ],
            "query": {
                "filter": {
                    "date_time_filter": {
                        "closed_at": {
                            "start_at": "2019-12-25T10:30:00+00:00",
                            "end_at": "2019-12-26T02:30:00+00:00"
                        }
                    },
                    "state_filter": {
                        "states": [
                            "COMPLETED"
                        ]
                    }
                },
                "sort": {
                    "sort_field": "CLOSED_AT",
                    "sort_order": "DESC"
                }
            }
        }
    )

    if result.is_success():
        print(json.dumps(result.body, indent=2, sort_keys=True))
        print(seq(result.body['orders'])
        .map(lambda x: 'line_items' in x))
        print(seq(result.body['orders'])
        .map(lambda x: seq(x['line_items'] if 'line_items' in x else [{'name':'N/A', 'quantity':0}])
        .map(lambda y: "name: " + (y['name'] if 'name' in y else "Custom Amount") + " quantity: " + str(y['quantity']))
        .to_list())
        .flatten())       
    elif result.is_error():
        print(result.errors)
