import os
import json
import logging
import re

logger = logging.getLogger(__name__)

#_DEFAULT_CLOUDFLARE_IP_RANGE = '100.96.0.1-25'
_DEFAULT_CLOUDFLARE_IP_RANGE = '100.96.0.1-254'


def get_route_to(addr:str) -> str:
    ''' get route to IP address '''
    output =  __call_command(f"ip --json route get {addr}")
    if len(output)>0: return json.loads(output)
    else:             return {}

def get_interfaces() -> str:
    ''' get a list of all interfaces  '''
    output = __call_command("ip  -j -br address")
    if len(output)>0: return json.loads(output)
    else:             return {}



def check_open_ports(ip_range:str=_DEFAULT_CLOUDFLARE_IP_RANGE, port:int|str='15650') -> str:
    ''' search for all open ports in the given IP range --> available clients!'''
    result_str = __call_command(f"nmap -p {port}  -oG  -  {ip_range}")
    result = []
    for line in result_str.splitlines():
        if not '/open/' in line: continue
        ip   = line.split(' ')[1]
        host = line.split(' ')[2]
        result.append( {'ip':ip, 'host':host} )
    return result
    
   
 

def __call_command(cmd:str) -> dict:
    ''' calls the command line commands and returns the output'''
    logger.info(f"cmd: {cmd}")
    stream = os.popen(cmd)
    output = stream.read()
    logger.info(f"returned:\n{output}")
    return output
    