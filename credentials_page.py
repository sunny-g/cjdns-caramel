from gi.repository import Gtk

class CredentialsPage(Gtk.Box):
	def __init__(self, app):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=5)

		self.app = app

		peering_info_label = Gtk.Label("<b>Peering Information:</b>")
		peering_info_label.set_use_markup(True)
		peering_info_label.set_alignment(0, 0.5)

		self.peer_info_grid = Gtk.Grid()
		self.peer_info_grid.set_row_spacing(4)
		self.peer_info_grid.set_column_spacing(8)
		self.peer_info_grid.set_margin_bottom(10)

		self.cjdns_ip_label = self.build_grid_row(0, "CJDNS IP")
		self.public_key_label = self.build_grid_row(1, "Public Key")

		auth_passwords_label = Gtk.Label("<b>Authorized Passwords:</b>")
		auth_passwords_label.set_use_markup(True)
		auth_passwords_label.set_alignment(0, 0.5)

		self.passwords_store = Gtk.ListStore(int, str, str, str)
		self.passwords_view = Gtk.TreeView(self.passwords_store)
		self.passwords_view.get_selection().set_mode(Gtk.SelectionMode.SINGLE)

		passwords_scroll = Gtk.ScrolledWindow()
		passwords_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		passwords_scroll.set_shadow_type(Gtk.ShadowType.IN)
		passwords_scroll.add(self.passwords_view)

		password_renderer = Gtk.CellRendererText()
		name_renderer = Gtk.CellRendererText()
		location_renderer = Gtk.CellRendererText()

		password_renderer.set_property('editable', True)
		name_renderer.set_property('editable', True)
		location_renderer.set_property('editable', True)

		password_renderer.connect('edited', self.password_row_edited('password', 1))
		name_renderer.connect('edited', self.password_row_edited('name', 2))
		location_renderer.connect('edited', self.password_row_edited('location', 3))

		password_column = Gtk.TreeViewColumn("Password", password_renderer, text=1)
		name_column = Gtk.TreeViewColumn("Name", name_renderer, text=2)
		location_column = Gtk.TreeViewColumn("Location", location_renderer, text=3)

		self.passwords_view.append_column(password_column)
		self.passwords_view.append_column(name_column)
		self.passwords_view.append_column(location_column)

		passwords_toolbar = Gtk.Toolbar()
		passwords_toolbar.set_can_focus(False)
		passwords_toolbar.set_icon_size(Gtk.IconSize.MENU)

		style_context = passwords_toolbar.get_style_context()
		style_context.add_class(Gtk.STYLE_CLASS_INLINE_TOOLBAR)

		add_password_button = Gtk.ToolButton()
		add_password_button.set_icon_name('list-add-symbolic')
		add_password_button.connect('clicked', self.add_password)
		passwords_toolbar.add(add_password_button)

		remove_password_button = Gtk.ToolButton()
		remove_password_button.set_icon_name('list-remove-symbolic')
		remove_password_button.connect('clicked', self.remove_password)
		passwords_toolbar.add(remove_password_button)

		passwords_vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 0)
		passwords_vbox.pack_start(passwords_scroll, True, True, 0)
		passwords_vbox.pack_start(passwords_toolbar, False, False, 0)

		self.set_border_width(10)
		self.pack_start(peering_info_label, False, False, 0)
		self.pack_start(self.peer_info_grid, False, False, 0)
		self.pack_start(auth_passwords_label, False, False, 0)
		self.pack_start(passwords_vbox, True, True, 0)
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

		self.peer_info_grid.attach(label, 0, row, 1, 1)
		self.peer_info_grid.attach(value, 1, row, 1, 1)

		return value

	def password_row_edited(self, field_name, field_index):
		def callback(widget, path, text):
			self.passwords_store[path][field_index] = text
			row = self.passwords_store[path][0]
			self.app.config.config['authorizedPasswords'][row][field_name] = text
			self.app.config.save()
		return callback

	def add_password(self, widget):
		index = len(self.passwords_store)

		try:
			password = self.app.generate_authorized_password()
		except:
			password = None

		iter = self.passwords_store.append([index, password, None, None])
		self.passwords_view.get_selection().select_iter(iter)

		self.app.config.config['authorizedPasswords'].append({'password': password})
		self.app.config.save()

	def remove_password(self, widget):
		if len(self.passwords_store) > 0:
			(model, iter) = self.passwords_view.get_selection().get_selected()

			if iter is not None:
				config_index = self.passwords_store[iter][0]
				self.passwords_store.remove(iter)
				self.app.config.config['authorizedPasswords'].pop(config_index)
				self.app.config.save()
				self.update()

	def update(self):
		if self.app.config is None:
			self.cjdns_ip_label.set_text('')
			self.public_key_label.set_text('')
		else:
			config = self.app.config.config
			self.cjdns_ip_label.set_text(config['ipv6'])
			self.public_key_label.set_text(config['publicKey'])

			self.passwords_store.clear()
			for index, password_dict in enumerate(config['authorizedPasswords']):
				password = password_dict['password']
				name = password_dict.get('name')
				location = password_dict.get('location')

				self.passwords_store.append([index, password, name, location])
