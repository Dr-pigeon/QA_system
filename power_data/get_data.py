import requests
import json
import csv
import time
import datetime
from threading import Timer


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

def get_data():
    zones = ['E1-E2', 'E12', 'E32', 'N6', 'N23', 'E21', 'N24', 'N21', 'E11', 'N1-N2', 'E33', 'N8', 'N25', 'E22', 'E34',
             'E3-E7', 'E31', 'N22', 'N26']
    headers = {"Authorization": "Bearer 5943d8ed-920d-3bf0-b01a-628f1e9294f1"}
    date_to = datetime.datetime.now().strftime('%Y-%m-%dT%H:00:00')
    for zone in zones:
        row = []
        url = 'https://api.data.um.edu.mo/service/facilities/power_consumption/v1.0.0/all?date_from=' + date_to + '&date_to=' + date_to + '&zone_code=' + zone
        response = requests.get(url, headers=headers)
        status = response.status_code
        while status != 200:
            url = 'https://api.data.um.edu.mo/service/facilities/power_consumption/v1.0.0/all?date_from=' + date_to + '&date_to=' + date_to + '&zone_code=' + zone
            response = requests.get(url, headers=headers)
            status = response.status_code
        r = response.json()['_embedded']
        f = open('./' + zone + '.csv', 'r')
        reader = csv.reader(f)
        for meters in reader:
            break
        f.close()
        for i in meters:
            if i == 'date_time':
                row.append(date_to)
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
                        url1 = 'https://api.data.um.edu.mo/service/facilities/power_consumption/v1.0.0/all?date_from=' + date_to + '&date_to=' + date_to + '&zone_code=' + zone + '&meter_code=' + i
                        response = requests.get(url1, headers=headers)
                        r1 = response.json()['_embedded']
                        if r1 != []:
                            if 'kwh' in r1[0]['readings'].keys():
                                row.append(r1[0]['readings']['kwh'])
                            else:
                                row.append('0')
                        else:
                            row.append('0')
                else:
                    row.append('0')
        print(row)
        #write_csv(row, zone)
        time.sleep(2)
    t = Timer(3600,get_data())
    t.start()


if __name__ == '__main__':
    get_data()

