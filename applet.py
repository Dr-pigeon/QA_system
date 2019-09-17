from cos_sim import *
import os
from voice_recog import *


appid = 'wxf57c9db2420b3019' #小程序id
secret = '8f3e23c558c56d442e6109acfcd873bf' #小程序密钥
token = get_token() #百度api


def recog():
    voice_file = request.files['voice']
    if voice_file:
        voice_file.save('./record/record.silk')
        msg = os.system('sudo sh silk-v3-decoder/converter.sh ../record/record.silk wav')
        noise_reduct('./record/record.wav','./record/en_record.wav')
        f = open('./record/en_record.wav','rb')
        result = recognize(signal,token)
        if result != '':
            ans = Dis_Ans(result)
        f.close()
        data = {"text":ans}
        return data
    return {'err_no':10010}


def getuserinfo(code):
    f=open('/home/ubuntu/weixin/userInfo.txt','a',encoding='utf-8')
    f.write(code+'\n')
    f.close()
    url = 'https://api.weixin.qq.com/sns/jscode2session?appid=%s&secret=%s&js_code=%s&grant_type=authorization_code' % (appid, secret, code)
    r = requests.get(url)
    result = r.text
    return result
 
