import requests
import udi_interface

SP_API_URL = 'https://api.sensorpush.com/api/v1/'
auth_code = ''
auth_token = ''

def authorize(email, password):
    global auth_code

    res = requests.post(SP_API_URL + 'oauth/authorize', data={
        'email': email,
        'password': password
    }).json()

    if 'authorization' in res:
        auth_code = res['authorization']
        return True
    else:
        return False
    
def refreshAuthToken():
    global auth_token

    res = requests.post(SP_API_URL + 'oauth/accesstoken', data={
        'authorization': auth_code
    }).json()

    auth_token = res['accesstoken']
    
def get(url):
    return requests.get(SP_API_URL + url, headers={
        'accept': 'application/json',
        'Authorization': auth_token
    })
