#-- 输入文本text，返回答案为string类型--#

# -*- coding:utf-8 -*-
# -*- created by: mo -*-
import requests
import json

def TL(text):
    api = 'http://www.tuling123.com/openapi/api'
    key = "6b7e6c13d8014e3794ad7ce22da52bb3"
    data = {"key": key, "info": text, "userid": "fool"}
    r = requests.post(api, data=json.dumps(data)).content
    return json.loads(r)['text']

def Dis_Ans(text):
    url = 'http://nlp2ct.cis.um.edu.mo/dev/question/api/ques_ans.php'
    headers = {'Content-Type': 'application/json'}
    data = {'text': text}
    r = requests.post(url, headers=headers, data=json.dumps(data))
    return json.loads(r.content)

