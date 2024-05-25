#!/usr/bin/env python

from nodes import Controller
import sys
from rest import SPService
from udi_interface import LOGGER, Custom, Interface

polyglot = None
oauthService = None
controller = None

def configDoneHandler():
    # We use this to discover devices, or ask to authenticate if user has not already done so
    polyglot.Notices.clear()

    # First check if user has authenticated
    try:
        oauthService.getAccessToken()
    except ValueError as err:
        LOGGER.warning('Access token is not yet available. Please authenticate.')
        polyglot.Notices['auth'] = 'Please initiate authentication'
        return
    
    controller.update()

def oauthHandler(token):
    # When user just authorized, pass this to your service, which will pass it to the OAuth handler
    oauthService.oauthHandler(token)

    # Then proceed with device discovery
    configDoneHandler()

def stopHandler():
    # Set nodes offline
    polyglot.stop()

if __name__ == "__main__":
	try:
		# Create an instance of the Polyglot interface. We need to
		# pass in array of node classes (or an empty array).

		polyglot = Interface([])
		polyglot.start({ 'version': '1.0.0', 'requestId': True }) 
          
		polyglot.setCustomParamsDoc()

		# Update the profile files
		polyglot.updateProfile()
          
		oauthService = SPService(polyglot)

		# Start the node server (I.E. create the controller node)
		controller = Controller(polyglot, "controller", "controller", "Sensorpush", oauthService)
        
		polyglot.subscribe(polyglot.STOP, stopHandler)
		polyglot.subscribe(polyglot.CUSTOMNS, oauthService.customNsHandler)
		polyglot.subscribe(polyglot.CUSTOMPARAMS, oauthService.customParamsHandler)
		polyglot.subscribe(polyglot.OAUTH, oauthHandler)
		polyglot.subscribe(polyglot.CONFIGDONE, configDoneHandler)
		
		polyglot.ready()

		# Enter main event loop waiting for messages from Polyglot
		polyglot.runForever()
	except (KeyboardInterrupt, SystemExit):
		sys.exit(0)
