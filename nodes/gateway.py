"""
SensorPush Node Server
Copyright (C) 2023 James Bennett

MIT License
"""

import udi_interface
import sys
import time
from nodes import sensor
import rest

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

'''
The SensorPush Gateway node class.
Represents a physical gateway that individual sensors connect to.

Any sensors updated by this gateway are represented as children of this node.
Individually gets the new samples for each sensor attached.

TODO: Add checking for disconnected sensors and gateways
'''

class GatewayNode(udi_interface.Node):
    id = 'ctl'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2}
            ]

    def __init__(self, polyglot, parent, address, name, limit):
        super(GatewayNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.n_queue = []
        self.limit = limit
        self.created = False
        
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def defineSensors(self, sensors):

        self.sensors = sensors

        for i in self.sensors.values():
            try:
                self.poly.addNode(i)
                self.wait_for_node_done()
            except Exception as e:
                LOGGER.error('Error when creating sensor: {}'.format(e))
        
        self.poly.subscribe(self.poly.POLL, self.poll)


    def poll(self, polltype):
        if 'shortPoll' in polltype:
            res = rest.post('samples', {
                'sensors': list(self.sensors.keys()),
                'limit': self.limit
            })

            sensor_data = res['sensors']
            for k in sensor_data:
                data = sensor_data[k][0]
                self.sensors[k].setDriver('GV0', float(data['temperature']), True, True)
                self.sensors[k].setDriver('GV1', float(data['humidity']), True, True)

    '''
    '''
    def stop(self):

        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':
                nodes[node].setDriver('ST', 0, True, True)

        self.poly.stop()
