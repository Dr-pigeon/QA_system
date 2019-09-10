# -*- coding:utf-8 -*-
# -*- created by: mo -*-
import json
import requests

def WordToVec(text):
    url = 'http://10.119.186.27:12031/encodeSent'
    headers = {'Content-Type': 'application/json'}
    data = {"text": text, "lang": "zh-CN"}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    decode_text = json.loads(response.content)
    vector = decode_text['result'][0]['enc']

    return vector


def cal_ques_vec():
    inputs = open('./Q_A.txt', 'r', encoding='utf-8')
    outputs = open('./Q_A_vec.txt', 'w', encoding='utf-8')
    for line in inputs:
        vector = WordToVec(line)
        outputs.write(str(vector)+'\n')

    inputs.close()
    outputs.close()


if __name__ == "__main__":
    cal_ques_vec()
