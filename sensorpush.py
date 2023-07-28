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

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

gateways = {}

def generateGateways(polyglot):
    global gateways

    gateway_data = rest.get('devices/gateways')

    gateways = {gateway_data[gateway]['id']:gateway for gateway in gateway_data}

    LOGGER.debug(gateways)

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
                    generateGateways(polyglot)
                else:
                    polyglot.Notices['nodes'] = 'Invalid username and/or password'
            else:
                polyglot.Notices['nodes'] = 'Please provide an E-Mail and Password'
        
        
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)

        # Create the controller node

        gateway.Controller(polyglot, 'controller', 'controller', 'Counter')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

