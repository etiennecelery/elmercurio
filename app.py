from bs4 import BeautifulSoup as bs
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime, timedelta
import re
import requests

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bulma@0.9.0/css/bulma.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def serve_layout():
    return html.Div([
        dcc.DatePickerSingle(
            id='date-picker-single',
            date=datetime.today()
        ),
        html.Img(src='https://merreader.emol.cl/assets/img/logo_mer.png', className='container content'),
        dcc.Tabs(id="tabs", value='A', children=[
            dcc.Tab(label='Portada', value='A'),
            dcc.Tab(label='Economía y Negocios', value='B'),
            dcc.Tab(label='Nacional', value='C'),
            dcc.Tab(label='Reportajes', value='R'),
            dcc.Tab(label='Deportes', value='P'),
            dcc.Tab(label='Revista Sábado', value='RVSB'),
            dcc.Tab(label='Domingo', value='RVDG'),
        ]),
        html.Br(),
        html.Div(
            className='container',
            children=html.Div(id='page-content')
        ),

    ],className='hero')

app.layout = serve_layout()

@app.callback(Output('page-content', 'children'),
              [Input('tabs', 'value'),
               Input('date-picker-single','date')])
def get_images(cuerpo, date):
    date = datetime.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
    idx = (date.weekday() + 1) % 7
    sun = date - timedelta(7+idx)
    sat = date - timedelta(7+idx-6)

    if cuerpo in ['R','RVDG']:
        date = sun
    elif cuerpo in ['RVSB']:
        date = sat

    url = f"https://digital.elmercurio.com/{date.strftime('%Y/%m/%d')}/{cuerpo}"
    site = requests.get(url)
    soup = bs(site.content, 'lxml')
    imgs = [x['src'] for x in soup.find(class_='newspaper swiper').find_all('img')]
    imgs = [x.replace('/tmb/','/big/') for x in imgs[3:]]
    if cuerpo in ['A','B','C','P']:
        imgs = [imgs[0]]+imgs[2:]+[imgs[1]]
    elif cuerpo in ['R','RVDG']:
        imgs = imgs[6:]
    else:
        imgs = imgs[5:]

    div = html.Div(
        className='columns is-multiline',
        children=[
            html.Img(src=x, className='column is-full')
            for x in imgs
        ]
    )
    return div

if __name__ == '__main__':
    app.run_server(debug=True)