import time, datetime, logging, re
import zipfile
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from gpiozero import LED #, Button
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from picamzero import Camera

# If you dont like my kumkuats, dont shake my tree

class Display():
	def __init__(self):
		self.epd=epd2in7_V2.EPD()
		self.epd.init()
		self.config=Config().load()
		self.home_dir=Path(__file__).parent.resolve()
		self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])
		self.fontsize=int(self.config['fontsize'])
		self.font=ImageFont.truetype(self.font_path, self.fontsize)
		self.header_font=ImageFont.truetype(self.font_path, self.fontsize+4)
		self.image=Image.new('1', (self.epd.height, self.epd.width), 255)
#		self.draw=self.image.transpose(self.image.ROTATE_180)
		self.draw=ImageDraw.Draw(self.image)

	# DRAW TEXT WITH A LARGER SIZED HEADER
	def text_with_header(self, x, y, header, text):
		self.draw.text((x, y), header, font=self.header_font, fill=0)
		self.draw.text((x, y+self.fontsize+10), text, font=self.font, fill=0)
		self.epd.display(self.epd.getbuffer(self.image))

	# DISPLAY PHOTO
	def photo(self, photo_path):
		Log().info(f"Loading file: {photo_path}....")
		image=Image.open(photo_path)
		image=image.resize((self.epd.height, self.epd.width))
		self.epd.display(self.epd.getbuffer(image))
		Log().info(f"Displayed file: {photo_path}")
		return None

	# CAMERA MESSAGE
	def camera_msg(self, data):
		if data[2]==False:
			txt="Menu button = Cancel"
			txt+=f"\n\nWhite Balance: {str(self.config['whitebalance'])}\n"
			txt+=f"Add Timestamp: {str(self.config['timestampphoto'])}\n"
			txt+=f"Brightness: {float(self.config['brightness'])}\n"
			txt+=f"Contrast: {str(self.config['contrast'])}\n"
#			txt+=f"Exposure: {str(self.config['exposure'])}\n"
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
		if data[2]==False:
			dur=Calc().convert_time_text(int(self.config['timelapseduration']))
			txt=f"\nWait time = {dur}\n\nPhoto button = Start\nMenu button = Cancel"
			Display().text_with_header(10, 5, "TIME-LAPSE READY", txt)
			data=[0, 'Time-Lapse', True, 0]
		return data

	# WARNING - PURGE ALL
	def purge_warning(self, data, photo_list):
		if data[2]==False:
			if len(photo_list)>0:
				Log().warning('Purge ALL Warning')
				txt=f"\n\nMenu button = Cancel\nPhoto button = Confirm"
				Display().text_with_header(10, 5, f"DELETE {len(photo_list)} PHOTOS?", txt)
				data=[0, 'Purge', True, 0]
			else:
				data=Display().no_photos(data)
		return data

	# NO PHOTOS MESSAGE
	def no_photos(self, data):
		if data[2]==False:
			Log().error("List selected, but no photos on file.")
			LEDs().LEDs(0, 0, 1)
			txt="\nThere are no photos\non file to show.\n\nPress menu button...."
			Display().text_with_header(10, 5, "NO PHOTOS", txt)
			data=[0, 'Main Menu', True, 0]
		return data

	# CHECK DELETE MESSAGE
	def delete_warning(self, data, photo_list):
		num=data[3]
		if data[2]==False:
			filename=photo_list[num]
			Log().info(f"Check delete: {filename}")
			image=Image.open(filename)
			draw=ImageDraw.Draw(image)
			draw.rectangle([(0, 0), (int(self.epd.width)*2, 70)], fill=0)
			font=ImageFont.truetype(self.font_path, self.fontsize+4)
			draw.text((10, 2), "DELETE PHOTO?", font=font, fill=255)
			font=ImageFont.truetype(self.font_path, self.fontsize-1)
			draw.text((10, self.fontsize+8), "Menu button = Cancel\nPhoto button = Confirm", font=font, fill=255)
			self.epd.display(self.epd.getbuffer(image))
			data=[0, 'Delete', True, num]
		else:
			data=[0, 'Delete', True, num]
		return data

	# SPLASH SCREEN
	def splash(self):
		if(self.config['showsplashscreen']=='Yes'):
			Display().photo(self.home_dir / 'Resources' / 'splash.jpg')
			image=Image.new('1', (self.epd.height, self.epd.width), 255)
			draw=ImageDraw.Draw(image)
			font=ImageFont.truetype(str(self.font_path), self.fontsize+4)
			draw.text((20, 50), "Starting up...", font=font, fill=0)
			self.epd.display(self.epd.getbuffer(image))

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
				# Camera options to add -- vflip, hflip, greyscale
				'Main Menu':['Camera', 'Time-Lapse', 'Manual Scroll', 'Autoscroll',  'Camera Options', 'Display Options', 'System Options'],

				'Camera Options':['Brightness', 'Contrast', 'Flash', 'Time-Lapse Duration', 'White Balance'],
				'Brightness':['-1.0', '-0.5', '-0.25', '0', '0.25', '0.5', '1.0'],
				'Contrast':['0', '1', '5', '10', '15', '20', '25', '32'],
#				'Exposure':['75', '200', '1000', '3000', '6000', '1238765'], # !!!!!!! In progress
				'Flash':['Auto', 'On', 'Off'],	
				'Time-Lapse Duration':['1', '30', '60', '300', '600', '1800', '3600'],
				'White Balance':['Auto', 'Cloudy', 'Daylight', 'Fluorescent', 'Indoor', 'Tungsten'],

				'Display Options':['Font', 'Font Size', 'Autoscroll Duration'], # 'Display Rotation', 
				'Font': self.font_list,
				'Font Size':['12', '14', '16', '18', '20', '22', '24'],
				'Autoscroll Duration':['10', '30', '60', '120', '300', '600'],
				'Display Rotation':['0', '90', '180', '270'],

				'System Options':['Archive Photos', 'Show Splash Screen', 'Timestamp Photo', 'Shut Down',  'Purge'],
				'Show Splash Screen':['Yes', 'No'],
				'Timestamp Photo':['Yes', 'No'],
				}
		# These do not need a menu created
		self.ignore_list=['Archive Photos', 'Autoscroll', 'Camera', 'Delete', 'Manual Scroll', 'Purge', 'Take Photo', 'Time-lapse Camera']

	# Build the selected menu
	# sel = selected menu to use, h = item that's highlighted, photo_list = to tally the total photos
	def build(self, h, sel, photo_list):
		config_val='- Im empty check me -'
		is_option_menu=False
		use_menu=self.menu_list[sel]
		options_list=Config().options_list()
		Log().info(f"{sel.upper()} -- {use_menu}")
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
			if check_config_item in options_list: saved_config_val=' - ('+self.config[check_config_item]+')'
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
		return

	# Function to navigate through the menu
	# h = highlighted item, p = photo button, m = menu button, u = up button, d = down button
	# sel = selected item that is returned when p is pressed to build the menu
	def navigate(self, h, p, m, u, d, sel, cam):
		use_menu=self.menu_list[sel]
		data=[h, sel, True, 0]
		limit=len(use_menu)-1
		if sel not in self.ignore_list:
			if p.is_pressed:
				data=[0, use_menu[h], False, 0]
				if (sel in self.menu_list['Camera Options']) or (sel in self.menu_list['Display Options']) or (sel in self.menu_list['System Options']):
					data=Config().save(sel, use_menu[h], cam)
			elif m.is_pressed: # go to main menu
				data=[0, 'Main Menu', False, 0]
			elif u.is_pressed:
				h+=1
				if h>limit:h=0
				data=[h, sel, False, 0]
			elif d.is_pressed:
				h-=1
				if h<0:h=limit
				data=[h, sel, False, 0]
		return data

class Action():
	def __init__(self):
		self.home_dir=Path(__file__).parent.resolve() # Current directory
		self.config=Config().load()
		self.image_dir=str(self.home_dir / 'Photos')
		self.fontsize=int(self.config['fontsize'])
		self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])
#		self.logger = logging.getLogger(__name__)
#		self.logging.basicConfig(filename='/home/pi/e-Paper-Pi-Cam/log.log', filemode='w', encoding='utf-8', level=logging.INFO)

	# PHOTO LIST
	# Build a list of saved photos already on file.
	# New photos will appended to the end of list.
	def photo_list(self):
			Log().info("Building list of previously saved photos")
			photo_list=[]
			dir=Path(self.image_dir)
			try:
				for filename in list(dir.glob('*jpg')):
					if Path(filename).is_file():
						img_path=self.image_dir / filename
						photo_list.append(img_path)
				Log().info(f"Photos currently on file: {len(photo_list)}.")
				return photo_list
			except Exception as e:
				Log().error(f"Could not create photo list.\nDetails:\n{e}")

	# TAKE PHOTO
	# cam = initialized camera object from main(), existing photo_list
	def take_photo(self, cam, photo_list):
		cam.brightness=float(self.config['brightness'])
		cam.contrast=float(self.config['contrast'])
#		cam.exposure=int(self.config['exposure'])
#		cam.gain=int(self.config['gain']) min and max vary
		cam.white_balance=str(self.config['whitebalance'].lower())
		LEDs().LEDs(0, 0, 1)
		timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
		filename=f'{timestamp}.jpg'

		# Any way to make the position dynamic based on the screen size? ??????? 
		if self.config['timestampphoto']=='Yes':
			cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5, 170])
		image_path=self.image_dir+'/'+filename
		Log().info(f"Taking photo: {image_path}")

		#Log().info(f"Taking photo:{image_path}")
		cam.take_photo(image_path)
		Display().photo(image_path)
		LEDs().LEDs(1, 0, 0)
		photo_list.append(image_path)
		return photo_list

	# MANUAL SCROLL
	# Tab through existing photos with u: up button, d: down button
	# Also uses: existing photo_list and data:[photo_increment, drawn - True or False]
	def manual_scroll(self, u, d, photo_list, data):
		num=data[3]
		drawn=data[2]
		if len(photo_list)>0:
			limit=len(photo_list)-1
			if drawn==True:
				if u.is_pressed:
					num+=1
					if num>limit:num=0
					data=[0, 'Manual Scroll', False, num]
				elif d.is_pressed:
					num-=1
					if num<0: num=limit
					data=[0, 'Manual Scroll', False, num]
			else:
				Display().photo(photo_list[num])
				data=[0, 'Manual Scroll', True, num]
		else:
			data=Display().no_photos(data)
		return data

	# DELETE
	# Deletes a single photo passed from Manual Scroll
	def delete_single_photo(self, num, file):
		Log().info(f"Attempting to delete: {file}....")
		try:
			next_num=num-1
			file=Path(file)
			file.unlink()
			txt=f"\nDeleted: {file}\nGoing back to photos...."
			Log().info(txt)
			Display().text_with_header(10, 5, "DELETED PHOTO", txt)
			time.sleep(.2) # ??????? Need sleep here?
			return [0, 'Manual Scroll', False, next_num]
		except Exception as e:
			Log().error(f"There was an error deleting file: {file}.\n Details:\n{e}")

	# ARCHIVE CONFIRMED
	# Creates a zip file to archive photos and then empty the Photos directory
	def archive_confirmed(self):
		archive_dir='Archived_Photos'
		now=datetime.datetime.now()
		Path(archive_dir).mkdir(parents=True, exist_ok=True)
		zip_path=f"{archive_dir}/Archived_Photos_{now.strftime('%Y-%m-%d_%H%M%S')}.zip"
		# Create the zip file
		Log().info(f"Attempting to archive photos to: {zip_path}....")
		try:
			photo_dir=Path('Photos')
			files=list(photo_dir.glob('*jpg'))
			with zipfile.ZipFile(zip_path, 'w') as zip_file:
				for f in files:
					if Path(f).is_file():
						try:
							zip_file.write(f)
							Log().info(f"Moved {f} to zip file.")
						except Exception as e:
							Log().error(f"Error archiving file: {f}.\n Details:\n{e}")
			Log().info(f"Archiving to {f} completed.")
		except Exception as e:
			Log().error(f"Error archiving to {zip_path}.\n Details:\n{e}")

		# Get total size of the Archive directory
		dir_size=0
		path=Path(archive_dir)
		dir_size=sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())
		dir_size=Calc().format_size(dir_size)
		success_text=f"Photos archived to: \n{archive_dir}.\nTotal size of archive: {dir_size}."
		Display().text_with_header(10, 5, "ARCHICE SUCCESSFUL", success_text)
		Log().info(success_text)
		time.sleep(3)
		data=Action().purge_confirmed(len(self.image_dir) , False) # False - dont need to show purge message
		return data

	# PURGE CONFIRMED
	# Delete ALL photos on file
	def purge_confirmed(self, num_photos, show_message):
		Log().info("Attempting to purge all photos...")
		del_dir=Path(self.image_dir)
		for file in del_dir.iterdir():
			if file.is_file():
				try:file.unlink()
				except Exception as e:Log().error(f"Could not delete: {file}.\n Details:\n{e}")
				Log().info(f"Deleted: {file}")
		Log().info(f"Deleted All {num_photos} photos")
		if show_message==True:
			txt="\nGoing back to main menu...."
			Display().text_with_header(10, 5, f"DELETED ALL\n{num_photos} PHOTOS", txt)
			time.sleep(2)
		return [0, 'Main Menu', False, 0]

class LEDs():
	def __init__(self):
		self.config=Config().load()

	# LEDs to show camera is busy or performing an action
	# Takes 0 or 1, 0=off, 1=on
	def LEDs(self, green, yellow, red):
		if self.config['showleds']=='Yes':
			LED_G=LED(20)
			LED_Y=LED(16)
			LED_R=LED(12)
			if green==1: LED_G.on()
			else: LED_G.off()
			if yellow==1: LED_Y.on()
			else: LED_Y.off()
			if red==1: LED_R.on()
			else: LED_R.off()

	# CAMERA FLASH
	# In progress ???????
	def flash(self, future):
		if self.config['photoflash']=='Yes':
			LED_FLASH=LED(23)
			now_time=datetime.datetime.now()
			now=int(time.mktime(now_time.timetuple()))
			if now>future:
				LED_FLASH.on()
				future=Calc().future(2)
			else:
				LED_FLASH.off()
			return future

class Calc():
	def __init__(self):
		self.config=Config().load()

	# Calculates a future time to load next picture in Autoscroll 
	# and to take a Time-Lapse photo
	def future(self, duration):
		now_time=datetime.datetime.now() # Get the current datetime
		now=int(time.mktime(now_time.timetuple())) # Make timestamp
		future_time=now_time+datetime.timedelta(seconds=duration) # Add autoscroll_duration to timestamp
		future=int(time.mktime(future_time.timetuple()))
		# Log the current and future timestamps
		Log().info(f"   NOW: {str(now)}")
		Log().info(f"FUTURE: {str(future)}")
		return future

	# Display the current timelapse setting
	# ??????? IN PROGRESS
	def convert_time_text(self, dur):
		suffix='...'
		if(dur<60):
			suffix=' second'
			dur=dur
		elif(dur>60 and dur<3600):
			suffix=' minute'
			dur=dur/60
		elif(dur>60 and dur>3600):
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
				Log().error(f"Could not load config.\nDetails:\n{e}")
		else:
			Log().error("No config file.")
		return config

	# Save config settings to txt file
	def save(self, config_item, v, cam):
		# Key names from the Camera/Display Options menus
		# Strip down, remove spaces and special characters, and make lowercase
		k=config_item.lower()
		k=re.sub(r'[^a-zA-Z0-9]', '', k)
		config=Config().load()
		config[k]=str(v) # Assign passed variable to item
		Log().info(f"Saving {config_item}....\n{k} - {v}")
		# Open txt file and save the updated config
		try:
			with open(self.config_path, 'w') as file:
				for key, value in config.items():
					file.write(f'{key}={value}\n')
				time.sleep(.5)
			txt=f"\n{config_item} = {str(v)}"
			Log().info(f"Saved {txt}")
			Display().text_with_header(10, 10, f"SAVED CONFIG", txt)
			time.sleep(1)
			return [0, 'Main Menu', False, 0]
		except Exception as e:
			Log().error(f"Could not save config.\nDetails:\n{e}")

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
				Log().error(f"Could create options list from config file.\nDetails:\n{e}")
		else:
			Log().error("No config file.")
		return options_list

class Log():
	def __init__(self):
		home_dir=Path(__file__).parent.resolve()
		self.logger=logging.getLogger(__name__)
		log_path=logging.FileHandler(home_dir/'log.log')
		format=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
		self.logger.setLevel(logging.DEBUG)
		log_path.setFormatter(format)
		self.logger.addHandler(log_path)
		console_handler=logging.StreamHandler()
		console_handler.setLevel(logging.DEBUG)
		console_handler.setFormatter(format)
		self.logger.addHandler(console_handler)

	def critical(self, msg): self.logger.critical(msg)
	def debug(self, msg): self.logger.debug(msg)
	def error(self, msg): self.logger.error(msg)
	def info(self, msg): self.logger.info(msg)
	def warning(self, msg): self.logger.warning(msg)

"""
### NEGATIVE EFFECT:
from picamzero import Camera
from time import sleep
import cv2
import os

home_dir = os.environ['HOME']
cam = Camera()
rgb_array = cam.capture_array()

bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
negative_bgr_array = 255 - bgr_array
cv2.imwrite(f"{home_dir}/Desktop/negativeImage.jpg", negative_bgr_array)


#### SKETCH
from time import sleep
import cv2
import os

home_dir = os.environ['HOME']
cam = Camera()
sleep(2)
rgb_array = cam.capture_array()
img = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)

# Convert to sketch
greyscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
inverted = 255 - greyscale
blur_inverted = cv2.GaussianBlur(inverted, (125, 125), 0)
inverted_blur = 255 - blur_inverted
sketch = cv2.divide(greyscale, inverted_blur, scale=256)
cv2.imwrite(f"{home_dir}/Desktop/sketchImage.jpg", sketch)

img=image.rotate(90,expand=True)
epd.set_frame_memory(img, 0, 0)
epd.display_frame()
epd.set_frame_memory(img, 0, 0)
epd.display_frame()

# just a little test example filling the screen black 8 pixels at a time:
pixel = Image.new('1', (8,8), 0)
for x in range(0,epd2in13.EPD_WIDTH,8):
    for y in range(0,epd2in13.EPD_HEIGHT,8):
        for fc in range(2):
            epd.set_frame_memory(pixel, x, y)
            epd.display_frame()
        print(x,y)

###################################
??????? Partial UPDATES ???????
###################################
The final test is about partial updates. To say the truth, I don’t love continuously updating an e-ink display as it has a limited number of refreshes (even if very big) and I think that you can use the full power of this kind of display when you want to show a static image which changes with a very low frequency.
The test shows partial updates on the e-ink display by showing a clock that runs for 10 seconds, with an inverse progress bar.
epd.displayPartBaseImage initializes the e-ink display to partial update mode. Then, a loop is executed for 10 seconds, continuously updating the image on the display.
The elapsed time will adjust the width of the progress bar by calculating at each loop the width of the first 3 rectangles. The 4th rectangle will just cover at each run the old time characters, in order to avoid the overlapping between old characters and new ones.
The updated image is displayed using epd.displayPartial, and there’s a pause of 0.2 seconds between each update.
After the end of the while loop, the display is switched back to full update mode.

	clear_display(epd)
	draw.text((0, 0), 'Test 9) Partial Updates', font = font15, fill = black)
	epd.displayPartBaseImage(epd.getbuffer(image))
	epd.init(epd.PART_UPDATE)

	num = 0
	start_time=time.time()
	elapsed = time.time()-start_time
	while (time.time()-start_time) <= 10:
		elapsed=time.time()-start_time
		progress = int(220-int(elapsed*10))
		draw.rectangle((120, 70, progress, 75), fill = black)
		draw.rectangle((progress, 70, 220, 75), fill = white)
		draw.rectangle([(progress,70),(220,75)],outline = black)

		draw.rectangle((120, 80, 220, 105), fill = white)
		draw.text((120, 80), time.strftime('%H:%M:%S'), font = font24, fill = black)
		epd.displayPartial(epd.getbuffer(image))
		time.sleep(0.2)
	epd.init(epd.FULL_UPDATE)
	time.sleep(2)

			# ??????? NEW RESIZING use "thumbnail" because it will keep image ratio
#			resized_image = image.copy() # thumbnail() modifies the image in place
#			resized_image.thumbnail((self.epd.height/2, self.epd.height/2), Image.LANCZOS) # LANCZOS = method for resampling or interpolating digital signals
#			resized_image.thumbnail((50, 50), Image.LANCZOS) # LANCZOS = method for resampling or interpolating digital signals
#			resized_image=resized_image.resize((500,500), Image.LANCZOS) 
#			image=resized_image

"""