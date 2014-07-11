#!/usr/bin/env python3

import asyncio
import datetime
import locale
import sys
import time

def create_server(router):
	class HTTPServer(asyncio.Protocol):
		def connection_made(self, transport):
			self.transport = transport
			self.data = bytes()

		def data_received(self, data):
			self.data += data
			if data.endswith(b'\r\n\r\n'):
				request = create_parsed_request(self.data)
				response = create_request_response(request)
				self.transport.write(response)
				self.transport.close()
				print('[{}]'.format(time.strftime('%Y-%m-%d %H:%M:%S')), request['method_arguments'])

	def create_parsed_request(received):
		request = {}

		received = received.decode()
		lines = received.split('\r\n')

		method_line = lines[0].strip()
		if len(method_line.split(' ')) < 2:
			return
		method = method_line.partition(' ')[0]
		method_args = method_line.split(' ')[1]
		if len(method_line.split(' ')) > 2:
			protocol = method_line.split(' ')[2]
		else:
			protocol = ''

		request['method'] = method
		request['method_arguments'] = method_args
		request['protocol'] = protocol
		request['headers'] = []

		for line in lines[1:]:
			if len(line) == 0:
				continue
			command = line.split(': ')[0]
			arguments = line.split(': ')[1].strip()
			request['headers'].append((command, arguments))

		return request

	def create_response(status, body=None):
		def list_to_resp(lst):
			resp_str = ''
			for elem in lst[:-1]:
				resp_str += elem + '\r\n'
			resp_str += lst[-1]
			return resp_str.encode()

		if body == None:
			body = status

		locale.setlocale(locale.LC_TIME, 'en_US')
		rfc1123_date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

		return list_to_resp([
			"HTTP/1.1 " + status,
			"Date: " + rfc1123_date,
			"Server: httpserver",
			"Connection: close",
			"",
			body])

	def create_request_response(request):
		if request == None:
			return create_response('500 Internal Server Error')
		if request['method'] == 'GET':
			path = request['method_arguments']
			if path in routes:
				return create_response("200 OK", routes[path]())
			return create_response("404 Not Found")
		return create_response("501 Not Implemented")

	def serve(host='localhost', port=7777):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(loop.create_server(HTTPServer, host, port))
		if host == None:
			print('Listening on all interfaces, port', str(port))
		else:
			print('Listening on', str(host) + ':' + str(port), '...')
		try:
			loop.run_forever()
		except KeyboardInterrupt:
			sys.exit(0)

	routes = router.routes
	return serve

def router(path):
	def wrapped(func):
		router.routes[path] = func
		return func

	if not hasattr(router, 'routes'):
		router.routes = {}
	return wrapped
