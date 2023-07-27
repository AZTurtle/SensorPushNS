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
            {'driver': 'GV1', 'value': 0, 'uom': 56}
            ]

    def __init__(self, polyglot, parent, sp_address, address, name):
        super(SensorNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.sp_address = sp_address