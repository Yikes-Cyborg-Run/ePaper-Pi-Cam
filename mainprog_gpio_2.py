# from gpiozero import LED, Button
import RPi.GPIO as GPIO
import time, datetime, os, logging
from datetime import datetime, date
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
#from waveshare_epd import epd4in2_V2 # -- the 4.2inch display
from PIL import Image, ImageDraw, ImageFont

now=datetime.now()
todays_date=now.strftime("%Y-%M-%D")
log_path="/home/pi/ePaper-Pi-Cam/log.log"
with open(log_path, "w") as file:
    file.write('####### '+todays_date+' #######\n')
    file.close()

logger=logging.getLogger(log_path)
logging.basicConfig(filename=log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)

def log(msg, err_type):
	global logger
	err=["ERROR", "INFO", "DEBUG", "CRITICAL", "WARNING"]
	print(err[err_type]+" : "+msg)
	if(err_type==0):logger.error(msg)
	elif(err_type==1):logger.info(msg)
	elif(err_type==2):logger.debug(msg)
	elif(err_type==3):logger.critical(msg)
	elif(err_type==4):logger.warning(msg)

def take_photo():
    global image_folder, photo_array, timestamp_photo
    LEDs(0,0,1)
    timestamp=datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
    filename=f"{timestamp}.jpg" # Construct the filename
    if timestamp_photo==True: # Check if timestamping is enabled in config...
        cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5,170]) # add a timestamp to photo if it is
    cam.take_photo(image_folder+filename)
    img_path=os.path.join(image_folder, filename)
    image=Image.open(img_path)
    image=image.resize((epd.height, epd.width))
    epd.display(epd.getbuffer(image)) # Display the final image
    LEDs(1,0,0)
    photo_array.append(img_path)
    return

def menu_pressed(go_to_menu):
    global selection
    selection=go_to_menu
    return selection

def up(list):
	global h
	limit=len(list)-1
	h+=1
	if(h>=limit):h=0
	log("Up pressed - h="+h, 1)
	menu(list)
	return h

def down(list):
	global h
	limit=len(list)-1
	h-=1
	if(h<=0):h=limit
	log("Down pressed - h="+h, 1)
	menu(list)
	return h

def make_selection(list):
    global h, selection
    selection=list[h]
    log("Selection: "+selection, 1)
    return selection

def menu(list):
    global h, selection
    print (selection.upper()) # Menu title
    for i in list:
        if i==list[h]:
            i="> "+item
        print(i)
	# epd here	
    return

# Define the GPIO pin #s for buttons and LEDs
photo_btn=Button(5, pull_up=True, bounce_time=0.3) # used to take photo or select a menu item
menu_btn=Button(19, pull_up=True, bounce_time=0.3) # opens the menu
up_btn=Button(13, pull_up=True, bounce_time=0.3)# menu selection up
down_btn=Button(6, pull_up=True, bounce_time=0.3)# menu selection down
LED_G=LED(20)
LED_Y=LED(16)
LED_R=LED(12)

# Main Menu & Options Menu control variables
main_menu_list=["Camera", "Camera Options", "Autoscroll", "Manual Scroll", "Delete Photos"]
options_menu_list=["Font Selection", "Display Rotation", "Autoscroll Duration", "White Balance", "Shut Down", "Delete Photos"]
# Set menu defaults to open to Main Menu when the program starts
selection="Main Menu"
h=0

try:
	while True:
		# MAIN MENU
		if selection=="Main Menu":
			camera_prompt==False
			up_btn.when_pressed=lambda:up(main_menu_list)
			down_btn.when_pressed=lambda:down(main_menu_list)
			photo_btn.when_pressed=lambda:make_selection(main_menu_list)
#			menu_btn.when_pressed=lambda:menu_pressed("Main Menu")

		elif selection=="Camera Options":
			up_btn.when_pressed=lambda:up(options_menu_list)
			down_btn.when_pressed=lambda:down(options_menu_list)
			photo_btn.when_pressed=lambda:make_selection(options_menu_list)
			menu_btn.when_pressed=lambda:menu_pressed("Main Menu")

		# If the take photo button is pressed (LOW)
		elif selection=="Camera":
			if camera_prompt==False:
				# Message to let user know camera is ready to take photos
				log("Camera selected."+str(len(photo_array))+" photos onfile.",1)
				LEDs(0,1,0)
				image=Image.new("1", (epd.height, epd.width), 255)
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype(config_font, 24)
				draw.text((10,50),"Ready to take photos.",font=font,fill=0)
				font=ImageFont.truetype(config_font, 14)
				draw.text((15,85),"Push photo button to take a photo.\nPush the Menu button to cancel",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				camera_prompt=True
			else:
				photo_btn.when_pressed=lambda:take_photo()

except KeyboardInterrupt:
    log("Process was interrupted.", 0)

# Close the camera
cam.close()