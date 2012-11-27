import socket
import hashlib
import bencoding

class RpcConnection:
	def __init__(self, host='localhost', port=11234, password=None):
		self.host = host
		self.port = port
		self.password = password

		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
			self.sock.shutdown(socket.SHUT_RDWR)
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
		except socket.error:
			self.connected = False
			self.broken = True
			return None
		else:
			return bencoding.decode(response)

	def ping(self):
		try:
			return self.call('ping')['q'] == 'pong'
		except (TypeError, KeyError):
			return False

	def cookie(self):
		return self.call('cookie')

	def memory(self):
		return self.call('memory')

	def dump_node_table(self, page=None):
		if page is None:
			page = 0
			routing_table = []
			response = {'more': 1}

			while 'more' in response:
				response = self.dump_node_table(page)

				if response is None:
					return None

				routing_table.extend(response['routingTable'])
				page += 1

			return {'routingTable': routing_table}
		else:
			return self.call('NodeStore_dumpTable', args={'page': page}, auth=True)

	def ip_tunnel_connections(self):
		return self.call('IpTunnel_listConnections', auth=True)

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
