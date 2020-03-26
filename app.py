import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go

mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

app = dash.Dash(__name__)

server = app.server
#Coordenadas
dfc = pd.read_csv("data/puntos_agua.csv",sep=';',decimal=',',encoding="ISO-8859-1")

#Series
df = pd.read_csv("data/niveles.csv",sep=';',decimal=',',encoding="ISO-8859-1")
df['Fecha'] = pd.to_datetime(df['Fecha'])
df = df.sort_values(by=['Fecha'])

codigos = list(df.codigo.unique())

options = []
for tic in codigos:
    options.append({'label':'{}'.format(tic), 'value':tic})

app.layout = html.Div([
    html.Div(className = "header" ,
     children = [html.Img(id="logo", src= '/assets/logo.png'),
                html.H1('Red de monitoreo piezométrica del Golfo de Urabá')]),

    html.P(),

    html.Div(className = "graficas" ,children =[
        html.Div(className = 'Div_serie',children =[
            html.Div(className = 'controles',children=[
                html.P('Seleccione los puntos de monitoreo'),
                html.Div(className = 'barra',children = [
                    dcc.Dropdown(
                        id='my_ticker_symbol',
                        options=options,
                        value=['PzC01'],
                        multi=True,
                        searchable= True),
                    html.Button(
                        id='submit-button',
                        n_clicks=0,
                        children='Enviar')
                        ])
                ]),

            html.P(),

            dcc.Graph(id='serie')
            ]),
        dcc.Graph(id='mapa'),
        ])
    ])


@app.callback(
    Output('serie', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value')])

def update_graph(n_clicks, stock_ticker):
    layout_serie = go.Layout(
          title = 'Niveles piezométricos',
          title_x=0.5,
          hovermode ='closest',
          plot_bgcolor = 'rgba(0,0,0,0)',
          paper_bgcolor = 'rgba(0,0,0,0)',
          xaxis_title  = "Fechas",
          yaxis_title = "msnm",)

    traces = []
    for tic in stock_ticker:
        punto = df[df['codigo'] == tic]

        traces.append(go.Scatter(
            x = punto['Fecha'],
            y = punto['Nivel'],
            mode = 'lines',
            name = tic))
        traces.append(go.Scatter(
            x = punto['Fecha'],
            y = punto['Nivel'],
            mode = 'markers',
            marker=dict(
              color='Red'),
            showlegend=False))
    return go.Figure(data = traces ,layout=layout_serie)

@app.callback(
    Output('mapa', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value')])

def update_map(n_clicks, stock_ticker):
    df1 = dfc[~dfc['codigo'].isin(stock_ticker)]
    df2 = dfc[dfc['codigo'].isin(stock_ticker)]

    layout = go.Layout(
        title = 'Distribución espacial de los puntos de monitoreo',
        title_x=0.5,
        hovermode='closest',
        showlegend=True,
        legend_title='<b> Puntos de agua </b>',
        legend=dict(x=0, y=1,bordercolor="Black",borderwidth=2,bgcolor="White"),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor = 'rgba(0,0,0,0)',
        mapbox=dict(
            accesstoken=mapbox_access_token,
            #bearing=0,
            center=dict(
                lat=7.85,
                lon=-76.7
            ),
            #pitch=0,
            zoom=9,
            style="light")
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
