#
#
#
###############################################################################
# pylint: disable=logging-fstring-interpolation

from flask import Flask, request 
import os
import json


from .cloudflare import warp_cli
from .wireguard import wireguard
from . import network
from . import defaults
from . import config
    
import logging
logger = logging.getLogger(__name__)


def main() -> Flask:

    ###########################################################
    # loading environmental variables
    ###########################################################

    if 'API_PORT' in os.environ.keys():
        api_port = int(os.environ['API_PORT'])
    else: 
        api_port = defaults.API_PORT 
        logger.warning(f"no server port given in environment, defaulting to {api_port}")

    if 'SERVER_NAME' in os.environ.keys():
        server_name = os.environ['SERVER_NAME']
    else: 
        server_name = defaults.SERVER_NAME
        logger.warning(f"no server name given in environment, defaulting to {server_name}")

    if 'TUNNEL_TOKEN' in os.environ.keys():
        tunnel_token = os.environ['TUNNEL_TOKEN']
    else:
        tunnel_token = ""
        logger.info("no tunnel token given in environment.")

    if 'AUTO_CONNECT' in os.environ.keys():
        auto_connect = int(os.environ['AUTO_CONNECT']) == 1
    else:
        auto_connect = defaults.AUTOCONNECT
        logger.info(f"No info about auto connect given in environment, defaulting to {auto_connect}")

    ###########################################################
    # loading the data from the configuration file
    ###########################################################

    cfg = config.BackendConfig()

    if cfg.data["SERVER_NAME"] is not "":
        server_name =cfg.data["SERVER_NAME"]
        logger.info(f"Server name <{server_name}> from config file used")

    if cfg.data["TUNNEL_TOKEN"] is not "":  
        tunnel_token =cfg.data["TUNNEL_TOKEN"]
        logger.info(f"Tunnel token <{tunnel_token}> from config file used")


    warpcli = warp_cli(tunnel_token)
    wg = wireguard()


    ###########################################################
    # starting the api server
    ###########################################################

    if server_name is "": 
        server_name = defaults.SERVER_NAME
        logger.info(f"No server name given, defaulting to <{server_name}>")

    logger.info("\n------------------------------------------------")
    logger.info(f"Backend server: {server_name}")
    logger.info(f"starting backend  at port:{api_port}")
    logger.info(f"tunnel_token: {tunnel_token}")

    app = Flask(__name__)

    ###########################################################
    # api general things
    ###########################################################

    @app.get("/")
    def root() -> str:    
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

    @app.get("/name")
    def name() -> str:    
        return {'name': server_name }


    @app.get("/version")
    def version() -> str:    
        return json.dumps({ "version":defaults.VERSION })

    @app.get("/builddate")
    def builddate() -> str:    
        with open(defaults.BUILD_DATE_FILE, "r",encoding="utf-8") as file:
            ret_str = file.read().strip()
        return json.dumps({ "builddate":ret_str })



    ###########################################################
    # api cloudflare warp-cli 
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
        if not tunnel_token is None and tunnel_token is not "":
            logger.info(f"Tunnel token form intertface: {tunnel_token}")
            cfg.data["TUNNEL_TOKEN"] = tunnel_token
            cfg.store()
            return warpcli.new_connector(tunnel_token)
        logger.info(f"Tunnel token form intertface <{tunnel_token}> ignored")
        return { "error" : "no tunnel token given" }        

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
    # api the wireguard interface
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
    # api the general network
    ###########################################################

    @app.get('/net/interfaces')
    def get_interfaces():    
        return network.get_interfaces()

    ###########################################################
    # starting the app and the main interface classes
    ###########################################################


    if auto_connect:
        logger.info("Autoconnect on, try to register")
        logger.info("Autoconnect on, try to connect")

    return app