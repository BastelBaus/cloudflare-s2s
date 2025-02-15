#
# Module to interact with the local interfaces
#
###############################################################################
# pylint: disable=logging-fstring-interpolation

import os
import json
import logging
import re

from . import defaults


logger = logging.getLogger(__name__)

def get_route_to(addr:str) -> str:
    ''' get route to IP address '''
    output =  __call_command(f"ip --json route get {addr}")
    if len(output)>0: return json.loads(output) #pylint: disable=multiple-statements
    else:             return {}                 #pylint: disable=multiple-statements

def get_interfaces() -> str:
    ''' get a list of all interfaces  '''
    output = __call_command("ip  -j -br address")
    if len(output)>0: return json.loads(output) #pylint: disable=multiple-statements
    else:             return {}                 #pylint: disable=multiple-statements

def check_open_ports(ip_range:str=defaults.CLOUDFLARE_IP_RANGE, port:int|str='15650') -> str:
    ''' search for all open ports in the given IP range --> available clients!'''
    result_str = __call_command(f"nmap -p {port}  -oG  -  {ip_range}")
    result = []
    for line in result_str.splitlines():
        if not '/open/' in line: continue       #pylint: disable=multiple-statements
        ip   = line.split(' ')[1]
        host = line.split(' ')[2]
        host = re.findall(r"\((.*?)\)", host)[0] # grep the values between the brackets
        result.append( {'ip':ip, 'host':host} )
    return result

def __call_command(cmd:str) -> dict:
    ''' calls the command line commands and returns the output'''
    logger.info(f"cmd: {cmd}")
    stream = os.popen(cmd)
    output = stream.read()
    logger.info(f"returned:\n{output}")
    return output
    