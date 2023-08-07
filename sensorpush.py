"""
SensorPush Node Server
Copyright (C) 2023 James Bennett

MIT License
"""

'''
TODO - Add more comments
'''

import udi_interface
import sys
from nodes import gateway
from nodes import sensor
import rest
import time

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

sample_num = 1
n_queue = []

update_sensors = {}

'''
Gives a delay for every node added before allowing them to be used
'''

def node_queue(data):
    global n_queue

    n_queue.append(data['address'])

def wait_for_node_done():
    global n_queue
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()


'''
Used to refresh the access_token after an hour
'''

def poll(pollType):
    if 'longPoll' in pollType:
        err = rest.refreshToken()
        if err:
            LOGGER.error(f'Failed to refresh token! Try authenticating again | {err}')   

        sensor_info = rest.get('devices/sensors')
        
        for id in update_sensors:
            if id in sensor_info:
                sensor_ = update_sensors[id]
                info = sensor_info[id]

                sensor_.setDriver('ST', info['active'], True, True)
                sensor_.setDriver('GV2', float(info['battery_voltage']), True, True)
            else:
                sensor_.setDriver('ST', False, True, True)


'''
Main function for generating nodes at beginning of server
'''

def generateGateways(polyglot):
    gateway_data = rest.get('devices/gateways')

    sensor_info = rest.get('devices/sensors')

    sample_data = rest.post('samples', {
        'limit': sample_num
    })

    sensor_data = sample_data['sensors']

    gateway_sensors = {}

    for k in sensor_data:
        sensor_ = sensor_data[k]
        addr = sensor_[0]['gateways']
        if addr in gateway_sensors:
            gateway_sensors[addr].append(k)
        else:
            gateway_sensors[addr] = []
            gateway_sensors[addr].append(k)

    num = 0
    sensor_num = 0
    for k in gateway_data:
        gateway_ = gateway_data[k]
        id = gateway_['id']
        try:
            sensors = gateway_sensors[id]

            if not sensors:
                LOGGER.debug('No sensors for {}'.format(gateway_['name']))

            addr = f'controller_{num}'
            node = gateway.GatewayNode(polyglot, addr, addr, gateway_['name'], sample_num)
            polyglot.addNode(node)
            wait_for_node_done()
            num += 1

            total_sensors = {}

            for i in sensors:
                sensor_addr = f'child_{sensor_num}'
                sensor_ = sensor.SensorNode(polyglot, addr, sensor_addr, sensor_info[i]['name'], i)
                total_sensors[i] = sensor_

                data = sensor_data[i][0]
                info = sensor_info[i]
                sensor_.setDriver('ST', info['active'], True, True)
                sensor_.setDriver('GV0', float(data['temperature']), True, True)
                sensor_.setDriver('GV1', float(data['humidity']), True, True)
                sensor_.setDriver('GV2', float(info['battery_voltage']), True, True)
                sensor_.setDriver('GV3', )

                sensor_num += 1

            update_sensors.update(total_sensors)
            node.defineSensors(total_sensors)
        except Exception as e:
            LOGGER.error('Error when creating gateway {}'.format(e))

def customEvents(event, data):
    if event == 'oauth':
        rest.refresh_data['client_id'] = data['client_id']
        rest.refresh_data['client_secret'] = data['client_secret']
    

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        Parameters = Custom(polyglot, 'customparams')

        
        def parameterHandler(params):
            global sample_num

            Parameters.load(params)
            polyglot.Notices.clear()

            sample_num = int(Parameters['Number of Samples'])
            
        '''
        Handles authorization by using OAuth2 and sensorpush's login portal
        '''
        def oauth(data):
            LOGGER.debug(data)

            rest.access_token = data['access_token']
            rest.refresh_data['refresh_token'] = data['refresh_token']

            generateGateways(polyglot)
        
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)
        polyglot.subscribe(polyglot.POLL, poll)
        polyglot.subscribe(polyglot.OAUTH, oauth)
        polyglot.subscribe(polyglot.CUSTOMNS, customEvents)


        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()

        # Just sit and wait for events
        polyglot.ready()
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

