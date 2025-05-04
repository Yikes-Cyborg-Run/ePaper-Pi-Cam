import RPi.GPIO as GPIO
import time, datetime, os
from picamzero import Camera
from waveshare_epd import epd4in2_V2 # epd2in7_V2  -- is for the GPIO HAT
from PIL import Image,ImageDraw,ImageFont

print("Initializing")

def save_config(config):
    with open("config.txt", 'w') as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")

def load_config():
	config={}
	if os.path.exists("config.txt"):
		with open("config.txt", 'r') as file:
			for line in file:
				if "=" in line:
					key, value=line.strip().split("=", 1)
					config[key]=value
	else:
		print("No config file")
	return config

def menu(title, highlight, menu_array):
	global config_font
	show=str(highlight)
	highlight=menu_array[highlight]
	print("Building menu, selected - "+show+" - "+highlight)
	image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
	draw=ImageDraw.Draw(image)
	y=100 # will increment to place menu items vertically
	# Load font and loop thorugh menu array
	font=ImageFont.truetype("/home/pi/epaperpicam/Fonts/"+config_font, 18)
	draw.text((20,50),title,font=font,fill=0)
	for item in menu_array:
		if item==highlight:
			show="- "+item
			if item=="Camera":
				show="- Camera - take photo..."
		else:
			show=item
		if item!="Menu":
			draw.text((20,y),show+"\n",font=font,fill=0)
			y+=30 # add so that the y position increments as menu items are added
	epd.display(epd.getbuffer(image))
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
	draw.text((20, 150), "Photos on File: "+str(num_photos), font=font, fill=0)
	epd.display(epd.getbuffer(image))
	return

# Load existing config
config=load_config()
print("Loaded settings:")
for key, value in config.items():
    print(f"{key}: {value}")

config_font=config["font"]
white_balance=config["white_balance"]
display_rotation=config["display_rotation"]
auto_scroll_duration=config["auto_scroll_duration"]
timestamp_photo=config["timestamp_photo"]
brightness=config["brightness"]

# Define the GPIO pin for the button
PHOTO_PIN=5
MENU_PIN=14
UP_PIN=6
DOWN_PIN=13
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
main_menu_array=["Menu", "Camera", "List", "Auto Scroll", "Camera Options", "Delete"]
options_menu_array=["White Balance", "Display Rotation", "Auto Scroll Duration", "Camera Options", "Delete"]
white_balance_array=["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"]
selection="Menu"
highlight=0
menu_made=False
options_menu_made=False
check_delete=False

# Initialize the display
epd=epd4in2_V2.EPD()
epd.init()

# ePaper display and Camera options
# white_balance=["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"]
home_dir=os.environ['HOME'] # set home dir
image_folder="/home/pi/epaperpicam/photos/" # where photos will be saved
cam=Camera() # Start camera
cam.greyscale=True # make the photo black & white
# cam.flip_camera(hflip=True)
# cam.flip_camera(vflip=False)
# cam.still_size = (264, 176) # resolution of the display
cam.still_size=(300,300) # resolution of the display
cam.brightness=int(brightness) # can be -1.0 - 1.0
# cam.brightness=0
cam.preview_size=(264, 176) # Don't need preview, keeping it for debugging purposes
cam.whitebalance=white_balance
# cam.start_preview()

# Build an array of saved photos
print("Building photo filename list")
photo_array=[]
photo_name_array=[]
list_increment=0
for filename in os.listdir(image_folder):
	if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
		img_path=str(os.path.join(image_folder, filename))
		photo_array.append(img_path)
		photo_name_array.append(img_path)
num_photos=len(photo_array)
num_photos-=1

# Create list of existing photos
photo_name_list=""
for photo_name in photo_name_array:
	photo_name_list+=photo_name+"\n"

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
				if highlight>5:
					highlight=0
				menu_made=menu("MENU - Photos: "+str(len(photo_array)), highlight, main_menu_array)
			elif down_state==False:
				highlight-=1
				if highlight<0:
					highlight=5
				menu_made=menu("MENU - Photos: "+str(len(photo_array)), highlight, main_menu_array)
			elif photo_state==False:
				selection=main_menu_array[highlight]
				highlight=0
				menu_made=False

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
				num_photos=len(photo_array)
				num_photos-=1

		# Manually tab through photos
		elif selection=="List":
			LED(0,1,0)
			if list_made==False:
				print("Increment: "+str(list_increment))
				display_photo(photo_array, list_increment)
				list_made=True
			if up_state==False:
				print("Up - Increment: "+str(list_increment))
				LED(1,0,0)
				list_increment+=1
				if list_increment>num_photos:
					list_increment=0
				display_photo(photo_array, list_increment)
				print("Photo increment = "+str(list_increment))
			elif down_state==False:
				print("Up - Increment: "+str(list_increment))
				LED(1,0,0)
				list_increment-=1
				if list_increment<0:
					list_increment=num_photos
				display_photo(photo_array, list_increment)
				print("Photo increment = "+str(list_increment))

		# Auto-scroll through photos every 30 seconds
		elif selection=="Auto Scroll":
			print("Start photo display")
			display_photo(photo_array,list_increment)
			print("Increment: "+str(list_increment))
			time.sleep(5)
			list_increment+=1
			if list_increment>=int(len(photo_array)):
				list_increment=0

		# Options Menu
		elif selection=="Camera Options":
			if menu_made==False:
				menu_made=menu("Camera Options", highlight, options_menu_array)
			if up_state==False:
				highlight+=1
				menu_made=menu("Camera Options", highlight, options_menu_array)
				if highlight>len(options_menu_array):
					highlight=0
			elif down_state==False:
				highlight-=1
				menu_made=menu("Camera Options", highlight, options_menu_array)
				if highlight<0:
					highlight=len(options_menu_array)
			elif photo_state==False:
				selection=options_menu_array[highlight]
				highlight=0
				menu_made=False

		# Ask to confirm purging all photos
		elif selection=="Delete":
			if check_delete==False:
				print("Confirm purging of all "+str(len(photo_array))+"photos.")
				LED(0,1,0)
				image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
				draw.text((20,50),"Are you SURE you want to \n delete all "+str(num_photos+1)+" photos on file?",font=font,fill=0)
				draw.text((20,120),"Press Menu button to cancel.",font=font,fill=0)
				draw.text((20,170),"Press Photo button to confirm.",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				check_delete=True
				time.sleep(3) # slows button press so it doesnt automatically jump to confirmed
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
Camera.close()
