import numpy as np
import csv


def create_csv(csv_head, zone):
    path = "./" + zone + '.csv'
    with open(path, 'w', newline='') as f:
        csv_write = csv.writer(f)
        # csv_head = ["good","bad"]
        csv_write.writerow(csv_head)


def write_csv(data_row, zone):
    path = "./" + zone + '.csv'
    with open(path, 'a+', newline='') as f:
        csv_write = csv.writer(f)
        # data_row = ["1","2"]
        csv_write.writerow(data_row)


def cal_data():
    zones = ['N23', 'E21', 'N24',  'E11', 'E3-E7', 'E1-E2', 'E12', 'E32', 'N6',  'N1-N2',  'N21']
    for zone in zones:
        data = []
        with open('./' + zone + '.csv', 'r') as f:
            reader = csv.reader(f)
            for i in reader:
                data.append(i)
        for i in range(2, len(data)):
            for j in range(1, len(data[0])):
                if data[i][j] == '0' and data[i - 1][j] != '0' and i == len(data) - 1:
                    data[i][j] = float(data[i - 1][j])
                elif data[i][j] == '0' and data[i - 1][j] != '0' and data[i + 1][j] != '0':
                    data[i][j] = float((float(data[i - 1][j]) + float(data[i + 1][j])) / 2)
                elif data[i][j] == '0' and data[i - 1][j] != '0':
                    data[i][j] = float(data[i - 1][j])
                elif data[i][j] == '0':
                    data[i][j] = 0
        create_csv(data[0], zone + '_new')
        for i in range(1, len(data)):
            write_csv(data[i], zone + '_new')

if __name__ == '__main__':
    cal_data()