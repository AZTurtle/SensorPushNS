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

    valid = 'authorization' in res
    auth_code = res['authorization'] if valid else 0

    return valid
    
def refreshAuthToken():
    global auth_token

    res = requests.post(SP_API_URL + 'oauth/accesstoken', data={
        'authorization': auth_code
    }).json()

    valid = 'accesstoken' in res
    auth_token = res['accesstoken'] if valid else 0

    return valid
    
def get(url_):
    refresh = 0
    url = SP_API_URL + url_

    while refresh < REFRESH_LIMIT:
        res = requests.post(url, headers={
            'accept': 'application/json',
            'Authorization': auth_token
        }, json={}).json()

        if 'type' in res and res['type'] == 'UNAUTHORIZED':
            LOGGER.debug('Unauthorized! Refreshing token.')
            refreshAuthToken()
        else: return res

        refresh += 1
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

        if 'type' in res and res['type'] == 'UNAUTHORIZED':
            LOGGER.debug('Unauthorized! Refreshing token.')
            refreshAuthToken()
        else: 
            LOGGER
            return res

        refresh += 1
    else:
        LOGGER.error(f'Failed to POST: {url}')
