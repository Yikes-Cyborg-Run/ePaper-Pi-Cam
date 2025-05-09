from gpiozero import LED, Button
import RPi.GPIO as GPIO
import time, datetime, os, logging
from datetime import datetime, date
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
#from waveshare_epd import epd4in2_V2 # -- the 4.2inch display
from PIL import Image,ImageDraw,ImageFont

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

log("Initializing", 1)

def save_config(config):
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

def menu(menu_title, items, up, down, func):
	global config_font, photo_array, h
	old=items[h]
	limit=len(items)-1
	if up==False: h+=1
	elif down==False: h-=1
	elif func==False:
		return items[h] # → selection
    # Check menu increment
	if h>limit: h=0
	elif h<0: h=limit
	new=items[h]

	# Highlight menu item
	print("New: "+new+" Old: "+old)
	if new!=old:
		y=40 # Will increment to place menu items vertically
		image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
		draw=ImageDraw.Draw(image)
		font=ImageFont.truetype(config_font, 24)
		draw.text((20,10),menu_title, font=font, fill=0)
		font=ImageFont.truetype(config_font, 18)
        # Loop through items
		for i in items:
			if i==items[h] and i!='Menu':
				i="> "+i
			if i!="Menu":
				draw.text((20,y),show+"\n",font=font,fill=0)
		epd.display(epd.getbuffer(image))
	return items[h] # return the old value if no btn press, so that menu doesn't rebuild

def config_menu(menu_title, items, up, down, func):
	global config_font, h
	old=items[h]
	limit=len(items)-1
	if up==False: h+=1
	elif down==False: h-=1
	elif func==False:
		return items[h] # → selection
    # Check menu increment
	if h>limit: h=0
	elif h<0: h=limit
	new=items[h]

	# Highlight menu item
	print("New: "+new+" Old: "+old)
	if new!=old:
		y=40 # Will increment to place menu items vertically
		image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
		draw=ImageDraw.Draw(image)
		font=ImageFont.truetype(config_font, 24)
		draw.text((20,10),menu_title, font=font, fill=0)
		font=ImageFont.truetype(config_font, 18)
        # Loop through items
		for i in items:
			if i==items[h] and i!='Menu':
				i="> "+i
			if i!="Menu":
				draw.text((20,y),show+"\n",font=font,fill=0)
		epd.display(epd.getbuffer(image))
	return items[h] # return the old value if no btn press, so that menu doesn't rebuild




"""
def menu(menu_title, items, up, down, func):
	global config_font, photo_array, h
	current=items[h]
	limit=len(items)-1
	if up==False: h+=1
	elif down==False: h-=1
	elif func==False:
		h=0
		return items[h] # → selection
    # Check menu increment
	if h>limit: h=0
	elif h<0: h=limit
	new=items[h]
	# Highlight menu item
	if new!=current:
		y=40 # Will increment to place menu items vertically
		image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
		draw=ImageDraw.Draw(image)
		font=ImageFont.truetype(config_font, 24)
		draw.text((20,10),menu_title, font=font, fill=0)
		font=ImageFont.truetype(config_font, 18)
		# Loop through items
		for i in items:
			if i==items[h] and i!='Menu':
				show="> "+i
			elif i!="Menu":
				show=i
			draw.text((20,y),show+"\n",font=font,fill=0)
			y+=25 # Increment y as menu items are added	
		epd.display(epd.getbuffer(image))
	else:
		return current
"""

def display_photo(photo_array, key):
	log("Loading file...", 1)
	filename=photo_array[key]
	log("display file: "+filename,1)
	image=Image.open(filename)
	image=image.resize((epd.height, epd.width))
#	draw=ImageDraw.Draw(image)
#	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
#	draw.text((5, 280), filename, font=font, fill=1)
	epd.display(epd.getbuffer(image))

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

# Control the LEDs, 1 = turn it on
def LED(green,yellow,red):
	if green==1: GPIO.output(LED_G, GPIO.HIGH)
	else: GPIO.output(LED_G, GPIO.LOW)
	if yellow==1: GPIO.output(LED_Y, GPIO.HIGH)
	else: GPIO.output(LED_Y, GPIO.LOW)
	if red==1: GPIO.output(LED_R, GPIO.HIGH)
	else: GPIO.output(LED_R, GPIO.LOW)

def draw_text(x,y,size,txt):
	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
	draw.text((20, 50), "Ready to take photo", font=font, fill=0)
	draw.text((20, 100), "Image Dir: "+image_folder, font=font, fill=0)
	epd.display(epd.getbuffer(image))
	return

def autoscroll():
	global list_increment
	log("Auto Scroll Increment: "+str(list_increment), 1)
	display_photo(photo_array, list_increment)
	time.sleep(5)
	list_increment+=1
	if list_increment>=len(photo_array): # removed int() around photo array
		list_increment=0

# Load existing config
config=load_config()
log("Loading config:", 1)
for key, value in config.items():
    log(f"{key}: {value}", 1)
config_font="/home/pi/ePaper-Pi-Cam/Fonts/"+str(config["font"])
white_balance=config["white_balance"]
display_rotation=config["display_rotation"]
auto_scroll_duration=config["auto_scroll_duration"]
timestamp_photo=config["timestamp_photo"]
brightness=config["brightness"]

# Define the GPIO pins for buttons and LEDs
PHOTO_PIN=5 # used to take photo or select a menu item
MENU_PIN=19 # opens the menu
UP_PIN=13 # menu selection up
DOWN_PIN=6 # menu selection down
LED_R=20
LED_G=16
LED_Y=12

# Set up button and LED pins -- button input with a pull-up resistor
GPIO.setwarnings(False) # Set to True to debug GPIO issues
GPIO.setmode(GPIO.BCM) # Set to Broadcom SOC channel numbering
GPIO.setup(PHOTO_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MENU_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_G,GPIO.OUT)
GPIO.setup(LED_Y,GPIO.OUT)
GPIO.setup(LED_R,GPIO.OUT)

# Main Menu & Options Menu control variables
main_menu_array=["Menu", "Camera", "List", "Auto Scroll", "Delete"]
options_menu_array=["Font Selection", "Display Rotation", "Auto Scroll Duration", "White Balance", "Clear and Shut Off", "Delete ALL Photos"]
white_balance_array=["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"]
auto_scroll_array=[10, 30, 60, 120, 300, 600]
timestamp_array=["True", "False"]

selection="Menu"
highlight=0
menu_made=False
check_delete=False
camera_prompt=False

# Initialize the display
# epd=epd4in2_V2.EPD()
epd=epd2in7_V2.EPD()
epd.init()

# ePaper display and Camera options
home_dir=os.environ['HOME'] # set home dir
image_folder="/home/pi/ePaper-Pi-Cam/photos/" # where photos will be saved
cam=Camera() # Start camera
cam.greyscale=True # make the photo black & white
cam.still_size = (264, 176) # resolution of the 2.7 GPIO display
# cam.still_size=(300,300) # resolution of the 4.2 display
cam.brightness=int(brightness) # can be -1.0 - 1.0
cam.whitebalance=white_balance
# cam.preview_size=(264, 176) # Don't need preview, keeping it for debugging purposes
# cam.start_preview()

# Build an array of saved photos
log("Building photo filename list", 1)
photo_array=[]
list_increment=0
for filename in os.listdir(image_folder):
	if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
		img_path=str(os.path.join(image_folder, filename))
		photo_array.append(img_path)

# Create a new image with a white background
image=Image.new("1", (epd.height, epd.width), 255)

if display_rotation==90:image=image.transpose(Image.ROTATE_90)
elif display_rotation==180:image=image.transpose(Image.ROTATE_180)
elif display_rotation==270:image=image.transpose(Image.ROTATE_270)

draw=ImageDraw.Draw(image)

LED(1,0,0)
log("Script Started", 1)

try:
	while True:

		# Read the button conditions
		photo_state=GPIO.input(PHOTO_PIN)
		menu_state=GPIO.input(MENU_PIN)
		up_state=GPIO.input(UP_PIN)
		down_state=GPIO.input(DOWN_PIN)

		# If not on menu page and menu btn is pressed, change selection to show menu
		if selection!="Menu" and menu_state==False:
			selection="Menu"
			log("Opening Main Menu", 1)

		# Main Menu
		if selection=="Menu":
			list_made=False # for the manual tabbing of photos
			check_delete=False # for checking delete vs canceling
			camera_prompt=False # for telling user that camera is ready
			selection=menu("MENU - Photos: "+str(len(photo_array)), main_menu_array, up_state, down_state, photo_state)

		# Options Menu
		elif selection=="Camera Options":
			selection=menu("Camera Options", options_menu_array, up_state, down_state, photo_state)

		# If the take photo button is pressed (LOW)
		elif selection=="Camera":
			if camera_prompt==False:
				log("Confirming purge of all "+str(len(photo_array))+" photos.",1)
				LED(0,1,0)
				image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype(config_font, 22)
				draw.text((20,50),"Ready to take photos.",font=font,fill=0)
				draw.text((20,100),"Push photo button.",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				camera_prompt=True
			else:
				if photo_state==False:
					LED(0,0,1)
					timestamp=datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
					filename=f"{timestamp}.jpg" # Construct the filename
					if timestamp_photo==True:
						cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5,170]) # add a timestamp to photo
					cam.take_photo(image_folder+filename)
					img_path=os.path.join(image_folder, filename)
					image=Image.open(img_path)
					image=image.resize((epd.height, epd.width))
					epd.display(epd.getbuffer(image)) # Display the final image
					LED(1,0,0)
					photo_array.append(img_path)

		# Manually tab through photos
		elif selection=="List":
			LED(0,1,0)
			log("Started manual list",1)
			if list_made==False:
				list_made=True
				LED(1,0,0)
				display_photo(photo_array, list_increment)
			if up_state==False:
				list_increment+=1
				if list_increment>len(photo_array)-1:
					list_increment=0
				LED(1,0,0)
				display_photo(photo_array, list_increment)
			elif down_state==False:
				list_increment-=1
				if list_increment<0:
					list_increment=len(photo_array)-1
				LED(1,0,0)
				display_photo(photo_array, list_increment)

		# Auto Scroll
		elif selection=="Auto Scroll":
			if menu_state==False:
				selection="Menu"
			autoscroll_thread=threading.Thread(target=autoscroll)
			if autoscroll_thread.is_alive()==False:
				autoscroll_thread.start()

		elif selection=="Auto Scroll Duration":
			selection=menu("Auto Scroll Duration", auto_scroll_array, up_state, down_state, photo_state)
			####### SAVE CONFIG !!!!!!!

		elif selection=="Timestamp Photo":
			selection=menu("Timestamp Photo", timestamp_array, up_state, down_state, photo_state)
			####### SAVE CONFIG !!!!!!!

		# Ask to confirm purging all photos
		elif selection=="Delete":
			if check_delete==False:
				log("Confirming purge of all "+str(len(photo_array))+" photos.",1)
				LED(0,1,0)
				image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
				draw.text((20,5),"Are you SURE you want to \n delete all "+str(len(photo_array))+"photos on file?",font=font,fill=0)
				draw.text((20,50),"Press Menu button to cancel.",font=font,fill=0)
				draw.text((20,100),"Press Photo button to confirm.",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				check_delete=True
			else:
					# pressing photo btn will confirm
					if photo_state==False:
						selection="Delete Confirmed"
						LED(0,0,0)
					elif menu_state==False:
						selection="Menu"
						LED(1,0,0)

		# PURGE ALL PHOTOS!
		elif check_delete==True and selection=="Delete Confirmed":
			log("Purging all photos....",1)	
			LED(0,0,1)
			purge_photo_dir(image_folder)
			LED(1,0,0)
			list_increment=0
			epd.Clear()
			selection="Menu"
			menu_made=False
			check_delete=False
			photo_array=[]
			log("Purge complete.",1)	

		elif selection=="SAVE CONFIG":
			# Get existing config that may have been edited while running the script
			config={"white_balance": white_balance, "display_rotation": display_rotation, "auto_scroll_duration":auto_scroll_duration, "timestamp_photo":timestamp_photo}
			# Save updated config
			save_config(config)
			log("Config saved.", 1)
			#Reload and display
			config=load_config()
			log("Reloaded settings:",1)
			for key, value in config.items():
				log(f"{key}: {value}", 1)

except KeyboardInterrupt:
    GPIO.cleanup() # Clean up GPIO

# Close the camera
cam.close()
