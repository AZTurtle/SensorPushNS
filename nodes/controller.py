import udi_interface

# My Template Node
from nodes import Sensor
from nodes import Gateway
import rest
import time

LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER
Custom = udi_interface.Custom
ISY = udi_interface.ISY

# IF you want a different log format than the current default
LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

class Controller(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, oauthService):
        super(Controller, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = name  # override what was passed in

        self.oauthService = oauthService

        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')
        
        self.n_queue = []

        self.poly.subscribe(self.poly.POLL, self.poll)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)

        self.poly.addNode(self)

        self.child_num = 0

    #---------NODE QUEUE------------

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.3)
        self.n_queue.pop()
    #-------------------------------

    def poll(self, flag):

        if 'longPoll' in flag:
            LOGGER.debug('longPoll (controller)')
        else:
            self.update()
    
    def update(self):

        #Update nodes
        gateway_data = self.oauthService.getGateways()
        sensor_data = self.oauthService.getSensors()

        sample_data = self.oauthService.getSamples()

        data = sample_data['sensors']
        
        nodes = self.poly.getNodes()
        node_names = [nodes[n].name for n in nodes]

        for gateway_name in gateway_data:
            if gateway_name not in node_names:
                #Make gateway node
                addr = f'child_{self.child_num}'
                gateway = Gateway(self.poly, self.address, addr, gateway_name)
                self.poly.addNode(gateway)
                self.wait_for_node_done()
                self.child_num += 1

        for sensor_id in sensor_data:
            sensor_info = sensor_data[sensor_id]
            sensor = 0
            if sensor_info['name'] not in node_names:
                #Make node for sensor
                addr = f'child_{self.child_num}'
                sensor = Sensor(self.poly, self.address, addr, sensor_info['name'])
                self.poly.addNode(sensor)
                self.wait_for_node_done()
                
                self.child_num += 1
            else:
                #Get created sensor
                for addr in nodes:
                    node = nodes[addr]
                    if node.name == sensor_info['name']:
                        sensor = node
                        break
                else:
                    LOGGER.error(f"Couldn't find sensor {sensor_info['name']}")

            #Update sensor data
            curr_data = data[sensor_id][0]
            sensor.setDriver('ST', int(sensor_info['active']), True, True)
            sensor.setDriver('GV0', float(curr_data['temperature']), True, True)
            sensor.setDriver('GV1', float(curr_data['humidity']), True, True)
            sensor.setDriver('GV2', float(sensor_info['battery_voltage']), True, True)
        

    def query(self,command=None):
        """
        Optional.

        The query method will be called when the ISY attempts to query the
        status of the node directly.  You can do one of two things here.
        You can send the values currently held by Polyglot back to the
        ISY by calling reportDriver() or you can actually query the 
        device represented by the node and report back the current 
        status.
        """
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def discover(self, *args, **kwargs):
        """
        Example
        Do discovery here. Does not have to be called discovery. Called from
        example controller start method and from DISCOVER command recieved
        from ISY as an exmaple.
        """

    def delete(self):
        """
        Example
        This is call3ed by Polyglot upon deletion of the NodeServer. If the
        process is co-resident and controlled by Polyglot, it will be
        terminiated within 5 seconds of receiving this message.
        """
        LOGGER.info('Oh God I\'m being deleted. Nooooooooooooooooooooooooooooooooooooooooo.')

    def stop(self):
        """
        This is called by Polyglot when the node server is stopped.  You have
        the opportunity here to cleanly disconnect from your device or do
        other shutdown type tasks.
        """
        LOGGER.debug('NodeServer stopped.')


    """
    This is an example of implementing a heartbeat function.  It uses the
    long poll intervale to alternately send a ON and OFF command back to
    the ISY.  Programs on the ISY can then monitor this and take action
    when the heartbeat fails to update.
    """
    def heartbeat(self,init=False):
        LOGGER.debug('heartbeat: init={}'.format(init))
        if init is not False:
            self.hb = init
        LOGGER.debug('heartbeat: hb={}'.format(self.hb))
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def check_params(self):
        """
        This is an example if using custom Params for user and password and an example with a Dictionary
        """
        pass

    """
    Optional.
    Since the controller is a node in ISY, it will actual show up as a node.
    Thus it needs to know the drivers and what id it will use. The controller
    should report the node server status and have any commands that are
    needed to control operation of the node server.

    Typically, node servers will use the 'ST' driver to report the node server
    status and it a best pactice to do this unless you have a very good
    reason not to.

    The id must match the nodeDef id="controller" in the nodedefs.xml
    """
    id = 'main'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2}
            ]