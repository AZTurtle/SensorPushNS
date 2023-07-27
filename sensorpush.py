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

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        Parameters = Custom(polyglot, 'customparams')

        def parameterHandler(params):
            Parameters.load(params)

            email = Parameters['email']
            password = Parameters['password']

            if email is not None and password is not None:
                rest.authorize(email, password)

                if rest.auth_token is None:
                    polyglot.Notices['nodes'] = 'Invalid username and/or password'
                else:
                    LOGGER.debug(rest.auth_token)
            else:
                polyglot.Notices['nodes'] = 'Please provide an E-Mail and Password'

        # Create the controller node

        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)

        gateway.Controller(polyglot, 'controller', 'controller', 'Counter')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

