# -- 输入文本text，返回答案为string类型--#

# -*- coding:utf-8 -*-
# -*- created by: mo -*-
import requests
import json
import time
from urllib import parse
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, LinearRegression
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
from date_extract import time_extract
import jieba.posseg as psg

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
f4 = open('./api_vec.txt', 'r', encoding='utf-8')
ques = [i for i in f3]
vec = [i for i in f1]
ans = [i for i in f2]
data = []
length = len(vec)
for i in range(length):
    data.append([vec[i], ans[i], ques[i]])
api_vec = [i for i in f4]
f1.close()
f2.close()
f3.close()
f4.close()

general_eles = {'E1-E2': {}, 'E12': {}, 'E32': {}, 'N6': {}, 'N23': {}, 'E21': {}, 'N24': {}, 'N21': {},
                'E11': {}, 'N1-N2': {}}
lim_eles = {'E1-E2': {}, 'E12': {}, 'E32': {}, 'N6': {}, 'N23': {}, 'E21': {}, 'N24': {}, 'N21': {},
            'E11': {}, 'N1-N2': {}}


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
    print(text)
    if text['_embedded'] == []:
        return ('澳门大学暂无最新新闻。')
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
            # print(results)
        if max(results) >= 0.8:
            e = electricity()
            locations = []
            date_extect = time_extract(text)
            if eval(ele_text[results.index(max(results))])[1] == 1:
                if len(date_extect) == 1:
                    date_to = date_extect[0]
                    date_from = None
                    date_to = date_to.replace(' ', 'T')
                elif len(date_extect) == 2:
                    date_from = date_extect[0]
                    date_to = date_extect[1]
                    date_to = date_to.replace(' ', 'T')
                    date_from = date_from.replace(' ', 'T')
                for k, v in psg.cut(text):
                    if v == 'ns':
                        locations.append(k)
                ans = e.check_ele(locations[0], date_from, date_to, None)
                return str({'text': ans, 'type': 'text'})
            elif eval(ele_text[results.index(max(results))])[1] == 2:
                for k, v in psg.cut(text):
                    if v == 'ns':
                        locations.append(k)
                if len(locations) >= 2:
                    date1 = date_extect[0][:10]
                    date2 = None
                elif len(locations) == 1:
                    date1 = date_extect[0][:10]
                    date2 = date_extect[1][:10]
                ans = e.compare_ele(locations, date1, date2, None, None)
                return str({'text': ans, 'type': 'text'})
            elif eval(ele_text[results.index(max(results))])[1] == 3:
                for k, v in psg.cut(text):
                    if v == 'ns':
                        locations.append(k)
                if len(date_extect) == 1:
                    date = date_extect[0][:10]
                    return str({'location': locations[0], 'date': date, 'meter': None, 'time1': None, 'time2': None,
                            'type': 'img'})
                elif len(date_extect) >= 2:
                    date = date_extect[0][:10]
                    time1 = date_extect[0][11:]
                    time2 = date_extect[1][11:]
                    return str({'location': locations[0], 'date': date, 'meter': None, 'time1': time1, 'time2': time2,
                            'type': 'img'})
            elif eval(ele_text[results.index(max(results))])[1] == 4:
                for k, v in psg.cut(text):
                    if v == 'ns':
                        locations.append(k)
                if len(date_extect) == 1:
                    date2 = date_extect[0][:10]
                    time1 = date_extect[0][11:19]
                    time2 = ((datetime.datetime.strptime(date_extect[0],'%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                        hours=1)).strftime('%Y-%m-%d %H:%M:%S'))[11:19]
                    ans = e.prediction(locations[0], None, date2, time1, time2)
                    return str({'text': ans, 'type': 'text'})
                elif len(date_extect) >= 2 and date_extect[0][11:19] == date_extect[1][11:19]:
                    date1 = date_extect[0][:10]
                    date2 = date_extect[1][:10]
                    ans = e.prediction(locations[0], date1, date2, None, None)
                    return str({'text': ans, 'type': 'text'})
                elif len(date_extect) >= 2 and date_extect[0][11:19] != date_extect[1][11:19]:
                    date2 = date_extect[0][:10]
                    time1 = date_extect[0][11:19]
                    time2 = date_extect[1][11:19]
                    ans = e.prediction(locations[0], None, date2, time1, time2)
                    return str({'text':ans, 'type':'text'})
                else:
                    return str({'text':'Umor暂时无法做出这个预测噢~', 'type':'text'})

        results = []
        for i in range(len(api_vec)):
            results.append(cosine_similarity(vec, eval(api_vec[i][:-1])))
        if max(results) >= 0.8:
            if results.index(max(results)) == 0 or results.index(max(results)) == 1:
                # 调用UM NEWS API
                yesterday = datetime.today() + timedelta(-1)
                yesterday_format = yesterday.strftime('%Y-%m-%d')
                date_from = str(yesterday_format + 'T00:00:00')
                date_to = str(yesterday_format + 'T23:59:59')
                return UM_news(date_from, date_to)
            elif results.index(max(results)) == 2 or results.index(max(results)) == 3:
                ans = UM_bus()
                return ans

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
                return ans
            ans = TL(text)
            record(text, 'None', ans, 0)
            return ans
        except BaseException:
            ans = TL(text)
            record(text, 'None', ans, 0)
            return ans


class electricity():
    def __init__(self):
        self.url = 'https://api.data.um.edu.mo/service/facilities/power_consumption/v1.0.0/all'
        self.headers = {"Authorization": "Bearer 5943d8ed-920d-3bf0-b01a-628f1e9294f1"}

    def check_ele(self, location=None, date_from=None, date_to=None, meter=None):
        try:
            if location is not None and date_from is not None and date_to is not None and meter is not None:
                # next_time = (datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S')+ datetime.timedelta(minutes=15)).strftime('%Y-%m-%d %H:%M')
                # next_time = next_time.replace(' ','T')
                url1 = self.url + '?zone_code=' + location + '&meter_code=' + meter + '&date_to=' + date_from
                response = requests.get(url1, headers=self.headers)
                r = response.json()['_embedded']
                start = r[0]['readings']['kwh']
                url1 = self.url + '?zone_code=' + location + '&meter_code=' + meter + '&date_to=' + date_to
                response = requests.get(url1, headers=self.headers)
                r = response.json()['_embedded']
                end = r[0]['readings']['kwh']
                result = end - start
                return str(round(result, 2)) + ' kwh'
            elif location is not None and date_to is not None and date_from is not None:
                url1 = self.url + '?zone_code=' + location + '&date_to=' + date_from
                response = requests.get(url1, headers=self.headers)
                r = response.json()['_embedded']
                date_from = date_from + '+08:00'
                start = 0
                for i in r:
                    if i['recordDatetime'] == date_from:
                        start += i['readings']['kwh']
                url1 = self.url + '?zone_code=' + location + '&date_to=' + date_to
                response = requests.get(url1, headers=self.headers)
                r = response.json()['_embedded']
                date_to = date_to + '+08:00'
                end = 0
                for i in r:
                    if i['recordDatetime'] == date_to:
                        end += i['readings']['kwh']
                result = end - start
                return str(round(result, 2)) + ' kwh'
            elif location is not None and date_to is not None and meter is not None:
                date_from = date_to[:10] + 'T00:00:00'
                url1 = self.url + '?zone_code=' + location + '&meter_code=' + meter + '&date_to=' + date_from
                response = requests.get(url1, headers=self.headers)
                r = response.json()['_embedded']
                start = r[0]['readings']['kwh']
                url1 = self.url + '?zone_code=' + location + '&meter_code=' + meter + '&date_to=' + date_to
                response = requests.get(url1, headers=self.headers)
                r = response.json()['_embedded']
                end = r[0]['readings']['kwh']
                result = end - start
                return str(round(result, 2)) + ' kwh'
            elif location is not None and date_to is not None:
                date_from = date_to[:10] + 'T00:00:00'
                url1 = self.url + '?zone_code=' + location + '&date_to=' + date_from
                response = requests.get(url1, headers=self.headers)
                r = response.json()['_embedded']
                date_from = date_from + '+08:00'
                start = 0
                for i in r:
                    if i['recordDatetime'] == date_from:
                        start += i['readings']['kwh']
                if date_to[:10] + 'T23:45:00' <= datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'):
                    date_to = date_to[:10] + 'T23:45:00'
                else:
                    date_to = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
                url1 = self.url + '?zone_code=' + location + '&date_to=' + date_to
                response = requests.get(url1, headers=self.headers)
                r = response.json()['_embedded']
                date_to = date_to + '+08:00'
                end = 0
                for i in r:
                    if i['recordDatetime'] == date_to:
                        end += i['readings']['kwh']
                result = end - start
                return str(round(result, 2)) + ' kwh'
            elif date_to is not None:
                zones = ['E1-E2', 'E12', 'E32', 'N6', 'N23', 'E21', 'N24', 'N21', 'E11', 'N1-N2']
                end = 0
                start = 0
                for zone in zones:
                    date_to = date_to[:19]
                    url1 = self.url + '?zone_code=' + zone + '&date_to=' + date_to
                    response = requests.get(url1, headers=self.headers)
                    r = response.json()['_embedded']
                    date_to = date_to + '+08:00'
                    for i in r:
                        if i['recordDatetime'] == date_to:
                            end += i['readings']['kwh']
                    date_from = date_to[:10] + 'T00:00:00'
                    url1 = self.url + '?zone_code=' + zone + '&date_to=' + date_from
                    response = requests.get(url1, headers=self.headers)
                    r = response.json()['_embedded']
                    date_from = date_from + '+08:00'
                    for i in r:
                        if i['recordDatetime'] == date_from:
                            start += i['readings']['kwh']
                result = end - start
                return str(round(result, 2)) + ' kwh'
            else:
                return '抱歉，我暂时没有这方面数据噢，我会尽快学习~'
        except KeyError:
            return '抱歉，我暂时没有这方面数据噢，我会尽快学习~'

    def compare_ele(self, locations, date1=None, date2=None, time1=None, time2=None):
        try:
            if len(locations) > 1 and date1 is not None and date2 is not None:
                return '我只能比较多个地点在统一时间段的电力使用噢~'
            elif len(locations) == 1 and date1 is not None and date2 is not None:
                url1 = self.url + '?zone_code=' + locations[0] + '&date_to=' + date1 + 'T00:00:00'
                r = requests.get(url1, headers=self.headers)
                r = r.json()['_embedded']
                start = 0
                for i in r:
                    if i['recordDatetime'] == date1 + 'T00:00:00+08:00':
                        start += i['readings']['kwh']
                end = 0
                if date1 + 'T23:45:00' <= datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'):
                    url1 = self.url + '?zone_code=' + locations[0] + '&date_to=' + date1 + 'T23:45:00'
                else:
                    url1 = self.url + '?zone_code=' + locations[0] + '&date_to=' + datetime.datetime.now().strftime(
                        '%Y-%m-%dT%H:%M:%S')
                r = requests.get(url1, headers=self.headers)
                r = r.json()['_embedded']
                date_to = r[0]['recordDatetime']
                for i in r:
                    if i['recordDatetime'] == date_to:
                        end += i['readings']['kwh']
                result1 = end - start
                url1 = self.url + '?zone_code=' + locations[0] + '&date_to=' + date2 + 'T00:00:00'
                r = requests.get(url1, headers=self.headers)
                r = r.json()['_embedded']
                start = 0
                for i in r:
                    if i['recordDatetime'] == date2 + 'T00:00:00+08:00':
                        start += i['readings']['kwh']
                end = 0
                if date2 + 'T23:45:00' <= datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'):
                    url1 = self.url + '?zone_code=' + locations[0] + '&date_to=' + date2 + 'T23:45:00'
                else:
                    url1 = self.url + '?zone_code=' + locations[0] + '&date_to=' + datetime.datetime.now().strftime(
                        '%Y-%m-%dT%H:%M:%S')
                r = requests.get(url1, headers=self.headers)
                r = r.json()['_embedded']
                date_to = r[0]['recordDatetime']
                for i in r:
                    if i['recordDatetime'] == date_to:
                        end += i['readings']['kwh']
                result2 = end - start
                if result1 >= result2:
                    return locations[0] + '在' + date1[5:].replace('-', '月') + '日用电多，足足用了' + str(
                        round(result1, 2)) + ' kwh'
                else:
                    return locations[0] + '在' + date2[5:].replace('-', '月') + '日用电多，足足用了' + str(
                        round(result2, 2)) + ' kwh'
            elif len(locations) > 1 and date1 is not None:
                result = []
                for zone in locations:
                    url1 = self.url + '?zone_code=' + zone + '&date_to=' + date1 + 'T00:00:00'
                    r = requests.get(url1, headers=self.headers)
                    r = r.json()['_embedded']
                    start = 0
                    for i in r:
                        if i['recordDatetime'] == date1 + 'T00:00:00+08:00':
                            start += i['readings']['kwh']
                    end = 0
                    if date1 + 'T23:45:00' <= datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'):
                        url1 = self.url + '?zone_code=' + zone + '&date_to=' + date1 + 'T23:45:00'
                    else:
                        url1 = self.url + '?zone_code=' + zone + '&date_to=' + datetime.datetime.now().strftime(
                            '%Y-%m-%dT%H:%M:%S')
                    r = requests.get(url1, headers=self.headers)
                    r = r.json()['_embedded']
                    date_to = r[0]['recordDatetime']
                    for i in r:
                        if i['recordDatetime'] == date_to:
                            end += i['readings']['kwh']
                    result.append(round(end - start, 2))
                return locations[result.index(max(result))] + '耗电更多，足足用了' + str(max(result)) + ' kwh。'
        except KeyError:
            return '抱歉啊，Umor暂时无法作出这个比较噢~'

    def prediction(self, location=None, date1=None, date2=None, time1=None, time2=None):
        try:
            if location is not None and date2 is not None and time1 is not None and time2 is not None:
                eles = []
                record = {}
                date_to = (datetime.datetime.strptime(date2 + ' 00:00:00', '%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                    days=-6)).strftime('%Y-%m-%d %H:%M:%S')
                date_from = (datetime.datetime.strptime(date2 + ' 00:00:00', '%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                    days=-7)).strftime('%Y-%m-%d %H:%M:%S')
                while date_to >= datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'):
                    date_to = (datetime.datetime.strptime(date_to, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                        days=-7)).strftime('%Y-%m-%d %H:%M:%S')
                    date_from = (datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                        days=-7)).strftime('%Y-%m-%d %H:%M:%S')
                while date_from <= date_to:
                    ele = 0
                    date_from = date_from.replace(' ', 'T')
                    url1 = self.url + '?zone_code=' + location + '&date_to=' + date_from
                    r = requests.get(url1, headers=self.headers)
                    r = r.json()['_embedded']
                    a = []
                    for i in r:
                        if i['recordDatetime'] == date_from + '+08:00':
                            a.append(i['meterCode'])
                            if i['meterCode'] in record.keys() and i['readings']['kwh'] != 0:
                                ele += i['readings']['kwh']
                                record[i['meterCode']] = i['readings']['kwh']
                            elif i['meterCode'] in record.keys() and record[i['meterCode']] != 0 and i['readings'][
                                'kwh'] == 0:
                                ele += record[i['meterCode']]

                            elif i['meterCode'] not in record.keys() and i['readings']['kwh'] != 0:
                                record[i['meterCode']] = i['readings']['kwh']
                                ele += record[i['meterCode']]
                                eles = [j + i['readings']['kwh'] for j in eles]
                    for i in record.keys():
                        if i not in a:
                            ele += record[i]
                    if ele != 0:
                        eles.append(round(ele, 2))
                    date_from = date_from.replace('T', ' ')
                    date_from = (datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                        hours=1)).strftime('%Y-%m-%d %H:%M:%S')
                y = []
                for i in range(len(eles) - 1):
                    y.append(round(eles[i + 1] - eles[i], 2))
                x = list(range(24))
                x = np.array(x)
                x = x.reshape(-1, 1)
                y = np.array(y)
                y = y.reshape(-1, 1)
                S = StandardScaler()
                S.fit(x)
                x = S.transform(x)
                Log = LogisticRegression(C=10)
                Log.fit(x, y.astype('int'))
                print(time1,time2)
                d = int(time2[:2]) - int(time1[:2])
                prediction = 0
                for i in range(d + 1):
                    x_pred = np.array(int(time1[:2]) + i).reshape(-1, 1)
                    prediction += Log.predict(x_pred)
                return location + '在' + date2[5:7] + '月' + date2[8:] + '日' + str(int(time1[:2])) + '点到' + str(
                    int(time2[:2])) + '点预计用电 ' + str(prediction[0]) + 'kwh。'
            elif location is not None and date2 is not None and date1 is not None:
                date_to = (datetime.datetime.strptime(date2, '%Y-%m-%d') + datetime.timedelta(
                    days=-6)).strftime('%Y-%m-%d')
                while date_to >= datetime.datetime.now().strftime('%Y-%m-%d'):
                    date_to = (datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(
                        days=-7)).strftime('%Y-%m-%d')
                diff_time = datetime.datetime(int(date2[:4]), int(date2[5:7]), int(date2[8:])) - datetime.datetime(
                    int(date_to[:4]), int(date_to[5:7]), int(date_to[8:]))
                diff_time = diff_time.days
                date_from = (datetime.datetime.strptime(date_to, '%Y-%m-%d') + datetime.timedelta(
                    days=-7)).strftime('%Y-%m-%d')
                while (datetime.datetime(int(date_to[:4]), int(date_to[5:7]), int(date_to[8:])) - datetime.datetime(
                        int(date_from[:4]), int(date_from[5:7]), int(date_from[8:]))).days < diff_time:
                    date_from = (datetime.datetime.strptime(date_from, '%Y-%m-%d') + datetime.timedelta(
                        days=-7)).strftime('%Y-%m-%d')
                eles = []
                date_from = date_from + ' 00:00:00'
                date_to = date_to + ' 00:00:00'
                record = {}
                while date_from <= date_to:
                    ele = 0
                    date_from = date_from.replace(' ', 'T')
                    url1 = self.url + '?zone_code=' + location + '&date_to=' + date_from
                    r = requests.get(url1, headers=self.headers)
                    r = r.json()['_embedded']
                    a = []
                    for i in r:
                        if i['recordDatetime'] == date_from + '+08:00':
                            a.append(i['meterCode'])
                            if i['meterCode'] in record.keys() and i['readings']['kwh'] != 0:
                                ele += i['readings']['kwh']
                                record[i['meterCode']] = i['readings']['kwh']
                            elif i['meterCode'] in record.keys() and record[i['meterCode']] != 0 and i['readings'][
                                'kwh'] == 0:
                                ele += record[i['meterCode']]

                            elif i['meterCode'] not in record.keys() and i['readings']['kwh'] != 0:
                                record[i['meterCode']] = i['readings']['kwh']
                                ele += record[i['meterCode']]
                                eles = [j + i['readings']['kwh'] for j in eles]
                    for i in record.keys():
                        if i not in a:
                            ele += record[i]
                    if ele != 0:
                        eles.append(round(ele, 2))
                    date_from = date_from.replace('T', ' ')
                    date_from = (datetime.datetime.strptime(date_from, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(
                        days=1)).strftime('%Y-%m-%d %H:%M:%S')
                y = []
                for i in range(len(eles) - 1):
                    y.append(round(eles[i + 1] - eles[i], 2))
                x = np.array(range(len(y))) + 1
                x = x.reshape(-1, 1)
                y = np.array(y)
                y = y.reshape(-1, 1)
                quadratic_featurizer = PolynomialFeatures(degree=2)
                x = quadratic_featurizer.fit_transform(x)
                model = LinearRegression()
                model.fit(x, y)

                x1 = len(eles) + (
                            datetime.datetime(int(date1[:4]), int(date1[5:7]), int(date1[8:])) - datetime.datetime(
                        int(date_from[:4]), int(date_from[5:7]), int(date_from[8:10]))).days
                x2 = len(eles) + (
                            datetime.datetime(int(date2[:4]), int(date2[5:7]), int(date2[8:])) - datetime.datetime(
                        int(date_from[:4]), int(date_from[5:7]), int(date_from[8:10]))).days
                x_pred = np.array(range(x1, x2 + 1)).reshape(-1, 1)
                x_pred = quadratic_featurizer.transform(x_pred)
                predictions = model.predict(x_pred)
                print(predictions)
                count = 0
                print(date1, date2)
                text = location + '在' + str(int(date1[5:7])) + '月' + str(int(date1[8:])) + '日至' + str(
                    int(date2[5:7])) + '月' + str(int(date2[8:])) + '日的用电预测如下：\n'
                while date1 <= date_to:
                    text += str(int(date1[5:7])) + '月' + str(int(date1[8:])) + '日：' + str(
                        round(predictions[count], 2)) + 'kwh\n'
                    count += 1
                    date1 = (dat etime.datetime.strptime(date1, '%Y-%m-%d') + datetime.timedelta(
                        days=1)).strftime('%Y-%m-%d')
                return text
        except (KeyError,ValueError):
            return '抱歉呀，UMor暂时无法做出这个预测噢~'


def TL(text):
    api = 'http://www.tuling123.com/openapi/api'
    key = "6b7e6c13d8014e3794ad7ce22da52bb3"
    data = {"key": key, "info": text, "userid": "fool"}
    r = requests.post(api, data=json.dumps(data)).content
    return json.loads(r.decode('utf-8'))['text']


if __name__ == '__main__':
    print(Dis_Ans('E12在11月30日下午5点的用电预测'))

