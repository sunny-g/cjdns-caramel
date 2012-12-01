from gi.repository import Gtk

from rpc_settings_window import RpcSettingsWindow

class MainWindow(Gtk.Window):
	def __init__(self, app):
		Gtk.Window.__init__(self)

		self.app = app

		self.set_title("CJDNS Configuration")
		self.set_position(Gtk.WindowPosition.CENTER)
		self.set_size_request(580, 400)

		self.cjdroute_path_infobar = self.build_cjdroute_path_infobar()
		self.auth_fail_infobar = self.build_auth_fail_infobar()

		inner_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 15)
		inner_vbox.set_border_width(10)
		inner_vbox.pack_start(self.cjdroute_path_infobar, False, False, 0)
		inner_vbox.pack_start(self.auth_fail_infobar, False, False, 0)
		inner_vbox.pack_start(self.build_notebook(), True, True, 0)

		menu_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 0)
		menu_vbox.pack_start(self.build_menubar(), False, False, 0)
		menu_vbox.pack_start(inner_vbox, True, True, 0)

		inner_vbox.show()
		menu_vbox.show()
		self.show()

		self.add(menu_vbox)

	def build_notebook(self):
		notebook = Gtk.Notebook()

		notebook.append_page(self.build_status_page(), Gtk.Label("Status"))
		notebook.append_page(self.build_credentials_page(), Gtk.Label("Credentials"))

		notebook.show()
		return notebook

	def build_infobar(self, label_text, button_text, action):
		infobar = Gtk.InfoBar()
		label = Gtk.Label(label_text)
		label.set_use_markup(True)

		infobar.get_content_area().add(label)
		infobar.add_button(button_text, Gtk.ResponseType.OK)
		infobar.connect("response", action)

		label.show()

		return infobar

	def build_auth_fail_infobar(self):
		return self.build_infobar("Password rejected by CJDNS", "RPC Settings",
			lambda sender, response: self.open_rpc_settings(sender)
		)

	def build_cjdroute_path_infobar(self):
		return self.build_infobar("Could not find the <b>cjdroute</b> tool", "Locate CJDNS Folder",
			lambda sender, response: self.app.locate_cjdroute()
		)

	def build_menubar(self):
		menubar = Gtk.MenuBar()
		accel_group = Gtk.AccelGroup()
		self.add_accel_group(accel_group)

		def build_menu(label, *items):
			root_item = Gtk.MenuItem.new_with_mnemonic(label)
			menu = Gtk.Menu()
			root_item.set_submenu(menu)

			for label, accel, action in items:
				item = Gtk.MenuItem.new_with_mnemonic(label)
				item.connect('activate', action)

				if accel is not None:
					key, mod = Gtk.accelerator_parse(accel)
					item.add_accelerator('activate', accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
				
				menu.add(item)

			return root_item
		

		menubar.add(build_menu("_File", 
			("_Quit", "<Control>Q", lambda sender: self.destroy())
		))

		menubar.add(build_menu("_Tools",
			("_RPC Settings", None, self.open_rpc_settings)
		))
		
		menubar.show_all()

		return menubar

	def build_status_page(self):
		self.status_icon = Gtk.Image.new_from_stock(Gtk.STOCK_NO, Gtk.IconSize.MENU)

		self.status_label = Gtk.Label()
		self.status_label.set_use_markup(True)

		self.peers_label = Gtk.Label()
		self.peers_label.set_use_markup(True)

		self.status_label.set_alignment(0, 0.5)
		self.peers_label.set_alignment(0, 0.5)

		self.start_button = Gtk.Button("Start")
		self.start_button.set_size_request(80, -1)
		self.start_button.set_valign(Gtk.Align.START)
		self.start_button.connect('clicked', lambda sender: self.app.start_cjdns())

		self.stop_button = Gtk.Button("Stop")
		self.stop_button.set_size_request(80, -1)
		self.stop_button.set_valign(Gtk.Align.START)
		self.stop_button.connect('clicked', lambda sender: self.app.stop_cjdns())

		status_grid = Gtk.Grid()
		status_grid.set_row_spacing(2)
		status_grid.set_column_spacing(5)

		status_grid.attach(self.status_icon, 0, 0, 1, 1)
		status_grid.attach(self.status_label, 1, 0, 1, 1)
		status_grid.attach(self.peers_label, 1, 1, 1, 1)

		status_hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL, spacing = 10)
		status_hbox.pack_start(status_grid, True, True, 0)
		status_hbox.pack_start(self.start_button, False, False, 0)
		status_hbox.pack_start(self.stop_button, False, False, 0)

		vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
		vbox.set_border_width(10)

		vbox.pack_start(status_hbox, True, True, 0)

		vbox.show_all()
		self.stop_button.hide()

		return vbox

	def build_credentials_page(self):
		def build_grid_row(row, label_text):
			label = Gtk.Label("{0}:".format(label_text))
			label.set_use_markup(True)

			value = Gtk.Label()
			value.set_selectable(True)

			label.set_alignment(1, 0.5)
			value.set_alignment(0, 0.5)
			value.set_hexpand(False)
			value.set_halign(Gtk.Align.FILL)

			grid.attach(label, 0, row, 1, 1)
			grid.attach(value, 1, row, 1, 1)

			return value

		peering_info_label = Gtk.Label("<b>Peering Information:</b>")
		peering_info_label.set_use_markup(True)
		peering_info_label.set_alignment(0, 0.5)

		grid = Gtk.Grid()
		grid.set_row_spacing(4)
		grid.set_column_spacing(8)
		grid.set_margin_bottom(10)

		self.cjdns_ip_label = build_grid_row(0, "CJDNS IP")
		self.public_key_label = build_grid_row(1, "Public Key")
		# self.external_ip_label = build_grid_row(2, "External IP")
		self.peering_port_label = build_grid_row(2, "Port")

		auth_passwords_label = Gtk.Label("<b>Authorized Passwords:</b>")
		auth_passwords_label.set_use_markup(True)
		auth_passwords_label.set_alignment(0, 0.5)

		self.passwords_store = Gtk.ListStore(str, str, str)
		self.passwords_view = Gtk.TreeView(self.passwords_store)
		self.passwords_view.get_selection().set_mode(Gtk.SelectionMode.SINGLE)

		scroll_view = Gtk.ScrolledWindow()
		scroll_view.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scroll_view.set_shadow_type(Gtk.ShadowType.IN)
		scroll_view.add(self.passwords_view)

		password_renderer = Gtk.CellRendererText()
		name_renderer = Gtk.CellRendererText()
		location_renderer = Gtk.CellRendererText()

		# name_renderer.set_fixed_size(130, -1)
		# location_renderer.set_fixed_size(130, -1)

		password_column = Gtk.TreeViewColumn("Password", password_renderer, text=0)
		name_column = Gtk.TreeViewColumn("Name", name_renderer, text=1)
		location_column = Gtk.TreeViewColumn("Location", location_renderer, text=2)

		self.passwords_view.append_column(password_column)
		self.passwords_view.append_column(name_column)
		self.passwords_view.append_column(location_column)

		vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing=5)
		vbox.set_border_width(10)
		vbox.pack_start(peering_info_label, False, False, 0)
		vbox.pack_start(grid, False, False, 0)
		vbox.pack_start(auth_passwords_label, False, False, 0)
		vbox.pack_start(scroll_view, True, True, 0)
		vbox.show_all()

		return vbox

	def update_credentials_page(self):
		if self.app.config is None:
			self.cjdns_ip_label.set_text('')
			self.public_key_label.set_text('')
			# self.external_ip_label.set_text('')
			self.peering_port_label.set_text('')
		else:
			config = self.app.config.config
			self.cjdns_ip_label.set_text(config['ipv6'])
			self.public_key_label.set_text(config['publicKey'])

			udp_bind_address = config['interfaces']['UDPInterface']['bind']
			udp_bind_port = int(udp_bind_address.split(':')[1])
			self.peering_port_label.set_text(str(udp_bind_port))

			self.passwords_store.clear()
			for password_dict in config['authorizedPasswords']:
				password = password_dict['password']
				name = password_dict.get('name')
				location = password_dict.get('location')

				self.passwords_store.append([password, name, location])

	def open_rpc_settings(self, sender):
		rpc_dialog = RpcSettingsWindow(self, self.app.rpc_settings)
		response = rpc_dialog.run()

		if response == Gtk.ResponseType.OK:
			host = rpc_dialog.host_entry.get_text()
			password = rpc_dialog.password_entry.get_text()

			try:
				port = int(rpc_dialog.port_entry.get_text())
			except ValueError:
				port = 11234

			self.app.rpc_settings = {
				'host': host,
				'port': port,
				'password': password
			}

			if self.app.config is not None:
				self.app.config.config['admin'].update({
					'bind': "{0}:{1}".format(host, port),
					'password': password
				})
				self.app.config.save()

			self.app.reset_connection()
			self.app.update_status()

		rpc_dialog.destroy()
