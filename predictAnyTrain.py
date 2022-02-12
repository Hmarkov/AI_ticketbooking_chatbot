import time

import numpy as np
import requests
import json
import pandas as pd

api_url = "https://hsp-prod.rockshore.net/api/v1/serviceMetrics"
api_url_details = "https://hsp-prod.rockshore.net/api/v1/serviceDetails"
headers = {"Content-Type": "application/json"}
auths = ("mep19zju@uea.ac.uk", "f7!3zaxpHPhGExp")

def predict_delay(from_loc, to_loc, from_time, to_time, days):
    data = {
        "from_loc": from_loc,
        "to_loc": to_loc,
        "from_time": from_time,
        "to_time": to_time,
        "from_date": "2021-10-20",
        "to_date": "2021-12-20",
        "days": days
    }

    r = requests.post(api_url, headers=headers, auth=auths, json=data)

    info = json.dumps(json.loads(r.text), sort_keys=True, indent=2, separators=(',', ': '))
    info2 = json.loads(info)
    print(info2)
    with open('Services.json', 'w') as outfile:
        json.dump(info2, outfile)
    rids = []

    for i in range(len(info2['Services'])):
        if int(info2['Services'][i]['Metrics'][0]['num_not_tolerance']) > 2:
            b = info2['Services'][i]['serviceAttributesMetrics']['rids']
            for j in b:
                rids.append(j)
    delayed_times = []
    df = open('serviceAttributeDetails.json', 'w')
    for rid in rids:
        rid_data = {
            "rid": str(rid)
        }
        request = requests.post(api_url_details, headers=headers, auth=auths, json=rid_data)
        details = json.dumps(json.loads(request.text), sort_keys=True, indent=2, separators=(',', ': '))
        a_details = json.loads(details)

        json_string = json.dumps(a_details)
        df.write(json_string)
        df.write('\n')

        arrival_time = a_details['serviceAttributesDetails']['locations'][-1]['actual_ta']
        predicted_arrival = a_details['serviceAttributesDetails']['locations'][-1]['gbtt_pta']
        if arrival_time != '' and predicted_arrival != '':
            if int(arrival_time) > int(predicted_arrival):
                delayed_times.append(arrival_time)
    df.close()
    return delayed_times

def enter_station(from_to):
    data = pd.read_csv("stations.csv")
    loc = str(input(f"Enter {from_to} station: "))
    station = data.loc[data['name'].str.contains(loc, case=False)]
    if len(station) == 1:
        return station['alpha3'][0]
    else:
        print(f"There are multiple stations containing '{loc}': ")
        for i in range(len(station)):
            print(station['name'][i])
        selected = input("Please enter a station from the list: ")
        new_station = data.loc[data['name'].str.contains(selected, case=False)]
        return new_station['alpha3'][0]

# Returns the 3 letter name of the stations
from_loc = enter_station('starting')
to_loc = enter_station('final')
start = time.time()
print(predict_delay('WEY', 'WAT', '0600', '2000', 'WEEKDAY'))
end = time.time()
print(end - start)


