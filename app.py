
from flask import Flask, request

        
import influxdb_client
import pandas as pd
from pandas.core.frame import DataFrame
import dash
import dash_bootstrap_components as dbc
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px


bucket = "<INSERT>"
measurment = "<INSERT>"
field = "<INSERT>"


client = influxdb_client.InfluxDBClient.from_config_file("config.ini")
query_api = client.query_api()


server = Flask(__name__)
# Dashboard is built using plotly's dash package. This also includes bootstap styles from dash_bootstrap
app = app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)


# Main HTML / Bootstap structure for front end app
app.layout = dbc.Container(
    [
        dbc.Container([
        dcc.Store(id="store"),
        html.H1("Example_Dashboard"),
        html.Hr(),
        # Add your new tabs hear.
        dbc.Tabs(
            [
                dbc.Tab(label="Data Explorer", tab_id="data_explorer"),
            ],
            id="tabs",
            active_tab="data_explorer",
        ),
        html.Div(id="tab-content", className="p-4"),])
    ]
)


@app.callback(
    Output("tab-content", "children"),
    [Input("tabs", "active_tab"), Input("store", "data")],
)
def render_tab_content(active_tab, data):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
    """
    if active_tab and data is not None:
        if active_tab == "data_explorer":
            return dbc.Row(
                [
                dbc.Col( dbc.Card([dcc.Graph(figure=data["data_explorer"])],style={"width": "auto"}), md=8),
                ]
            )
    return "No tab selected"



@app.callback(Output("store", "data"), [Input("button", "n_clicks")])
def generate_graphs(n):
# Generate graphs based upon pandas data frame. 
   
    df = getData(bucket, measurment, field )
    data_explorer = px.line(df, x="_time", y="_value", title=measurment)

    ########

    # save figures in a dictionary for sending to the dcc.Store
    return {"data_explorer": data_explorer,
            }


def getData(bucket, measurment, field) -> DataFrame:
        query = open("../flux/graph.flux").read().format(bucket, measurment, field)
        result = query_api.query_data_frame(query)
        return result


if __name__ == '__main__':
  app.run_server(host='0.0.0.0', port=5000, debug=True)
        