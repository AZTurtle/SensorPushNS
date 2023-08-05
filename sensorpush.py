#!/usr/bin/env python3
"""
Polyglot v3 node server Example 2
Copyright (C) 2021 Robert Paauwe

MIT License
"""
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

def node_queue(data):
    global n_queue

    n_queue.append(data['address'])

def wait_for_node_done():
    global n_queue
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()

'''

'''

def poll(pollType):
    if 'longPoll' in pollType:
        err = rest.refreshToken()
        if err:
            LOGGER.error(f'Failed to refresh token! Try authenticating again | {err}')
        

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
                sensor_.setDriver('ST', float(info['active']), True, True)
                sensor_.setDriver('GV0', float(data['temperature']), True, True)
                sensor_.setDriver('GV1', float(data['humidity']), True, True)
                sensor_.setDriver('GV2', float(info['battery_voltage']), True, True)

                sensor_num += 1

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
        

