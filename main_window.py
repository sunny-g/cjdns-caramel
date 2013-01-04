from gi.repository import Gtk

from rpc_settings_window import RpcSettingsWindow
from credentials_page import CredentialsPage

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

		inner_vbox.show()
		
		self.add(inner_vbox)
		self.show()

	def build_notebook(self):
		notebook = Gtk.Notebook()

		self.credentials_page = CredentialsPage(self.app)

		notebook.append_page(self.build_status_page(), Gtk.Label("Status"))
		notebook.append_page(self.credentials_page, Gtk.Label("Credentials"))

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
