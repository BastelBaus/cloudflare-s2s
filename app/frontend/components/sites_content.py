from nicegui import ui, app, run
import logging

from frontend.config import FrontendConfig
from frontend import defaults

from .. import api


logger = logging.getLogger(__name__)



@ui.refreshable
def warp_status(site_api) -> None:
    warp_status = site_api.get_warp_status()
    ui.label(f"Warp Status X: {warp_status}")

###########################################################################################
# the site handler
###########################################################################################

class siteHandler:

    def __init__(self,site,cfg):
        self.cfg  = cfg # the config storage elememnt
        self.site = site # the site config element
        self.name = site["name"]
        self.set_api_addr( site["address"] )     

        self.connection_state    = False
        self.warp_conn_state     = "Unchecked"

        self._set_site_connection_state(self.connection_state)
        self._set_warp_connection_state(self.warp_conn_state )

        ui.timer(defaults.SERVER_CHECK_TIME , lambda: self.check_connection() )
        ui.timer(defaults.WARP_CHECK_TIME, lambda: self.check_warp_connection() )

    def set_api_addr(self,api_addr):
        self.address = api_addr
        self.api = api.site( self.address )     

    #######################################################################################

  
    def check_connection(self):
        ''' checks connection states and updates the icon and texts '''

        current_state =  self.api.is_connected()
        if self.connection_state == current_state: return
        self.connection_state = current_state
        self._set_site_connection_state(current_state)

        current_warp_conn_state = self.api.get_warp_status()
        if self.warp_conn_state == current_warp_conn_state: return
        self.warp_conn_state = current_warp_conn_state
        self._set_warp_connection_state(current_warp_conn_state)


    def _set_site_connection_state(self,connected:bool) -> None:
        ''' sets all site connection state icons and texts'''
        
        logger.info(f"Set site connection state: {connected} !!")

        if connected: # if true, we changed from not connected to connected
            version    = self.api.get_version()
            builddate  = self.api.get_builddate()
            token      = self.api.get_connector()
            site_name  = self.api.get_site_name()
            self.site_name           = site_name
            self.site_connected_icon = "cloud_done"
            self.server_info         = "Version: v"+ version + " Build:" + builddate
            self.connection_tooltip  = f"Status of server connection, checked every {defaults.SERVER_CHECK_TIME} seconds<br>" \
                                       f"&nbsp;&nbsp;<b>connected</b><br>" \
                                       f"&nbsp;&nbsp;Version: v{version}<br>" \
                                       f"&nbsp;&nbsp;Build:   {builddate}"
            self.warp_visible        = True
            self.warp_token          = token

        else: # we change from connected to not connected
            self.site_name           = "unknown"
            self.site_connected_icon = "cloud_off"
            self.server_info         = "unkown"
            self.connection_tooltip  = f"Status of server connection, checked every {defaults.SERVER_CHECK_TIME} seconds"
            self.warp_visible        = False # only visible when connected
            self.warp_token          = "unknown"

    def check_warp_connection(self):
        if not self.connection_state:
            status = "Unchecked"
            self._set_warp_connection_state(status)
        else:             
            status = self.api.get_warp_status()
            if not status: status = "Unchecked"
            if self.warp_conn_state == status: return #FIXME: we might update the warp information as well, especiily if the first check did not work !
            self.warp_conn_state = status
            self._set_warp_connection_state(status)

    def _set_warp_info(self) -> str:
        info = self.api.warp_register_show()
        if not isinstance(info,dict): return f"Error: {info}"
        mysubnet  = self.api.warp_my_subnet()
        nat_target_subnet =  self.api.nat_get_target()
        nat_target_subnet = nat_target_subnet['target'] if 'target' in nat_target_subnet.keys() else nat_target_subnet
        myip      = self.api.warp_my_ip()
        vnets     = self.api.warp_get_vnets()
        docker_if = self.api.docker_interfaces()
        str1 = f'account ({info["account"]["type"]}): {info["account"]["organization"]} (id: {info["account"]["id"]})<br>' 
        str2 = f'my warp IP: {myip["myip"]}<br>'        
        str3 = f'my warp subnet: {mysubnet["mysubnet"]}'
        str3 += f' => natting to {nat_target_subnet}<br>'        
            # TODO: only when not empty, chaneg field add tooltip !
            #self.api.nat_set_target(self,target:str) 
            # TODO: make subnet editable to change manually
            # TODO validate subnet

        str4 = f'virtual networks: <br><ul>'      
        # {'active_vnet_id': 'b3dc53bd-febe-45f7-8b65-9ccc2450990b', 'virtual_networks': [{'default': False, 'description': 'tunnel between my sites', 'id': '26e0a6d2-0cea-42c0-b587-a37de3d51cf5', 'name': 'cloudflare-s2s'}, {'default': True, 'description': 'This network was autogenerated because this account lacked a default one', 'id': 'b3dc53bd-febe-45f7-8b65-9ccc2450990b', 'name': 'default'}]}
        for v in vnets["virtual_networks"]:
            str4 += "\n<li>&nbsp;&nbsp; "
            active = vnets["active_vnet_id"] == v["id"]
            if active: str4 += "active: "
            str4 += f'{v["name"]} ({v["description"]})'    
            if v["description"]: str4 += " [default network]"
            str4 += "</li>\n"        
        str4 += "</ul>\n"

        str5 = f'docker_if:<br><ul>'        
        # [{'addr_info': [{'local': '127.0.0.1', 'prefixlen': 8}], 'ifname': 'lo', 'operstate': 'UNKNOWN'}, {'addr_info': [{'local': '100.96.0.10', 'prefixlen': 32}], 'ifname': 'CloudflareWARP', 'operstate': 'UNKNOWN'}, {'addr_info': [{'local': '172.18.0.2', 'prefixlen': 16}], 'ifname': 'eth0', 'link_index': 111, 'operstate': 'UP'}, {'addr_info': [{'local': '192.168.0.25', 'prefixlen': 24}], 'ifname': 'eth1', 'link_index': 3, 'operstate': 'UP'}]
        for interface in docker_if:
            str5 += "\n<li>&nbsp;&nbsp; "
            str5 += f'{interface["ifname"]} ({interface["operstate"]}): '
            for i,addr in enumerate(interface['addr_info']):
                if i>0: str5 += ", "
                str5 += f"{addr['local']}/{addr['prefixlen']}"
            str5 += "</li>\n"
        str5 += f'</ul>\n'        
        
        return str1 + str2 + str3 + str4 + str5
    

    def _set_warp_connection_state(self,state:str) -> None:
        ''' sets all warp connection state icons and texts'''
        logger.info(f"Set warp connection state: {state} !!")

        self.warp_tooltip          =  f"Status of warp connection, checked every {defaults.WARP_CHECK_TIME} seconds"

        # TODO: need state "registering" to wait until registering is complete

        if state == "Connected": # if true, we changed from not connected to connected
            self.warp_connected        = True
            self.warp_registered       = True
            self.warp_connected_icon   = "link"
            self.warp_register_button  = "unregister"
            self.warp_register_enable  = False
            self.warp_connect_button   = "disconnect"
            self.warp_connect_enable   = True
            self.warp_info             = self._set_warp_info()
            self.warp_network          = ""
            self.warp_backend_search   = True

        elif state == "Disconnected": 
            self.warp_connected        = False
            self.warp_registered       = True
            self.warp_connected_icon   = "link_off"
            self.warp_register_button  = "unregister"
            self.warp_register_enable  = True
            self.warp_connect_button   = "connect"
            self.warp_connect_enable   = True
            self.warp_info             = ""
            self.warp_network          = ""
            self.warp_backend_search   = False

        elif state == "Connecting": 
            self.warp_connected        = False
            self.warp_registered       = True
            self.warp_connected_icon   = "link_off"
            self.warp_register_button  = "unregister"
            self.warp_register_enable  = False
            self.warp_connect_button   = "connecting"
            self.warp_connect_enable   = False
            self.warp_info             = ""
            self.warp_network          = ""
            self.warp_backend_search   = False

        elif state == "Unregistered": 
            self.warp_connected        = False
            self.warp_registered       = False
            self.warp_connected_icon   = "app_registration"
            self.warp_register_button  = "register"
            self.warp_register_enable  = True
            self.warp_connect_button   = "connect"
            self.warp_connect_enable   = False
            self.warp_info             = ""
            self.warp_network          = ""
            self.warp_backend_search   = False

        elif state=="Unchecked": 
            self.warp_connected        = False
            self.warp_registered       = False
            self.warp_connected_icon   = "no_accounts"
            self.warp_register_button  = "unknown"
            self.warp_register_enable  = False
            self.warp_connect_button   = "unknown"
            self.warp_connect_enable   = False
            self.warp_info             = ""
            self.warp_network          = ""
            self.warp_backend_search   = False

        elif state=="Failure": 
            self.warp_connected        = False
            self.warp_registered       = False
            self.warp_connected_icon   = "error"
            self.warp_register_button  = "unknown"
            self.warp_register_enable  = False
            self.warp_connect_button   = "unknown"
            self.warp_connect_enable   = False
            self.warp_info             = ""
            self.warp_network          = ""
            self.warp_backend_search   = False

        else: 
            self.warp_connected        = False
            self.warp_registered       = False
            self.warp_connected_icon   = "no_accounts"
            self.warp_register_button  = "unknown"
            self.warp_register_enable  = False
            self.warp_connect_button   = "unknown"
            self.warp_connect_enable   = False
            self.warp_info             = ""
            self.warp_network          = ""
            self.warp_backend_search   = False
            logger.warning(f"Should never end here when checking warp status (state: {state})!")
    #######################################################################################

    def site_name_changed(self,new_name):
        self.site["name"] = new_name
        self.cfg.store()
        self.name = new_name

    def site_addr_changed(self,event):
        new_addr = str(event.sender.value)
        logger.info(f"changed address from {self.address} to {new_addr}")
        self.site["address"] = new_addr
        self.cfg.store()
        self.set_api_addr( new_addr )  
        #self.check_connection() # if both sites are connected this would not refresh anything
        #content.refresh()

    def tunnel_token_changed(self,event):
        token = str(event.sender.value)
        self.site["token"] = token.strip()
        self.cfg.store()
        #sites[site_index].set_api_addr(new_addr.strip())
        
    def register_button(self):
        if self.warp_registered:
            status = self.api.warp_unregister()
        else:
            status = self.api.warp_register(self.site["token"])
        #print("Register Button",self.warp_registered,status)
        self.check_warp_connection()

    def connect_button(self):
        if self.warp_connected:
            status = self.api.warp_disconnect()
        else: 
            status = self.api.warp_connect()
        #print("Connect Button ",self.warp_connected,status)
        self.check_warp_connection()

    async def check_warp_backends(self):
        print("start search")
        self.warp_backend_search   = False
        #ui.timer(0.01, lambda: self._check_warp_backends() )
        await self._check_warp_backends() 

    async def _check_warp_backends(self):
        print("start timer search")
        result = await run.io_bound(self.api.warp_search_backends)
        logger.info(f"warp backends serach results: {result}")
        if result is None: str = "error occured"
        else:
            self.warp_backend_search   = True
            str =  "\n".join( [f" <li>&nbsp; &nbsp; {res['ip']} ({res['host']})</li>" for res in result] )
            str = f"Backends with open ports:<br><ul>{str}</ul>"
        self.warp_network = str
        ui.notify(f'Finished backend search: {str} ')
        
###########################################################################################
# here is the layout of the site
###########################################################################################

@ui.refreshable
def content() -> None:
    ''' the function doing the layout of the site'''

    cfg = FrontendConfig()
    #config.cfg.load() # reload the config file each time !

    sites = []
    for site in cfg.data['sites']:
        sites.append( siteHandler(site,cfg) )

    # delete a site
    with ui.dialog() as dialog, ui.card():
        ui.label('Are you sure to delete ?')
        with ui.row():
            ui.button('Yes', on_click=lambda: dialog.submit('Yes'))
            ui.button('No', on_click=lambda: dialog.submit('No'))
    async def show(i):
        result = await dialog
        #ui.notify(f'You chose {result} in dialog {i}')
        if result == 'Yes':
            del cfg.data['sites'][i]
            cfg.store()
            content.refresh()
            ui.notify(f'deleted')
        else: return

    # add a site
    def add_site():
        cfg.data['sites'].append({"name":"new site","address":"http://localhost:15651"}) # TODO: checnge default values
        cfg.store()
        content.refresh()
        ui.notify(f'site added')
            
        
    with ui.page_sticky(position="right"):
        ui.button('add site', on_click=add_site)
    for i,site in enumerate(sites):
        with ui.card().classes('center'):

            # handle the different inputrs
                
            with ui.row():
                # the site address and connection status
                with ui.input(  label='site address', value=site.address,
                                #on_change=lambda e,i=i: sites[i].site_addr_changed(e.value),
                                #validation={'Input too long': lambda value: len(value) < 40} # TODO: could have some fun with hostname validator :-)
                            ).on("blur",lambda e,i=i: sites[i].site_addr_changed(e)) \
                            .props("size=40") as ip_input:
                    with ip_input.add_slot('append'):
                        with ui.icon('cloud_off').bind_name_from(site,"site_connected_icon"): # color="#FF0000"
                            with ui.tooltip():
                                ui.html().bind_content_from(site,"connection_tooltip")

                # the site name
                ui.input(label='site name', value="unknown").props("size=40") \
                    .bind_value_from(site,'site_name')
                #ui.input(label='site name', value=site.name,
                    #on_change=lambda e,i=isite: site_name_changed(e.value,i),
                    #on_change=lambda e,i=i: sites[i].site_name_changed(e.value) ).props("size=40")

                # delete the site
                ui.button('delete', on_click=lambda i=i: show(i))

            ui.separator().classes('w-full')
            
            # the tunnel token and tunnel connection status
            with ui.row():
                with ui.input(label='connector (tunnel token)', value="",
                    #on_change=lambda e,i=i: sites[i].tunnel_token_changed(e.value)
                    )  \
                    .props("size=40") \
                    .on("blur",lambda e,i=i: sites[i].tunnel_token_changed(e)) \
                    .bind_value_from(site,"warp_token") \
                    .bind_visibility_from(site,"warp_visible") as warp_token:
                    with warp_token.add_slot('append'):
                        with ui.icon('cloud_off').bind_name_from(site,"warp_connected_icon"): # color="#FF0000"
                            with ui.tooltip():
                                ui.html().bind_content_from(site,"warp_tooltip")

                ui.button("register",on_click=lambda i=i: sites[i].register_button()) \
                    .bind_text_from(site,'warp_register_button') \
                    .bind_enabled_from(site,'warp_register_enable') \
                    .bind_visibility_from(site,"warp_visible")
                
                ui.button("connect",on_click=lambda i=i: sites[i].connect_button()) \
                    .bind_text_from(site,'warp_connect_button') \
                    .bind_enabled_from(site,'warp_connect_enable') \
                    .bind_visibility_from(site,"warp_visible")
            
            # add the warp status information            
            ui.html()   .bind_content_from(site,'warp_info') \
                        .bind_visibility_from(site,"warp_visible")

            with ui.button("seach backends",on_click=lambda i=i: sites[i].check_warp_backends()  ) \
                    .bind_visibility_from(site,"warp_visible") \
                    .bind_enabled_from(site,"warp_backend_search") :
                ui.tooltip("Note, this might take a while sincve the backend nmap's a large address range ")
            ui.html()   .bind_content_from(site,'warp_network') \


            # helper with some styles
            #.classes('bg-green')                
            # classes('text-xl')
            #.style('color: black; font-family: "Rational Display", sans-serif; font-size:28px;')
            #.style('color: black; font-family: "Rational Display", sans-serif; font-size:18px;')
