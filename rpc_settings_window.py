from gi.repository import Gtk

class RpcSettingsWindow(Gtk.Dialog):
	def __init__(self, parent, rpc_settings):
		Gtk.Dialog.__init__(self)
		
		self.set_title("RPC Settings")
		self.set_transient_for(parent)
		self.set_resizable(False)
		self.set_border_width(5)

		self.add_button(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
		self.add_button(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

		help_label = Gtk.Label("Find these settings in <b>cjdroute.conf</b> under the <b>admin</b> section")
		help_label.set_use_markup(True)
		help_label.set_alignment(0, 0)

		grid = Gtk.Grid()
		grid.set_column_spacing(10)
		grid.set_row_spacing(5)
		grid.set_hexpand(True)

		host_label = Gtk.Label("Host:")
		port_label = Gtk.Label("Port:")
		password_label = Gtk.Label("Password:")

		host_label.set_alignment(1, 0.5)
		port_label.set_alignment(1, 0.5)
		password_label.set_alignment(1, 0.5)

		self.host_entry = Gtk.Entry()
		self.port_entry = Gtk.Entry()
		self.password_entry = Gtk.Entry()
		self.save_pass_check = Gtk.CheckButton.new_with_label('Save password in keyring')

		self.host_entry.set_text(rpc_settings.get('host', 'localhost'))
		self.port_entry.set_text(str(rpc_settings.get('port', 11234)))
		self.password_entry.set_text(rpc_settings.get('password', ''))
		self.save_pass_check.set_active(True)

		self.host_entry.set_hexpand(True)

		grid.attach(host_label, 0, 0, 1, 1)
		grid.attach(self.host_entry, 1, 0, 1, 1)

		grid.attach(port_label, 0, 1, 1, 1)
		grid.attach(self.port_entry, 1, 1, 1, 1)

		grid.attach(password_label, 0, 2, 1, 1)
		grid.attach(self.password_entry, 1, 2, 1, 1)

		grid.attach(self.save_pass_check, 1, 3, 1, 1)


		vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL, spacing = 10)
		vbox.set_border_width(5)
		vbox.pack_start(help_label, False, False, 0)
		vbox.pack_start(grid, False, False, 0)

		content = self.get_content_area()
		content.add(vbox)

		self.get_action_area().set_border_width(0)

		self.show_all()
