#!/usr/bin/python3

import json
import os.path

from gi.repository import GLib
from gi.repository import Gtk
from main_window import MainWindow

from rpc_connection import *
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
		def pluralize(count, word, plural):
			if count != 1:
				word = plural
			return "{0} {1}".format(count, word)

		if self.rpc_conn.broken:
			self.reset_connection()

		connected = False
		main_status = "CJDNS is stopped"
		sub_status = None

		try:
			if self.rpc_conn.broken:
				raise ConnectionError()
			else:
				if not self.rpc_conn.ping():
					sub_status = "Ping was not returned"
				else:
					connected = True
					main_status = "CJDNS is running"

					if self.rpc_settings.get('password') is not None:
						unique_nodes = self.rpc_conn.count_unique_nodes()
						sub_status = "{0} found".format(pluralize(unique_nodes, "node", "nodes"))
					
		except ConnectionError:
			sub_status = "Could not connect to port {0}".format(self.rpc_conn.port)
		except AuthFailed:
			self.window.infobar_label.set_text("Password rejected by CJDNS")
			self.window.infobar.show()

		self.window.update_status_page(connected, main_status, sub_status)

		return True

if __name__ == "__main__":
	app = CaramelApplication()
	app.run(None)
