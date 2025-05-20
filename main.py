from camera_classes import Config, Warn, Action, Menu, Log
import time, datetime
from gpiozero import LED, Button
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def main():
	home_dir=Path(__file__).parent.resolve() # Current directory
#	home_dir=Path.cwd() # Current directory

	# Create the log file and put today's date at the top
	# This file will be overwritten each time the script runs
	now=datetime.datetime.now()
	todays_date=now.strftime('%Y-%M-%D')
	with open(home_dir / 'log.log', 'w') as file:
		file.write('####### '+todays_date+' #######\n')
		file.close()

	# Initialize the ePaper display
	epd=epd2in7_V2.EPD()
	epd.init()

	# Create a list of fonts for font menu
	font_dir=home_dir/'Fonts'
	font_list=[]
	for f in list(font_dir.glob('*ttf')):
		if Path(f).is_file():
			font_list.append(f)

	# These items have a warning or message that will prompt the user for a response
	warn_list=['Camera', 'Delete All', 'Delete Single Photo', 'Camera', 'Time-Lapse Camera']

	config=Config().load()
	font_path=font_dir / config['font']
	fontsize=int(config['fontsize'])

	# Show splash.jpeg upon startup
	# This can be disabled in Camera Options
	image_dir=home_dir / 'Photos'
	if(config['showsplashscreen']=='Yes'):
		splash_photo=[home_dir / 'Resources' / 'splash.jpg']
		Action.display_photo(splash_photo, 0)
		image=Image.new('1', (epd.height, epd.width), 255)
		draw=ImageDraw.Draw(image)
		font=ImageFont.truetype(font_path, fontsize+4)
		draw.text((20, 50), "Starting up...", font=font, fill=0)
		epd.display(epd.getbuffer(image))

	# !!!!!!! Camera Options
	# https://raspberrypifoundation.github.io/picamera-zero/camera/
	# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	# There is an option in picamzero to set a timelapse!!!!!!!
	# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

	cam=Camera() # Start camera
	cam.greyscale=True # Take photos in black & white
	cam.still_size=(264, 176) # Resolution of the 2.7 GPIO display
	cam.brightness=int(config['brightness']) # can be -1.0 - 1.0

	# Build a list of saved photos already on file. 
	# New photos will appended to the end of list.
	Log().log("Building list of previously saved photos", 1)
	photo_list=[]
	for filename in list(image_dir.glob('*bmp', '*jpg', '*jpeg', '*gif', '*png')):
		if Path(f).is_file():
			img_path=image_dir/filename
			photo_list.append(img_path)
	Log().log(f"Photos currently on file: {len(photo_list)}.",1)

	p=Button(5, pull_up=True) # used to take photo or select a menu item
	m=Button(19, pull_up=True) # opens the menu/goes back
	u=Button(13, pull_up=True) # menu selection +1
	d=Button(6, pull_up=True) # menu selection -1

	data=[0, 'Main Menu', False] # set initial data to: [highlight=0, sel="Main Menu", drawn=False]
	scroll_data=[0, False] # set photo scrolling data to: [highlight=0, drawn=False]

	# Start looping
	while True:
		h=data[0] # item to highlight in the menu
		sel=data[1] # selected item from menu
		drawn=data[2] # menu drawn, True or False

		# Main Menu selected
		if m.is_pressed:
			data=[0,'Main Menu', False] # item highlighted, menu name, drawn
			scroll_data=[0, False, 0] # photo num, drawn, future

		# Warnings and Notices
		elif sel in warn_list:
			data=Warn().warn(p, sel, scroll_data[0], photo_list)

		# Actions and menu items that don't need a menu drawn
		elif sel=='Take Photos':
			photo_list=Action().take_photo(p, cam, photo_list)

		elif sel=='Manual Scroll':
			scroll_data=Action.manual_scroll(u, d, photo_list, scroll_data)
			if p.is_pressed:
				data=[0, 'Delete Single Photo', False]

		elif sel=='Autoscroll':
			scroll_data=Action().autoscroll(photo_list, scroll_data)

		elif sel=='Purge Confirmed':
			scroll_data=Action().purge_photo_dir(photo_list, scroll_data)

		# Build the selected menu
		else:
			if drawn==False:
				Menu().build(h, sel, photo_list)
				drawn=True
			data=Menu().navigate(h, p, m, u, d, sel)

if __name__ == '__main__':
    main()