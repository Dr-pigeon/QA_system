# -*- coding:utf-8 -*-
# -*- created by: mo -*-
import json
import requests
from flask import Flask, request, make_response
import time
from cos_sim import *
from handle import Handle
import xmltodict
import os
from ques_ans import ques_ans 

handle = Handle()  #微信公众号

app = Flask(__name__)

#词向量
@app.route('/wordtovec',methods=['POST'])
def wordtovec():
    resp_data = request.data
    resp_data = resp_data.decode('utf-8')
    text = resp_data['text']
    text_vec = WordToVec(text)
    return text_vec


#微信公众号问答
@app.route('/qa_api', methods=['GET', 'POST'])
def qa_api():
    result = ''
    if request.method == 'POST':    
        print ('Post request')
        resp_data = request.data
        resp_data = resp_data.decode('utf-8')
        xml_parse = resp_data.replace('\\/', '/').replace('\\n', '')[1:-1]
#        print (xml_parse)

        resp_dict = xmltodict.parse(xml_parse).get('xml')

#        text = resp_dict.get('Content', 'UNKNOWN TEXT')
#        ans = Dis_Ans(text)
#        result = json.dumps(ans)

        if resp_dict.get('MsgType') == 'text':
#            print (resp_dict.get('Content'))
            content = resp_dict.get('Content')
#            content = "b'" + content + "'"
#            content = eval(content).decode('utf-8') 
            content = content.encode('utf-8').decode('unicode_escape')
            print (content)
            
            ans = Dis_Ans(content)
            response = {
                "ToUserName": resp_dict.get('FromUserName'),
                "FromUserName": resp_dict.get('ToUserName'),
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": ans,
            }
        elif resp_dict.get('MsgType') == 'voice':
            content = resp_dict.get('Content')
            content = content.encode('utf-8').decode('unicode_escape')
            ans = Dis_Ans(content)
            
            response = {
                "ToUserName": resp_dict.get('FromUserName'),
                "FromUserName": resp_dict.get('ToUserName'),
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": ans,
            }
        else:
            pass

        response = {"xml": response}
        response = xmltodict.unparse(response)
        return make_response(response)

        print (result)
            
    return result

#微信公众号认证
@app.route('/wx', methods=['GET', 'POST'])
def wx():
    handle = Handle()
    result = handle.GET()


#小程序
@app.route('/applet', methods=['POST'])
def applet():
    if request.method == 'POST':
        data = request.data
        data = eval(data.decode('utf-8'))
        if data['action'] == 'login':
            return str(time.asctime(time.localtime(time.time())))
        elif data['action'] == 'text':
            text = data['text']
            ans = ques_ans(text)
            return {'text':ans[0:-1]}
        elif data['action'] == 'voice':
            pass

if __name__ == '__main__':
    #app.config['SERVER_NAME'] = 'www.kenchan.net.cn'
    app.run(host='0.0.0.0',port=13011,debug=True,ssl_context=('1_www.kenchan.net.cn_bundle.crt','2_www.kenchan.net.cn.key'))





#        s = '<xml><ToUserName><![CDATA[gh_df23ae4e6849]]></ToUserName><FromUserName><![CDATA[oXgg5wRikHIYuAiZAHokqqFhZSoE]]></FromUserName><CreateTime>1565259951</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[\\u6fb3\\u9580\\u5927\\u5b78\\u5728\\u54ea\\ud855\\ude83]]></Content><MsgId>22409136513325645</MsgId></xml>'
