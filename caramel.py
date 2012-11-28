#!/usr/bin/python3

import json
import os.path
import subprocess

from gi.repository import GLib
from gi.repository import Gtk
from main_window import MainWindow

from rpc_connection import *
from cjdns_config import *

class CaramelApplication(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self, application_id = 'info.cjdns.caramel')
		self.connect("activate", self.activate)

		self.load_config()
		self.rpc_conn = None
		self.reset_connection()

		GLib.timeout_add_seconds(5, self.update_status)

	def activate(self, data=None):
		self.window = MainWindow(self)
		self.add_window(self.window)
		self.update_status()

	def load_config(self):
		current_dir = os.path.dirname(os.path.realpath(__file__))
		config_path = os.path.join(current_dir, 'cjdroute.conf')
		self.config = CjdnsConfig(config_path)
		self.config.load_or_generate()
		self.rpc_settings = self.config.rpc_settings()

	def start_cjdns(self):
		current_dir = os.path.dirname(os.path.realpath(__file__))
		cjdroute = os.path.join(current_dir, 'cjdroute')
		proc = subprocess.Popen(['pkexec', '--user', 'root', cjdroute], stdin=subprocess.PIPE,  close_fds=True)

		proc.stdin.write(self.config.dump().encode())
		proc.stdin.close()

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

		icon = {True: Gtk.STOCK_YES, False: Gtk.STOCK_NO}[connected]
		self.window.status_icon.set_from_stock(icon, Gtk.IconSize.MENU)
		self.window.status_label.set_markup('<b>' + (main_status or '') + '</b>')

		peers_markup = "<span size='small'>" + (sub_status or '') + "</span>"
		self.window.peers_label.set_markup(peers_markup)

		return True

if __name__ == "__main__":
	app = CaramelApplication()
	app.run(None)
