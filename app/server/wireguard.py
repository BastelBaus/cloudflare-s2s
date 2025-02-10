import os


WG_IF = "wg0"

class wireguard:    

    def get_privatkey(self) -> str:
        return self.__call_command("wg genkey").strip()
    
    def get_publickey(self,privatkey) -> str:
        return self.__call_command(f'echo "{privatkey}" | wg pubkey').strip()
    
#    f"wg showconf {WG_IF0}"

 #       wg set wg0 listen-port 51821


    def __call_command(self,cmd:str) -> str:
        ''' calls the command line commands and returns the output'''
        print(f"call: {cmd}")
        stream = os.popen(cmd)
        output = stream.read()
        print(f"returned:\n{output}")
        return output