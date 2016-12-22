# All Objects
__all__ = [
        "VirtualGPIO",
        "VirtualGPIOBaseHandler",
        "ConnectSignal",
        "DisconnectSignal"
        ]
        
# All Exceptions
__all__.extend([
        "DisconnectingError",
        "PathError",
        "VirtualGPIOError"
        ])

from .exceptions import *
from .signals import *
from .basehandler import *
from .signals import *
from zashel.utils import daemonize
from uuid import uuid1
import datetime
import os
import time
import shutil

#Folder names
INPUT = "input"
OUTPUT = "output"
CLIENTS = "clients"

#Default values
DEFAULT_TIMEOUT = datetime.timedelta(minutes=30)
DEFAULT_SLEEP = 1

#Values to use
TIMEOUT = DEFAULT_TIMEOUT #TODO: implement Timeout
SLEEP = DEFAULT_SLEEP

#Main Class of the VirtualGPIO Object
class VirtualGPIO(object):
    #~~~~~~~~~VirtualGPIO~~~~~~~~#
    #~~~~~~~~~~BUILT-IN~~~~~~~~~~#
    def __init__(
            self,
            path,
            handler=VirtualGPIOBaseHandler(),
            *,
            timeout = DEFAULT_TIMEOUT):
        '''
        Instantiate a Virtual GPIO.
        
        path: path for the required files to be created/modified
        '''
        self._connected = False
        if not os.path.exists(path):
            raise PathError(
                    "Path {} does not exist".format(
                            path
                    )
            )
        self._path = path
        self._uuid = uuid1()
        self._input = os.path.join(self.path, INPUT)    #See property path ahead
        self._output = os.path.join(self.path, OUTPUT)
        self.connections = dict()
        self._handler = handler
        self._handler.connect_virtualgpio(self)

    def __del__(self): #I thought this to be fun
        self.disconnect()
            
    #~~~~~~~~~VirtualGPIO~~~~~~~~#  
    #~~~~~~~~~PROPERTIES~~~~~~~~~#
    #Path for clients
    @property
    def clients(self):
        return os.path.join(self._path, CLIENTS)

    #True if connected
    @property
    def connected(self):
        return self._connected
    
    #Handler
    @property
    def handler(self):
        return self._handler
        
    #Path of the Input Interface
    @property
    def input(self):
        return self._input
        
    #Path of the Output Interface
    @property
    def output(self):
        return self._output
                
    #Path of the VirtualGPIO
    @property
    def path(self):
        return os.path.join(self._path, self.uuid)

    #Unique Identifier of the Virtual GPIO
    @property
    def uuid(self):
        return self._uuid.hex
        
    #~~~~~~~~~VirtualGPIO~~~~~~~~#
    #~~~~~~~~~~FUNCTIONS~~~~~~~~~#
    def _raw_send(self, destination, message): #Send it anyway
        if destination != self.uuid:
            now = self.timeout()    #Twice
            if isinstance(message, str):
                message = bytearray(message, "utf-8")
            if isinstance(message, bytearray):
                file_name = "{}-{}".format(now, destination)
                file_path = os.path.join(self.output, file_name)
                with open(file_path, "wb") as message_file:
                    message_file.write(message)
                destination_path = os.path.join(
                        self._path,
                        destination,
                        INPUT,
                        file_name) #Now we move the data.
                try:
                    os.rename(file_path, destination_path)
                except:
                    raise Exception #Look for an Exception
            else:
                return TypeError("message must be a bytearray or a str")
            
            
    def connect(self):      #Make file and GPIO Visible
        if not os.path.exists(self.clients):
            os.mkdir(self.clients)
        lsdir = os.listdir(self.clients)
        now = datetime.datetime.now()
        for uuid_file_name in lsdir: #Check other connections
            if uuid_file_name != self.uuid:
                with open(os.path.join(self.clients, uuid_file_name), "r") as uuid_file:
                    timeout = datetime.datetime.strptime( 
                            uuid_file.readline().strip("\n"),
                            "%Y%m%d%H%M%S"
                            )
                    if timeout >= now:
                        self.connections[uuid_file_name] = timeout
        self.keep_alive()   #See function ahead
        os.mkdir(self.path)
        os.mkdir(self.input)
        os.mkdir(self.output)
        for connection in self.connections:
            signal = ConnectSignal(self.uuid, self.timeout())
            self.send(connection, signal)
        self._connected = True

    def disconnect(self):   #Say Goodbye
        if self.connected is True:
            for connection in self.connections:
                self.send(connection, DisconnectSignal(self.uuid))
            x = int()
            while x < 10:
                try:
                    os.remove(os.path.join(self.clients, self.uuid))
                    break
                except:
                    time.sleep(SLEEP)
                    x+=1
            if x==10:
                raise DisconnectingError
            try:
                shutil.rmtree(self.path)
            except:
                pass
            self._connected = False

    def disconnect_client(self, uuid):   #It's sad, but the've said you goodbye
        try:
            del(self.connections[uuid])
        except:
            pass
            
    def keep_alive(self):    #Set next timeout
        timeout = self.timeout()     #First
        with open(os.path.join(self.clients, self.uuid), "w") as uuid_file:
            uuid_file.write(timeout)
            
    def timeout(self):           #First Golden Rule: If you use it twice, write it once.
        now = datetime.datetime.now()
        timeout = now + TIMEOUT
        timeout = timeout.strftime("%Y%m%d%H%M%S")
        return timeout #I should change all nows for timeout
        
    @daemonize
    def listen(self): #Let's listen on Input
        lsdir = list()
        print("VGPIO listening on {}".format(self.input))
        while True: #This will listen almost all the messages
            if len(lsdir)>0:
                lsdir.sort()
                for message_file_name in lsdir:
                    try:
                        with open(os.path.join(self.input, message_file_name), "r") as message_file:
                            signal = message_file.readline()
                            signal = signal.strip("\n").strip(":")
                            args = list()
                            next = message_file.readline().strip("\n")
                            while next != "":
                                args.append(next)
                                next = message_file.readline().strip("\n")
                            self.handler.get_signal(signal)(*args)
                        os.remove(os.path.join(self.input, message_file_name)) #Another thing I forgot
                    except:
                        raise #By now
            lsdir = os.listdir(self.input)
            time.sleep(SLEEP)

    def run(self):
        self.connect()
        self.listen()
        
    def send(self, destination, signal): #signal from MetaSignal
        self._raw_send(destination, signal.bytearray)

    def send_all(self, signal):
        for destination in self.connections:
            self.send(destination,signal)