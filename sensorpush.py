#!/usr/bin/env python3
"""
Polyglot v3 node server Example 2
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys
from nodes import gateway
import requests

LOGGER = udi_interface.LOGGER
SP_API_URL = "https://api.sensorpush.com/api/v1/"

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        # Create the controller node

        res = requests.post(SP_API_URL + "oauth/authorize", data={
            "email":"hunterbennett@hunterbennett.com",
            "password":"gHfsensor123"
        }).json()

        LOGGER.debug(res)

        gateway.Controller(polyglot, 'controller', 'controller', 'Counter')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
        

