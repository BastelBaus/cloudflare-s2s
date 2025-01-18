
# hello.py

from flask import Flask, request 
import os
import logging

from cloudflared import warp_cli
from wireguard import wireguard

logger = logging.getLogger(__name__)

#logger.error("error !!! ")
#logger.warn("warn !!! ")
#logger.info("info !!! ")
#logger.debug("debug !!! ")
#logging.basicConfig(level=logging.DEBUG)



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
def main():
    return "Hello, World!"

def get_api_list():
    list_of_aps =  ['%s' % rule for rule in app.url_map.iter_rules()]
    list_of_aps.pop(0) # remove the static paths
    return list_of_aps

@app.get('/api')
def api():
    return get_api_list()
    
#flask --app ./server/main run -p $API_PORT &

@app.get('/api/html')
def api_html():
    list_of_aps = [f'<a href="http://localhost:{api_port}{ap}"> {ap} </a>' for ap in get_api_list()]
    str_of_aps  = "<br>\n".join(list_of_aps)
    return str_of_aps + "<br>\n"
#flask --app ./server/main run -p $API_PORT &

###########################################################
# cloudflare warp-cli
###########################################################

@app.get('/warp/status')
def get_incomes():
    return warpcli.get_status()

@app.get('/warp/connect')
def connect():
    return warpcli.connect()

@app.get('/warp/disconnect')
def disconnect():
    return warpcli.disconnect()

@app.get('/warp/connector/new')
def new_connector():
    tunnel_token = request.args.get('tunnel_token')
    logger.warn(f"{tunnel_token}") 
    return warpcli.new_connector(tunnel_token)

@app.get('/warp/registration/show')
def show_registration():    
    return warpcli.show_registration()

@app.get('/warp/registration/delete')
def delete_registration():    
    return warpcli.delete_registration()

@app.get('/warp/registration/organization')
def show_organization():    
    return warpcli.show_organization()

@app.get('/warp/settings')
def settings():    
    return warpcli.settings()



###########################################################
# The wireguard interface
###########################################################


@app.get('/wg/keys/private')
def get_privatkey():    
    return wg.get_privatkey()

@app.get('/wg/keys/public')
def get_publickey():    
    privatekey = request.args.get('privatekey')
    if privatekey is None: return None
    return wg.get_publickey( privatekey )
