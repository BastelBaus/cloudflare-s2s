
import os
import subprocess
import queue    
import threading
import json
import logging

from . import network

logger = logging.getLogger(__name__)

class warp_cli:
    ''' interface to the warp-cli command line tool'''

    
    #################################################################
    # Initialization 
    #################################################################
    
    def __init__(self,tunnel_token : str|None = None):
        ''' Intializes a new cloudflared instance. 
            If a uuid is given in use_uuid, uses this uuid certificate (if available)
        '''

        self.tunnel_token = tunnel_token

        #create unique ID
        #self.uuid = str(uuid.uuid4()) if use_uuid is None else use_uuid      
        self.queue = queue.Queue()
        self.async_proc  = None
        #print(f"created cloudflare instance with uuid: {self.uuid}")
        
    #################################################################
    # Direct interface to the warp client
    #################################################################

    def get_status(self):
        #return self.__call_cloudflare('--accept-tos --json status')
        return self.__call_cloudflare('status')

    def registration_delete(self):
        return self.__call_cloudflare('registration delete')

    def disconnect(self):
        return self.__call_cloudflare('disconnect')

    def connect(self):
        return self.__call_cloudflare('connect')        
        
    def new_connector(self,tunnel_token:str|None=None):
        ''' a (new) tunnel token can optionally be passed. 
            If so, this is stored as new tunnel_token
            If not, it the current tunnel token is used
        '''
        if not tunnel_token is None:
            self.tunnel_token = tunnel_token            
        return self.__call_cloudflare(f'connector new {self.tunnel_token}')        

    def show_registration(self):
        return self.__call_cloudflare('registration show')            
    
    def delete_registration(self):
        return self.__call_cloudflare('registration delete')            
    
    def show_organization(self):
        return self.__call_cloudflare('registration organization')            
    
    def settings(self):
        return self.__call_cloudflare('settings')            
        
    def debug_network(self):
        return self.__call_cloudflare('debug network')            

    def debug_dex(self):
        return self.__call_cloudflare('debug dex')            

    def tunnel_ip(self):
        return self.__call_cloudflare('tunnel ip list')       

    def tunnel_stats(self):
        return self.__call_cloudflare('tunnel stats')       

    def vnet(self):
        return self.__call_cloudflare('vnet')       

    #################################################################
    # Private functions to handle the communication over the shell
    #################################################################

    def __call_cloudflare(self,argument:str) -> str:
        ''' calls cloudflared with given arguments and returns the output as string '''
        #cmd = f"warp-cli {argument}"
        cmd = f"warp-cli -j --accept-tos {argument}"
        logger.debug(f"cmd: {cmd}")
        stream = os.popen(cmd)
        output = stream.read()
        logger.debug(f"returned:\n{output}")
        if len(output)>0: return json.loads(output)
        else:             return {}

    def __call_cloudflare_async(self,argument:str) -> None :
        ''' calls cloudflared with given arguments and returns the output as string '''

        if self.async_proc is not None: raise ValueError('process not finished, stop it before ')
        
        print(f"call 'cloudflared {argument}' asynchroniously")
        self.async_proc = subprocess.Popen(['cloudflared',argument],stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t = threading.Thread(target=self.__output_reader, args=(self.async_proc ,))
        t.start()
        

    def __output_reader(self,proc):
        ''' reads the output from the console and stores each line in the queue '''
        for line in iter(proc.stdout.readline, b''):
            print('got line: {0}'.format(line.decode('utf-8')), end='')
            self.queue.put(line)


    #################################################################
    # Functions to get more information 
    #################################################################


    def estimate_own_subnet(self) -> str:
        ''' Try to estimate the subnet of the own adapter.
            ping all possible subnets and check for which subnet
            nftables did not use CloudflareWARP adapter.
        '''
        own_subnet = ''
        tunnels = self.tunnel_ip()
        logger.debug(f"Tunnels: {tunnels}")
        try:
            is_cloudflare = [0] * len(tunnels['routes'])
            for i,tunnel in enumerate(tunnels['routes']):
                logger.debug(f"{i} : {tunnel}")
                ip = tunnel['value'].split('/')[0]
                ip_parts = ip.split('.')
                ip_parts[3]= '1' # TODO: change to +1!
                ip = '.'.join(ip_parts)
                logger.debug(f"ip -->  {ip}")
                route_to = network.get_route_to(ip)
                logger.debug(f"route -->  {route_to}")
                dev = [a for a in route_to if a['dev']=='CloudflareWARP' ]
                if len(dev)>0: continue # this is cloudflare !
                own_subnet = tunnel['value']                
                # tunnel['description']
                break # there should be only one none cloudflare tunnel,
                
                # the the first non cloud flare!
                #own_subnet = route_to[0]["prefsrc"]
            # this is the subnet of this adapter

        except: # TODO, catch only specific exceptions !!
            pass
            
        return own_subnet


    def get_interface_ip(self) -> str:
        ''' returns the internal IP of the cloudflare interface as string. '''
        interfaces = network.get_interfaces()
        logger.debug(f"interfaces: {interfaces}")
        if not isinstance(interfaces,list): interfaces = [interfaces]
        try:
            ip = [a for a in interfaces if a['ifname']=='CloudflareWARP' ][0]['addr_info'][0]
            logger.debug(f"ip: {ip}")
            ip = ip['local'] + '/' + str(ip['prefixlen'])
            logger.debug(f"ip: {ip}")
        except:
            ip = ''
        return ip
        


    

    
    
    
    
 #################################################################
 # If called as module, perform a simple test run
 #################################################################       

if __name__ == "__main__":
    pass
    
    

