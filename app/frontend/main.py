#
#
#
###############################################################################
# pylint: disable=logging-fstring-interpolation

import os
import pathlib
from nicegui import app, ui
import logging

from . import header
from . import footer
from . import defaults

from .components import api_content
from .components import sites_content
from .components import home_content
from .components import controls_content
from .components import data_content


logger = logging.getLogger(__name__)



# Nice starter: https://github.com/frycodelab/nicegui-component-based/tree/main

@ui.page('/')
def index():

    ui.colors(primary='#28323C', secondary="#B4C3AA", positive='#53B689', accent='#111B1E')

    with header.frame(title=defaults.APP_NAME, version=defaults.VERSION):

        with ui.header().classes(replace='row items-center') \
            .style('background-color:white; border-bottom: 1px solid #D4D6D8;') as header_below:
            with ui.column().classes('w-full items-center'):

                with ui.tabs().props("active-color=blue-grey-14 active-bg-color=white") as tabs1:

                    # check database: https://fonts.google.com/icons
                    with ui.row():

                        with ui.tab("tab_sites", label="") \
                            .style('color: black; font-family: "Rational Display", sans-serif;') \
                            .props("no-caps"):
                            ui.icon("o_home").classes('text-3xl')
                            ui.label("sites")

                        with ui.tab("tab_1", label="") \
                            .style('color: black; font-family: "Rational Display", sans-serif;') \
                            .props("no-caps"):
                            ui.icon("o_home").classes('text-3xl')
                            ui.label("Home")

                        with ui.tab("tab_2", label="") \
                            .style('color: black; font-family: "Rational Display", sans-serif;') \
                            .props("no-caps"):
                            ui.icon("tune").classes('text-3xl')
                            ui.label("Controls")

                        with ui.tab("tab_3", label="") \
                            .style('color: black; font-family: "Rational Display", sans-serif;') \
                            .props("no-caps"):
                            ui.icon("o_analytics").classes('text-3xl')
                            ui.label("Data")

                        with ui.tab("tab_4", label="") \
                            .style('color: black; font-family: "Rational Display", sans-serif;') \
                            .props("no-caps"):
                            ui.icon("thumb_up").classes('text-3xl')
                            ui.label("API")



        with ui.tab_panels(tabs1, value='tab_sites').classes('w-full') as tab_panel:

            with ui.tab_panel('tab_1').style('font-family: "Rational Display", sans-serif;'):
                home_content.content()

            with ui.tab_panel('tab_2').style('font-family: "Rational Display", sans-serif;'):
                controls_content.content()

            with ui.tab_panel('tab_3').style('font-family: "Rational Display", sans-serif;'):
                data_content.content()

            with ui.tab_panel('tab_4').style('font-family: "Rational Display", sans-serif;'):
                api_content.content()

            with ui.tab_panel('tab_sites').style('font-family: "Rational Display", sans-serif;'):
                sites_content.content()


        header_below.tailwind("pt-16")
        tab_panel.tailwind("pt-16 pl-16 pr-16")

        footer.frame(title=defaults.APP_NAME, version=defaults.VERSION)

def handle_shutdown() -> None:
    ''' function called when app is shut down '''
    logger.info("Ending cloudflare-s2s frontend server ")


if  'WEBUI_PORT' in os.environ.keys(): # pylint: disable=consider-iterating-dictionary
    app_port = int(os.environ['WEBUI_PORT'])
else:
    app_port = defaults.WEB_PORT

#TODO: make this favicon working
#ui.run(storage_secret="myStorageSecret",title=appName,port=appPort,favicon="/assets/images/favicon.ico") 
ui.run(storage_secret="myStorageSecret",title=defaults.APP_NAME,port=app_port,favicon="🚀")

def main() -> None:
    app.on_shutdown(handle_shutdown)
    logger.info("\n------------------------------------------------")
    logger.info(f"Starting cloudflare-s2s frontend server @ port:{app_port}")

    CUR_DIR = pathlib.Path(__file__).parent.resolve()
    app.add_static_files("/assets",f'{CUR_DIR}/assets')
