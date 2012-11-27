from gi.repository import Gtk

from rpc_settings_window import RpcSettingsWindow
import gnome_keyring as GnomeKeyring

class MainWindow(Gtk.Window):
	def __init__(self, app):
		Gtk.Window.__init__(self)

		self.app = app

		self.set_title("CJDNS Configuration")
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_size_request(500, 400)

		self.infobar = self.build_infobar()

		inner_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 15)
		inner_vbox.set_border_width(10)
		inner_vbox.pack_start(self.infobar, False, False, 0)
		inner_vbox.pack_start(self.build_notebook(), True, True, 0)

		menu_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 0)
		menu_vbox.pack_start(self.build_menubar(), False, False, 0)
		menu_vbox.pack_start(inner_vbox, True, True, 0)

		self.add(menu_vbox)
		self.show_all()
		self.update_infobar()

	def build_notebook(self):
		notebook = Gtk.Notebook()

		notebook.append_page(self.build_status_page(), Gtk.Label("Status"))
		notebook.append_page(Gtk.Label("Placeholder"), Gtk.Label("Peers"))
		notebook.append_page(Gtk.Label("Placeholder"), Gtk.Label("Credentials"))
		notebook.append_page(Gtk.Label("Placeholder"), Gtk.Label("Discovery"))

		return notebook

	def build_infobar(self):
		infobar = Gtk.InfoBar()
		infobar.add_button("RPC Settings", Gtk.ResponseType.OK)
		infobar.get_content_area().add(Gtk.Label("Password required to configure CJDNS"))
		infobar.connect("response", 
			lambda sender, response: self.open_rpc_settings(sender)
		)
		return infobar

	def update_infobar(self):
		if 'password' in self.app.rpc_settings:
			self.infobar.hide()
		else:
			self.infobar.show()

	def build_menubar(self):
		def build_menu(label, *items):
			root_item = Gtk.MenuItem.new_with_mnemonic(label)
			menu = Gtk.Menu()
			root_item.set_submenu(menu)

			for label, action in items:
				item = Gtk.MenuItem.new_with_mnemonic(label)
				item.connect("activate", action)
				menu.add(item)

			return root_item

		menubar = Gtk.MenuBar()

		menubar.add(build_menu("_File", 
			("_Quit", lambda sender: self.destroy())
		))

		menubar.add(build_menu("_Tools",
			("_RPC Settings", self.open_rpc_settings)
		))
		
		return menubar

	def build_status_page(self):
		self.status_icon = Gtk.Image.new_from_stock(Gtk.STOCK_NO, Gtk.IconSize.MENU)

		self.status_label = Gtk.Label()
		self.status_label.set_use_markup(True)

		self.peers_label = Gtk.Label()
		self.peers_label.set_use_markup(True)

		self.status_label.set_alignment(0, 0.5)
		self.peers_label.set_alignment(0, 0.5)

		button = Gtk.Button("Stop")
		button.set_size_request(80, -1)
		button.set_valign(Gtk.Align.START)
		button.set_sensitive(False)

		status_grid = Gtk.Grid()
		status_grid.set_row_spacing(2)
		status_grid.set_column_spacing(5)

		status_grid.attach(self.status_icon, 0, 0, 1, 1)
		status_grid.attach(self.status_label, 1, 0, 1, 1)
		status_grid.attach(self.peers_label, 1, 1, 1, 1)

		status_hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 10)
		status_hbox.pack_start(status_grid, True, True, 0)
		status_hbox.pack_start(button, False, False, 0)

		vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
		vbox.set_border_width(10)

		vbox.pack_start(status_hbox, True, True, 0)

		return vbox

	def open_rpc_settings(self, sender):
		rpc_dialog = RpcSettingsWindow(self, self.app.rpc_settings)
		response = rpc_dialog.run()

		try:
			port = int(rpc_dialog.port_entry.get_text())
		except ValueError:
			port = 11234

		if response == Gtk.ResponseType.OK:
			self.app.rpc_settings = {
				'host': rpc_dialog.host_entry.get_text(),
				'port': port,
				'password': rpc_dialog.password_entry.get_text()
			}

			if rpc_dialog.save_pass_check.get_active():
				GnomeKeyring.set(
					'CJDNS Admin Password',
					self.app.rpc_settings['password'],
					{'key-type': 'cjdns-rpc-admin'}
				)

			self.app.reset_connection()
			self.app.update_status()

		rpc_dialog.destroy()
		self.update_infobar()

	def update_status_page(self, connected, node_count=None):
		def pluralize(count, word, plural):
			if count != 1:
				word = plural
			return "{0} {1}".format(count, word)

		if connected:
			icon = Gtk.STOCK_YES
			label = "CJDNS is running"
		else:
			icon = Gtk.STOCK_NO
			label = "CJDNS is stopped"

		self.status_icon.set_from_stock(icon, Gtk.IconSize.MENU)
		self.status_label.set_markup('<b>' + label + '</b>')

		peers_markup = "<span size='small'>" + pluralize(node_count, "entry", "entries") + " in routing table</span>"
		self.peers_label.set_markup(peers_markup)