import requests

SP_API_URL = 'https://api.sensorpush.com/api/v1/'

def authorize(email, password):
    global auth_token
    res = requests.post(SP_API_URL + 'oauth/authorize', data={
            'email': email,
            'password': password
        }).json()
    auth_token = res["authorization"]