from gpiozero import LED, Button
import RPi.GPIO as GPIO
import time, datetime, os, logging
from datetime import datetime, date
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- is for the GPIO HAT
#from waveshare_epd import epd4in2_V2 # -- is for the 4inch display
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
	else:
		log("No config file.", 0)
	return config

def menu(items, up, down, func):
	global config_font, photo_array, h
	current=items[h]
	print(str(len(items)))
	if up==False: h+=1
	elif down==False: h-=1
	elif func==False:
		selection=items[h]
		h=0
		return selection

    # Check menu increment
	if h>len(items)-1: h=0
	elif h<0: h=len(items)-1
	new=items[h]    

	# Highlight menu item
	if new!=current:
		y=40 # will increment to place menu items vertically
		image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
		draw=ImageDraw.Draw(image)
		font=ImageFont.truetype(config_font, 24)
		draw.text((20,10),title,font=font,fill=0)
		font=ImageFont.truetype(config_font, 18)
		# loop through items
		for i in items:
			if i==items[h] and i!='Menu':
				show="> "+i
			elif i!="Menu":
				show=i
			draw.text((20,y),show+"\n",font=font,fill=0)
			y+=25 # increment y as menu items are added	

def OLD_menu(title, highlight, menu_array):
	global config_font, photo_array
	show=str(highlight)
	highlight=menu_array[highlight]
	num_photos=str(len(photo_array))
	log("Building menu, selected - "+show+" - "+highlight, 1)
	image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
	draw=ImageDraw.Draw(image)
	y=40 # will increment to place menu items vertically
	# Load font and loop thorugh menu array
	font=ImageFont.truetype(config_font, 24)
	draw.text((20,10),title,font=font,fill=0)
	font=ImageFont.truetype(config_font, 18)
	for item in menu_array:
		if item==highlight:
			show="> "+item
			if item=="List":
				show="> List - "+num_photos+" photos..."
			elif item=="Autoscroll":
				show="> Autoscroll - "+num_photos+" photos..."
		else:
			show=item
		if item!="Menu":
			draw.text((20,y),show+"\n",font=font,fill=0)
			y+=25 # add so that the y position increments as menu items are added
	epd.display(epd.getbuffer(image))
	return True

def display_photo(photo_array, key):
	log("Loading file...", 1)
	filename=photo_array[key]
	log("display file: "+filename,1)
	image=Image.open(filename)
	image=image.resize((epd.height, epd.width)) # ADDED THIS to check if scroll images woud work
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
	draw.text((5, 280), filename, font=font, fill=1)
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

def master_menu(menu_made, selection, highlight, array_to_use, config, config_key, return_selection):
	global up_state, down_state, photo_state
	if menu_made==False:
		menu_made=menu(selection, highlight, array_to_use)
	if up_state==False:
		highlight+=1
		menu_made=menu(selection, highlight, array_to_use)
		if highlight>len(array_to_use):
			highlight=0
	elif down_state==False:
		highlight-=1
		menu_made=menu(selection, highlight, array_to_use)
		if highlight<0:
			highlight=len(array_to_use)
	elif photo_state==False:
		new_value=array_to_use[highlight]
		config[config_key]=new_value
		save_config(config)
		highlight=0
		menu_made=False
		selection=return_selection
		result=[{"selection":selection}, {"highlight":highlight}, {"menu_made":menu_made}, {"config_key_to_save":config_key}, {"config_value_to_save": new_value}]
		return result

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
			if menu_made==False:
				menu_made=menu("MENU - Photos: "+str(len(photo_array)), highlight, main_menu_array)
			if up_state==False:
				highlight+=1
				if highlight>int(len(main_menu_array)-1):
					highlight=0
				menu_made=menu("MENU - Photos: "+str(len(photo_array)), highlight, main_menu_array)
			elif down_state==False:
				highlight-=1
				if highlight<0:
					highlight=int(len(main_menu_array)-1)
				menu_made=menu("MENU - Photos: "+str(len(photo_array)), highlight, main_menu_array)
			elif photo_state==False:
				selection=main_menu_array[highlight]
				highlight=0
				menu_made=False

		# Options Menu
		elif selection=="Camera Options":
			if menu_made==False:
				log("Init options menu", 1)
				highlight=0
				menu_made=menu(selection, highlight, options_menu_array)
			if up_state==False:
				highlight+=1
				if highlight>int(len(options_menu_array)):
					highlight=0
				menu_made=menu(selection, highlight, options_menu_array)
			elif down_state==False:
				highlight-=1
				if highlight<0:
					highlight=int(len(options_menu_array))
				menu_made=menu(selection, highlight, options_menu_array)
			elif photo_state==False:
				selection=options_menu_array[highlight]
				highlight=0
				menu_made=True

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
				if list_increment>int(len(photo_array)-1):
					list_increment=0
				LED(1,0,0)
				display_photo(photo_array, list_increment)
			elif down_state==False:
				list_increment-=1
				if list_increment<0:
					list_increment=int(len(photo_array)-1)
				LED(1,0,0)
				display_photo(photo_array, list_increment)

		# Auto-scroll through photos every 30 seconds
		elif selection=="Auto Scroll":
			"""
			log("Auto Scroll Increment: "+str(list_increment), 1)
			display_photo(photo_array,list_increment)
			time.sleep(5)
			list_increment+=1
			if list_increment>=int(len(photo_array)):
				list_increment=0
			"""
		elif selection=="Auto Scroll Duration":
			menu_vars=master_menu(menu_made, "Auto Scroll Duration", highlight, auto_scroll_array, config, "autoscroll_duration", "Camera Options")
			selection=menu_vars["selection"]
			highlight=menu_vars["highlight"]
			menu_made=menu_vars["menu_made"]

		elif selection=="Timestamp Photo":
			menu_vars=master_menu(menu_made, "Timestamp Photo", highlight, timestamp_array, config, "timestamp_photo", "Camera Options")
			selection=menu_vars["selection"]
			highlight=menu_vars["highlight"]
			menu_made=menu_vars["menu_made"]

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

#		time.sleep(1) # ??????? will this debounce?
except KeyboardInterrupt:
    GPIO.cleanup() # Clean up GPIO

# Close the camera
cam.close()
