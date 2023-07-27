import requests
import udi_interface

SP_API_URL = 'https://api.sensorpush.com/api/v1/'
auth_token = ''

def authorize(email, password):
    global auth_token
    res = requests.post(SP_API_URL + 'oauth/authorize', data={
            'email': email,
            'password': password
        }).json()
    if 'authorization' in res:
        auth_token = res['authorization']
        return True
    else:
        return False
    
def get(url):
    return requests.post(SP_API_URL + url, headers={
        'accept': 'application/json',
        'Authorization': auth_token
    })
