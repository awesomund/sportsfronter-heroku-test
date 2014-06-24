import sys
import urllib
import urllib2
import json


def create_request_data_dict(title, message, recipients):
    data = { "registration_ids" : recipients, "data": {"title": title, "message": message, "event_id" : "44"}}
    return json.dumps(data)

url = 'https://android.googleapis.com/gcm/send'
headers = {
    'Content-Type' : 'application/json',
    'Authorization' : 'key=AIzaSyBJ6uTxUs9QAAgN34AryaVI68uu2hKIdPg' 
}
title= "Hello, good sir.. "
#recipients =  ['APA91bEvVJsKAvcLin3biVHK2hVI-Tby2MEOmBBfqPGglAIhpgJfvKTfm-_3407L-KU5Lg-nySqSpvbs4mcP6uU5J6ytyPbUqKa5pPXmUGTKjgQbuKT0z0tnYBv0wZSzorzJ-1PcH6q5']
#recipients = ['APA91bGWHnYAVrM2Bm3u-LTSEKqiY1QSc869JidX8b0Z9xfKbvalR6w1oxMEFUgNf7LbCQUK4aNMu3ZlDlwPrXoqkbZCnwam59oOczBnjMWyMN5qhUpVNQbH7dhevM9o5l5oVE-eiC2-']
#recipients  = ['APA91bFD6HCC3BfUVHiSSXhK4840nky5y_CXGnOdjksLxc7RAlLE0jGFX-GrrowEla3FeX7YA4E6cN_ACfFiYnq_p-Gld92VxtyCz4uwN3A7gaoOM3IFrQDaDoaRVTQNPgdDCMCnAmHh']
#recipients = ['APA91bHqRZRvv6WbQmshlQL2hrow0r1xB3fMzCn-ViUu5NB8sqRaO5H4Sdkx6XB75Asr6vUqAM_sa4J5CbXuXOrYDOptGLoije2gbFt7-3yRR4YSwHT28IieX89oLykut_BI0CRnNyaltLKkHxYPye8Z1xy921efSQ']
#recipients = ['APA91bHqRZRvv6WbQmshlQL2hrow0r1xB3fMzCn-ViUu5NB8sqRaO5H4Sdkx6XB75Asr6vUqAM_sa4J5CbXuXOrYDOptGLoije2gbFt7-3yRR4YSwHT28IieX89oLykut_BI0CRnNyaltLKkHxYPye8Z1xy921efSQ']
#recipients = ['APA91bHqRZRvv6WbQmshlQL2hrow0r1xB3fMzCn-ViUu5NB8sqRaO5H4Sdkx6XB75Asr6vUqAM_sa4J5CbXuXOrYDOptGLoije2gbFt7-3yRR4YSwHT28IieX89oLykut_BI0CRnNyaltLKkHxYPye8Z1xy921efSQ']
#recipients = ['APA91bFEd705ulZlWbckxrwRAVfottalSEIn4X3-JIMC8KF4lxgXTvfhA-NoXSQlGihHivc03kC88d7NBKAxfLT77mdIEvXNI8lV1WQSEDucADwIWSUlZHBAk4cTIzYAELbkRacM87PM']
#recipients = ['APA91bGXuh7Yv1s9udQZNbjjWqlg89mHVr06Szr_HIdoRY84yZ3BaBRsV25QXjgVCFL7y8_fbvkeigvkLI2jNu4VDkcIIFeuf1F0_VU8xTAMcq4NpAYl_SOUzmiuHS5GZGrhTMdrxseA']
data = create_request_data_dict(title, message, recipients)

# Send request
print url
request = urllib2.Request(url, data, headers)
f = urllib2.urlopen(request)
