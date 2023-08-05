import requests
import udi_interface

SP_API_URL = 'https://api.sensorpush.com/api/v1/'
access_token = ''
refresh_data = {'grant_type': 'access_token'}

REFRESH_LIMIT = 10

LOGGER = udi_interface.LOGGER

def refreshToken():
    global refresh_data
    global access_token

    refresh = 0
    code = 0

    LOGGER.debug('--REFRESHING TOKEN--')

    while refresh < REFRESH_LIMIT:
        res = requests.post(SP_API_URL + 'oauth/token', headers={
            'accept': 'application/json',
            'Authorization': access_token
        }, data=refresh_data).json()
        
        LOGGER.debug(res)
        LOGGER.debug(refresh_data)

        if 'statusCode' in res:
            code = res['statusCode']

            refresh += 1
            continue
        
        access_token = res['access_token']
        refresh_data['refresh_token'] = res['refresh_token']

    return code
    
def get(url_):
    refresh = 0
    url = SP_API_URL + url_

    while refresh < REFRESH_LIMIT:
        res = requests.post(url, headers={
            'accept': 'application/json',
            'Authorization': access_token
        }, json={}).json()

        if 'statusCode' in res:
            code = res['statusCode']
            if code == 400:
                LOGGER.debug('Failed to GET! Refreshing token...')
                refreshToken()
                refresh += 1
        else:
            return res
    else:
        LOGGER.error(f'Failed to GET: {url}')

def post(url_, data):
    refresh = 0
    url = SP_API_URL + url_

    while refresh < REFRESH_LIMIT:
        res = requests.post(url, headers={
            'accept': 'application/json',
            'Authorization': access_token
        }, json=data).json()

        if 'statusCode' in res:
            code = res['statusCode']
            if code == 400:
                LOGGER.debug('Failed to POST! Refreshing token...')
                refreshToken()
                refresh += 1
        else:
            return res
    else:
        LOGGER.error(f'Failed to POST: {url}')
