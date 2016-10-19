#Exceptions:

class DisconnectingError(Exception):
    '''
    Error disconnecting
    '''
    pass

class PathError(Exception):
    '''
    Bad Path Name
    '''
    pass

class VirtualGPIOError(Exception):
    '''
    Given VirtualGPIO not a VirtualGPIO
    '''
    pass
