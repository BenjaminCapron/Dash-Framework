import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc, callback_context, dash_table
import dash_bootstrap_components as dbc

import dash_admin_components as dac

from dash.exceptions import PreventUpdate

# =============================================================================
# Dash App and Flask Server
# =============================================================================
app = dash.Dash(__name__)
server = app.server 

#NEXT STEPS
'''
Generation auto output
'''

# Navbar                       
navbar = dac.Navbar(color = "white")

#ici liste de fonctions, ID = unique

def sum(a:int, b:int):
    return a+b

def multiply(a:int, b:int):
    return a*b

function_list = [
    {'id':'1', 'label':'Maths', 'tier':'0'},
    {'id':'2', 'label':'Sum', 'function':sum, 'icon':'', 'tier':'1', 'active':'yes'},
    {'id':'3', 'label':'Multiply', 'function':multiply, 'icon':'', 'tier':'1', 'active':'yes'},  
    {'id':'__last__', 'label':'', 'function':'', 'icon':'', 'tier':'0'},
]


#TAB ID LIST
tab_id_list = []
button_id_list = []
tab_id_list_input = []
tab_id_list_output = []
content_id_list = []
button_id_list_output = []
query_id_list = []
function_id_list = []
for function in function_list:
    if (function['tier'] == '1' or function['tier'] == '3') and function['active']=='yes':
        tab_id_list.append("tab_"+function["id"])
        button_id_list.append("button_"+function["id"])
        tab_id_list_input.append(Input("tab_"+function["id"], 'n_clicks'))
        tab_id_list_output.append(Output("tab_"+function["id"], 'active'))
        content_id_list.append(Output("content_"+function["id"], 'active'))
        button_id_list_output.append(Input("button_"+function['id'], 'n_clicks'))
        query_id_list.append(Output("query_"+function['id'], 'children'))
        function_id_list.append(function['function'])

#Construction de la sidebar
SidebarMenuItem_function_list = []
parent_children = []
previous_tier = None
for function in function_list:
    if previous_tier=='3' and function['tier']!='3':
        SidebarMenuItem_function_list += dac.SidebarMenuItem(label=parent_label, icon=parent_icon, children=parent_children),
        parent_children = []
        previous_tier = None
    if function['tier']=='0':
        SidebarMenuItem_function_list += [dac.SidebarHeader(children=function['label'])]
    if function['tier']=='1':
        if function['active']=='yes':
            SidebarMenuItem_function_list += [dac.SidebarMenuItem(id="tab_"+function['id'], label=function['label'], icon=function['icon'])]
        else:
            SidebarMenuItem_function_list += [dac.SidebarMenuItem(id="tab_"+function['id'], label=function['label'], icon=function['icon'], badge_label='dev', badge_color='success')]
    if function['tier']=='2':
        parent_label = function['label']
        parent_icon = function['icon']
    if function['tier']=='3':
        if function['active']=='yes':
            parent_children += [dac.SidebarMenuItem(id="tab_"+function['id'], label=function['label'], icon=function['icon'])]
        else:
            parent_children += [dac.SidebarMenuItem(id="tab_"+function['id'], label=function['label'], icon=function['icon'], badge_label='dev', badge_color='success')]
        previous_tier = '3'
        #pas de trigger si 3 = last, d'où le __last__

# Sidebar
sidebar = dac.Sidebar(
	dac.SidebarMenu(SidebarMenuItem_function_list),
    title='Collectionapp',
	skin="dark",
    color="primary",
	brand_color="secondary",
    url="https://google.com",
    src="https://adminlte.io/themes/AdminLTE/dist/img/user2-160x160.jpg",
    elevation=3,
    opacity=0.8
)

# Body
import inspect
body_item = []
parameter_list_item = []
for function in function_list:
    if (function['tier'] == '1' or function['tier'] == '3') and function['active']=='yes':
        body_content = []
        parameter_list_content = []
        for parameter in inspect.signature(function['function']).parameters:
            current_parameter = inspect.signature(function['function']).parameters[parameter]
            label_parameter = str(current_parameter).split(" ")[0][:-1]
            type_parameter = str(current_parameter).split(" ")[1]
            if type_parameter == "str":
                body_content += [dbc.Input(id="input_"+label_parameter+"_"+function['id'], placeholder=label_parameter+" ("+type_parameter+")", type="text"), html.Br()]
            elif type_parameter == "int" or type_parameter == "float":
                body_content += [dbc.Input(id="input_"+label_parameter+"_"+function['id'], placeholder=label_parameter+" ("+type_parameter+")", type="number"), html.Br()]
            else:
                body_content += [dbc.Input(id="input_"+label_parameter+"_"+function['id'], placeholder=label_parameter+" ("+type_parameter+")", type="text"), html.Br()]
            #if type = bool ?
            parameter_list_content.append(State("input_"+label_parameter+"_"+function['id'], 'value'))
        tab_id_list_input.append(Input("tab_"+function["id"], 'n_clicks'))
        body_content += [dbc.Button("Query", color="primary", id="button_"+function['id'])]
        body_content += [html.Div(id="query_"+function['id'])]
        body_item += [dac.TabItem(html.Div(body_content), id="content_"+function['id'])]
        parameter_list_item += [parameter_list_content]

body = dac.Body(
    dac.TabItems(body_item)
)

# Controlbar
controlbar = dac.Controlbar(
    [
        html.Br(),
        html.P("Slide to change graph in Basic Boxes"),
        dcc.Slider(
            id='controlbar-slider',
            min=10,
            max=50,
            step=1,
            value=20
        )
    ],
    title = "My right sidebar",
    skin = "light"
)

# Footer
footer = dac.Footer(
	html.A("@Benjamin Capron",
		href = "https://google.com", 
		target = "_blank", 
	),
)

# =============================================================================
# App Layout
# =============================================================================
app.layout = dac.Page([navbar, sidebar, body, controlbar, footer])

# =============================================================================
# Callbacks
# =============================================================================
#Init output list pour conserver entre les tab
output_list = [None]*len(tab_id_list)
#None dans arg provoque pbs

def activate_output(input_id, *args):
    current_id = button_id_list.index(input_id)
    current_function = function_id_list[current_id](*args[len(tab_id_list)+int(current_id)])
    output_list[current_id] = [dcc.Markdown(str(current_function))]
    return output_list

@app.callback(query_id_list, button_id_list_output, parameter_list_item)
def display_tab(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]   
    return activate_output(input_id, *args)

def activate(input_id, *args):
    activate_list = [False]*len(tab_id_list)
    activate_list[tab_id_list.index(input_id)]=True
    return activate_list

@app.callback(content_id_list, tab_id_list_input)
def display_tab(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]   
    return activate(input_id, *args)

@app.callback(tab_id_list_output, tab_id_list_input)
def activate_tab(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]   
    return activate(input_id, *args)
# =============================================================================
# Run app    
# =============================================================================
if __name__ == '__main__':
    app.run_server(debug=True)
