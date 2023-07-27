#!/usr/bin/env python3
"""
Polyglot v3 node server Example 3
Copyright (C) 2021 Robert Paauwe

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
Controller is interfacing with both Polyglot and the device. In this
case the device is just a count that has two values, the count and the count
multiplied by a user defined multiplier. These get updated at every
shortPoll interval.
'''
class Controller(udi_interface.Node):
    id = 'ctl'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.n_queue = []
        self.sample_num = 1
        self.sp_nodes = {}

        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.poly.Notices.clear()

        try:
            email = self.Parameters['E-Mail']
            password = self.Parameters['Password']
            self.sample_num = self.Parameters["Number of Samples"]
        except Exception as e:
            LOGGER.error(e)

        if email and password:
            if rest.authorize(email, password):
                self.poly.Notices.clear()
                LOGGER.debug(rest.auth_code)
            else:
                self.poly.Notices['nodes'] = 'Invalid username and/or password'
        else:
            self.poly.Notices['nodes'] = 'Please provide an E-Mail and Password'

    '''
    node_queue() and wait_for_node_event() create a simple way to wait
    for a node to be created.  The nodeAdd() API call is asynchronous and
    will return before the node is fully created. Using this, we can wait
    until it is fully created before we try to use it.
    '''
    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    '''
    This is called when the node is added to the interface module. It is
    run in a separate thread.  This is only run once so you should do any
    setup that needs to be run initially.  For example, if you need to
    start a thread to monitor device status, do it here.

    Here we load the custom parameter configuration document and push
    the profiles to the ISY.
    '''
    def start(self):
        self.poly.setCustomParamsDoc()
        # Not necessary to call this since profile_version is used from server.json
        self.poly.updateProfile()

        try:
            while not rest.auth_code:
                LOGGER.info("Couldn't obtain authorization... Waiting")
                time.sleep(10)

            rest.refreshAuthToken()
            LOGGER.debug(rest.auth_token)
        except Exception as e:
            LOGGER.error("Failed to authorize")

        self.defineSensors()

    '''
    Create the children nodes.  Since this will be called anytime the
    user changes the number of nodes and the new number may be less
    than the previous number, we need to make sure we create the right
    number of nodes.  Because this is just a simple example, we'll first
    delete any existing nodes then create the number requested.
    '''

    def defineSensors(self):
        sensors = rest.get('devices/sensors').json()
        num = 0
        nodes = self.poly.getNodes()
        for i in sensors:
            sensor_ = sensors[i]
            found = False
            for node_ in nodes:
                node = nodes[node_]
                if node_[:5] == "child" and node.sp_address == i:
                    found = True
                    break
            if not found:
                try:
                    address = f'child_{num}'
                    node = sensor.SensorNode(self.poly, self.address, sensor_['address'], address, sensor_['name'])
                    self.sp_nodes[i] = address
                    self.poly.addNode(node)
                    self.wait_for_node_done()
                except Exception as e:
                    LOGGER.error("Couldn't create sensor: {}".format(e))
            num += 1
        LOGGER.debug(self.sp_nodes)
        
        self.setDriver('GV0', 2, True, True)
        
        nodes = self.poly.getNodes()
        LOGGER.debug(nodes)


    '''
    Change all the child node active status drivers to false
    '''
    def stop(self):

        nodes = self.poly.getNodes()
        for node in nodes:
            if node != 'controller':   # but not the controller node
                nodes[node].setDriver('ST', 0, True, True)

        self.poly.stop()


    '''
    Just to show how commands are implemented. The commands here need to
    match what is in the nodedef profile file. 
    '''
    def noop(self):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}
