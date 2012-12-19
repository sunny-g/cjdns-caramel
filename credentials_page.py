from gi.repository import Gtk

class CredentialsPage(Gtk.Box):
	def __init__(self, app):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=5)

		self.app = app

		peering_info_label = Gtk.Label("<b>Peering Information:</b>")
		peering_info_label.set_use_markup(True)
		peering_info_label.set_alignment(0, 0.5)

		self.grid = Gtk.Grid()
		self.grid.set_row_spacing(4)
		self.grid.set_column_spacing(8)
		self.grid.set_margin_bottom(10)

		self.cjdns_ip_label = self.build_grid_row(0, "CJDNS IP")
		self.public_key_label = self.build_grid_row(1, "Public Key")

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

		password_renderer.set_property('editable', True)
		name_renderer.set_property('editable', True)
		location_renderer.set_property('editable', True)

		password_renderer.connect('edited', self.password_edited)
		name_renderer.connect('edited', self.name_edited)
		location_renderer.connect('edited', self.location_edited)

		password_column = Gtk.TreeViewColumn("Password", password_renderer, text=0)
		name_column = Gtk.TreeViewColumn("Name", name_renderer, text=1)
		location_column = Gtk.TreeViewColumn("Location", location_renderer, text=2)

		self.passwords_view.append_column(password_column)
		self.passwords_view.append_column(name_column)
		self.passwords_view.append_column(location_column)

		scroll_view_toolbar = Gtk.Toolbar()
		scroll_view_toolbar.set_can_focus(False)
		scroll_view_toolbar.set_icon_size(Gtk.IconSize.MENU)

		add_password_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
		scroll_view_toolbar.add(add_password_button)

		remove_password_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
		scroll_view_toolbar.add(remove_password_button)

		scroll_view_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 0)
		scroll_view_vbox.pack_start(scroll_view, True, True, 0)
		scroll_view_vbox.pack_start(scroll_view_toolbar, False, False, 0)

		self.set_border_width(10)
		self.pack_start(peering_info_label, False, False, 0)
		self.pack_start(self.grid, False, False, 0)
		self.pack_start(auth_passwords_label, False, False, 0)
		self.pack_start(scroll_view_vbox, True, True, 0)
		self.show_all()

	def build_grid_row(self, row, label_text):
		label = Gtk.Label("{0}:".format(label_text))
		label.set_use_markup(True)

		value = Gtk.Label()
		value.set_selectable(True)

		label.set_alignment(1, 0.5)
		value.set_alignment(0, 0.5)
		value.set_hexpand(False)
		value.set_halign(Gtk.Align.FILL)

		self.grid.attach(label, 0, row, 1, 1)
		self.grid.attach(value, 1, row, 1, 1)

		return value

	def password_edited(self, widget, path, text):
		self.passwords_store[path][0] = text
		self.update_app_config()

	def name_edited(self, widget, path, text):
		self.passwords_store[path][1] = text
		self.update_app_config()

	def location_edited(self, widget, path, text):
		self.passwords_store[path][2] = text
		self.update_app_config()

	def update_app_config(self):
		app_config = self.app.config
		app_config.config['authorizedPasswords'] = []

		for row in self.passwords_store:
			password_dict = {}
			password_dict['password'] = row[0]
			if row[1]: password_dict['name'] = row[1]
			if row[2]: password_dict['location'] = row[2]

			app_config.config['authorizedPasswords'].append(password_dict)

		app_config.save()

	def update(self):
		if self.app.config is None:
			self.cjdns_ip_label.set_text('')
			self.public_key_label.set_text('')
		else:
			config = self.app.config.config
			self.cjdns_ip_label.set_text(config['ipv6'])
			self.public_key_label.set_text(config['publicKey'])

			self.passwords_store.clear()
			for password_dict in config['authorizedPasswords']:
				password = password_dict['password']
				name = password_dict.get('name')
				location = password_dict.get('location')

				self.passwords_store.append([password, name, location])
