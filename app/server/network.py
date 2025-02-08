import os

class network:    

    def get_interfaces(self) -> str:
        return self.__call_command("ip  -j -br address")
   

    def __call_command(self,cmd:str) -> str:
        ''' calls the command line commands and returns the output'''
        print(f"call: {cmd}")
        stream = os.popen(cmd)
        output = stream.read()
        print(f"returned:\n{output}")
        return output
     

