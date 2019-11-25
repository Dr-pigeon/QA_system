# -- 输入文本text，返回答案为string类型--#

# -*- coding:utf-8 -*-
# -*- created by: mo -*-
import requests
import json
import time
from urllib import parse
import hashlib
import http.client
from datetime import timedelta, datetime
import math
import dateutil.parser
import random
import numpy as np
import jieba
import matplotlib.pyplot as plt
import re
from sklearn.preprocessing import PolynomialFeatures
import datetime
from search_summary import search_enginee
from langconv import *
import jieba.posseg as psg
import sys
sys.path.append('./date_extract')
from date_extract.TimeNormalizer import *


jieba.initialize()
r = 1
jieba.add_word('E12', freq=None, tag='ns')
jieba.add_word('E1-E2', freq=None, tag='ns')
jieba.add_word('E32', freq=None, tag='ns')
jieba.add_word('N6', freq=None, tag='ns')
jieba.add_word('N23', freq=None, tag='ns')
jieba.add_word('E21', freq=None, tag='ns')
jieba.add_word('N24', freq=None, tag='ns')
jieba.add_word('N21', freq=None, tag='ns')
jieba.add_word('E11', freq=None, tag='ns')
jieba.add_word('N1-N2', freq=None, tag='ns')
f1 = open('./ele_text.txt', 'r', encoding='utf-8')
f2 = open('./ele_vec.txt', 'r', encoding='utf-8')
ele_text = [i.replace('\n', '') for i in f1]
ele_vec = [i for i in f2]
f2.close()
f1.close()

# 百度翻译API
appid = '20190612000306940'  # 你的appid
secretKey = 'nQ5ZYndkvs9t6N3CIte8'  # 你的密钥

f1 = open('./Q_A_vec.txt', 'r', encoding='utf-8-sig')
f2 = open('./Q_A_ans.txt', 'r', encoding='utf-8')
f3 = open('./Q_A.txt', 'r', encoding='utf-8')
ques = [i for i in f3]
vec = [i for i in f1]
ans = [i for i in f2]
data = []
length = len(vec)
for i in range(length):
    data.append([vec[i], ans[i], ques[i]])
f1.close()
f2.close()
f3.close()

tn = TimeNormalizer()

def WordToVec(text):
    url = 'http://10.119.186.27:12031/encodeSent'
    headers = {'Content-Type': 'application/json'}
    form_data = {"text": text, "lang": "zh-CN"}
    response = requests.post(url, headers=headers, data=json.dumps(form_data))
    decode_text = json.loads(response.content)
    vector = decode_text['result'][0]['enc']

    return vector


def translate_BD(text):
    httpClient = None
    q = text
    myurl = '/api/trans/vip/translate'
    fromLang = 'en'
    toLang = 'zh'
    salt = random.randint(32768, 65536)
    sign = appid + q + str(salt) + secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode(encoding='utf-8'))
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        response = httpClient.getresponse()
        form_data = response.read().decode('utf-8')
        text = eval(form_data)
        zh_text = text['trans_result'][0]['dst']
        return zh_text
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()


def record(text, ans, ques, src):
    f = open('./history.txt', 'a', encoding='utf-8')  # 记录问题，方便更新
    f.write(str(
        [str(time.asctime(time.localtime(time.time()))), str(text + ' ' + ques + ' ' + ans + ' ' + str(src))]) + '\n')
    f.close()


def cosine_similarity(vector1, vector2):
    dot_product = 0.0
    normA = 0.0
    normB = 0.0
    for a, b in zip(vector1, vector2):
        dot_product += a * b
        normA += a ** 2
        normB += b ** 2
    if normA == 0.0 or normB == 0.0:
        return 0
    else:
        return round(dot_product / ((normA ** 0.5) * (normB ** 0.5)) * 100, 2) / 100


def course_search(course_code, sentence):
    url = 'https://api.data.um.edu.mo/service/academic/course_catalog/v1.0.0/all?course_code=' + str(course_code)
    headers = {'Authorization': 'Bearer 5943d8ed-920d-3bf0-b01a-628f1e9294f1'}
    r = requests.get(url, headers=headers)
    if eval(r.text[:-1])['_embedded'] == []:
        return '你是不是搞错啦，澳大没有这门课呀~'
    form_data = eval(r.text[:-1])['_embedded'][0]

    title_ques = [course_code + '这门课是什么', course_code + '的title是啥', course_code + '的课名是什么']
    oldcode_ques = [course_code + '旧的代码是什么', course_code + '以前的代码是啥']
    content_ques = [course_code + '这门课是学啥的', course_code + '这门课教什么', course_code + '是学什么的', course_code + '讲什么内容',
                    course_code + '内容是啥']

    results = []
    all_ques = title_ques + oldcode_ques + content_ques
    for i in all_ques:
        results.append(cosine_similarity(WordToVec(i), WordToVec(sentence)))

    if all_ques[results.index(max(results))] in title_ques:
        return form_data['courseTitle']
    elif all_ques[results.index(max(results))] in oldcode_ques:
        try:
            return form_data['oldCourseCode']
        except KeyError:
            return '这门课没有老代码呀，应该是新开的吧。'
    elif all_ques[results.index(max(results))] in content_ques:
        try:
            ans = translate_BD(form_data['courseDescription'])
            return ans
        except KeyError:
            return '抱歉呀，我暂时没有这门课的介绍。'


def UM_news(date_from, date_to):
    url = 'https://api.data.um.edu.mo/service/media/news/v1.0.0/all?date_from=' + date_from + '&date_to=' + date_to
    headers = {"Authorization": "Bearer 5943d8ed-920d-3bf0-b01a-628f1e9294f1"}
    r = requests.get(url, headers=headers)
    # 处理数据
    text = eval(r.text)
    count = 0
    ans = str('澳门大学最新新闻：\n')
    if text['_embedded'] == []:
        return ('澳门大学昨日暂无新闻。')
    for news in text['_embedded'][0]['details']:
        count += 1
        ans = ans + str(str(count) + '. ' + news['title'] + '\n')
    return ans


def UM_bus():
    url = 'https://api.data.um.edu.mo/service/facilities/shuttle_bus_arrival_time/v1.0.0/all'
    headers = {'Authorization': "Bearer 5943d8ed-920d-3bf0-b01a-628f1e9294f1"}
    r = requests.get(url, headers=headers)
    data = eval(r.text)['_embedded'][0]
    bus_dict = {'time': data['datetime'][11:19], 'station': data['station']}
    # start_time = dateutil.parser.parse(data['datetime'][:19].replace('T', '/'))
    # end_time = dateutil.parser.parse(datetime.now().isoformat()[:19].replace('T', '/'))
    # mins = math.ceil((end_time - start_time).seconds / 60)
    template = ['环校巴士在' + bus_dict['time'] + '经停' + bus_dict['station'] + '车站。',
                '环校巴士上一站刚过' + bus_dict['station'] + '呀！']
    text = random.sample(template, 1)
    return str(text[0])


def Dis_Ans(text):
    # inputs = open('./Q_A_vec.txt', 'r', encoding='utf-8-sig')
    global r
    if r == 1:
        text = Converter('zh-hans').convert(text)
        # print(text)
        results = []
        vec = WordToVec(text)

        seg_list = jieba.cut(text)
        seg_text = "，".join(seg_list)
        pattern = re.compile('[0-9A-Za-z]+')
        if pattern.findall(seg_text) != [] and re.match('[A-Z]{4}[0-9]{3,4}|[a-z]{4}[0-9]{3,4}',
                                                        pattern.findall(seg_text)[0]):
            ans = course_search(pattern.findall(seg_text)[0], text)
            if ans != []:
                return ans

        for i in range(len(ele_text)):
            results.append(cosine_similarity(vec, eval(ele_vec[i])))
        if max(results) >= 0.8:
            locations = []
            text1 = text
            for k, v in psg.cut(text):
                if v == 'ns':
                    locations.append(k)
                    text1 = text1.replace(k, '')
            date_extect = tn.parse(text1)
            print(date_extect)
            if eval(ele_text[results.index(max(results))])[1] == 1:
                meter = None
                if date_extect['type'] == 'timestamp':
                    date_to = date_extect['timestamp']
                    date_from = None
                    date_to = date_to.replace(' ', 'T')
                elif date_extect['type'] == 'timespan':
                    date_from = date_extect['timespan'][0]
                    date_to = date_extect['timespan'][1]
                    date_to = date_to.replace(' ', 'T')
                    date_from = date_from.replace(' ', 'T')
                else:
                    return str({'text': '请输入正确的时间呀！', 'type': 'text'})
                return str({'ques': 1, 'type': 'ele', 'date1': date_from, 'date2': date_to, 'meters': meter})
            elif eval(ele_text[results.index(max(results))])[1] == 2:
                meter = None
                if len(locations) >= 2 and date_extect['type'] == 'timestamp':
                    date1 = date_extect[0][:10]
                    date2 = None
                elif len(locations) == 1 and date_extect['type'] == 'timespan':
                    date1 = date_extect['timespan'][0][:10]
                    date2 = date_extect['timespan'][1][:10]
                else:
                    return str({'text': '请输入正确的时间呀！', 'type': 'text'})
                return str({'ques': 2, 'type': 'ele', 'date1': date1, 'date2': date2, 'locations': locations, 'meters': meter})
            elif eval(ele_text[results.index(max(results))])[1] == 3:
                meter = None
                if date_extect['type'] == 'timestamp':
                    date = date_extect['timestamp'][:10]
                    return str({'location': locations, 'date': date, 'meter': None, 'time1': None, 'time2': None,
                            'type': 'ele', 'ques': 3, 'meters': meter})
                elif date_extect['type'] == 'timespan':
                    date = date_extect['span'][0][:10]
                    time1 = date_extect['span'][0][11:]
                    time2 = date_extect['span'][1][11:]
                    return str({'location': locations, 'date': date, 'meter': None, 'time1': time1, 'time2': time2,
                            'type': 'ele', 'ques': 3, 'meters': meter})
            elif eval(ele_text[results.index(max(results))])[1] == 4:
                meter = None
                if date_extect['type'] == 'timestamp':
                    date1 = None
                    date2 = date_extect['timestamp'][:10]
                    time1 = date_extect['timestamp'][11:]
                    time2 = ((datetime.datetime.strptime(date_extect['timestamp'],'%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                        hours=1)).strftime('%Y-%m-%d %H:%M:%S'))[11:19]
                elif ldate_extect['type'] == 'timespan':
                    date1 = date_extect['timespan'][0][:10]
                    date2 = date_extect['timespan'][1][:10]
                    time1 = date_extect['timespan'][0][11:]
                    time2 = date_extect['timespan'][1][11:]
                else:
                    return str({'text': '我暂时无法做出这个预测额。。。', 'type': 'text'})
                return str({'ques': 4, 'type': 'ele', 'time1': time1, 'time2': time2, 'date2': date2,
                                'locations': locations, 'date1': date1, 'meters': meter})
            elif eval(ele_text[results.index(max(results))])[1] == 5:
                # 调用UM NEWS API
                yesterday = datetime.datetime.today() + timedelta(-1)
                yesterday_format = yesterday.strftime('%Y-%m-%d')
                date_from = str(yesterday_format + 'T00:00:00')
                date_to = str(yesterday_format + 'T23:59:59')
                return str({'text':UM_news(date_from, date_to), 'type':'text'})
            elif eval(ele_text[results.index(max(results))])[1] == 6:
                ans = UM_bus()
                return str({'text':ans, 'type': 'text'})

        results = []
        for i in range(length):
            results.append(cosine_similarity(vec, eval(data[i][0][:-1])))

        if max(results) >= 0.8:
            # ans = open('./Q_A_ans.txt', 'r', encoding='utf-8')
            record(text, data[results.index(max(results))][1], data[results.index(max(results))][2], max(results))
            return data[results.index(max(results))][1]

        try:
            ans = search_enginee(text)
            if ans != None:
                ans = re.split('(。|！|\!|\.|？|\?)', ans)[0] + '。'
                record(text, 'None', ans, 1)
                return str({'text':ans, 'type': 'text'})
            ans = TL(text)
            record(text, 'None', ans, 0)
            return str({'text':ans, 'type': 'text'})
        except BaseException:
            ans = TL(text)
            record(text, 'None', ans, 0)
            return str({'text':ans, 'type': 'text'})

def TL(text):
    api = 'http://www.tuling123.com/openapi/api'
    key = "6b7e6c13d8014e3794ad7ce22da52bb3"
    data = {"key": key, "info": text, "userid": "fool"}
    r = requests.post(api, data=json.dumps(data)).content
    return json.loads(r.decode('utf-8'))['text']


if __name__ == '__main__':
    print(Dis_Ans('我想知道明晚8点E11的用电量'))

