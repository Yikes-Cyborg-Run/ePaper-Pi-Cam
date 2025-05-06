import RPi.GPIO as GPIO
import time, datetime, os
from picamzero import Camera
from waveshare_epd import epd2in7_V2 #   -- is for the GPIO HAT
#from waveshare_epd import epd4in2_V2 # epd2in7_V2  -- is for the GPIO HAT
from PIL import Image,ImageDraw,ImageFont
#	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)

print("Initializing")

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
		print("No config file.")
	return config

def menu(title, highlight, menu_array):
	global config_font, photo_array
	show=str(highlight)
	highlight=menu_array[highlight]
	print("Building menu, selected - "+show+" - "+highlight)
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
		# print(item)
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
	print("menu_made=True")
	return True

def display_photo(photo_array, key):
	print("Loading file...")
	filename=photo_array[key]
	print(filename)
	image=Image.open(filename)
	image=image.resize((epd.height, epd.width)) # ADDED THIS to check if scroll images woud work
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
	draw.text((5, 280), filename, font=font, fill=1)
	epd.display(epd.getbuffer(image))

def purge_photo_dir(image_folder):
	for filename in os.listdir(image_folder):
		file_path=os.path.join(image_folder, filename)
		try:
			if os.path.isfile(file_path) or os.path.islink(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path):
				shutilrmtree(file_path)
		except Exception as e:
			print("Failed to delete")

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
print("Loading config:")
for key, value in config.items():
    print(f"{key}: {value}")
config_font="/home/pi/ePaper-Pi-Cam/Fonts/"+str(config["font"])
white_balance=config["white_balance"]
display_rotation=config["display_rotation"]
auto_scroll_duration=config["auto_scroll_duration"]
timestamp_photo=config["timestamp_photo"]
brightness=config["brightness"]

"""
white_balance="auto"
display_rotation=0
auto_scroll_duration=3
timestamp_photo=False
brightness=0
"""

# Define the GPIO pin for the button
PHOTO_PIN=5 # used to take photo or select a menu item
MENU_PIN=19 # opens the menu
UP_PIN=13 # menu selection up
DOWN_PIN=6 # menu selection DOWN
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

# !!!!!!! do these need to be in an array to start?
#selection=menu_vars["selection"]
#highlight=menu_vars["highlight"]
#menu_made=menu_vars["menu_made"]

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
print("Building photo filename list")
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
print("Script Started")

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
			print("Opening Main Menu")

		# Make the menu and navigation
		if selection=="Menu":
			list_made=False # for the manual tabbing of photos
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
				print("Init options menu")
				highlight=0
				menu_made=menu(selection, highlight, options_menu_array)
				sleep(3)
			if up_state==False:
				print("up")
				highlight+=1
				if highlight>int(len(options_menu_array)):
					highlight=0
				menu_made=menu(selection, highlight, options_menu_array)
			elif down_state==False:
				print("down")
				highlight-=1
				if highlight<0:
					highlight=int(len(options_menu_array))
				menu_made=menu(selection, highlight, options_menu_array)
			elif photo_state==False:
				print("photo btn / select")
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
			print("Start photo display")
			display_photo(photo_array,list_increment)
			print("Increment: "+str(list_increment))
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

		# Ask to confirm purging all photos
		elif selection=="Delete":
			if check_delete==False:
				print("Confirm purging of all "+str(len(photo_array))+"photos.")
				LED(0,1,0)
				image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
				draw.text((20,5),"Are you SURE you want to \n delete all "+str(len(photo_array))+" photos on file?",font=font,fill=0)
				draw.text((20,50),"Press Menu button to cancel.",font=font,fill=0)
				draw.text((20,100),"Press Photo button to confirm.",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				check_delete=True
				print("checking delete confirmation....")
				time.sleep(1) # slows button press so it doesnt automatically jump to confirmed
			# pressing photo btn will confirm
			elif check_delete==True and photo_state==False:
				print("Deleting...")
				selection="Delete Confirmed"
				check_delete=False
				LED(0,0,0)
			elif check_delete==True and menu_state==False:
				print("Back to main menu")
				selection="Menu"
				check_delete=False
				LED(1,0,0)

		# PURGE ALL PHOTOS!
		elif check_delete==False and selection=="Delete Confirmed":
			print("Purging all photos")	
			LED(0,0,1)
			purge_photo_dir(image_folder)
			LED(1,0,0)
			list_increment=0
			epd.Clear()
			selection="Menu"
			menu_made=False
			check_delete=False
			photo_array=[]

		elif selection=="SAVE CONFIG":
			# Load existing config
			config={"white_balance": white_balance, "display_rotation": display_rotation, "auto_scroll_duration":auto_scroll_duration, "timestamp_photo":timestamp_photo}
			# Save updated config
			save_config(config)
			print("Settings saved.\n")

			#Reload and display
			config=load_config()
			print("Reloaded settings:")
			for key, value in config.items():
				print(f"{key}: {value}")	



except KeyboardInterrupt:
    GPIO.cleanup() # Clean up GPIO

# Close the camera
cam.close()
