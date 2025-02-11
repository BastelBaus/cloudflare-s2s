import os
import json
import logging


logger = logging.getLogger(__name__)



def get_route_to(addr:str) -> str:
    return __call_command("ip --json route get {addr}")

def get_interfaces() -> str:
    return __call_command("ip  -j -br address")
   

def __call_command(cmd:str) -> dict:
    ''' calls the command line commands and returns the output'''
    logger.info(f"cmd: {cmd}")
    stream = os.popen(cmd)
    output = stream.read()
    logger.info(f"returned:\n{output}")
    return json.loads(output)
    

