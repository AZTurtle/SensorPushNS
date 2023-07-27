#!/usr/bin/env python3
"""
Polyglot v3 node server Example 3
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

'''
This is our Counter device node.  All it does is update the count at the
poll interval.
'''
class SensorNode(udi_interface.Node):
    id = 'child'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            {'driver': 'GV1', 'value': 0, 'uom': 56},
            {'driver': 'GV2', 'value': 1, 'uom': 2}
            ]

    def __init__(self, polyglot, parent, sp_address, address, name):
        super(SensorNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.sp_address = sp_address

        # subscribe to the events we want

    '''
    Read the user entered custom parameters. In this case, it is just
    the 'multiplier' value that we want.  
    '''

    '''
    This is where the real work happens.  When we get a shortPoll, increment the
    count, report the current count in GV0 and the current count multiplied by
    the user defined value in GV1. Then display a notice on the dashboard.
    '''

    def set_increment(self,val=None):
        # On startup this will always go back to true which is the default, but how do we restort the previous user value?
        LOGGER.debug(f'{self.address} val={val}')
        self.setDriver('GV2',val)

    def cmd_set_increment(self,command):
        val = int(command.get('value'))
        LOGGER.debug(f'{self.address} val={val}')
        self.set_increment(val)

    commands = {
        "SET_INCREMENT": cmd_set_increment,
    }