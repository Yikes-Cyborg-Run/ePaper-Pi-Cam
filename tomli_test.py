# https://tomlkit.readthedocs.io/en/latest/

import tomlkit, re
from pathlib import Path

class Config():
	def __init__(self):
		self.home_dir=Path(__file__).parent.resolve()
#		self.config_path=self.home_dir / 'config.txt'
		self.config_path=self.home_dir / 'config.toml'

	# Load config settings from txt file
	def load(self):
		try:
			with open(self.config_path, "rb") as f:
				data = tomlkit.load(f)
			return(data)
		except FileNotFoundError:
			print(f"Error: File not found at '{self.config_path}'")
			return None
		except tomlkit.TOMLDecodeError as e:
			print(f"Error: TOML parsing error: {e}")
			return None

	# Save config settings to txt file
	def save(self, config_item, v):
		# Key names from the Camera/Display Options menus
		# Strip down, remove spaces and special characters, and make lowercase
		k=config_item.lower()
		k=re.sub(r'[^a-zA-Z0-9]', '', k)
		config=Config().load()
		config[k]=str(v)
		with open(self.config_path, 'w') as file:
		    tomlkit.dump(config, file)

Config().save('whitebalance', 'indoor')