import json
import os
import time

def append_record(record):
    with open('test.json', 'rb+') as f:
        f.seek(-1, os.SEEK_END)
        f.truncate()
    with open('test.json', 'a') as f:
        f.write(',')
        f.write(os.linesep)
        json.dump(record, f)
        f.write(']')

# demonstrate a program writing multiple records

my_dict = {'oil_is': 10, 'oil_set': 20, 'time': 2, 'water': 7}

while True:
    append_record(my_dict)
    time.sleep(1)
    print "blub"