import os
import asyncio
import subprocess
import queue    
import threading
import time
import uuid
import json


class cloudflared:
	
    DEFAULT_CERT_FILE = "/root/.cloudflared/cert.pem"
    
    #################################################################
    # Initialization and general functions
    #################################################################
    
    def __init__(self,use_uuid:str = None):
        ''' Intializes a new cloudflared instance. 
            If a uuid is given in use_uuid, uses this uuid certificate (if available)
        '''
        #create unique ID
        self.uuid = str(uuid.uuid4()) if use_uuid is None else use_uuid      
        self.queue = queue.Queue()
        self.async_proc  = None
        print(f"created cloudflare instance with uuid: {self.uuid}")
        
    def get_version(self) -> str:        
        ''' returns the current cloudflare app version  '''
        version = str(self.__call_cloudflared('version')).strip()        
        return version
        
    @property
    def certfile(self) -> str:
        ''' returns the path to the unique cert file '''
        return f"/root/.cloudflared/cert_{self.uuid}.pem"        
    
    def has_certificate(self) -> bool:        
        ''' Returns true if there is already a (valid) certificate, else False '''
        return os.path.exists(self.certfile)
        
    #################################################################
    # Authorizing the connection to a tunnel
    #################################################################
    
    
    def start_authorize(self, renew: bool = False) -> str:        
        ''' Starts the authorization progress and  returns a link to 
            the web-site which should be used to authorize access.
            
            To re-autohrize the renew flag muist be set to True. Else the 
            authorization is not started and an empty string is returned.
            
        '''

        # check if certificate already exists and should be overwritten
        if not renew and not self.has_certificate():
            print('Already a certificate available, use renew flag if you')
            return ""
        
        # remove any temp certificate
        if os.path.exists(cloudflared.DEFAULT_CERT_FILE): os.remove(cloudflared.DEFAULT_CERT_FILE)  
        #else: print("file did not exist")

        # call the login async
        self.__call_cloudflared_async('login')        
        
        # the third line is the line with the link
        for i in range(3): link = self.queue.get()
        return link
        
    def is_authorize_finished(self) -> bool:
        ''' return True if the authorization process is finished '''
        poll = self.async_proc.poll()
        finished = poll is not None
        return finished
  
  
    def abort_authorize(self):        
        raise NotImplementedError('')
    
    def check_authorize(self) -> bool:        
        ''' Check if authorisation was successfull and hanldes the certificates.
            Returns True if successfull            
        '''
        
        # is_authorize_finished
                
        while not self.queue.empty():
            lastline = self.queue.get()
            
        success = lastline.decode('ascii').strip() is cloudflared.DEFAULT_CERT_FILE
        
        #os.mkdir(directory_name)
        print(f"copy {cloudflared.DEFAULT_CERT_FILE} to {self.certfile}")
        os.rename(cloudflared.DEFAULT_CERT_FILE,self.certfile)
        
        #"~/.cloudflared/cert.pem"
        # TODO: copy to certificate folder + self.uid
        
        return success

    #################################################################
    # Creastion and deletion of tunnels
    #################################################################

    def create_tunnel(self):
        pass
    
    def delete_tunnel(self):
        pass
        
    #################################################################
    # Get informatio about tunnels
    #################################################################

    def tunnnels_list(self) -> list[hash]:        
        ''' returns a list of hash with all tunnels for this connector.
        '''
        if not self.has_certificate: 
            prtint('There is no cert file, cannot use tunnel')
            return []
        
        
        result = self.__call_cloudflared(f'tunnel --origincert {self.certfile} list -o json')    
        return json.loads(result)
        
    def tunnnel_connection_info(self,id:str) -> list[hash] | None:        
        ''' Returns a list of connectors with their connection info like version, source IP and so on. 
            If there are no connections, returns None
        '''
        
        if not self.has_certificate: 
            prtint('There is no cert file, cannot use tunnel')
            return []
        
        
        result = self.__call_cloudflared(f'tunnel --origincert {self.certfile} info -o json {id}')    
        return json.loads(result)
                
        
        
    #################################################################
    # Private functions to handle the communication over the shell
    #################################################################

    def __call_cloudflared(self,argument:str) -> str:
        ''' calls cloudflared with given arguments and returns the output as string '''
        print(f"call 'cloudflared {argument}'")
        stream = os.popen(f'cloudflared {argument}')
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
    print("executing cloudflared test")
    
    do_authorization = False
    uuid = None if do_authorization else "f8a3f3b0-cc4f-4825-baa2-0ff9e9ee3276" 
    
    cf = cloudflared(uuid)
    
    print ("version: ",cf.get_version() )
    
    if do_authorization: # do the authorization 
        link = cf.start_authorize()
        print("Use this authorize link:",link)    
        while not cf.is_authorize_finished():
            time.sleep(3)
            print("waiting")
        print("success:",cf.check_authorize())
    
    print("Are we authorized?:",cf.has_certificate())
    
    tunnel_info = cf.tunnnels_list()
    print("List Tunnels:",tunnel_info)
    
    for tunnel in tunnel_info:
        print("Details Tunnels:",cf.tunnnel_connection_info(tunnel['id']))
    
    print("finished cloudflared test")
    
    