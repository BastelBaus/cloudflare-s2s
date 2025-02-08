
import os
import asyncio
import subprocess
import queue    
import threading
import time
import uuid
import json


class warp_cli:
	
    
    #################################################################
    # Initialization and general functions
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
        
    def get_status(self):
        #return self.__call_cloudflared('--accept-tos --json status')
        return self.__call_cloudflared('status')

    def registration_delete(self):
        return self.__call_cloudflared('registration delete')

    def disconnect(self):
        return self.__call_cloudflared('disconnect')

    def connect(self):
        return self.__call_cloudflared('connect')        
        
    def new_connector(self,tunnel_token:str|None=None):
        ''' a (new) tunnel token can optionally be passed. 
            If so, this is stored as new tunnel_token
            If not, it the current tunnel token is used
        '''
        if not tunnel_token is None:
            self.tunnel_token = tunnel_token            
        return self.__call_cloudflared(f'connector new {self.tunnel_token}')        

    def show_registration(self):
        return self.__call_cloudflared('registration show')            
    
    def delete_registration(self):
        return self.__call_cloudflared('registration delete')            
    
    def show_organization(self):
        return self.__call_cloudflared('registration organization')            
    
    def settings(self):
        return self.__call_cloudflared('settings')            
        
    def debug_network(self):
        return self.__call_cloudflared('debug network')            

    def debug_dex(self):
        return self.__call_cloudflared('debug dex')            
        
    #################################################################
    # Private functions to handle the communication over the shell
    #################################################################

    def __call_cloudflared(self,argument:str) -> str:
        ''' calls cloudflared with given arguments and returns the output as string '''
        #cmd = f"warp-cli {argument}"
        cmd = f"warp-cli -j --accept-tos {argument}"
        print(f"call: {cmd}")
        stream = os.popen(cmd)
        output = stream.read()
        print(f"returned:\n{output}")
        return output

    def __call_cloudflared_async(self,argument:str) -> None :
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
 # If called as module, perform a simple test run
 #################################################################       

if __name__ == "__main__":
    pass
    
    

