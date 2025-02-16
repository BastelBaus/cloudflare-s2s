#
# The header which is shown above all
#
###############################################################################
# pylint: disable=logging-fstring-interpolation

from contextlib import contextmanager
from nicegui import ui
import logging

logger = logging.getLogger(__name__)

@contextmanager
def frame(title: str, version : str):
    """Custom page frame to share the same styling and behavior across all pages"""
    with ui.header().classes(replace='row items-center h-16') as header:
        ui.label("").tailwind("pr-6")
        #ui.image('assets/images/logo.png').classes("w-24")
        ui.label("").tailwind("px-0.5")

        ui.label(title).style('color: white; font-size: 125%;')\
            .tailwind("px-2.5 pl-4", "font-bold", "text-white-800")
        #ui.chip(version, color="grey").style("").props("outline")

        ui.space()

        def refresh():
            ui.run_javascript("location.reload();")
            logger.info('refreshed the gui')

        with ui.button(on_click= refresh).props("outline").style("margin-right:4px"):
            ui.icon("refresh", color="white")
            ui.tooltip("Reload application")

    yield
