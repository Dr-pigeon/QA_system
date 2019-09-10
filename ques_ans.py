# -*- coding:utf-8 -*-
# -*- created by: mo -*-
import requests
import json

def ques_ans(text):
	url = 'http://nlp2ct.cis.um.edu.mo/dev/question/api/ques_ans_api.php'
	headers={'Content-Type': 'application/json'}
	data = {'text':text}
	r=requests.post(url,headers=headers,data=json.dumps(data))
	ans = r.content.decode('utf-8')
	return ans[1:]