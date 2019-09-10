#-- 输入文本text，返回答案为string类型--#

# -*- coding:utf-8 -*-
# -*- created by: mo -*-
import requests
import json
import time


f1 = open('./Q_A_vec.txt', 'r', encoding='utf-8-sig')
f2 = open('./Q_A_ans.txt', 'r', encoding='utf-8')
f3 = open('./Q_A.txt','r',encoding='utf-8')
ques = [i for i in f3]
vec = [i for i in f1]
ans = [i for i in f2]
data = []
length = len(vec)
for i in range(length):
    data.append([vec[i], ans[i],ques[i]])


def WordToVec(text):
    url = 'http://10.119.186.27:12031/encodeSent'
    headers = {'Content-Type': 'application/json'}
    data = {"text": text, "lang": "zh-CN"}
    response = requests.post(url, headers=headers, data=json.dumps(data))
    decode_text = json.loads(response.content)
    vector = decode_text['result'][0]['enc']

    return vector


def reocord(text,ans,ques,src):
    f = open('./history.txt', 'a', encoding='utf-8') #记录问题，方便更新
    f.write(str([str(time.asctime(time.localtime(time.time()))),str(text+' '+ques+' '+ans+' '+str(src))])+'\n')
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


def Dis_Ans(text):
    #inputs = open('./Q_A_vec.txt', 'r', encoding='utf-8-sig')
    results = []
    vec = WordToVec(text)

    for i in range(length):
        results.append(cosine_similarity(vec, eval(data[i][0][:-1])))

    if max(results) >= 0.8:
        #ans = open('./Q_A_ans.txt', 'r', encoding='utf-8')
        record(text,data[results.index(max(results))][1], data[results.index(max(results))][2], max(results))
        return data[results.index(max(results))][1] 
    else:
        ans = TL(text)
        record(text,'None',ans, 0)
        return TL(text)


def TL(text):
    api = 'http://www.tuling123.com/openapi/api'
    key = "6b7e6c13d8014e3794ad7ce22da52bb3"
    data = {"key": key, "info": text, "userid": "fool"}
    r = requests.post(api, data=json.dumps(data)).content
    return json.loads(r.decode('utf-8'))['text']
