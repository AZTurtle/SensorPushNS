"""
SensorPush Node Server
Copyright (C) 2023 James Bennett

MIT License
"""
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
"""

"""
External service sample code
Copyright (C) 2024 Universal Devices

MIT License
"""
import requests
from udi_interface import LOGGER, Custom, OAuth

# This class implements the API calls to your external service
# It inherits the OAuth class
class SPService(OAuth):
    yourApiEndpoint = 'https://api.sensorpush.com/api/v1'

    def __init__(self, polyglot):
        # Initialize the OAuth class as well
        super().__init__(polyglot)

        self.poly = polyglot
        self.customParams = Custom(polyglot, 'customparams')
        LOGGER.info('External service initialized...')
        
    # The OAuth class needs to be hooked to these 2 handlers
    def customNsHandler(self, key, data):
        # This provides the oAuth config (key='oauth') and saved oAuth tokens (key='oauthTokens))
        super().customNsHandler(key, data)

    def oauthHandler(self, token):
        # This provides initial oAuth tokens following user authentication
        super().oauthHandler(token)

    # Your service may need to access custom params as well...
    def customParamsHandler(self, data):
        self.customParams.load(data)
        # Example for a boolean field

    # Call your external service API
    def _callApi(self, method='GET', url=None, body=None):
        if url is None:
            LOGGER.error('url is required')
            return None

        completeUrl = self.yourApiEndpoint + url

        LOGGER.info(f"Making call to { method } { completeUrl }")

        # When calling an API, get the access token (it will be refreshed if necessary)
        # If user has not authenticated yet, getAccessToken will raise a ValueError exception
        accessToken = self.getAccessToken()

        headers = {
            'accept': 'application/json',
            'Authorization': accessToken
        }

        if method in [ 'PATCH', 'POST'] and body is None:
            LOGGER.error(f"body is required when using { method } { completeUrl }")

        try:
            if method == 'GET':
                response = requests.get(completeUrl, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(completeUrl, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(completeUrl, headers=headers, json=body)
            elif method == 'POST':
                response = requests.post(completeUrl, headers=headers, json=body)
            elif method == 'PUT':
                response = requests.put(completeUrl, headers=headers)

            response.raise_for_status()
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return response.text

        except requests.exceptions.HTTPError as error:
            LOGGER.error(f"Call { method } { completeUrl } failed: { error }")
            return None

    # Then implement your service specific APIs
    def getSensors(self):
        return self._callApi(method='POST', url='/devices/sensors', body={})

    def getGateways(self):
        return self._callApi(method='POST', url='/devices/gateways', body={})

    def getSamples(self):
        return self._callApi(method='POST', url='/samples', body={
                'limit': 5
            })