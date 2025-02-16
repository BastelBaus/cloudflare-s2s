#
# The footer  which is shown above all
#
###############################################################################
# pylint: disable=logging-fstring-interpolation

from contextlib import contextmanager
from nicegui import ui

from . import defaults

@contextmanager
def frame(title: str, version : str) -> None:
    ui.add_head_html('<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />')

    with ui.footer().classes('w-full items-center'):
        ui.space()
        ui.html(f"""<p>Copyright &copy; 2025, All Right Reserved | <a href="{defaults.GITHUB_LINK}">BastelBaus</a></p>""")
        ui.space()

        # add hackaday

        with ui.button(on_click= lambda: ui.run_javascript(f"window.open('{defaults.HACKADAY_LINK}','_newtab')")).props("outline").style("margin-right:4px"):
            ui.image('assets/images/hackaday.png').classes('text-5xl')
            #ui.tooltip("bastelbaus @ hackaday")

        with ui.button(on_click= lambda: ui.run_javascript(f"window.open('{defaults.DOCKER_LINK}','_newtab')")).props("outline").style("margin-right:4px"):
            ui.image('assets/images/docker.png').classes('text-5xl')
            #ui.tooltip("Docker repo @bastelbaus")

        with ui.button(on_click= lambda: ui.run_javascript(f"window.open('{defaults.GITHUB_LINK}','_newtab')")).props("outline").style("margin-right:4px"):
            ui.image('assets/images/github-mark-white.png').classes('text-5xl')
            #ui.icon('/assets/images/github-mark-white.svg', color="white").classes('text-5xl')
            #ui.icon('eva-github', color="white").classes('text-5xl')
            #ui.tooltip("GitHub repo @bastelbaus")

        ui.space()

        # https://dash.cloudflare.com/