import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go

mapbox_access_token = "pk.eyJ1IjoiYmFhcmVuYXNnIiwiYSI6ImNrODJlZWwyMjBnYTQzZHBjZDFwcTJkeHgifQ.zPN5UFpYwuXLC9D8xBtAOA"


app = dash.Dash(__name__)

#server = app.server
#Coordenadas
dfc = pd.read_csv("data/puntos_agua.csv",sep=';',decimal=',',encoding="ISO-8859-1")

#Series
df = pd.read_csv("data/niveles.csv",sep=';',decimal=',',encoding="ISO-8859-1")
df['Fecha'] = pd.to_datetime(df['Fecha'])
df = df.sort_values(by=['Fecha'])

codigos = list(df.codigo.unique())

punto = df[df['codigo'] == 'PzC01']

options = []
for tic in codigos:
    options.append({'label':'{}'.format(tic), 'value':tic})

app.layout = html.Div([
    html.Div([
        html.Img(className="logo", src= '/assets/logo.png', style={'display':'inline-block'}),
        html.H1('Red de monitoreo piezométrica del Golfo de Urabá',style={'display':'inline-block'})]),
    html.Div([
        html.H3('Seleccione los puntos de monitoreo',style={'marginLeft':'30px','display':'inline-block'}),
        dcc.Dropdown(
            id='my_ticker_symbol',
            options=options,
            value=['PzC01'],
            multi=True,
            searchable= True,
            style={ 'marginLeft':'30px','marginRight':'30px','display':'inline-block'}),
        html.Button(
            id='submit-button',
            n_clicks=0,
            children='Enviar',
            style={'fontSize':24, 'marginLeft':'30px','display':'inline-block'})
        ]),


    html.Div([
        dcc.Graph(id='mapa',style={'width':'50%', 'height':'100%','display':'inline-block'}),

        dcc.Graph(id='serie',
              figure = {'data':[go.Scatter(
                  x = punto['Fecha'],
                  y = punto['Nivel'],
                  mode = 'lines',
                  name = 'PzC01'
              ),
              # create traces
              go.Scatter(
                  x = punto['Fecha'],
                  y = punto['Nivel'],
                  mode = 'markers',
                  marker=dict(
                    color='Red'),
                  showlegend=False
              )],
                  'layout':go.Layout(
                      title = 'Niveles piezométricos de {}'.format('PzC01'))},
            style={'width':'50%','display':'inline-block', 'vertical-align': 'top'})])
])

@app.callback(
    Output('serie', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value')])

def update_graph(n_clicks, stock_ticker):
    traces = []
    for tic in stock_ticker:
        punto = df[df['codigo'] == tic]
        traces.append({'x':punto['Fecha'], 'y': punto['Nivel'], 'mode' : 'lines','name':tic})
        traces.append({'x':punto['Fecha'], 'y': punto['Nivel'], 'mode' : 'markers', 'marker' : dict(color= 'Red'),'showlegend':False})
    fig = {
        'data': traces,
        'layout': {'title': 'Niveles piezométricos  de ' + ', '.join(stock_ticker), 'hovermode':'closest'}
    }
    return fig

@app.callback(
    Output('mapa', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value')])

def update_map(n_clicks, stock_ticker):
    df1 = dfc[~dfc['codigo'].isin(stock_ticker)]
    df2 = dfc[dfc['codigo'].isin(stock_ticker)]

    layout = go.Layout(
        autosize=True,
        width=700,
        height=700,
        hovermode='closest',
        showlegend=True,
        legend_title='<b> Puntos de agua </b>',
        legend=dict(x=0, y=1,bordercolor="Black",borderwidth=2),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            #bearing=0,
            center=dict(
                lat=7.85,
                lon=-76.7
            ),
            #pitch=0,
            zoom=10,
            style='dark')
        )
    return go.Figure(
        data = [go.Scattermapbox(
                    lat=df2.lat,
                    lon=df2.lon,
                    mode='markers',
                    name="Seleccionados",
                    marker=go.scattermapbox.Marker(
                        size=17,
                        color='rgb(0, 0, 255)',
                        opacity=0.7),
                    text=df2.codigo,
                    hoverinfo='text'),
                go.Scattermapbox(
                    lat = df1.lat,
                    lon = df1.lon,
                    mode='markers',
                    name="No seleccionados",
                    marker=go.scattermapbox.Marker(
                        size=17,
                        color='rgb(255, 0, 0)',
                        opacity=0.7),
                    text=df1.codigo,
                    hoverinfo='text'),
                    ],
        layout=layout,
        )


if __name__ == '__main__':
    app.run_server(debug=True)
