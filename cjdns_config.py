import os.path
import subprocess
import json
import re

class CjdnsConfig:
	def __init__(self, path):
		self.path = path
		self.config = {}

	def load(self):
		config_file = open(self.path)
		string = config_file.read()
		config_file.close()

		string = self.strip_comments(string)
		self.config = json.loads(string)
		
		return self.config

	def load_or_generate(self):
		if os.path.exists(self.path):
			return self.load()
		else:
			self.generate()
			self.save()
			return self.config

	def save(self):
		config_file = open(self.path, 'w')
		json.dump(self.config, config_file, indent=4)
		config_file.close()

	def dump(self):
		return json.dumps(self.config, indent=4)

	def generate(self):
		current_dir = os.path.dirname(self.path)
		cjdroute = os.path.join(current_dir, 'cjdroute')

		proc = subprocess.Popen([cjdroute, '--genconf'], stdout=subprocess.PIPE)

		string = proc.stdout.read().decode('utf-8')
		string = self.strip_comments(string)
		self.config = json.loads(string)

		return self.config

	def strip_comments(self, string):
		single_line_comment = re.compile(r"^\s*//.*$", re.MULTILINE)
		multi_line_comment = re.compile(r"/\*.*?\*/", re.DOTALL)

		string = re.sub(single_line_comment, "", string)
		string = re.sub(multi_line_comment, "", string)

		return string

	def rpc_settings(self):
		address = self.config['admin']['bind']
		password = self.config['admin']['password']
		host, port = address.split(':') # TODO: Won't work with IPv6
		return {'host': host, 'port': int(port), 'password': password}
