from nicegui import ui, app

from config import cfg

import requests
#response.json()

#@ui.refreshable
#def api_call_result(x:str) -> None:
#    ui.label("label: "+x)
    
#def call_api(api, id) -> None:
#    ui.label(f"{api} --> {id}")
#    pass

#@ui.refreshable
#def counter(name: str):
#    with ui.card():
#        count, set_count = ui.state(0)
#        color, set_color = ui.state('black')
#        ui.label(f'{name} = {count}').classes(f'text-{color}')
#        ui.button(f'{name} += 1', on_click=lambda: set_count(count + 1))
#        ui.select(['black', 'red', 'green', 'blue'],
#                  value=color, on_change=lambda e: set_color(e.value))

#with ui.row():
#    counter('A')
#    counter('B')

def do_api_call(api,set_result):
    x = requests.get(api)
    set_result(x.text)

@ui.refreshable
def api_call(api: str):
    with ui.card():
        result, set_result = ui.state('none')
        ui.button(f'{api}', on_click=lambda: do_api_call(api,set_result))
        ui.label(f'{result}')



def content() -> None:

    #ui.select(['black', 'red', 'green', 'blue'],
    #          value=color, on_change=lambda e: set_color(e.value))

    with ui.card().classes('w-full'):

        #with ui.row():
        #    ui.icon("o_info").classes('text-xl')

        #ui.label("Welcome!").style('color: black; font-family: "Rational Display", sans-serif; font-size:28px;')

        #ui.label("This App is build based on the NiceGUI framework - modified and adapted for easyier modularized use.").style('color: black; font-family: "Rational Display", sans-serif; font-size:18px;')

        #ui.link('http://localhost:15650/api','http://localhost:15650/api')

        base_url = "http://localhost:15650/"
        base_url = "http://192.168.0.23:15651/"
        api_url = base_url + "api"
        response = requests.get(api_url)
        for api_point in response.json():
            with ui.row():
                api = base_url+api_point
                api_call(api)
                #with ui.column():
                    #ui.label(api)
                    #api_call_result("none")
#                    ui.button(api, on_click=lambda x=api: call_api(x))
                    #button = ui.button(api)
                    #label = ui.label(f"None")
                    #button. .on_click(lambda x=api: call_api(api, label.id))
                    #ui.label(f"{api} -> {x.status_code} : {x.text} ")


#@ui.refreshable
#def number_ui() -> None:
 #   ui.label(', '.join(str(n) for n in sorted(numbers)))

#def add_number() -> None:
    #numbers.append(random.randint(0, 100))
#    number_ui.refresh()
#
#number_ui()
