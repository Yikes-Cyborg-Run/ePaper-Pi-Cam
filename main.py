import time, datetime, logging, os, re, time, zipfile
# -- Using the 2.7inch GPIO HAT
# -- See README for help with using another display
from waveshare_epd import epd2in7_V2 
from PIL import Image, ImageDraw, ImageFont
from gpiozero import LED, Button
from picamzero import Camera
from pathlib import Path

home_dir=Path(__file__).parent.resolve()
logger=logging.getLogger(__name__)
log_path=logging.FileHandler(home_dir/'log.log')
format=logging.Formatter(fmt='%(asctime)s - %(name)s - Line %(lineno)d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger.setLevel(logging.DEBUG)
log_path.setFormatter(format)
logger.addHandler(log_path)

class Display():
	def __init__(self):
		self.epd=epd2in7_V2.EPD() # -- EDIT HERE if using a different display
		self.epd.init()
		self.config=Config().load()
		self.home_dir=Path(__file__).parent.resolve()
		self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])
		self.fontsize=int(self.config['fontsize'])
		self.font=ImageFont.truetype(self.font_path, self.fontsize)
		self.header_font=ImageFont.truetype(self.font_path, self.fontsize+4)
		self.image=Image.new('1', (self.epd.height, self.epd.width), 255)
		self.draw=ImageDraw.Draw(self.image)

	# DRAW TEXT WITH A LARGER SIZED HEADER
	def text_with_header(self, x, y, header, text):
		self.draw.text((x, y), header, font=self.header_font, fill=0)
		self.draw.text((x, y+self.fontsize+10), text, font=self.font, fill=0)
		self.epd.display(self.epd.getbuffer(self.image))

	# DISPLAY PHOTO
	def photo(self, photo_path):
		logger.info(f"Loading file: {photo_path}....")
		image=Image.open(photo_path)
		image=image.resize((self.epd.height, self.epd.width))
		self.epd.display(self.epd.getbuffer(image))
		logger.info(f"Displayed file: {photo_path}")
		LEDs().LEDs(1, 0, 0)

	# CAMERA MESSAGE
	def camera_msg(self, data):
		if data[2]==False:
			txt="Menu button = Cancel\n"
			txt+=f"\nFlash = {self.config['flash']}\n"
			txt+=f"White Balance = {self.config['whitebalance']}\n"
			txt+=f"Exposure = {str(self.config['exposure'])}\n"
			txt+=f"Photo Color = {str(self.config['photocolor'])}\n"
			txt+=f"Brightness = {float(self.config['brightness'])}\n"
			txt+=f"Contrast = {str(self.config['contrast'])}\n"
			Display().text_with_header(10, 5, "CAMERA READY ", txt)
			return [0, 'Camera', True, 0]
		else:
			return data

	# AUTOSCROLL MESSAGE
	def autoscroll_msg(self, data, photo_list):
		if len(photo_list)>0:
			if data[2]==False:
				dur=Calc().convert_time_text(int(self.config['autoscrollduration']))
				txt=f"\nWait time = {dur} \n\nPhoto button = Start\nMenu button = Cancel"
				Display().text_with_header(10, 5, "START AUTOSCROLL", txt)
				data=[0,'Autoscroll', True, 0]
		else:
			data=Display().no_photos(data) # data=[0, 'Autoscroll', True, 0]
		return data

	# ARCHIVE MESSAGE
	def archive_msg(self, data, photo_list):
		s='s'
		LEDs().LEDs(0, 1, 0)
		num_photos=len(photo_list)
		if num_photos>0:
			if data[2]==False:
				if num_photos==1: s=''
				txt=f"Create zip file \n{len(photo_list)} photo{s} on file.\n"
				txt+="All files will then be deleted.\n\nPhoto button = Confirm\nMenu button = Cancel"
				Display().text_with_header(10, 5, "ARCHIVE PHOTOS", txt)
				data=[0,'Archive Photos', True, 0]
		else:
			data=Display().no_photos(data)
		return data

	# TIMELAPSE MESSAGE
	def timelapse_msg(self, data):
		LEDs().LEDs(0, 1, 0)
		if data[2]==False:
			dur=Calc().convert_time_text(int(self.config['timelapseduration']))
			txt=f"\nWait time = {dur}\n\nPhoto button = Start\nMenu button = Cancel"
			Display().text_with_header(10, 5, "TIME-LAPSE READY", txt)
			data=[0, 'Time-Lapse', True, 0]
		return data

	# NO PHOTOS MESSAGE
	def no_photos(self, data):
		LEDs().LEDs(0, 0, 1)
		if data[2]==False:
			logger.error("List selected, but no photos on file.")
			txt="\nThere are no photos\non file to show.\n\nPress menu button...."
			Display().text_with_header(10, 5, "NO PHOTOS", txt)
			data=[0, 'Main Menu', True, 0]
		return data

	# CHECK DELETE MESSAGE
	def delete_warning(self, data, photo_list):
		num=data[3]
		LEDs().LEDs(0, 0, 1)
		if data[2]==False:
			filename=photo_list[num]
			logger.info(f"Check delete: {filename}")
			image=Image.open(filename)
			image=image.resize((self.epd.height, self.epd.width))
			draw=ImageDraw.Draw(image)
			draw.rectangle([(0, 0), (int(self.epd.width)*2, 70)], fill=255)
			font=ImageFont.truetype(self.font_path, self.fontsize+5)
			draw.text((10, 2), "DELETE PHOTO?", font=font, fill=0)
			font=ImageFont.truetype(self.font_path, self.fontsize-1)
			draw.text((10, self.fontsize+8), "Menu button = Cancel\nPhoto button = Confirm", font=font, fill=0)
			self.epd.display(self.epd.getbuffer(image))
			data=[0, 'Delete', True, num]
		else:
			data=[0, 'Delete', True, num]
		return data

	# WARNING - PURGE ALL
	def purge_warning(self, data, photo_list):
		LEDs().LEDs(0, 0, 1)
		if data[2]==False:
			if len(photo_list)>0:
				logger.warning('Purge ALL Warning')
				txt=f"\n\nMenu button = Cancel\nPhoto button = Confirm"
				Display().text_with_header(10, 5, f"DELETE {len(photo_list)} PHOTOS?", txt)
				data=[0, 'Purge', True, 0]
			else:
				data=Display().no_photos(data)
		return data

	# SPLASH SCREEN
	def splash(self):
		if(self.config['showsplashscreen']=='Yes'):
			LEDs().LEDs(0, 1, 0)
			Display().photo(self.home_dir / 'Resources' / 'splash.jpg')
			time.sleep(1)

	def clear_and_shutdown(self):
		LEDs().LEDs(0, 1, 0)
		logger.info(f"Clearing display and shutting down.")
		self.epd.Clear()
		os.system("sudo shutdown -h now")

	def show_photo_and_shutdown(self, photo_list):
		if len(photo_list)>0:
			LEDs().LEDs(0, 1, 0)
			photo=photo_list[len(photo_list)-1]
			Display().photo(photo)
			logger.info(f"Showing photo: {photo} and shutting down.")
			os.system("sudo shutdown -h now")
		else:
			LEDs().LEDs(0, 0, 1)
			data=Display().no_photos(data=[0, 'Main Menu', False, 0])
			return data

class Menu():
	def __init__(self):
		self.config=Config().load()
		self.home_dir=Path(__file__).parent.resolve()
		self.image_dir=self.home_dir / 'Photos'
		self.font_dir=self.home_dir / 'Fonts'
		self.font_list=[] # Font menu
		fonts=list(Path(self.font_dir).glob('*ttf'))
		for f in fonts:
			if Path(f).is_file():
				self.font_list.append(f.name)
		self.font_size=int(self.config['fontsize'])
		self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])
		self.menu_list={
				'Main Menu':['Camera', 'Time-Lapse', 'Autoscroll', 'Manual Scroll', 'Camera Options', 'Display Options', 'System Options'],

				'Camera Options':['Brightness', 'Contrast', 'Exposure', 'Flash', 'Photo Resolution', 'Time-Lapse Duration', 'White Balance', 'Photo Color'],

				'Brightness':['-1.0', '-0.5', '-0.25', '0', '0.25', '0.5', '1.0'], 
				'Contrast':['0', '1', '5', '10', '15', '20', '25', '32'], 
				'Exposure':['100', '5000', '20000', '100000', '250000', '500000', '1000000',], 
				'Flash':['On', 'Off'], # - 'Auto' 
				'Photo Resolution':['264 x 176', '424 x 318', '708 x 532', '1180 x 886', '1968 x 1478', '3280 x 2464'],
				'Time-Lapse Duration':['1', '10', '30', '60', '300', '600', '1800', '3600'], 
				'Photo Color':['Black and White', 'Color'], 
				'White Balance':['Auto', 'Cloudy', 'Daylight', 'Fluorescent', 'Indoor', 'Tungsten'], 

				'Display Options':['Font', 'Font Size', 'Autoscroll Duration'], # 'Display Rotation', 
				'Font': self.font_list, 
				'Font Size':['12', '14', '16', '18', '20', '22', '24'], 
				'Autoscroll Duration':['10', '30', '60', '120', '300', '600'], 

				'System Options':['Archive Photos', 'Show Splash Screen', 'LEDs', 'Clear Display and Shut Down',  'Show Photo and Shut Down', 'Purge'],
				'Show Splash Screen':['Yes', 'No'],
				'LEDs':['On', 'Off'],
				}
		# These item selections don't need a menu created
		self.ignore_list=['Archive Photos', 'Autoscroll', 'Camera', 'Delete', 'Manual Scroll', 'Purge', 'Take Photo', 'Time-lapse Camera']

	# Build the selected menu
	# sel = selected menu to use, h = item that's highlighted, photo_list = to tally the total photos
	def build(self, h, sel, photo_list):
		config_val=''
		use_menu=self.menu_list[sel]
		options_list=Config().options_list()
		logger.info(f"h: {h} -- {sel.upper()} -- {use_menu}")
		if (sel in self.menu_list['Camera Options']) or (sel in self.menu_list['Display Options']) or (sel in self.menu_list['System Options']):
			k=sel.lower()
			k=re.sub(r'[^a-zA-Z0-9]', '', k)
			config_val=str(self.config[k])
		final_menu=''
		highlighted=use_menu[h]
		for item in use_menu:
			item=str(item)
			saved_config_val=''
			# If its a config option item, show value
			check_config_item=item.lower()
			check_config_item=re.sub(r'[^a-zA-Z0-9]', '', check_config_item)
			# Check config values for Option Menus
			if check_config_item in options_list: saved_config_val=' = '+self.config[check_config_item]
			# Mark the current config
			if item==config_val: config_notch=' x '
			else: config_notch=''
			# Show the total number of photos for these items
			if item=='Autoscroll' or item=='Manual Scroll' or item=='Purge' or item=='Archive Photos':
				final_item=item+f' - {str(len(photo_list))} photos'
			else:
				final_item=item+saved_config_val+config_notch
			if item==highlighted:
				final_item='-- '+final_item # add a mark to the one that's highlighted
			final_menu+=final_item+'\n'
		Display().text_with_header(10, 0, sel.upper(), final_menu)

	# Function to navigate through the menu
	# h = highlighted item, p = photo button, m = menu button, u = up button, d = down button
	# sel = selected item that is returned when p is pressed to build the menu
	def navigate(self, h, p, m, u, d, sel, cam):
		use_menu=self.menu_list[sel]
		data=[h, sel, True, 0]
		limit=len(use_menu)-1
		if sel not in self.ignore_list:
			if p.is_pressed:
				LEDs().LEDs(0, 0, 1)
				data=[0, use_menu[h], False, 0]
				if (sel in self.menu_list['Camera Options']) or (sel in self.menu_list['Display Options']) or (sel in self.menu_list['System Options']):
					data=Config().save(sel, use_menu[h], cam)
			elif m.is_pressed: # go to main menu
				LEDs().LEDs(0, 0, 1)
				data=[0, 'Main Menu', False, 0]
			elif u.is_pressed:
				LEDs().LEDs(0, 1, 0)
				h+=1
				if h>limit:h=0
				data=[h, sel, False, 0]
			elif d.is_pressed:
				LEDs().LEDs(0, 1, 0)
				h-=1
				if h<0:h=limit
				data=[h, sel, False, 0]
		return data

class Action():
	def __init__(self):
		self.home_dir=Path(__file__).parent.resolve()
		self.config=Config().load()
		self.image_dir=str(self.home_dir / 'Photos')
		self.fontsize=int(self.config['fontsize'])
		self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])

	# PHOTO LIST
	# Build a list of saved photos already on file.
	# New photos will appended to the end of list.
	def photo_list(self):
			logger.info("Building list of previously saved photos")
			photo_list=[]
			dir=Path(self.image_dir)
			try:
				for filename in list(dir.glob('*jpg')):
					if Path(filename).is_file():
						img_path=self.image_dir / filename
						photo_list.append(img_path)
				logger.info(f"Photos currently on file: {len(photo_list)}.")
				return photo_list
			except Exception as e:
				logger.error(f"Could not create photo list.\nDetails:\n{e}")

	# TAKE PHOTO
	# cam = initialized camera object from main(), existing photo_list
	def take_photo(self, cam, photo_list):
		cam.brightness=float(self.config['brightness'])
		cam.contrast=float(self.config['contrast'])
		cam.exposure=int(self.config['exposure'])
		res_str=self.config['photoresolution']
		res_width, res_height=res_str.split(' x ')
		if str(self.config['photocolor']) =='Black and White': cam.greyscale=True
		cam.still_size=(int(res_width), int(res_height)) # Resolution of photo that will be taken
		cam.white_balance=str(self.config['whitebalance'].lower())
		LEDs().LEDs(0, 0, 1)
		timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		filename=f'{timestamp}.jpg'
		image_path=self.image_dir+'/'+filename
		logger.info(f"Taking photo: {image_path}")
		cam.take_photo(image_path)
		Display().photo(image_path)
		photo_list.append(image_path)
		return photo_list

	# MANUAL SCROLL
	# Tab through existing photos with u: up button, d: down button
	# Also uses: existing photo_list and data:[photo_increment, drawn - True or False]
	def manual_scroll(self, u, d, photo_list, data):
		num=data[3]
		drawn=data[2]
		LEDs().LEDs(1, 0, 0)
		if len(photo_list)>0:
			limit=len(photo_list)-1
			if drawn==True:
				if u.is_pressed:
					LEDs().LEDs(0, 1, 0)
					num+=1
					if num>limit:num=0
					data=[0, 'Manual Scroll', False, num]
				elif d.is_pressed:
					LEDs().LEDs(0, 1, 0)
					num-=1
					if num<0: num=limit
					data=[0, 'Manual Scroll', False, num]
			else:
				Display().photo(photo_list[num])
				data=[0, 'Manual Scroll', True, num]
				LEDs().LEDs(1, 0, 0)
		else:
			data=Display().no_photos(data)
		return data

	# DELETE
	# Deletes a single photo passed from Manual Scroll
	def delete_single_photo(self, num, file):
		logger.info(f"Attempting to delete: {file}....")
		try:
			LEDs().LEDs(0, 0, 1)
			next_num=num-1
			file=Path(file)
			file.unlink()
			txt=f"\nDeleted: {file}\nGoing back to photos...."
			logger.info(txt)
			Display().text_with_header(10, 5, "DELETED PHOTO", txt)
			time.sleep(.2)
			LEDs().LEDs(0, 0, 0)
			return [0, 'Manual Scroll', False, next_num]
		except Exception as e:
			logger.error(f"There was an error deleting file: {file}.\n Details:\n{e}")

	# ARCHIVE CONFIRMED
	# Creates a zip file to archive photos and then empty the Photos directory
	def archive_confirmed(self):
		LEDs().LEDs(1, 0, 0)
		archive_dir=self.home_dir/'Archived_Photos'
		now=datetime.datetime.now()
		Path(archive_dir).mkdir(parents=True, exist_ok=True)
		zip_path=f"{archive_dir}/Archived_Photos_{now.strftime('%Y-%m-%d_%H%M%S')}.zip"
		# Create the zip file
		logger.info(f"Attempting to archive photos to: {zip_path}....")
		try:
			photo_dir=Path(self.home_dir / 'Photos')
			files=list(photo_dir.glob('*jpg'))
			with zipfile.ZipFile(zip_path, 'w') as zip_file:
				for f in files:
					if Path(f).is_file():
						try:
							zip_file.write(f)
							logger.info(f"Moved {f} to zip file.")
						except Exception as e:
							logger.critical(f"Error archiving file: {f}.\n Details:\n{e}")
				zip_file.close()

			logger.info(f"Archiving to {f} completed.")
		except Exception as e:
			logger.error(f"Error archiving to {zip_path}.\n Details:\n{e}")

		# Get total size of the Archive directory
		dir_size=0
		path=Path(archive_dir)
		dir_size=sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
		dir_size=Calc().format_size(dir_size)
		success_text=f"Photos archived to: \n{archive_dir}.\nTotal size of archive: {dir_size}."
		Display().text_with_header(10, 5, "ARCHICE SUCCESSFUL", success_text)
		logger.info(success_text)
		time.sleep(3)
		data=Action().purge_confirmed(len(self.image_dir) , False) # False - dont need to show purge message
		LEDs().LEDs(0, 0, 0)
		return data

	# PURGE CONFIRMED
	# Delete ALL photos on file
	def purge_confirmed(self, num_photos, show_message):
		LEDs().LEDs(1, 1, 1)
		logger.info("Attempting to purge all photos...")
		del_dir=Path(self.image_dir)
		for file in del_dir.iterdir():
			if file.is_file():
				try:file.unlink()
				except Exception as e:logger.error(f"Could not delete: {file}.\n Details:\n{e}")
				logger.info(f"Deleted: {file}")
		logger.info(f"Deleted All {num_photos} photos")
		if show_message==True:
			txt="\nGoing back to main menu...."
			Display().text_with_header(10, 5, f"DELETED ALL\n{num_photos} PHOTOS", txt)
			time.sleep(2)
		LEDs().LEDs(0, 0, 0)
		return [0, 'Main Menu', False, 0]

class LEDs():
	def __init__(self):
		self.config=Config().load()
		self.LED_G=LED(20)
		self.LED_Y=LED(16)
		self.LED_R=LED(12)

	# LEDs to show camera is busy or performing an action
	# Takes 0 or 1, 0=off, 1=on
	def LEDs(self, green, yellow, red):
		if self.config['leds']=='On':
			if green==1: self.LED_G.on()
			else: self.LED_G.off()
			if yellow==1: self.LED_Y.on()
			else: self.LED_Y.off()
			if red==1: self.LED_R.on()
			else: self.LED_R.off()

	# CAMERA FLASH
	def flash(self, LED_FLASH, on_or_off):
		if self.config['flash']=='On':
			if on_or_off==1:
				LED_FLASH.on()
			else:
				LED_FLASH.off()

class Calc():
	def __init__(self):
		self.config=Config().load()

	# Calculates a future time to load next picture in Autoscroll and to take a Time-Lapse photo
	def future(self, duration):
		now_time=datetime.datetime.now() # Get the current datetime
		now=int(time.mktime(now_time.timetuple())) # Make timestamp
		future_time=now_time+datetime.timedelta(seconds=duration) # Add autoscroll_duration to timestamp
		future=int(time.mktime(future_time.timetuple()))
		# Log the current and future timestamps
		logger.info(f"     NOW: {str(now)}")
		logger.info(f"DURATION: {str(duration)}")
		logger.info(f"  FUTURE: {str(future)}")
		return future

	# Display a readable time setting
	def convert_time_text(self, dur):
		suffix='...'
		if(dur<=60):
			suffix=' second'
			dur=dur
		elif(dur>60 and dur<3600):
			suffix=' minute'
			dur=dur/60
		elif(dur>60 and dur>=3600):
			suffix=' hour'
			dur=dur/3600
		# format the text to display
		if dur!=1: 
			final=str(dur)+suffix+'s'
		else: 
			final=str(dur)+suffix
		return final

	# Convert bytes into a readable format
	def format_size(self, size_bytes):
		if size_bytes < 1024:
			return f"{size_bytes} B"
		elif size_bytes < 1024 * 1024:
			size_kb = size_bytes / 1024
			return f"{size_kb:.2f} KB"
		elif size_bytes < 1024 * 1024 * 1024:
			size_mb = size_bytes / (1024 * 1024)
			return f"{size_mb:.2f} MB"
		else:
			size_gb = size_bytes / (1024 * 1024 * 1024)
			return f"{size_gb:.2f} GB"

class Config():
	def __init__(self):
		self.home_dir=Path(__file__).parent.resolve()
		self.config_path=self.home_dir / 'config.txt'

	# Load config settings from txt file
	def load(self):
		config={}
		if Path(self.config_path).is_file():
			try:
				with open(self.config_path, 'r') as file:
					for line in file:
						if '=' in line:
							key, value=line.strip().split('=', 1)
							config[key]=value
			except Exception as e:
				logger.error(f"Could not load config.\nDetails:\n{e}")
		else:
			logger.error("No config file.")
		return config

	# Save config settings to txt file
	def save(self, config_item, v, cam):
		# Key names from the Camera Options and Display Options menus
		# Strip down, remove spaces and special characters, and make lowercase
		k=config_item.lower()
		k=re.sub(r'[^a-zA-Z0-9]', '', k)
		config=Config().load()
		config[k]=str(v) # Assign passed variable 'v' to item
		logger.info(f"Saving {config_item}....\n{k} - {v}")
		# Open file and save the updated config
		try:
			with open(self.config_path, 'w') as file:
				for key, value in config.items():
					file.write(f'{key}={value}\n')
				time.sleep(.5)
			txt=f"\n{config_item} = {str(v)}"
			logger.info(f"Saved {txt}")
			Display().text_with_header(10, 10, f"SAVED CONFIG", txt)
			time.sleep(1)
			return [0, 'Main Menu', False, 0]
		except Exception as e:
			logger.error(f"Could not save config.\nDetails:\n{e}")

	def options_list(self):
		options_list=[]
		if Path(self.config_path).is_file():
			try:
				with open(self.config_path, 'r') as file:
					for line in file:
						if '=' in line:
							l=line.strip().split('=')
							key=l[0]
							options_list.append(key)
			except Exception as e:
				logger.error(f"Could create options list from config file.\nDetails:\n{e}")
		else:
			logger.error("No config file.")
		return options_list

#################################################
# -- Main
#################################################
def main():
	LEDs().LEDs(0, 1, 0)
	home_dir=Path(__file__).parent.resolve() # Current directory

	# Create Photos dir if it doesn't exist
	photo_dir=Path(home_dir / 'Photos')
	photo_dir.mkdir(parents=True, exist_ok=True)

	# Create the log file and print today's date at the header
	# This file will be overwritten each time the script runs
	now=datetime.datetime.now()
	todays_date=now.strftime('%Y-%M-%D')
	with open(home_dir / 'log.log', 'w') as file:
		file.write('####### '+todays_date+' #######\n')
		file.close()

	# Load saved configuration
	config=Config().load()

	# Show splash.jpg upon startup -- can be disabled from System Options menu
	Display().splash()

	# Start Camera() and set its configuration
	cam=Camera()

	# Create a list of existing photos
	photo_list=Action().photo_list() 

	# Button setup
	p=Button(5, pull_up=True) # used to take photo or select a menu item
	m=Button(19, pull_up=True) # opens the menu/goes back
	u=Button(13, pull_up=True) # menu selection +1
	d=Button(6, pull_up=True) # menu selection -1

	data=[0, 'Main Menu', False, 0] # set initial data to: [highlight=0, sel="Main Menu", drawn=False, photonum=0]
	future=0
	LED_FLASH=LED(23)
	logger.info("Starting")

	try:
		# Start program loop
		while True:
			h=data[0] # item to highlight in the menu
			sel=data[1] # selected item from menu
			drawn=data[2] # menu drawn, True or False
			num=data[3] # current photo number

			# MAIN MENU SELECTED
			if m.is_pressed:
				LEDs().LEDs(0, 1, 0)
				if sel=='Delete':
					data=[0,'Manual Scroll', False, num]
				else:
					data=[0,'Main Menu', False, 0]
				time.sleep(0.5) # need short delay or it will immediately revert to Main Menu

			# CAMERA MESSSAGE
			elif sel=='Camera':
				data=Display().camera_msg(data)
				LEDs().LEDs(1, 0, 0)
				if p.is_pressed: 
					data=[0, 'Take Photos', False, num]

			# Actions and menu items that don't need a menu drawn
			elif sel=='Take Photos':
				now_time=datetime.datetime.now() # Get the current datetime
				now=int(time.mktime(now_time.timetuple())) # Make timestamp
				if p.is_pressed:
					future=Calc().future(1.75) # Keep the flash LED on for 1.75 seconds
					LEDs().flash(LED_FLASH, 1)
					photo_list=Action().take_photo(cam, photo_list)
				if now>future:
					LEDs().flash(LED_FLASH, 0)
				LEDs().LEDs(1, 0, 0)

			# Manually Scroll through photos
			# Option to delete when photo button is pushed 
			elif sel=='Manual Scroll':
				if len(photo_list)>0:
					data=Action().manual_scroll(u, d, photo_list, data)
					if p.is_pressed:
						LEDs().LEDs(0, 1, 0)
						data=[0, 'Delete', False, num]
				else:
					data=Display().no_photos(data)

			# DELETE SINGLE PHOTO WARNING
			# Confirmed when photo button is pressed
			elif sel=='Delete':
				data=Display().delete_warning(data, photo_list)
				if p.is_pressed: data=[0, 'Delete Confirmed', False, num]

			# DELETE CONFIRMED
			elif sel=='Delete Confirmed':
				data=Action().delete_single_photo(num, photo_list[num])
				photo_list=Action().photo_list()

			# ARCHIVE MESSAGE
			# Confirmed when photo button is pressed
			elif sel=='Archive Photos':
				data=Display().archive_msg(data, photo_list)
				if p.is_pressed: data=[0, 'Archive Confirmed', False, num]

			# ARCHIVE CONFIRMED
			elif sel=='Archive Confirmed':
				data=Action().archive_confirmed()
				photo_list=[]

			# PURGE WARNING MESSAGE
			# Confirmed when photo button is pressed
			elif sel=='Purge':
				data=Display().purge_warning(data, photo_list)
				if p.is_pressed: data=[0, 'Purge Confirmed', False, num]

			# Confirmed purge of all photos - All photos will be deleted
			elif sel=='Purge Confirmed':
				data=Action().purge_confirmed(len(photo_list), True) # True = display the msg
				photo_list=[]
	
			# Clear display and shut down
			elif sel=='Clear Display and Shut Down':
				data=Display().clear_and_shutdown()

			# Show Photo and Shut Down
			# Displays most recent photo taken before shutting down
			elif sel=='Show Photo and Shut Down':
				data=Display().show_photo_and_shutdown(photo_list)

			# TIMELAPSE MESSAGE
			# Confirmed when photo button is pressed
			elif sel=='Time-Lapse':
				data=Display().timelapse_msg(data)
				if p.is_pressed:
					logger.info("Timelapse initial button pushed")
					photo_list=Action().take_photo(cam, photo_list)
					data=[0, 'Timelapse Confirmed', False, num]
					future=0

			# TIMELAPSE - Confirmed
			elif sel=='Timelapse Confirmed':
				if drawn==True:
					LEDs().LEDs(1, 0, 0)
					now_time=datetime.datetime.now()
					now=int(time.mktime(now_time.timetuple()))
					if now>future:
						photo_list=Action().take_photo(cam, photo_list)
						logger.info("Timelapse photo taken")
						future=Calc().future(int(config['timelapseduration']))
						data=[0, sel, False, 0]
				else:
					data=[0, sel, True, 0]

			# AUTOSCROLL - MESSAGE
			elif sel=='Autoscroll':
				data=Display().autoscroll_msg(data, photo_list)
				if p.is_pressed:
					data=[0, 'Autoscroll Confirmed', False, num]
					future=0

			# AUTOSCROLL
			# Needed to put this in main, in order to better calculate the time comparisson.
			elif sel=='Autoscroll Confirmed':
				if len(photo_list)>0:
					if drawn==True:
						now_time=datetime.datetime.now()
						now=int(time.mktime(now_time.timetuple()))
						if now>future:
							num+=1
							if num>=len(photo_list)-1: num=0
							logger.info("Autoscroll Increment: "+str(num))
							future=Calc().future(int(config['autoscrollduration']))
							data=[0, sel, False, num]
					else:
						Display().photo(photo_list[num])
						data=[0, sel, True, num]
				else:
					data=Display().no_photos(data)

			# Build the selected menu
			else:
				if drawn==False:
					Menu().build(h, sel, photo_list)
					drawn=True
				data=Menu().navigate(h, p, m, u, d, sel, cam)
				LEDs().LEDs(1, 0, 0)

	except KeyboardInterrupt:
		logger.error("Interrupted by user - Keyboard cancel.")
	finally:
		logger.info("Exiting program.")

if __name__ == '__main__':
	main()