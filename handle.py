from cos_sim import *
from flask import Flask, request, make_response, json
import hashlib
import xmltodict
import time


class Handle(object):
    def GET(self):
        #args = request.args
        args = request.json
#        args = json.parse(str(args))
        signature = args.get('signature')
        timestamp = args.get('timestamp')
        nonce = args.get('nonce')
        echostr = args.get('echostr')
        WECHAT_TOKEN = 'UMer2019'
        temp = [WECHAT_TOKEN, timestamp, nonce]
        temp.sort()
        temp = "".join(temp)
        sig = hashlib.sha1(temp.encode('utf-8')).hexdigest()
        if sig == signature:
            return echostr
        else:
            return 'errno', 403

    def POST(self):
        resp_data = request.data
        resp_dict = xmltodict.parse(resp_data).get('xml')

        if resp_dict.get('MsgType') == 'text':
            print (resp_dict.get('Content'))
            ans = Dis_Ans(resp_dict.get('Content'))
            response = {
                "ToUserName": resp_dict.get('FromUserName'),
                "FromUserName": resp_dict.get('ToUserName'),
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": ans,
            }
        elif resp_dict.get('MsgType') == 'voice':
            ans = Dis_Ans(resp_dict.get('Recognition'))
            response = {
                "ToUserName": resp_dict.get('FromUserName'),
                "FromUserName": resp_dict.get('ToUserName'),
                "CreateTime": int(time.time()),
                "MsgType": "text",
                "Content": ans,
            }
        else:
            pass
        if response:
            response = {"xml": response}
            response = xmltodict.unparse(response)
        else:
            response = ''
        return make_response(response)
