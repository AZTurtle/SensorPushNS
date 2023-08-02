import requests
import udi_interface

SP_API_URL = 'https://api.sensorpush.com/api/v1/'
auth_code = ''
auth_token = ''

REFRESH_LIMIT = 10

LOGGER = udi_interface.LOGGER

def authorize(email, password):
    global auth_code

    res = requests.post(SP_API_URL + 'oauth/authorize', data={
        'email': email,
        'password': password
    }).json()

    if 'authorization' not in res:
        return res['statusCode']
    
    auth_code = res['authorization']
    return 0
    
def refreshAuthToken():
    global auth_token

    res = requests.post(SP_API_URL + 'oauth/accesstoken', data={
        'authorization': auth_code
    }).json()

    if 'accesstoken' not in res:
        return res['statusCode']
    
    auth_token = res['accesstoken']
    return 0
    
def get(url_):
    refresh = 0
    url = SP_API_URL + url_

    while refresh < REFRESH_LIMIT:
        res = requests.post(url, headers={
            'accept': 'application/json',
            'Authorization': auth_token
        }, json={}).json()

        if 'statusCode' in res:
            code = res['statusCode']
            if code == 400:
                LOGGER.debug('Failed to GET! Refreshing token...')
                refreshAuthToken()
                refresh += 1
                continue
        
        return res
    else:
        LOGGER.error(f'Failed to GET: {url}')

def post(url_, data):
    refresh = 0
    url = SP_API_URL + url_

    while refresh < REFRESH_LIMIT:
        res = requests.post(url, headers={
            'accept': 'application/json',
            'Authorization': auth_token
        }, json=data).json()

        if 'statusCode' in res:
            code = res['statusCode']
            if code == 400:
                LOGGER.debug('Failed to POST! Refreshing token...')
                refreshAuthToken()
                refresh += 1
                continue
        
        return res
    else:
        LOGGER.error(f'Failed to POST: {url}')
