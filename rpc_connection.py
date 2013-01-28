import socket
import select
import hashlib
import bencoding

class ConnectionError(Exception):
	pass

class PingNotReturned(Exception):
	pass

class MissingCredentials(Exception):
	pass

class AuthFailed(Exception):
	pass

class RpcConnection:
	def __init__(self, host='127.0.0.1', port=11234, password=None):
		self.host = host
		self.port = port
		self.password = password

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.settimeout(0.1)
		self.connected = False
		self.broken = False

	def connect(self):
		try:
			self.sock.connect((self.host, self.port))
			self.connected = True
			return True
		except socket.error:
			self.connected = False
			self.broken = True
			return False

	def close(self):
		try:
			self.connected = False
			self.broken = True
			self.sock.shutdown(socket.SHUT_RDWR)
			self.sock.close()
		except socket.error:
			pass

	def call(self, query, args=None, auth=False):
		dict = {'q': query}

		if args is not None:
			dict['args'] = args

		if auth:
			dict = self.authenticate(dict)

		query = bencoding.encode(dict)

		try:
			self.sock.send(query)

			response = self.sock.recv(1024 * 1024)
			if len(response) < 1:
				raise ConnectionError()
			response = bencoding.decode(response)

			if self.check_respose_auth_failed(response):
				raise AuthFailed()
			else:
				return response

		except (socket.error, ConnectionError):
			self.connected = False
			self.broken = True
			raise ConnectionError()
		except bencoding.DecodeError:
			return None

	def authenticate(self, dict):
		cookie = self.cookie()
		if cookie is None:
			return False

		cookie = cookie.get('cookie')
		password = self.password or ''
		hash = hashlib.sha256((password + cookie).encode('utf-8')).hexdigest()

		if 'q' in dict:
			dict['aq'] = dict['q']

		dict['q'] = 'auth'
		dict['hash'] = hash
		dict['cookie'] = cookie

		request = bencoding.encode(dict)
		dict['hash'] = hashlib.sha256(request).hexdigest()

		return dict

	def check_respose_auth_failed(self, response):
		return isinstance(response, dict) and ('error' in response) and (response['error'] == 'Auth failed.')

	def test_auth(self):
		try:
			response = self.dump_routing_table(0)
			return True
		except AuthFailed:
			return False

	def ping(self):
		try:
			return self.call('ping')['q'] == 'pong'
		except (TypeError, KeyError):
			return False

	def cookie(self):
		return self.call('cookie')

	def memory(self):
		return self.call('memory')

	def exit(self):
		dict = self.authenticate({'q': 'Core_exit'})
		query = bencoding.encode(dict)

		try:
			self.sock.send(query)
			self.close()
		except socket.error:
			self.connected = False
			self.broken = True

	def dump_routing_table(self, page=None):
		if page is None:
			page = 0
			routing_table = []
			response = {'more': 1}

			while 'more' in response:
				response = self.dump_routing_table(page)

				if response is None:
					return None

				routing_table.extend(response['routingTable'])
				page += 1

			return {'routingTable': routing_table}
		else:
			return self.call('NodeStore_dumpTable', args={'page': page}, auth=True)

	def count_unique_nodes(self):
		routing_table = self.dump_routing_table()
		if routing_table is not None:
			nodes = set([route['ip'] for route in routing_table['routingTable']])
			return len(nodes)
