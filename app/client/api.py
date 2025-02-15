#
# Abstracts the call to the cloudflare-s2s backend api
#
###################################################################
#pylint: disable=logging-fstring-interpolation

import requests
from urllib3.exceptions import (ConnectTimeoutError, MaxRetryError,
                                NewConnectionError, SSLError,
                                ReadTimeoutError, NameResolutionError)
import json
import logging
logger = logging.getLogger(__name__)

_DEFAULT_API_TIMEOUT = 1

###################################################################
# the baser class to call the api and handling errors
###################################################################

def apicall(api_url:str, timeout:int=_DEFAULT_API_TIMEOUT) -> tuple[bool,str|dict]:
    ''' Calls the API url and returns a tuple with a 
        boolean status and the result as hash / list .
        On error (False), the content contains the 
        error message as string.
    '''
    try:
        logger.debug(f"API: {api_url}")
        response = requests.get(api_url, timeout=timeout)
        logger.debug(f"RET: {response.status_code}\n{response.content}")        
        
    except requests.exceptions.ReadTimeout as error: 
        logger.debug(f"ReadTimeout: {error}")
        status = False
        result = str(error)
        return  status, result    
    except requests.exceptions.ConnectTimeout as error: 
        logger.debug(f"ConnectTimeout: {error}")
        status = False
        result = str(error)
        return  status, result    
    except requests.exceptions.ConnectionError as error: 
        logger.debug(f"ConnectionError: {error}")
        status = False
        result = str(error)
        return  status, result    
    except requests.exceptions.MissingSchema as error:
        logger.debug(f"MissingSchema: {error}")
        status = False
        result = str(error)
        return  status, result        
    except MaxRetryError as error:        
        logger.debug(f"MaxRetryError: {error}")
        status = False
        result = str(error)
        return  status, result    
    except NewConnectionError as error:
        logger.debug(f"NewConnectionError: {error}")
        status = False
        result = str(error)
        return  status, result    
    except ConnectTimeoutError as error:
        logger.debug(f"ConnectTimeoutError: {error}")
        status = False
        result = str(error)
        return  status, result    
    except SSLError as error:
        logger.debug(f"SSLError: {error}")
        status = False
        result = str(error)
        return  status, result    
    except ReadTimeoutError as error:
        logger.debug(f"ReadTimeoutError: {error}")
        status = False
        result = str(error)
        return  status, result    
    except Exception as error: # FIXME: this should not be needed !!
        logger.warning(f"\nUnknown error type: {type(error)}\n{str(error)}")
        status = False
        result = str(error)
        return  status, result   
    
    # processing the results     
    status   = (response.status_code == 200)
    content  = response.content.decode('ascii')
    # in error return the raw content    
    if not status: 
        return status, content

    result   = json.loads(response.content.decode('ascii'))
    if isinstance(result,dict): return  status, result
    if isinstance(result,list): return  status, result
    
    return  status, {}

###################################################################
# functions to abstract teh API to python interface
###################################################################
    

def get_version(addr:str) -> str:
    ''' returns the version, on error return empty '''
    success,result = apicall( addr + "/version" )
    return result["version"] if success and "version" in result.keys() else ""

def get_builddate(addr:str) -> str:
    ''' returns the builddate, on error return "failure" '''
    success,result = apicall( addr + "/builddate" )
    return result["builddate"] if success and "builddate" in result.keys() else  "unkown"

def get_connector(addr:str) -> str:
    ''' returns the connector id, on error return "failure" '''
    success,result = apicall( addr + "/warp/connector/get" )
    return result["token"] if success and "token" in result.keys() else "unkown"


def warp_register(addr:str) -> bool:
    success,result = apicall( addr + "/warp/connector/new" )
    return success

def warp_unregister(addr:str) -> bool:
    success,result =  apicall( addr + "/warp/registration/delete" )
    return success

def warp_register_show(addr:str) -> str:
    success,result =  apicall( addr + "/warp/registration/show" )
    return result if success else "error"


def warp_connect(addr:str) -> bool:
    success,result = apicall( addr + "/warp/connect" )
    return success
    if not success: return "failure"
    return "success"

def warp_disconnect(addr:str) -> bool:
    success,result = apicall( addr + "/warp/disconnect" )
    return success
    if not success: return "failure"
    return "success"

def warp_get_vnets(addr:str) -> dict|str:
    success,result = apicall( addr + "/warp/vnet" )
    return result if success else "error"

def wget_active_vnet(addr:str) -> str:
    result = warp_get_vnets(addr)
    if result == "failure": return "failure"

    active_id = result["active_vnet_id"]
    active_network = [network for network in result["virtual_networks"] if network["id"] == active_id ][0]
    return active_network

def warp_my_subnet(addr:str) -> dict|str:
    success,result = apicall( addr + "/warp/interface/mysubnet" )
    return result if success else "error"
def warp_my_ip(addr:str) -> dict|str:
    success,result = apicall( addr + "/warp/interface/ip" )
    return result if success else "error"


def docker_interfaces(addr:str) -> dict|str:
    success,result = apicall( addr + "/net/interfaces" )
    return result if success else "error"

def get_warp_status(addr:str) -> str:
    ''' returns the status of the warp interface 
            'Failure': on any failures including unknown statis
            'Connected': if there is a connection
            'Disconnected': if the connector is disconnected
            'unregistered': there is no registration
            'unknown': if ther eis an unkown status retured
    '''
    # {'reason': 'Manual', 'status': 'Disconnected'}
    # {'status': 'Connecting'}

    success,result = apicall( addr + "/warp/status" )
    if not success: return "Failure"
    if result["status"] in ["Connected", "Disconnected","Connecting"]: 
        return result["status"]
    if result["status"] == "Unable":
         if result["reason"] == "RegistrationMissing": return "Unregistered"
         else: return "unkown"
    logger.warning(f'unkown return from /warp/status: {result}')
    return "Failure"

async def warp_search_backends(addr:str) -> dict|str:
    success,result = apicall( addr + "/warp/search_backends", timeout=120 )
    return result if success else "error"


###################################################################
# functions wrapped in class whcih stores the API address
###################################################################

class WARP_STATE: pass
class WARP_STATE_FAILURE(WARP_STATE): pass
class WARP_STATE_CONNECTED(WARP_STATE): pass
class WARP_STATE_CONNECTING(WARP_STATE): pass
class WARP_STATE_DISCONNECTED(WARP_STATE): pass

class site:
    def __init__(self,addr:str):
        self.addr = addr
    
    def is_connected(self) -> bool:
        ''' returns true if one could connect to teh server api '''
        # TODO: change to multiple  state, can ping host, can ping port can connect to api!
        return len(get_version(self.addr))>0

    def get_version(self) -> str:
        ''' returns the version, on error return empty '''
        return get_version(self.addr)

    def get_builddate(self) -> str:
        ''' returns the builddate, on error return "failure" '''
        return get_builddate(self.addr)
    
    def get_connector(self) -> str:
        ''' returns the connector id, on error return "failure" '''
        return get_connector(self.addr)
    

    def warp_register(self) -> bool:
        return warp_register(self.addr)
    
    def warp_unregister(self) -> bool:
        return warp_unregister(self.addr)

    def warp_register_show(self) -> str:        
        return warp_register_show(self.addr)

    def warp_connect(self) -> str:
        return warp_connect(self.addr)

    def warp_disconnect(self) -> str:
        return warp_disconnect(self.addr)
    
    def warp_my_subnet(self) -> dict|str:
        return warp_my_subnet(self.addr)
    def warp_my_ip(self) -> dict|str:
        return warp_my_ip(self.addr)

    def docker_interfaces(self) -> dict|str:
        return docker_interfaces(self.addr)
    
    def warp_get_vnets(self) -> dict|str:
        return warp_get_vnets(self.addr)

    def wget_active_vnet(self) -> str:
        return wget_active_vnet(self.addr)

    async def warp_search_backends(self) -> str:
        return await warp_search_backends(self.addr)


    def get_warp_status(self) -> str:
        ''' returns the status of the warp interface 
                'Failure': on any failures including unknown statis
                'Connected': if there is a connection
                'Disconnected': if the connector is disconnected
                'unregistered': there is no registration
                'unknown': if ther eis an unkown status retured
        '''
        return get_warp_status(self.addr)



