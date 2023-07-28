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

gateways = {}
n_queue = []

def generateGateways(polyglot):
    global gateways

    gateway_data = rest.get('devices/gateways')
    LOGGER.debug(gateway_data)

    for k in gateway_data:
        gateway_ = gateway_data[k]
        try:
            gateway.Controller(polyglot, 'controller', 'controller', gateway_['name'])
        except Exception as e:
            LOGGER.error('Error when creating gateway {}'.format(e))

def node_queue(data):
    global n_queue

    n_queue.append(data['address'])

def wait_for_node_done():
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        LOGGER.debug(polyglot.getNodesFromDb())

        Parameters = Custom(polyglot, 'customparams')
        sample_num = 0

        def parameterHandler(params):
            global sample_num

            Parameters.load(params)
            polyglot.Notices.clear()

            email = Parameters['E-Mail']
            password = Parameters['Password']
            sample_num = Parameters['Number of Samples']

            if email and password:
                if rest.authorize(email, password):
                    polyglot.Notices.clear()
                    polyglot.ready()
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
        

