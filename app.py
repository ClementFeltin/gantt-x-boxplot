import base64
import datetime
import io

import dash
import dash_auth
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table

import pandas as pd

from utils import proba_gantt, ws_to_df
from authentification import VALID_USERNAME_PASSWORD_PAIRS

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

app.layout = html.Div([
    html.Header("Gantt X Boxplot"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    dcc.Graph(id="Mygraph", figure={}),
    html.Footer("Made by Clément FELTIN. Contact : clement.feltin@rte-france")
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            # df = pd.read_excel(io.BytesIO(decoded))
            df = ws_to_df(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return df


@app.callback(Output('Mygraph', 'figure'), [
Input('upload-data', 'contents'),
Input('upload-data', 'filename'),
Input('upload-data', 'last_modified')
])
def update_graph(contents, filename, date):
    x = []
    y = []
    if contents:
        contents = contents[0]
        filename = filename[0]
        df = parse_contents(contents, filename, date[0])

        fig = proba_gantt(df)
        return fig
    else:
        return dash.no_update


if __name__ == '__main__':
    app.run_server(debug=True)