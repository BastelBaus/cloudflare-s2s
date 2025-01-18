import os

class wireguard:    

    def get_privatkey(self) -> str:
        return self.__call_command("wg genkey")
    
    def get_publickey(self,privatkey) -> str:
        return self.__call_command(f'echo "{privatkey}" | wg pubkey')
    

    def __call_command(self,cmd:str) -> str:
        ''' calls the command line commands and returns the output'''
        print(f"call: {cmd}")
        stream = os.popen(cmd)
        output = stream.read()
        print(f"returned:\n{output}")
        return output