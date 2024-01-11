import yaml
import json
from datetime import datetime
from json import JSONEncoder
class MyEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return str(o)
        return JSONEncoder.default(o)

    

cur_yaml = ""
papers = []

while True:
    s = input()
    if s in ['END', '---']:
        papers.append(yaml.safe_load(cur_yaml))
        cur_yaml = ""
    if s == 'END':
        break
    cur_yaml += s +'\n'

print(json.dumps(papers, indent=2, cls=MyEncoder))