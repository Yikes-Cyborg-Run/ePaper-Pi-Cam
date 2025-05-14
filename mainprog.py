from gpiozero import LED, Button
import time, datetime, os, logging
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from PIL import Image, ImageDraw, ImageFont

now=datetime.datetime.now()
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

def write_config_file(config):
    with open("/home/pi/ePaper-Pi-Cam/config.txt", 'w') as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")

def load_config():
	config={}
	if os.path.exists("/home/pi/ePaper-Pi-Cam/config.txt"):
		with open("/home/pi/ePaper-Pi-Cam/config.txt", 'r') as file:
			for line in file:
				if "=" in line:
					key, value=line.strip().split("=", 1)
					config[key]=value
		log("Loaded config.", 1)
	else:
		log("No config file.", 0)
	return config

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!! NEW FUNCTIONS
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def take_photo():
    global image_folder, photo_list, timestamp_photo
    LEDs(0,0,1)
#    timestamp=datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
    timestamp=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
    filename=f"{timestamp}.jpg" # Construct the filename
    if timestamp_photo==True: # Check if timestamping is enabled in config...
        cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5,170]) # add a timestamp to photo if it is
    cam.take_photo(image_folder+filename)
    img_path=os.path.join(image_folder, filename)
    image=Image.open(img_path)
    image=image.resize((epd.height, epd.width))
    epd.display(epd.getbuffer(image)) # Display the final image
    LEDs(1,0,0)
    photo_list.append(img_path)
    return

def menu_pressed(go_to_menu):
    global selection, made_menu
    made_menu=False
    selection=go_to_menu
    return selection

def up_menu(list):
	global h
	limit=len(list)-1
	h+=1
	if(h>=limit):h=0
	log("Up pressed - h="+str(h), 1)
	menu(list)
	return None

def down_menu(list):
	global h
	limit=len(list)-1
	h-=1
	if(h<0):h=limit
	log("Down pressed - h="+str(h), 1)
	menu(list)
	return None

def up_photo(photo_list):
	global photo_increment
	limit=len(photo_list)-1
	photo_increment+=1
	if(photo_increment>=limit):photo_increment=0
	log("Up pressed - photo_increment="+str(photo_increment), 1)
	display_photo(photo_list, photo_increment)
	return photo_increment

def down_photo(photo_list):
	global photo_increment
	limit=len(photo_list)-1
	photo_increment-=1
	if(photo_increment<=0):photo_increment=limit
	log("Down pressed - photo_increment="+str(photo_increment), 1)
	menu(list)
	return photo_increment

def make_selection(list):
    global h, selection, made_menu
    selection=list[h]
    made_menu=False
    log("Selection: "+selection, 1)
    h=0
    return selection

def menu(list):
	global h, selection, font_path, made_menu
	LEDs(0,1,0)
	y=40 # Will increment to place menu items vertically
	image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype(font_path, 24)
	draw.text((20,10), selection.upper(), font=font, fill=0)
	font=ImageFont.truetype(font_path, 20)
	for i in list:
		if i==list[h]:
			i="> "+str(i)
		draw.text((20,y),str(i)+"\n",font=font,fill=0)
		y=y+20 # Increment y position for next item
	epd.display(epd.getbuffer(image)) # Show the final output
	LEDs(1,0,0)
	made_menu=True
	return
# !!!!!!! NEW FUNCTIONS END # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def display_photo(photo_list, key):
	log("Loading file...", 1)
	filename=photo_list[key]
	image=Image.open(filename)
	image=image.resize((epd.height, epd.width))
#	draw=ImageDraw.Draw(image)
#	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
#	draw.text((5, 280), filename, font=font, fill=1)
	epd.display(epd.getbuffer(image))
	log("Displayed file: "+filename,1)

def purge_photo_dir(image_folder):
	log("Attempting to purge all photos...",1)
	for filename in os.listdir(image_folder):
		file_path=os.path.join(image_folder, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutilrmtree(file_path)
		except Exception as e:
			log("Failed to delete", 0)

def no_photos_msg():
	log("List selected but no photos on file.", 0)
	LEDs(0,0,1)
	image=Image.new("1", (epd.height, epd.width), 255)
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype(font_path, 24)
	draw.text((20,50),"No photos to show.",font=font,fill=0)
	font=ImageFont.truetype(font_path, 18)
	draw.text((20,100),"Press menu button.",font=font,fill=0)
	epd.display(epd.getbuffer(image))

def autoscroll():
	global list_increment
	log("Autoscroll Increment: "+str(list_increment), 1)
	display_photo(photo_list, list_increment)
	time.sleep(5)
	list_increment+=1
	if list_increment>=len(photo_list)-1:
		list_increment=0

def autoscroll_time_calc():
	global now_time, now, future_time, future, list_made, autoscroll_duration
	# Get the current timestamp
	now_time=datetime.datetime.now()
	now=int(time.mktime(now_time.timetuple()))
	# Add autoscroll_duration to timestamp
	future_time=now_time+datetime.timedelta(seconds=autoscroll_duration)
	future=int(time.mktime(future_time.timetuple()))
	# Print the original and updated timestamps
	log("   NOW: "+str(now),1)
	log("FUTURE: "+str(future),1)
	list_made=True
	return

log("Initializing", 1)

# Load existing config
config=load_config()
for key, value in config.items():
    log(f"{key}: {value}", 1)
config_font=str(config["font"])
font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config_font
white_balance=config["white_balance"]
display_rotation=config["display_rotation"]
autoscroll_duration=int(config["autoscroll_duration"])
timestamp_photo=config["timestamp_photo"]
brightness=int(config["brightness"])

def save_config():
	global config, config_font, white_balance, display_rotation, autoscroll_duration, timestamp_photo
	config={"font": config_font, "white_balance": white_balance, "display_rotation": display_rotation, "autoscroll_duration":autoscroll_duration, "timestamp_photo":timestamp_photo}
	# Save updated config
	write_config_file(config)
	log("Config saved.", 1)
	#Reload and display
	config=load_config()
	return

def save_autoscroll():
	global selection, autoscroll_duration, config
	autoscroll_duration=selection
	save_config()
	return

def save_display_rotation():
	global selection, display_rotation, config
	display_rotation=selection
	save_config()
	return

def save_white_balance():
	global selection, white_balance, config
	white_balance=selection
	save_config()
	return

def save_font():
	global selection, config_font, config
	config_font=selection
	save_config()
	return

def save_options(key_name):
	global selection, config
	config[key_name]=selection
	save_config
	return

def LEDs(green,yellow,red):
	if green==1: LED_G.on()
	else:  LED_G.off()
	if yellow==1: LED_Y.on()
	else: LED_Y.off()
	if red==1: LED_R.on()
	else: LED_R.off()

# Define the GPIO pin #s for buttons and LEDs
photo_btn=Button(5, pull_up=True) # used to take photo or select a menu item
menu_btn=Button(19, pull_up=True) # opens the menu
up_btn=Button(13, pull_up=True)# menu selection up
down_btn=Button(6, pull_up=True)# menu selection down
#photo_btn=Button(5, pull_up=False, bounce_time=0.3) # used to take photo or select a menu item
#menu_btn=Button(19, pull_up=False, bounce_time=0.3) # opens the menu
#up_btn=Button(13, pull_up=False, bounce_time=0.3)# menu selection up
#down_btn=Button(6, pull_up=False, bounce_time=0.3)# menu selection down
LED_G=LED(20)
LED_Y=LED(16)
LED_R=LED(12)

# Menu & Options lists
main_menu_list=["Camera", "Camera Options", "Autoscroll", "Manual Scroll", "Delete Photos"]
options_menu_list=["Font Selection", "Display Rotation", "Autoscroll Duration", "White Balance", "Shut Down", "Delete Photos"]
white_balance_list=["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"]
autoscroll_list=[10, 30, 60, 120, 300, 600]
display_rotation_list=[90, 180, 270]
timestamp_list=["True", "False"]

# Set menu defaults to open to Main Menu when the program starts
selection="Main Menu"
h=0
check_delete=False # Alert message
camera_prompt=False # Camera ready message
list_made=False
made_menu=False
# Initialize the display
epd=epd2in7_V2.EPD()
epd.init()

# ePaper display and Camera options
home_dir=os.environ['HOME'] # set home dir
image_folder="/home/pi/ePaper-Pi-Cam/photos/" # where photos will be saved
cam=Camera() # Start camera
cam.greyscale=True # make the photo black & white
cam.still_size=(264, 176) # resolution of the 2.7 GPIO display
cam.brightness=int(brightness) # can be -1.0 - 1.0
cam.whitebalance=white_balance
# cam.preview_size=(264, 176) # Don't need preview, keeping it for debugging purposes
# cam.start_preview()

# Build a list of saved photos already on file. New photos will appended to the end of this list
log("Building list of previously saved photos", 1)
photo_list=[]
list_increment=0
for filename in os.listdir(image_folder):
	if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
		img_path=str(os.path.join(image_folder, filename))
		photo_list.append(img_path)

# Create a new image with a white background
# image=Image.new("1", (epd.height, epd.width), 255) # !!!!!!! NEED ???????

# Set image rotation ???????
if display_rotation==90:image=image.transpose(Image.ROTATE_90)
elif display_rotation==180:image=image.transpose(Image.ROTATE_180)
elif display_rotation==270:image=image.transpose(Image.ROTATE_270)

log("Script Started", 1)
LEDs(1,0,0)

try:
	while True:
		# MAIN MENU
		if selection=="Main Menu":
			if made_menu==True:
				camera_prompt==False
				list_made==False
				check_delete=False
				up_btn.when_pressed=lambda:up_menu(main_menu_list)
				down_btn.when_pressed=lambda:down_menu(main_menu_list)
				photo_btn.when_pressed=lambda:make_selection(main_menu_list)
			else:
				menu(main_menu_list)

		# CAMERA OPTIONS
		elif selection=="Camera Options":
			if made_menu==True:
				up_btn.when_pressed=lambda:up_menu(options_menu_list)
				down_btn.when_pressed=lambda:down_menu(options_menu_list)
				photo_btn.when_pressed=lambda:make_selection(options_menu_list)
				menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
			else:
				menu(options_menu_list)

		# CAMERA
		elif selection=="Camera":
			if made_menu==False:
				log("Camera selected."+str(len(photo_list))+" photos onfile.",1)
				LEDs(1,0,0)
				image=Image.new("1", (epd.height, epd.width), 255)
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype(font_path, 24)
				draw.text((10,50),"Ready to take photos.",font=font,fill=0)
				font=ImageFont.truetype(font_path, 14)
				draw.text((15,85),"Push photo button to take a photo.\nPush the Menu button to cancel",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				made_menu=True
			else:
				made_menu==True
				photo_btn.when_pressed=lambda:take_photo()
			menu_btn.when_pressed=lambda:menu_pressed("Main Menu")	

		# MANUAL LIST
		elif selection=="Manual Scroll":
			if(len(photo_list)>0):
				menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
				up_btn.when_pressed=lambda:up_photo(options_menu_list)
				down_btn.when_pressed=lambda:down_photo(options_menu_list)
			else:
				if list_made==False:
					list_made=True
					no_photos_msg()

		# AUTOSCROLL
		elif selection=="Autoscroll":
			menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
			if len(photo_list)>0:
				if list_made==True:
					now_time=datetime.datetime.now()
					now=int(time.mktime(now_time.timetuple()))
					if now>future:
						list_increment+=1
						if list_increment>=len(photo_list)-1:
							list_increment=0
						log("Autoscroll Increment: "+str(list_increment), 1)
						display_photo(photo_list, list_increment)
						autoscroll_time_calc()
				else:
					display_photo(photo_list, list_increment)
					autoscroll_time_calc()
			else:
				if list_made==False:
					list_made=True
					no_photos_msg()

		# AUTOSCROLL DURATION
		elif selection=="Autoscroll Duration":
			menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
			if made_menu==True:
				up_btn.when_pressed=lambda:up_menu(autoscroll_list)
				down_btn.when_pressed=lambda:down_menu(autoscroll_list)
	#			photo_btn.when_pressed=lambda:save_autoscroll()
				photo_btn.when_pressed=lambda:save_options("autoscroll")
			else:
				menu(autoscroll_list)

		# FONT SELECTION
		elif selection=="Font Selection":
			if made_menu==True:
				menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
				up_btn.when_pressed=lambda:up_menu(font_list)
				down_btn.when_pressed=lambda:down_menu(font_list)
	#			photo_btn.when_pressed=lambda:save_font()
				photo_btn.when_pressed=lambda:save_options("font")
			else:
				menu(font_list)

		# TIMESTAMP PHOTO
		elif selection=="Timestamp Photo":
			if made_menu==True:
				menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
				up_btn.when_pressed=lambda:up_menu(timestamp_list)
				down_btn.when_pressed=lambda:down_menu(timestamp_list)
	#			photo_btn.when_pressed=lambda:save_timestamp()
				photo_btn.when_pressed=lambda:save_options("timestamp")
			else:
				menu(timestamp_list)

		# DISPLAY ROTATION
		elif selection=="Display Rotation":
			if made_menu==True:
				menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
				up_btn.when_pressed=lambda:up_menu(display_rotation_list)
				down_btn.when_pressed=lambda:down_menu(display_rotation_list)
	#			photo_btn.when_pressed=lambda:save_display_rotation()
				photo_btn.when_pressed=lambda:save_options("display_rotation")
			else:
				menu(display_rotation_list)

		# WHITE BALANCE
		elif selection=="White Balance":
			if made_menu==True:
				menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
				up_btn.when_pressed=lambda:up_menu(white_balance_list)
				down_btn.when_pressed=lambda:down_menu(white_balance_list)
	#			photo_btn.when_pressed=lambda:save_white_balance()
				photo_btn.when_pressed=lambda:save_options("white_balance")
			else:
				menu(white_balance_list)

		# CONFIRM PURGE
		elif selection=="Delete Photos":
			if check_delete==False:
				check_delete=True
				log("Confirming purge of all "+str(len(photo_list))+" photos.",1)
				LEDs(0,1,0)
				image=Image.new("1", (epd.height, epd.width), 255)
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype(font_path, 20)
				draw.text((15,5),"Are you SURE you want to \ndelete all "+str(len(photo_list))+" photos?",font=font,fill=0)
				font=ImageFont.truetype(font_path, 16)
				draw.text((20,75),"Press Menu button to cancel.",font=font,fill=0)
				draw.text((20,100),"Press Photo button to confirm.",font=font,fill=0)
				epd.display(epd.getbuffer(image))
			else:
				menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
				photo_btn.when_pressed=lambda:menu_pressed("Delete Confirmed")

		# PURGE ALL PHOTOS!
		elif check_delete==True and selection=="Delete Confirmed":
			log("Purging all photos....",1)	
			LEDs(0,0,1)
			purge_photo_dir(image_folder)
			LEDs(1,0,0)
			list_increment=0
			epd.Clear()
			selection="Main Menu"
			photo_list=[]
			log("Purge complete.",1)	

		# Shut down the camera
		elif selection=="Shut Down":
			log("Shutdown requested..... Shutting down in 3 seconds.", 1)
			image=Image.new("1", (epd.height, epd.width), 255)
			epd.display(epd.getbuffer(image))
			LEDs(0,0,0)
			os.system("sudo shutdown -h now")

		"""
		elif selection=="SAVE CONFIG":
			# Get existing config that may have been edited while running the script
			config={"white_balance": white_balance, "display_rotation": display_rotation, "autoscroll_duration":autoscroll_duration, "timestamp_photo":timestamp_photo}
			# Save updated config
			save_config(config)
			log("Config saved.", 1)
			#Reload and display
			config=load_config()
			log("Reloaded settings:",1)
			for key, value in config.items():
				log(f"{key}: {value}", 1)
		"""

except KeyboardInterrupt:
    log("Process was interrupted.", 0)
	# Close the camera
    cam.close()
