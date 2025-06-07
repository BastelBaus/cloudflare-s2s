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


###############################################################################
# general command about IP addresses and interfaces
###############################################################################

def get_route_to(addr:str) -> dict:
    ''' get route to IP address '''
    output =  __call_command(f"ip --json route get {addr}")
    if len(output)>0: return json.loads(output) #pylint: disable=multiple-statements
    else:             return {}                 #pylint: disable=multiple-statements

def get_interfaces() -> dict:
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

###############################################################################
# NFTables routing firewalling
###############################################################################

_NFT = "/usr/sbin/nft"
_NATTABLE = "natrouting"
 
def nft_get_ruleset() -> dict:
    return json.loads(__call_command(f"{_NFT} -j list ruleset") ) 

def nft_clear_nattable() -> None:
    ''' delete the custom nat tables '''
    __call_command(f"{_NFT} add table ip {_NATTABLE}")  # ensure, table exists
    __call_command(f"{_NFT} delete table ip {_NATTABLE}") 

def __old_nft_create_nattable(warpcli,cfg) -> None | str:
    ''' returns None on success else the error message as string '''
    #from_subnet = "192.168.16.0/23"
    #to_subnet   = "192.168.0.0/23"

    #return _nft_create_nattable(from_subnet,to_subnet)
    pass

def nft_create_nattable(from_subnet,to_subnet) -> bool:
    ''' returns None on success else the error message as string '''
    ret = __call_command(f"{_NFT} add table ip {_NATTABLE}")  # ensure, table exists

    if ret !="": return ret

    ret = __call_command(f"{_NFT} add 'chain ip {_NATTABLE} dnating " 
                         f"{{ type nat hook prerouting priority dstnat; policy accept; }}'")
    if ret !="": return ret
    ret = __call_command(f"{_NFT} add 'rule {_NATTABLE} dnating "
                              f"ip daddr {from_subnet} dnat ip prefix to "
                              f"ip daddr map {{ {from_subnet} : {to_subnet} }}'" )
    print("len",len(ret))
    print(f">{ret}<")    
    if ret !="": return ret

    ret = __call_command(f"{_NFT} add 'chain ip {_NATTABLE} snating {{ type nat hook postrouting priority srcnat; policy accept; }}'")
    if ret !="": return ret
    ret = __call_command(f"{_NFT} add 'rule {_NATTABLE} snating iifname \"CloudflareWARP\" masquerade'")
    if ret !="": return ret

    return "success"


###############################################################################
# interface to the shell
###############################################################################

def __call_command(cmd:str) -> str:
    ''' calls the command line commands and returns the output'''
    logger.info(f"cmd: {cmd} 2>&1")
    stream = os.popen(cmd + " 2>&1")
    output = stream.read()
    logger.info(f"returned:\n{output}")
    return output

