#!/usr/bin/env python3
"""
Polyglot v3 node server Example 2
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys
from nodes import gateway
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
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()

def generateGateways(polyglot):
    global gateways

    gateway_data = rest.get('devices/gateways')
    LOGGER.debug(gateway_data)

    sensor_info = rest.get('devices/sensors')

    sample_data = rest.post('samples', {
        'limit': sample_num
    })

    LOGGER.debug(sample_data)

    sensor_data = sample_data['sensors']

    gateway_sensors = {}

    for k in sensor_data:
        sensor_ = sensor_data[k]
        addr = sensor_[0]['gateways']
        if addr in gateway_sensors:
            gateway_sensors[addr].append([k, sensor_info[k]['name']])
        else:
            gateway_sensors[addr] = [k, sensor_info[k]['name']]

    for k in gateway_data:
        gateway_ = gateway_data[k]
        id = gateway_['id']
        try:
            sensors = gateway_sensors[id]

            if not sensors:
                LOGGER.debug('No sensors for {}'.format(gateway_['name']))

            node = gateway.Controller(polyglot, 'controller', 'controller', gateway_['name'], sensors)
            polyglot.addNode(node)
            wait_for_node_done()
        except Exception as e:
            LOGGER.error('Error when creating gateway {}'.format(e))

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        LOGGER.debug(polyglot.getNodesFromDb())

        Parameters = Custom(polyglot, 'customparams')

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
                    
                    try:
                        while not rest.auth_code:
                            LOGGER.info("Couldn't obtain authorization... Waiting")
                            time.sleep(10)

                        rest.refreshAuthToken()
                    except Exception as e:
                        LOGGER.error("Failed to authorize")

                    generateGateways(polyglot)
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
        

