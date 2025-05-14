import RPi.GPIO as GPIO
from gpiozero import LED, Button, PWMLED
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

log=logging.getLogger("__name__")
logging.basicConfig(filename=log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)

#	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

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

def menu(title, highlight, menu_array):
	global config_font, photo_array
	show=str(highlight)
	highlight=menu_array[highlight]
	log("Building menu, selected - "+show+" - "+highlight, 1)
	image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
#	image=image.transpose(Image.ROTATE_180)
	draw=ImageDraw.Draw(image)
#	draw=draw.transpose(Image.ROTATE_180)
	y=40 # will increment to place menu items vertically
	# Load font and loop thorugh menu array
	font=ImageFont.truetype(str(config_font), 18)
	draw.text((20,10),title,font=font,fill=0)
	font=ImageFont.truetype(str(config_font), 16)
	for item in menu_array:
		# log(item,1)
		if item==highlight:
			show="- "+item
			if item=="Camera":
				show="- Camera - push photo button..."
			elif item=="List":
				show="- List - "+str(len(photo_array))+" photos..."
		else:
			show=item
		if item!="Menu":
			draw.text((20,y),show+"\n",font=font,fill=0)
			y+=25 # add so that the y position increments as menu items are added
	epd.display(epd.getbuffer(image))
	log("menu_made=True", 1)
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
	log("Attempting to purge all photos...")
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
	if green==1: LED_g.on()
	else:  LED_g.off()
	if yellow==1: LED_y.on()
	else: LED_y.off()
	if red==1: LED_r.on()
	else: LED_r.off()

def draw_text(x,y,size,txt):
	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
	draw.text((20, 50), "Ready to take photo", font=font, fill=0)
	draw.text((20, 100), "Image Dir: "+image_folder, font=font, fill=0)
	epd.display(epd.getbuffer(image))
	return

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

# This code runs only in python 3.10 or above versions
def nts(argument):
	match argument:
		case 0: 
			return "Menu"
		case 1:
			return "Camera"
		case 2:
			return "List"
		case 3:
			return "Auto Scroll"
		case 4:
			return "Options"
		case 5:
			return "Delete Check"
		case 6:
			return "Delete Confirmed"
		case default:
			return "Menu"

def up_increment(limit):
	menu_increment+=1
	if(menu_increment>=limit):
		menu_increment=0
	return menu_increment

def down_increment(limit):
	menu_increment-=1
	if(menu_increment<=0):
		menu_increment=limit
	return menu_increment

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

# Define the GPIO pin for the button
photo_btn=Button(5, bounce_time=0.3) # used to take photo or select a menu item
menu_btn=Button(19, bounce_time=0.3) # opens the menu
up_btn=Button(13, bounce_time=0.3)# menu selection up
down_btn=Button(6, bounce_time=0.3)# menu selection down
LED_g=LED(20)
LED_y=LED(16)
LED_r=LED(12)

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

# Initialize the display
# epd=epd4in2_V2.EPD()
epd=epd2in7_V2.EPD()
epd.init()

# ePaper display and Camera options
home_dir=os.environ['HOME'] # set home dir
image_folder="/home/pi/ePaper-Pi-Cam/photos/" # where photos will be saved
cam=Camera() # Start camera
cam.greyscale=True # make the photo black & white
# cam.flip_camera(hflip=True)
# cam.flip_camera(vflip=False)
cam.still_size = (264, 176) # resolution of the 2.7 GPIO display
# cam.still_size=(300,300) # resolution of the 4.2 display
cam.brightness=int(brightness) # can be -1.0 - 1.0
# cam.brightness=0
# cam.preview_size=(264, 176) # Don't need preview, keeping it for debugging purposes
cam.whitebalance=white_balance
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

def menu_selected(menu_array, current_increment):
	up_btn.when_pressed=up_increment(len(menu_array))
	down_btn.when_pressed=down_increment(len(menu_array))
	new_increment=nts(menu_num)
	if new_increment!=current_increment:
		menu_made=menu("MENU - Photos: "+str(len(photo_array)), highlight, main_menu_array)
	selection="Menu"
	return selection

try:
	while True:
		# Read the button conditions
		photo_btn.when_pressed=photo_pressed
		menu_btn.when_pressed=menu_pressed

		selection=nts(menu_num)

		# If not on menu page and menu btn is pressed, change selection to show menu
		if selection!="Menu":
			menu_btn.when_pressed=menu_selected(menu_array, 1)
			selection="Menu"
			log("Opening Main Menu", 1)

		# Make the menu and navigation
		if selection=="Menu":
			up_btn.when_pressed=up_increment(len(menu_array))
			down_btn.when_pressed=down_increment(len(menu_array))
			photo_btn.when_pressed=select_menu_item(menu_increment)

		# Options Menu
		elif selection=="Camera Options":
			if menu_made==False:
				log("Init options menu", 1)
				highlight=0
				menu_made=menu(selection, highlight, options_menu_array)
			if up_state==False:
				log("up", 1)
				highlight+=1
				if highlight>int(len(options_menu_array)):
					highlight=0
				menu_made=menu(selection, highlight, options_menu_array)
			elif down_state==False:
				log("down", 1)
				highlight-=1
				if highlight<0:
					highlight=int(len(options_menu_array))
				menu_made=menu(selection, highlight, options_menu_array)
			elif photo_state==False:
				log("photo btn / select", 1)
				selection=options_menu_array[highlight]
				highlight=0
				menu_made=True

		# If the take photo button is pressed (LOW)
		elif selection=="Camera":
			if photo_state==False:
				LED(0,0,1)
				timestamp=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
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
			log("Started Auto Scroll", 1)
			display_photo(photo_array,list_increment)
			log("Auto Scroll Increment: "+str(list_increment), 1)
			time.sleep(5)
			list_increment+=1
			if list_increment>=int(len(photo_array)):
				list_increment=0

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

		time.sleep(0.3) # ??????? will this debounce?
except KeyboardInterrupt:
    GPIO.cleanup() # Clean up GPIO

# Close the camera
cam.close()
