import pandas as pd 
import numpy as np 
import os
from datetime import datetime

# plotly/dash components
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import sl as serviceLayer
import utils.url as url

# css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app
dash_app = dash.Dash(external_stylesheets=external_stylesheets)
app = dash_app.server

# load data
sl = serviceLayer.Covid19SL()
data = sl.data
df_jhu, df_nytimes_county, df_covidtracking_country, df_covidtracking_state, df_dxy_region, df_dxy_Country = sl.getIndividualData(data)

metrics = sl.getMetrics()

# dash_app layout
dash_app.layout = html.Div([
    html.Div([
        dcc.Dropdown(
            id = 'filter-country',
            options = [
                {'label': i, 'value': i} for i in sl.getListOfCountries(df_jhu)
            ],
            style = {'min-width': '30%', 'display': 'inline-block'}
        ),

        dcc.Dropdown(
            id = 'yaxis-metric',
            options = [
                {'label': i, 'value': i} for i in metrics
            ],
            value = 'Confirmed',
            style = {'min-width': '30%', 'display': 'inline-block'}
        ), 

        dcc.RadioItems(
            id = 'yaxis-type',
            options = [
                {'label': i, 'value': i} for i in ['Linear', 'Log']
            ],
            value = 'Linear',
            labelStyle = {'display': 'inline-block'},
            style = {'min-width': '30%', 'display': 'inline-block'}
        )
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id = 'graph-byCountry-basic',
                config = {'displayModeBar': False})
        ], style= {'display': 'inline-block'}),
        html.Div([
            dcc.Graph(id = 'graph-byCountry-pctChange',
                config = {'displayModeBar': False})
        ], style= {'display': 'inline-block'}),
    ]),

    html.Footer([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'), 
        html.Span('Sources', style={'font-weight': 'bold'}),
        html.Span(children=" | The New York Times | COVID-19 Dashboard by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University | DXY-COVID-19-Data | The COVID Tracking Project", id='sources')
    ])
])


# GRAPHIC: By Country
@dash_app.callback(
    [
        Output('graph-byCountry-basic', 'figure'),
        Output('graph-byCountry-pctChange', 'figure')
    ],
    [
        Input('filter-country', 'value'),
        Input('yaxis-metric', 'value'),
        Input('yaxis-type', 'value')
    ]
)
def byCountryGraph(country, yAxisMetric, yAxisType):
    return sl.getDataByCountry(data, country, yAxisMetric, yAxisType)

# DATA REFRESH
@dash_app.callback(
    Output('page-content', 'children'),
    [
        Input('url', 'search')
    ]
)
def refreshData(search):
    val = url.getParam('refresh', search)
    if str(val) == '1':
        global data, df_jhu, df_nytimes_county, df_covidtracking_country, df_covidtracking_state, df_dxy_region, df_dxy_Country

        data = sl.getData()
        df_jhu, df_nytimes_county, df_covidtracking_country, df_covidtracking_state, df_dxy_region, df_dxy_Country = sl.getIndividualData(data)
        
        update = 'Data refresh triggered. Updated at %s' % str(datetime.date(datetime.now()))
        return update 
    else: 
        return ''

# dash_app main
if __name__ == '__main__':
    dash_app.run_server(debug=False)
