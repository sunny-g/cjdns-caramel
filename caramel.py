#!/usr/bin/python3

import json
import os.path

from gi.repository import GLib
from gi.repository import Gtk
from main_window import MainWindow

from rpc_connection import RpcConnection
import gnome_keyring as GnomeKeyring

class CaramelApplication(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self, application_id = 'info.cjdns.caramel')
		self.connect("activate", self.activate)

		self.load_rpc_settings()
		self.rpc_conn = None
		self.reset_connection()

		GLib.timeout_add_seconds(5, self.update_status)

	def activate(self, data=None):
		self.window = MainWindow(self)
		self.add_window(self.window)
		self.update_status()

	def load_rpc_settings(self):
		self.rpc_settings = {'host': 'localhost', 'port': 11234}

		config_file = None
		try:
			config_file = open(os.path.expanduser('~/.cjdnsadmin'), 'r')
			config = json.load(config_file)
			self.rpc_settings = {
				'host': str(config['addr']),
				'port': int(config['port']),
				'password': str(config['password'])
			}

		except:
			password = GnomeKeyring.get({'key-type': 'cjdns-rpc-admin'})
			if password is not None:
				self.rpc_settings['password'] = password
		finally:
			if config_file is not None:
				config_file.close()

	def reset_connection(self):
		if self.rpc_conn:
			self.rpc_conn.close()

		self.rpc_conn = RpcConnection(
			self.rpc_settings.get('host'),
			self.rpc_settings.get('port'),
			self.rpc_settings.get('password')
		)

		return self.rpc_conn.connect()

	def update_status(self):
		if self.rpc_conn.broken:
			self.reset_connection()

		connected = self.rpc_conn.ping()

		try:
			routes = self.rpc_conn.dump_node_table()['routingTable']
			node_count = len(routes)
		except:
			node_count = None

		self.window.update_status_page(connected = connected, node_count = node_count)

		return True

if __name__ == "__main__":
	app = CaramelApplication()
	app.run(None)
