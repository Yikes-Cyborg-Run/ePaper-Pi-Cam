from camera_classes import Config, Warn, Action, Menu, Calc, Log
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
	config=Config().load()
	font_path=font_dir / config['font']
	fontsize=int(config['fontsize'])

	# Show splash.jpeg upon startup
	# This can be disabled in Camera Options
	if(config['showsplashscreen']=='Yes'):
		Action().display_photo(home_dir / 'Resources' / 'splash.jpg')
		image=Image.new('1', (epd.height, epd.width), 255)
		draw=ImageDraw.Draw(image)
		font=ImageFont.truetype(str(font_path), fontsize+4)
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
	cam.whitebalance=str(config['whitebalance'].lower())

	photo_list=Action().photo_list()

	p=Button(5, pull_up=True) # used to take photo or select a menu item
	m=Button(19, pull_up=True) # opens the menu/goes back
	u=Button(13, pull_up=True) # menu selection +1
	d=Button(6, pull_up=True) # menu selection -1

	data=[0, 'Main Menu', False, 0] # set initial data to: [highlight=0, sel="Main Menu", drawn=False, photonum=0]

	# Start loop
	while True:
		h=data[0] # item to highlight in the menu
		sel=data[1] # selected item from menu
		drawn=data[2] # menu drawn, True or False
		num=data[3]

		# MAIN MENU SELECTED
		if m.is_pressed:
			data=[0,'Main Menu', False, 0] # item highlighted, menu name, drawn, photonum

		# CAMERA MESSSAGE
		elif sel=='Camera':
			data=Warn().camera_msg(data)
			if p.is_pressed:
				data=[0, 'Take Photos', False, num]

		# Actions and menu items that don't need a menu drawn
		elif sel=='Take Photos':
			if p.is_pressed:
				photo_list=Action().take_photo(cam, photo_list)

		# Manually Scroll through photos
		# Option to delete when photo button s pushed 
		elif sel=='Manual Scroll':
			data=Action().manual_scroll(u, d, photo_list, data)
			if p.is_pressed:
				data=[0, 'Delete', False, num]

		# DELETE SINGLE PHOTO WARNING
		elif sel=='Delete':
			data=Warn().delete_warning(data, photo_list)
			if p.is_pressed:
				data=[0, 'Delete Confirmed', False, num]

		# DELETE CONFIRMED
		elif sel=='Delete Confirmed':
			data=Action().delete_single_photo(photo_list[num])
			photo_list=Action().photo_list()

		# PURGE WARNING MSG
		elif sel=='Purge':
			data=Warn().purge_warning(data, photo_list)
			if p.is_pressed:
				data=[0, 'Purge Confirmed', False, num]

		# Confirmed purge of all photos - All photos will be deleted
		elif sel=='Purge Confirmed':
			data=Action().purge_photo_dir(photo_list)
			photo_list=[]

		# TIMELAPSE - MSG
		elif sel=='Time-Lapse Photo':
			data=Warn().timelapse_msg(data)
			if p.is_pressed:
				print('tmelapse initial button pusehed')
				photo_list=Action().take_photo(cam, photo_list)
				future=Calc().future(int(config['timelapseduration']))
				data=[0, 'Timelapse Confirmed', False, num]

		# TIMELAPSE
		elif sel=='Timelapse Confirmed':
			if drawn==True:
				now_time=datetime.datetime.now()
				now=int(time.mktime(now_time.timetuple()))
				if now>future:
					photo_list=Action().take_photo(cam, photo_list)
					Log().log("Timelapse photo taken", 1)
					future=Calc().future(int(config['timelapseduration']))
					data=[0, "Timelapse Confirmed", False, 0]
			else:
				future=Calc().future(int(config['timelapseduration']))
				data=[0, "Timelapse Confirmed", True, 0]


		# AUTOSCROLL - MSG
		elif sel=='Autoscroll':
			data=Warn().autoscroll_msg(data, photo_list)
			if p.is_pressed:
				data=[0, 'Autoscroll Confirmed', False, num]
				future=Calc().future(int(config['autoscrollduration']))

		# AUTOSCROLL
		# Needed to put this in main, in order to better calculate the time comparisson.
		elif sel=='Autoscroll Confirmed':
			print('autoscroll going now')
			if len(photo_list)>0:
				if drawn==True:
					now_time=datetime.datetime.now()
					now=int(time.mktime(now_time.timetuple()))
					if now>future:
						num+=1
						if num>=len(photo_list)-1: num=0
						Log().log("Autoscroll Increment: "+str(num), 1)
						future=Calc().future(int(config['autoscrollduration']))
						data=[0, "Autoscroll Confirmed", False, num]
				else:
					Action().display_photo(photo_list[num])
					future=Calc().future(int(config['autoscrollduration']))
					data=[0, "Autoscroll Confirmed", True, num]
			else:
				data=Warn().no_photos(data)

		# Build the selected menu
		else:
			if drawn==False:
				Menu().build(h, sel, photo_list)
				drawn=True
			data=Menu().navigate(h, p, m, u, d, sel)

if __name__ == '__main__':
    main()