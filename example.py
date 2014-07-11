#!/usr/bin/env python3

import datetime
import os

from aitch import create_server, router

@router('/')
def index():
	return 'This is the index page.'

@router('/another-page')
def another_page():
	return '<html><h2>...and another page, but in HTML!</h2></html>'

@router('/time')
def time():
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@router('/load-average')
def load_average():
	return ('Load average: ' + 3 * '{:.2f} ').format(*os.getloadavg())[:-1]

server = create_server(router)
server()
