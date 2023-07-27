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

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        def parameterHandler(params):
            self.Parameters.load(params)

            email = self.Parameters['email']
            password = self.Parameters['password']

            if email is not None and password is not None:
                rest.authorize("hunterbennett@hunterbennett.com", "gHfsensor123")

                if rest.auth_token is None:
                    polyglot.Notices['nodes'] = 'Invalid username and/or password'
                else:
                    LOGGER.debug(rest.auth_token)

        # Create the controller node

        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)

        gateway.Controller(polyglot, 'controller', 'controller', 'Counter')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

