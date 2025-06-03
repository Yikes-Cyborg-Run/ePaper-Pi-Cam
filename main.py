from camera_classes import Action, Calc, Config, Display, LEDs, Log, Menu
import time, datetime
from gpiozero import LED, Button
from picamzero import Camera
# from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
# from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def main():
	home_dir=Path(__file__).parent.resolve() # Current directory

	# Create Photos dir if it doesn't exist
#	if not os.path.exists('Photos'): os.makedirs(archive_dir)
	photo_dir=Path(home_dir / 'Photos')
	photo_dir.mkdir(parents=True, exist_ok=True)

	# Create the log file and put today's date at the top
	# This file will be overwritten each time the script runs
	now=datetime.datetime.now()
	todays_date=now.strftime('%Y-%M-%D')
	with open(home_dir / 'log.log', 'w') as file:
		file.write('####### '+todays_date+' #######\n')
		file.close()

	# Initialize the ePaper display
#	epd=epd2in7_V2.EPD()
#	epd.init()

	# Create a list of fonts for font menu
#	font_dir=home_dir/'Fonts'
#	config=Config().load()
#	font_path=font_dir / config['font']
#	fontsize=int(config['fontsize'])

	# Load saved configuration
	config=Config().load()

	# Show splash.jpg upon startup -- can be disabled from Display Options menu
	Display().splash()

	# Start Camera() and set its configuration
	cam=Camera()
	# !!!!!!! Check to see if there is a difference in performance if they're color?
	cam.greyscale=True # Take photos in black & white... duh
	cam.still_size=(264, 176) # Resolution of the 2.7 GPIO display
	cam.brightness=int(config['brightness']) # can be -1.0 - 1.0
	cam.white_balance=str(config['whitebalance'].lower())

	photo_list=Action().photo_list() # Create a list of existing photos

	p=Button(5, pull_up=True) # used to take photo or select a menu item
	m=Button(19, pull_up=True) # opens the menu/goes back
	u=Button(13, pull_up=True) # menu selection +1
	d=Button(6, pull_up=True) # menu selection -1

	data=[0, 'Main Menu', False, 0] # set initial data to: [highlight=0, sel="Main Menu", drawn=False, photonum=0]

	try:
		# Start loop
		while True:
			h=data[0] # item to highlight in the menu
			sel=data[1] # selected item from menu
			drawn=data[2] # menu drawn, True or False
			num=data[3] # current photo number
			# MAIN MENU SELECTED
			if m.is_pressed:
				if sel=='Delete':
					data=[0,'Manual Scroll', False, num]
				else:
					data=[0,'Main Menu', False, 0]
				time.sleep(0.5) # need short delay or it will immediately revert to Main Menu

			# CAMERA MESSSAGE
			elif sel=='Camera':
				data=Display().camera_msg(data)
				if p.is_pressed: data=[0, 'Take Photos', False, num]

			# Actions and menu items that don't need a menu drawn
			elif sel=='Take Photos':
				if p.is_pressed:
					LEDs().flash(1)
					photo_list=Action().take_photo(cam, photo_list)
	#				LEDs().flash(0)

			# Manually Scroll through photos
			# Option to delete when photo button is pushed 
			elif sel=='Manual Scroll':
				data=Action().manual_scroll(u, d, photo_list, data)
				if p.is_pressed: data=[0, 'Delete', False, num]

			# DELETE SINGLE PHOTO WARNING
			elif sel=='Delete':
				data=Display().check_delete(data, photo_list)
				if p.is_pressed: data=[0, 'Delete Confirmed', False, num]

			# DELETE CONFIRMED
			elif sel=='Delete Confirmed':
				data=Action().delete_single_photo(num, photo_list[num])
				photo_list=Action().photo_list()

			# ARCHIVE MSG
			elif sel=='Archive Photos':
				data=Display().archive_msg(data, photo_list)
				if p.is_pressed: data=[0, 'Archive Confirmed', False, num]

			# ARCHIVE CONFIRMED
			elif sel=='Archive Confirmed':
				data=Action().archive_confirmed()

			# PURGE WARNING MSG
			elif sel=='Purge':
				data=Display().purge_warning(data, photo_list)
				if p.is_pressed: data=[0, 'Purge Confirmed', False, num]

			# Confirmed purge of all photos - All photos will be deleted
			elif sel=='Purge Confirmed':
				data=Action().purge_photo_dir(len(len(photo_list), True)) # True = display the msg
				photo_list=[]

			# TIMELAPSE - Message warning
			elif sel=='Time-Lapse Photography':
				data=Display().timelapse_msg(data)
				if p.is_pressed:
					Log().info("Timelapse initial button pushed")
					photo_list=Action().take_photo(cam, photo_list)
					future=Calc().future(int(config['timelapseduration']))
					data=[0, 'Timelapse Confirmed', False, num]

			# TIMELAPSE - Confirmed
			elif sel=='Timelapse Confirmed':
				if drawn==True:
					now_time=datetime.datetime.now()
					now=int(time.mktime(now_time.timetuple()))
					if now>future:
						photo_list=Action().take_photo(cam, photo_list)
						Log().info("Timelapse photo taken")
						future=Calc().future(int(config['timelapseduration']))
						data=[0, sel, False, 0]
				else:
					future=Calc().future(int(config['timelapseduration']))
					data=[0, sel, True, 0]

			# AUTOSCROLL - MSG
			elif sel=='Autoscroll':
				data=Display().autoscroll_msg(data, photo_list)
				if p.is_pressed:
					data=[0, 'Autoscroll Confirmed', False, num]
					future=Calc().future(int(config['autoscrollduration']))

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
							Log().info("Autoscroll Increment: "+str(num))
							future=Calc().future(int(config['autoscrollduration']))
							data=[0, sel, False, num]
					else:
						Action().display_photo(photo_list[num])
						future=Calc().future(int(config['autoscrollduration']))
						data=[0, sel, True, num]
				else:
					data=Display().no_photos(data)

			# Build the selected menu
			else:
				if drawn==False:
					Menu().build(h, sel, photo_list)
					drawn=True
				data=Menu().navigate(h, p, m, u, d, sel)
	except KeyboardInterrupt:
		Log().error("Interrupted by user keyboard.")
	finally:
		Log().info("Exiting program.")

if __name__ == '__main__':
	main()