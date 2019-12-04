import requests
import json
import csv
import datetime
from cal_data import cal_data
import time


def create_csv(csv_head, zone):
    path = "./" + zone + '.csv'
    with open(path, 'w', newline='') as f:
        csv_write = csv.writer(f)
        # csv_head = ["good","bad"]
        csv_write.writerow(csv_head)


def write_csv(data_row,zone):
    path = "./" + zone + '.csv'
    with open(path, 'a+', newline='') as f:
        csv_write = csv.writer(f)
        # data_row = ["1","2"]
        csv_write.writerow(data_row)


zones = ['E12', 'E32', 'N6', 'N23', 'E21', 'N24', 'N21', 'E11', 'N1-N2', 'E3-E7', 'N22', 'E1-E2']

if __name__ == '__main__':
    while 1:
        for zone in zones:
            date_from = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime('%Y-%m-%dT01:00:00')
            date_to = datetime.datetime.now().strftime('%Y-%m-%dT00:00:00')
            url = 'https://api.data.um.edu.mo/service/facilities/power_meter_locations/v1.0.0/' + zone
            # url = 'https://api.data.um.edu.mo/service/facilities/power_consumption/v1.0.0/' + zone + '/?date_from=' + date_to + '&date_to=' + date_to
            headers = {"Authorization": "Bearer 2c16a143-9fb3-3baf-ab8a-dcfedd62fd29"}
            response = requests.get(url, headers=headers)
            count = 0
            if response.json()['_embedded'] != []:
                r = response.json()['_embedded'][0]['meters']
                meters = ['date_time']
                for i in r:
                    meters.append(i['code'])
                # create_csv(meters, zone)
                while date_from <= date_to:
                    try:
                        row = []
                        url = 'https://api.data.um.edu.mo/service/facilities/power_consumption/v1.0.0/all?date_from=' + date_from + '&date_to=' + date_from + '&zone_code=' + zone
                        response = requests.get(url, headers=headers)
                        while not response.content:
                            response = requests.get(url, headers=headers)
                        r = response.json()['_embedded']
                        for i in meters:
                            if i == 'date_time':
                                row.append(date_from)
                            else:
                                if r != []:
                                    for j in r:
                                        if j['meterCode'] == i:
                                            if 'kwh' in j['readings'].keys():
                                                row.append(j['readings']['kwh'])
                                            else:
                                                row.append('0')
                                            break
                                    if len(row) != meters.index(i) + 1:
                                        url1 = 'https://api.data.um.edu.mo/service/facilities/power_consumption/v1.0.0/all?date_from=' + date_from + '&date_to=' + date_from + '&zone_code=' + zone + '&meter_code=' + i
                                        response = requests.get(url1, headers=headers)
                                        while not response.content:
                                            response = requests.get(url1, headers=headers)
                                        r1 = response.json()['_embedded']
                                        if r1 != []:
                                            if 'kwh' in r1[0]['readings'].keys():
                                                row.append(r1[0]['readings']['kwh'])
                                            else:
                                                row.append(0)
                                        else:
                                            row.append(0)
                                else:
                                    row.append(0)
                        date_from = (datetime.datetime.strptime(date_from, '%Y-%m-%dT%H:%M:%S') + datetime.timedelta(
                    hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
                        write_csv(row, zone)
                        count += 1
                        if count == 24:
                            time.sleep(3)
                            count = 0
                    except requests.exceptions.ConnectionError:
                        time.sleep(2)
                    except json.decoder.JSONDecodeError:
                        time.sleep(2)
        cal_data()
        time.sleep(60*60*24)