# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup as bs
import dash
import dash_auth
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime, timedelta
import requests
import re
from flask import Flask

VALID_USERNAME_PASSWORD_PAIRS = {
    'diario': ''
}

server = Flask(__name__)

external_stylesheets = ['https://cdn.jsdelivr.net/npm/bulma@0.9.0/css/bulma.min.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)
app.title = 'El Mercurio'
app.config['suppress_callback_exceptions'] = True

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

def serve_layout():
    return html.Div([
        dcc.DatePickerSingle(id='date-picker-single', date=datetime.today()),
        html.Img(id='imagen-principal', src='https://merreader.emol.cl/assets/img/logo_mer.png', className='container content'),
        dcc.Tabs(id="tabs", value='A', children=[
            dcc.Tab(label='Portada', value='A'),
            dcc.Tab(label='Economía y Negocios', value='B'),
            dcc.Tab(label='Nacional', value='C'),
            dcc.Tab(label='Reportajes', value='R'),
            dcc.Tab(label='Deportes', value='P'),
            dcc.Tab(label='Revista Sábado', value='RVSB'),
            dcc.Tab(label='Domingo', value='RVDG'),
            dcc.Tab(label='Vivienda y Decoración', value='RVVI'),
            dcc.Tab(label='Ya', value='RVYA'),
            dcc.Tab(label='La Segunda', value='LASEGUNDA'),
        ]),
        html.Br(),
        html.Div(
            className='container',
            children=html.Div(id='page-content')
        ),
    ],className='hero')

app.layout = serve_layout

@app.callback([Output('page-content', 'children'),
               Output('imagen-principal', 'src'),
               Output('imagen-principal', 'style')],
              [Input('tabs', 'value'),
               Input('date-picker-single','date')])
def get_images(cuerpo, date):
    date = datetime.strptime(re.split('T| ', date)[0], '%Y-%m-%d')
    idx = (date.weekday() + 1) % 7
    sun = date - timedelta(idx)
    sat = date - timedelta(7+idx-6)
    martes = date - timedelta(idx-2)

    if cuerpo in ['R','RVDG',]:
        date = sun
    elif cuerpo in ['RVSB','RVVI']:
        date = sat
    elif cuerpo in ['RVYA']:
        date = martes

    if cuerpo == 'LASEGUNDA':
        url = f"https://digital.lasegunda.com/{date.strftime('%Y/%m/%d')}/A"
        imagen_principal = 'https://segreader.emol.cl/assets/img/logo_lasegunda.png'
        style = {'background' :'#159E89'}
    else:
        url = f"https://digital.elmercurio.com/{date.strftime('%Y/%m/%d')}/{cuerpo}"
        imagen_principal = 'https://merreader.emol.cl/assets/img/logo_mer.png'
        style = None


    site = requests.get(url)
    soup = bs(site.content, 'lxml')

    imgs = [x['src'] for x in soup.find(class_='newspaper swiper').find(class_='swiper-wrapper').find_all('img')]
    imgs = [x.replace('/tmb/','/big/') for x in imgs]
    if cuerpo in ['A','B','C','P','LASEGUNDA']:
        imgs = [imgs[0]]+imgs[2:]+[imgs[1]]

    div = html.Div(
        className='columns is-multiline',
        children=[
            html.Figure(
                className='image',
                children=html.Img(src=x, className='column is-full')
            )
            for x in imgs
        ]
    )

    return div, imagen_principal, style


@server.route('/.well-known/acme-challenge/<challenge>')
def letsencrypt_check(challenge):
    return 'FJI3h26D3YEaYPKu5bhJX8BVlIiz89GDX0KfFAU75oI.QvQH9_ohXpCYFE2SCPln-4s4Z-_GLhAiv19xnRUVkPQ'


if __name__ == '__main__':
    app.run_server(debug=False, port=1112, host='0.0.0.0',
        ssl_context=('/etc/letsencrypt/live/diario.estadosfinancieros.cl/fullchain.pem',
        '/etc/letsencrypt/live/diario.estadosfinancieros.cl/privkey.pem')
    )
