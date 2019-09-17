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
import jieba
import re

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
        print(round(dot_product / ((normA ** 0.5) * (normB ** 0.5)) * 100, 2) / 100)
        return round(dot_product / ((normA ** 0.5) * (normB ** 0.5)) * 100, 2) / 100


def course_search(course_code, sentence):
    url = 'https://api.data.um.edu.mo/service/academic/course_catalog/v1.0.0/all?course_code=' + str(course_code)
    headers = {'Authorization': 'Bearer 5943d8ed-920d-3bf0-b01a-628f1e9294f1'}
    r = requests.get(url, headers=headers)
    form_data = eval(r.text[:-1])['_embedded'][0]
    if form_data == []:
        return '你是不是搞错啦，澳大没有这门课呀~'
    title_ques = [course_code + '这门课是什么', course_code + '的title是啥', course_code + '的课名是什么']
    oldcode_ques = [course_code + '旧的代码是什么', course_code + '以前的代码是啥']
    content_ques = [course_code + '这门课是学啥的', course_code + '这门课教什么', course_code + '是学什么的', course_code+'讲什么内容',course_code+'内容是啥']

    results = []
    all_ques = title_ques+oldcode_ques+content_ques
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
        return ('澳门大学暂无最新新闻。')
    for news in text['_embedded'][0]['details']:
        count += 1
        ans = ans + str(ans + str(count) + '. ' + news['title'] + '\n')
    return ans


def UM_bus():
    url = 'https://api.data.um.edu.mo/service/facilities/shuttle_bus_arrival_time/v1.0.0/all'
    headers = {'Authorization': "Bearer 5943d8ed-920d-3bf0-b01a-628f1e9294f1"}
    r = requests.get(url, headers=headers)
    data = eval(r.text)['_embedded'][0]
    bus_dict = {'time': data['datetime'][11:19], 'station': data['station']}
    start_time = dateutil.parser.parse(data['datetime'][:19].replace('T', '/'))
    end_time = dateutil.parser.parse(datetime.now().isoformat()[:19].replace('T', '/'))
    mins = math.ceil((end_time - start_time).seconds / 60)
    template = ['环校巴士在' + bus_dict['time'] + '经停' + bus_dict['station'] + '车站。',
                '环校巴士上一站刚过' + bus_dict['station'] + '呀！', \
                '校巴在' + str(mins) + '分钟前经停了' + bus_dict['station'] + '啦']
    text = random.sample(template, 1)
    return text


def Dis_Ans(text):
    # inputs = open('./Q_A_vec.txt', 'r', encoding='utf-8-sig')
    results = []
    vec = WordToVec(text)

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
        elif results.index(max(results)) == 4 or results.index(max(results)) == 5:
            seg_list = jieba.cut(text)
            seg_text = ", ".join(seg_list)
            pattern = re.compile('[0-9A-Za-z]+')
            for i in seg_text:
                if pattern.findall(i)[0] == i:
                    ans = course_search(i, text)
                    return ans

    results = []
    for i in range(length):
        results.append(cosine_similarity(vec, eval(data[i][0][:-1])))

    if max(results) >= 0.8:
        # ans = open('./Q_A_ans.txt', 'r', encoding='utf-8')
        record(text, data[results.index(max(results))][1], data[results.index(max(results))][2], max(results))
        return data[results.index(max(results))][1]
    else:
        ans = TL(text)
        record(text, 'None', ans, 0)
        return TL(text)


def TL(text):
    api = 'http://www.tuling123.com/openapi/api'
    key = "6b7e6c13d8014e3794ad7ce22da52bb3"
    data = {"key": key, "info": text, "userid": "fool"}
    r = requests.post(api, data=json.dumps(data)).content
    return json.loads(r.decode('utf-8'))['text']