# coding: utf-8
import xmltodict

k = "\u6fb3\u9580\u5927\u5b78\u5728\u54ea\ud855\ude83"
k = k.encode('utf-8').decode('unicode_escape')

with open('junk', 'w', encoding='utf-8') as f:
	f.write(k)
