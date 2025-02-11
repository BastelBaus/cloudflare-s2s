import header
import footer
import components.api
import components.home_content
import components.controls_content
import components.data_content
import sys
import os

from nicegui import app, ui

import logging
logger = logging.getLogger(__name__)

#logging.basicConfig(
#    level=logging.INFO,
#    format="frontend %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
#    stream=sys.stdout)

import pathlib
CUR_DIR = pathlib.Path(__file__).parent.resolve()

_DEFAULT_WEB_PORT = 8080
appName = "cloudflare-s2s"
appVersion = "0.1"

if  'WEBUI_PORT' in os.environ.keys():
      appPort = int(os.environ['WEBUI_PORT'])
else: appPort = _DEFAULT_WEB_PORT

print(f'\n\n{CUR_DIR}/assets\n\n')
app.add_static_files("/assets",f'{CUR_DIR}/assets')

# Nice starter: https://github.com/frycodelab/nicegui-component-based/tree/main


@ui.page('/')
def index():


    ui.colors(primary='#28323C', secondary="#B4C3AA", positive='#53B689', accent='#111B1E')
    #ui.add_head_html("<style>" + open(Path(__file__).parent / "assets" / "css" / "global-css.css").read() + "</style>")

    with header.frame(title=appName, version=appVersion):

        with ui.header().classes(replace='row items-center').style('background-color:white; border-bottom: 1px solid #D4D6D8;') as header_below:
            with ui.column().classes('w-full items-center'):

                with ui.tabs().props("active-color=blue-grey-14 active-bg-color=white") as tabs1:
                    
                    with ui.row():

                        with ui.tab("tab_1", label="").style('color: black; font-family: "Rational Display", sans-serif;').props("no-caps") as tab_three:
                            ui.icon("o_home").classes('text-3xl')
                            ui.label("Home")

                        with ui.tab("tab_2", label="").style('color: black; font-family: "Rational Display", sans-serif;').props("no-caps") as tab_one:
                            ui.icon("tune").classes('text-3xl')
                            ui.label("Controls")

                        with ui.tab("tab_3", label="").style('color: black; font-family: "Rational Display", sans-serif;').props("no-caps") as tab_two:
                            ui.icon("o_analytics").classes('text-3xl')
                            ui.label("Data")

                        with ui.tab("tab_4", label="").style('color: black; font-family: "Rational Display", sans-serif;').props("no-caps") as tab_two:
                            ui.icon("thumb_up").classes('text-3xl')
                            ui.label("API")


        with ui.tab_panels(tabs1, value='tab_1').classes('w-full') as tab_panel:

                with ui.tab_panel('tab_1').style('font-family: "Rational Display", sans-serif;'):
                    components.home_content.content()
                    
                with ui.tab_panel('tab_2').style('font-family: "Rational Display", sans-serif;'):
                    
                    components.controls_content.content()
                    
                with ui.tab_panel('tab_3').style('font-family: "Rational Display", sans-serif;'):
                    components.data_content.content()

                with ui.tab_panel('tab_4').style('font-family: "Rational Display", sans-serif;'):
                    components.api.content()
                                        
        header_below.tailwind("pt-16")
        tab_panel.tailwind("pt-16 pl-16 pr-16")

        footer.frame(title=appName, version=appVersion)

def handle_shutdown():
    logger.info(f"Ending cloudflare-s2s frontend server ")

app.on_shutdown(handle_shutdown)



#ui.run(storage_secret="myStorageSecret",title=appName,port=appPort,favicon="/assets/images/favicon.ico") 
ui.run(storage_secret="myStorageSecret",title=appName,port=appPort,favicon="🚀") 


if __name__=="__main__":
    logger.info("\n------------------------------------------------")
    logger.info(f"Starting cloudflare-s2s frontend server @ port:{appPort}")


