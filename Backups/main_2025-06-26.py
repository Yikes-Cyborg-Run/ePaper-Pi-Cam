# MAIN BRANCH
from eppc import Action, Calc, Config, Display, LEDs, Log, Menu
import time, datetime #, logging, threading 
from gpiozero import LED, Button
from picamzero import Camera
from pathlib import Path

def main():
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
	cam.greyscale=True # Take photos in black & white... duh

	size=cam.still_size
	print(f"{size}")
	# Create a list of existing photos
	photo_list=Action().photo_list() 

	# Button setup
	p=Button(5, pull_up=True) # used to take photo or select a menu item
	m=Button(19, pull_up=True) # opens the menu/goes back
	u=Button(13, pull_up=True) # menu selection +1
	d=Button(6, pull_up=True) # menu selection -1

	data=[0, 'Main Menu', False, 0] # set initial data to: [highlight=0, sel="Main Menu", drawn=False, photonum=0]

	future=0

#	flash_LED=threading.Thread(target=LEDs.flash)
#	flash_LED.start()
#	print("Loop start")

	LED_FLASH=LED(23)

	try:
		# Start program loop
		while True:
			h=data[0] # item to highlight in the menu
			sel=data[1] # selected item from menu
			drawn=data[2] # menu drawn, True or False
			num=data[3] # current photo number

			# MAIN MENU SELECTED
			if m.is_pressed:
				LEDs().LEDs(1, 0, 0)
				if sel=='Delete':
					data=[0,'Manual Scroll', False, num]
				else:
					data=[0,'Main Menu', False, 0]
				time.sleep(0.5) # need short delay or it will immediately revert to Main Menu
				LEDs().LEDs(0, 0, 0)

			# CAMERA MESSSAGE
			elif sel=='Camera':
				data=Display().camera_msg(data)
				if p.is_pressed: data=[0, 'Take Photos', False, num]

			# Actions and menu items that don't need a menu drawn
			elif sel=='Take Photos':
				now_time=datetime.datetime.now() # Get the current datetime
				now=int(time.mktime(now_time.timetuple())) # Make timestamp
				if p.is_pressed:
					future=Calc().future(1.75) # Keep the flash LED on for 1.75 seconds
					LEDs().flash(LED_FLASH, 1)
					photo_list=Action().take_photo(cam, photo_list)
#				Log().info(f"Now: {now} -- Future: {future}")
				if now>future:
					LEDs().flash(LED_FLASH, 0)

			# Manually Scroll through photos
			# Option to delete when photo button is pushed 
			elif sel=='Manual Scroll':
				if len(photo_list)>0:
					data=Action().manual_scroll(u, d, photo_list, data)
					if p.is_pressed:
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
			elif sel=='Show Photo and Shut Down':
				data=Display().show_photo_and_shutdown(photo_list)

			# TIMELAPSE MESSAGE
			# Confirmed when photo button is pressed
			elif sel=='Time-Lapse':
				data=Display().timelapse_msg(data)
				if p.is_pressed:
					Log().info("Timelapse initial button pushed")
					photo_list=Action().take_photo(cam, photo_list)
					data=[0, 'Timelapse Confirmed', False, num]
					future=0

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
							Log().info("Autoscroll Increment: "+str(num))
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
	except KeyboardInterrupt:
		Log().error("Interrupted by user - Keyboard cancel.")
#		cam.close()
	finally:
		Log().info("Exiting program.")

if __name__ == '__main__':
	main()
