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
                sensor_ = sensor.SensorNode(polyglot, addr, sensor_addr, sensor_info[i]['name'])
                total_sensors[i] = sensor_

                data = sensor_data[i][0]
                sensor_.setDriver('GV0', int(data['temperature']), True, True)
                sensor_.setDriver('GV1', int(data['humidity']), True, True)

                sensor_num += 1

            node.defineSensors(total_sensors)
        except Exception as e:
            LOGGER.error('Error when creating gateway {}'.format(e))

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        Parameters = Custom(polyglot, 'customparams')

        '''
        Handles authorization by using an e-mail and password obtained by custom parameters to get an auth key.
        The auth key is then used to generate an auth token.
        '''
        def parameterHandler(params):
            global sample_num

            Parameters.load(params)
            polyglot.Notices.clear()

            email = Parameters['E-Mail']
            password = Parameters['Password']
            sample_num = int(Parameters['Number of Samples'])

            if email and password:
                if rest.authorize(email, password):
                    polyglot.Notices.clear()
                    
                    if rest.refreshAuthToken():
                        generateGateways(polyglot)
                    else:
                        LOGGER.info("Couldn't obtain authorization token...")
                else:
                    polyglot.Notices['nodes'] = 'Invalid username and/or password'
            else:
                polyglot.Notices['nodes'] = 'Please provide an E-Mail and Password'
        
        
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)


        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()

        # Create the controller node
        polyglot.ready()
        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

