import requests
import json

url = 'http://123.24.205.250:9696/Api/Common/Login?user={0}&pass={1}'
headers = {'content-type': 'application/json'}

r = requests.post(url.format('dtkien@viegrid.com', 'Abc123-='))
print(json.loads(r.json())["Id"])
