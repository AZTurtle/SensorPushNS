"""
SensorPush Node Server
Copyright (C) 2023 James Bennett

MIT License
"""

import requests
import udi_interface

SP_API_URL = 'https://api.sensorpush.com/api/v1/'
access_token = ''
refresh_data = {'grant_type': 'refresh_token'}

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

        if 'statusCode' in res:
            code = res['statusCode']

            refresh += 1
            continue
        
        access_token = res['access_token']
        refresh_data['refresh_token'] = res['refresh_token']

        break

    return code
    
def get(url_):
    refresh = 0
    url = SP_API_URL + url_

    while refresh < REFRESH_LIMIT:
        try:
            res = requests.post(url, headers={
                'accept': 'application/json',
                'Authorization': access_token
            }, json={}).json()

            if 'statusCode' in res:
                code = res['statusCode']
                if code == 400:
                    LOGGER.debug('Failed to GET!')
                    refresh += 1
            else:
                return res
        except Exception as e:
            LOGGER.error(f'Error when GETing {e}')
    else:
        LOGGER.error(f'Timeout GET: {url}')

def post(url_, data):
    refresh = 0
    url = SP_API_URL + url_

    while refresh < REFRESH_LIMIT:
        try:
            res = requests.post(url, headers={
                'accept': 'application/json',
                'Authorization': access_token
            }, json=data).json()

            if 'statusCode' in res:
                code = res['statusCode']
                if code == 400:
                    LOGGER.debug('Failed to POST!')
                    refresh += 1
            else:
                return res
        except Exception as e:
            LOGGER.error(f'Error when POSTing {e}')
    else:
        LOGGER.error(f'Timeout POST: {url}')
