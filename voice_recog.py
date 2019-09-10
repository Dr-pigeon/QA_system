import argparse
import time
import uuid
import base64
import requests
import json


def get_token():
    ApiKey = 'tTenGANmzK2yjoEtbHOBDsbQ'
    SecretKey = 'ycsKcXPEG5KTUQSxhaHuMppOGeNWhers'
    url = 'https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id={}&client_secret={}'.format(
        ApiKey, SecretKey)
    r = requests.get(url, verify=False)
    token = json.loads(r.text).get("access_token")
    return token


def recognize(sig, token):
    url = "http://vop.baidu.com/server_api"
    speech = base64.b64encode(sig).decode("utf-8")
    speech_length = len(sig)
    mac_address = uuid.UUID(int=uuid.getnode()).hex[-12:]
    data = {
        "format": "wav",
        "token": token,
        "rate": 16000,
        "speech": speech,
        "len": speech_length,
        "cuid": mac_address,
        "channel": 1,
        "dev_pid": 1537,
    }
    data_length = len(json.dumps(data).encode("utf-8"))
    headers = {"Content-Type": "application/json",
               "Content-Length": str(data_length)}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    if json.loads(r.content)['err_msg'] == 'success.':
        return str(str(json.loads(r.content)['result']).replace('u\'', '\'').decode("unicode-escape"))
    else:
        return ''