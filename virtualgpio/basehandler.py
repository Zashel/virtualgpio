from .exceptions import *
from zashel.basehandler import *
import datetime

class VirtualGPIOBaseHandler(BaseHandler):
    def __init__(self):
        '''
        You must subclass it to handle the GPIO and other Stuff
        '''
        super().__init__()

    #~~~~~~~~~PROPERTIES~~~~~~~~~#  
    @property
    def is_virtualgpio_connected(self):
        return "virtualGPIO" in dir(self._connected_stuff)

    #~~~~~~~~~FUNCTIONS~~~~~~~~~~#
    def connect_virtualgpio(self, gpio):
        self.connect_stuff(virtualGPIO=gpio)

    #Handling functions:
    #All signals must begin with "signal_"
    def signal_connect(self, uuid, timeout):
        if self.is_virtualgpio_connected:
            timeout = datetime.datetime.strptime(timeout, "%Y%m%d%H%M%S")
            self.virtualGPIO.connections[uuid] = timeout #TODO: debug this. This is going to f*ck up all.

    def signal_disconnect(self, uuid):
        self.virtualGPIO.disconnect_client(uuid)
