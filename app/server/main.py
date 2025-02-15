
# hello.py

from flask import Flask, request 
import os
import sys
import logging
import json


from cloudflare import warp_cli
from wireguard import wireguard
import network

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="backend %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
    stream=sys.stdout)


#logger.error("error !!! ")
#logger.warn("warn !!! ")
#logger.info("info !!! ")
#logger.debug("debug !!! ")
#logging.basicConfig(level=logging.DEBUG)

_BUILD_DATE_FILE = "/build-date.txt"
_VERSION = "0.1"

if 'API_PORT' in os.environ.keys():
      api_port = int(os.environ['API_PORT'])
else: api_port = '15651'

tunnel_token = os.environ['TUNNEL_TOKEN']

warpcli = warp_cli(tunnel_token)
wg = wireguard()

logger.info("\n------------------------------------------------")
logger.info(f"starting backend server at port:{api_port}")
logger.info(f"tunnel_token: {tunnel_token}")

app = Flask(__name__)



###########################################################
# general things
###########################################################

@app.get("/")
def main() -> str:    
    ret_str = '<html><body>Welcome to bastelbaus cloudflared-s2s!<br>Link to a list of access points: <a href="/api/html">api</a></body></html>'
    return ret_str 

def get_api_list() -> list:
    list_of_aps =  ['%s' % rule for rule in app.url_map.iter_rules()]
    list_of_aps.pop(0) # remove the static paths
    return list_of_aps

@app.get('/api')
def api() -> str:
    return json.dumps(get_api_list())

@app.get('/api/html')
def api_html() -> str:
    list_of_aps = [f'<a href="http://localhost:{api_port}{ap}"> {ap} </a>' for ap in get_api_list()]
    str_of_aps  = "<br>\n".join(list_of_aps)
    return str_of_aps + "<br>\n"


@app.get("/version")
def version() -> str:    
    return json.dumps({ "version":_VERSION })

@app.get("/builddate")
def builddate() -> str:    
    with open(_BUILD_DATE_FILE, "r") as file:
        ret_str = file.read().strip()
    return json.dumps({ "builddate":ret_str })



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

@app.get('/warp/connector/get')
def get_connector() -> str:
    return {"token":warpcli.tunnel_token } 

@app.get('/warp/connector/new')
def new_connector() -> str:
    tunnel_token = request.args.get('tunnel_token')
    logger.info(f"Tunnel token form intertface: {tunnel_token}") 
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

@app.get('/warp/interface/ip')
def interface_ip() -> str:
    return { 'myip':warpcli.get_interface_ip()}
    
@app.get('/warp/interface/mysubnet')
def interface_mysubnet() -> str:
    return { 'mysubnet': warpcli.estimate_own_subnet() }
 
 
@app.get('/warp/search_backends')
def warp_search_backends():    
    return network.check_open_ports()


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
    return network.get_interfaces()



