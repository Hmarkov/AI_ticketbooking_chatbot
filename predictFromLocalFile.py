"""
Written by Boyan Yonkov
This file is used to obtain past data of delays at the station that the user is at the moment
and uses @regression.py and @kNN.py for predicting the delay at the final destination.
Note: 'This is only for the journey between Weymouth and London Waterloo as the data is stored locally
to reduce waitting time'
"""
from datetime import datetime, date
from regression import regression_prediction
from kNN import knn_prediction
import json

# Documentation can be found at
#   https://wiki.openraildata.com/index.php/HSP

api_url = "https://hsp-prod.rockshore.net/api/v1/serviceMetrics"
api_url_details = "https://hsp-prod.rockshore.net/api/v1/serviceDetails"

headers = {"Content-Type": "application/json"}
auths = ("mep19zju@uea.ac.uk", "f7!3zaxpHPhGExp")


# Function to extract all the delays at the current station and all the delays was at the final
# destination for that specific journey.
# Input: Station name
# Output: Two arrays - [delays at current station] and [delays at final station]
def get_delays(station):
    details = open('C:/Users/icko5/Desktop/chatbot/BotChat/serviceAttributeDetails.json')
    example = json.loads(details.readline().strip())
    loc = example['serviceAttributesDetails']['locations']
    station_index = -1
    for location in loc:
        station_index += 1
        if location['location'] == station:
            break
    end_delay = []
    at_station_delay = []

    for line in details:
        json_obj = json.loads(line.strip())
        actual_arrival = json_obj['serviceAttributesDetails']['locations'][-1]['actual_ta']
        planned_arrival = json_obj['serviceAttributesDetails']['locations'][-1]['gbtt_pta']
        if len(json_obj['serviceAttributesDetails']['locations']) <= station_index:
            continue
        if actual_arrival != '' and planned_arrival != '':
            if int(actual_arrival) > int(planned_arrival):
                planned_time = datetime.strptime(planned_arrival, '%H%M')
                actual_time = datetime.strptime(actual_arrival, '%H%M')
                final_delay = datetime.combine(date.today(), actual_time.time()) - datetime.combine(date.today(),
                                                                                                    planned_time.time())
                end_delay.append(final_delay.seconds // 60)
                actual_at_station = json_obj['serviceAttributesDetails']['locations'][station_index]['actual_ta']
                planned_at_station = json_obj['serviceAttributesDetails']['locations'][station_index]['gbtt_pta']
                if actual_at_station == '':
                    at_station_delay.append(0)
                elif int(actual_at_station) < int(planned_at_station):
                    at_station_delay.append(0)
                else:
                    actual_at_station = datetime.strptime(actual_at_station, '%H%M')
                    planned_at_station = datetime.strptime(planned_at_station, '%H%M')
                    delay_at_station = datetime.combine(date.today(), actual_at_station.time()) - datetime.combine(
                        date.today(),
                        planned_at_station.time())
                    at_station_delay.append(delay_at_station.seconds // 60)

    return end_delay, at_station_delay

# Helper functions for finding the delay using regression and kNN predictive models
# Input: Current Station (e.g. "WAT") & Delay at current station in minutes (e.g. 5)
# Output: Expected Delay at final station in minutes
def predict_using_regression(station, delay_at_station):
    a, b = get_delays(station)
    prediction = regression_prediction(delay_at_station, b, a)
    return round(prediction[0][0], 2)


def predict_using_knn(station, delay_at_station):
    a, b = get_delays(station)
    prediction = knn_prediction(delay_at_station, b, a)
    return round(prediction[0][0], 2)

def predict_total(currentloc,currentdelay):
    return predict_using_regression(currentloc,currentdelay)

# print(predict_using_regression('WAT', 5))
# print(predict_using_knn('WAT', 5))