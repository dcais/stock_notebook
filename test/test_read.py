import json

with open('../config.json') as json_file:
    data = json.load(json_file)
    print (data)

p =data
b = p['mysql']
print (b)