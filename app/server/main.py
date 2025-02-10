
# hello.py

from flask import Flask, request 
import os
import logging
import json


from cloudflared import warp_cli
from wireguard import wireguard
import network

logger = logging.getLogger(__name__)

#logger.error("error !!! ")
#logger.warn("warn !!! ")
#logger.info("info !!! ")
#logger.debug("debug !!! ")
#logging.basicConfig(level=logging.DEBUG)

_BUILD_DATE_FILE = "/build-date.txt"
_VERSION = "0.1"

api_port = os.environ['API_PORT']
webui_port = os.environ['WEBUI_PORT']
tunnel_token = os.environ['TUNNEL_TOKEN']

print(f"{api_port=}")
print(f"{webui_port=}")
print(f"{tunnel_token=}")


warpcli = warp_cli(tunnel_token)
wg = wireguard()


app = Flask(__name__)

###########################################################
# general  things
###########################################################

@app.get("/")
def main() -> str:    
    ret_str = 'Welcome to bastelbaus cloudflared-s2s!\nlink to <a href="/api">api</s> '
    return ret_str 

def get_api_list() -> str:
    list_of_aps =  ['%s' % rule for rule in app.url_map.iter_rules()]
    list_of_aps.pop(0) # remove the static paths
    return list_of_aps

@app.get('/api')
def api() -> str:
    return get_api_list()
    
#flask --app ./server/main run -p $API_PORT &

@app.get('/api/html')
def api_html() -> str:
    list_of_aps = [f'<a href="http://localhost:{api_port}{ap}"> {ap} </a>' for ap in get_api_list()]
    str_of_aps  = "<br>\n".join(list_of_aps)
    return str_of_aps + "<br>\n"


@app.get("/version")
def version() -> str:    
    return _VERSION

@app.get("/builddate")
def builddate() -> str:    
    with open(_BUILD_DATE_FILE, "r") as file:
        ret_str = file.read()
    return ret_str



###########################################################
# cloudflare warp-cli 
###########################################################

@app.get('/warp/status')
def get_incomes() -> str:
    return warpcli.get_status()

@app.get('/warp/connect')
def connect() -> str:
    return warpcli.connect()

@app.get('/warp/disconnect')
def disconnect() -> str:
    return warpcli.disconnect()


@app.get('/warp/connector/new')
def new_connector() -> str:
    tunnel_token = request.args.get('tunnel_token')
    logger.warn(f"{tunnel_token}") 
    return warpcli.new_connector(tunnel_token)

@app.get('/warp/registration/show')
def show_registration() -> str:
    return warpcli.show_registration()

@app.get('/warp/registration/delete')
def delete_registration() -> str:
    return warpcli.delete_registration()

@app.get('/warp/registration/organization')
def show_organization() -> str:
    return warpcli.show_organization()

@app.get('/warp/settings')
def settings() -> str:
    return warpcli.settings()

@app.get('/warp/debug/network')
def debug_network() -> str: 
    return warpcli.debug_network()

@app.get('/warp/debug/dex')
def debug_dex() -> str:
    return warpcli.debug_dex()


@app.get('/warp/tunnel/ip')
def tunnel_ip() -> str:
    return warpcli.tunnel_ip()

@app.get('/warp/tunnel/stats')
def tunnel_stats() -> str:
    return warpcli.tunnel_stats()

@app.get('/warp/vnet')
def vnet() -> str:
    return warpcli.vnet()

    

###########################################################
# The wireguard interface
###########################################################


@app.get('/wg/keys/private')
def get_privatkey():    
    return { "status":"success", "privatekey":wg.get_privatkey()}
    
@app.get('/wg/keys/public')
def get_publickey():    
    privatekey = request.args.get('privatekey')
    if privatekey is None: return {"status":"error","reason":"no private key given"}
    return { "status":"success", "publickey":wg.get_publickey( privatekey ), "privatekey":privatekey}
    

###########################################################
# The general network
###########################################################



@app.get('/net/interfaces')
def get_interfaces():    
    #y = json.loads(x)
    return network.get_interfaces()



