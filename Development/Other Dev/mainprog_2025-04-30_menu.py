import RPi.GPIO as GPIO
import time, datetime, os
from picamzero import Camera
from waveshare_epd import epd4in2_V2 # epd2in7_V2  -- is for the GPIO HAT
from PIL import Image,ImageDraw,ImageFont

print("initialize")

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for the button
TAKE_PIC_PIN=5
MENU_PIN=14
PIC_UP_PIN=6
PIC_DOWN_PIN=13
LED_R=20
LED_G=16
LED_Y=12

GPIO.setwarnings(False) #  where does this need to be???? after next block?????

# Set up the button pin as an input with a pull-up resistor
GPIO.setup(TAKE_PIC_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(MENU_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIC_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIC_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_G,GPIO.OUT)
GPIO.setup(LED_Y,GPIO.OUT)
GPIO.setup(LED_R,GPIO.OUT)

# Initialize the display
epd=epd4in2_V2.EPD()
epd.init()
epd.Clear()
# Display options
white_balance=["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"]
menu_selection=0
menu_highlight=0
home_dir=os.environ['HOME'] # set home dir
# image_folder=home_dir+"/camapp/photos/"
image_folder="/home/pi/camapp/photos/"

# Start camera set camera options
cam=Camera()
cam.greyscale=True # make it black and white
# cam.flip_camera(hflip=True)
# cam.flip_camera(vflip=False)
# Resolution sizes
#cam.still_size = (264, 176) # resolution of the display
#cam.still_size = (132, 88) # resolution of the display
cam.still_size=(300,300) #resolution of the display
cam.brightness=0 # can be -1.0 - 1.0
cam.preview_size=(264, 176)
cam.whitebalance=white_balance[4]

# cam.start_preview()

# Build an array of the current files
print("Build photo filename list")
photo_array=[]
photo_name_array=[]
photo_increment=0
for filename in os.listdir(image_folder):
	if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
		img_path=str(os.path.join(image_folder, filename))
		photo_array.append(img_path)
		photo_name_array.append(img_path)
		photo_increment+=1

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# here it is

max_photo_increment=len(photo_array)
max_photo_increment-=1

# create list of existing photos
photo_name_list=""
for photo_name in photo_name_array:
	photo_name_list+=photo_name+"\n"

def make_menu(menu_highlight):
#	epd.Clear()
	menu_array=["Menu", "Camera", "List", "Auto Scroll", "Camera Options", "Delete"]
	
	# ???????????????????????????????????????????????????????? Set partial refresh ??????????????
	Image.setPartialWindow(120, 55, 200, 60) # Set the window where the contents within are going to be refreshed

	print("Building menu...")
	# Create a new image with a white background
	image=Image.new("1", (epd.height, epd.width), 255)
	draw=ImageDraw.Draw(image)
	y=100 # will increment to place menu items vertically
	# Load a font and loop thorugh menu array
	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
	draw.text((20, 50), "MENU", font=font, fill=0)
	menu_item_num=0
	for item in menu_array:
		if menu_item_num==menu_highlight:
			item="→ "+item
		draw.text((20, y), item+"\n", font=font, fill=0)
		y+=30 # add so that the y position increments as items are added
		menu_count+=1

	# Display it
	epd.display(epd.getbuffer(image))

def display_photo(photo_array, key):
#	epd.Clear()
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

# Create a new image with a white background
image=Image.new("1", (epd.height, epd.width), 255)
# Rotate the screen ???????????????????????????????????????????????????????????????????????????????????????????
# image.setRotation(1) # 0--> No rotation ,  1--> rotate 90 deg
image=image.transpose(Image.ROTATE_90) # ROTATE_90, ROTATE_180, ROTATE_270

draw=ImageDraw.Draw(image)

# Load a font and draw some text
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
draw.text((20, 50), "Ready to take photo", font=font, fill=0)
draw.text((20, 100), "Image Dir: "+image_folder, font=font, fill=0)
draw.text((20, 150), "Photos on File: "+str(max_photo_increment), font=font, fill=0)
# draw.text((20, 200), "Photo List: \n"+photo_name_list, fill=0)

# Display the image
epd.display(epd.getbuffer(image))

GPIO.output(LED_G, GPIO.HIGH)
GPIO.output(LED_Y, GPIO.LOW)
GPIO.output(LED_R, GPIO.LOW)

print("Script Started")

try:
	while True:
		# Read the button conditions
		take_pic_state=GPIO.input(TAKE_PIC_PIN)
		menu_state=GPIO.input(MENU_PIN)
		btn_up_state=GPIO.input(PIC_UP_PIN)
		btn_down_state=GPIO.input(PIC_DOWN_PIN)

		if menu_selection!=0 and menu_state==False:
			menu_selection=0

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
# Stopped here, need to add a variable that will store the highlighted item and then 
# if the camera button is pushed to select it, variable will = menu_selection and load apropriate page
		if menu_selection==0:
			make_menu(menu_highlight)
			if btn_up_state==False:
				menu_highlight+=1
				if menu_highlight<len(menu_array):
					menu_highlight=0
			elif btn_down_state==False:
				menu_highlight-=1
				if menu_highlight<0:
					menu_highlight=len(menu_array)
			elif btn_down_state==False:
				menu_selection=menu_highlight
				menu_highlight=0

		# If the take photo button is pressed (LOW)
		elif menu_selection==1:
			if take_pic_state==False:
				GPIO.output(LED_G,GPIO.LOW)
				GPIO.output(LED_Y,GPIO.LOW)
				GPIO.output(LED_R,GPIO.HIGH)
				timestamp=datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # Get the current timestamp
				filename=f"{timestamp}.jpg" # Construct the filename
	#			cam.annotate(filename, 'plain-small', 'white', 1, 2, [5,170]) # add a timestamp to photo
	#			cam.take_photo("/home/pi/camapp/photos/"+timestamp+".jpg") # save the image
				cam.take_photo(image_folder+filename)
				img_path=os.path.join(image_folder, filename)
				image=Image.open(img_path)
	#			image=image.convert('1')  # Convert to black and white
				image=image.resize((epd.height, epd.width))
				epd.display(epd.getbuffer(image)) # Display the final image
				GPIO.output(LED_R, GPIO.LOW)
				GPIO.output(LED_Y, GPIO.LOW)
				GPIO.output(LED_G, GPIO.HIGH)
				photo_array.append(img_path)
				max_photo_increment=len(photo_array)
				max_photo_increment-=1

		# Manually tab through photos
		elif menu_selection==2:
			if btn_up_state==False:
				GPIO.output(LED_R, GPIO.LOW)
				GPIO.output(LED_G, GPIO.LOW)
				GPIO.output(LED_Y, GPIO.HIGH)
				photo_increment+=1
				if photo_increment>max_photo_increment:
					photo_increment=0
				display_photo(photo_array, photo_increment)
				print(str(photo_increment))
			elif btn_down_state==False:
				GPIO.output(LED_R, GPIO.LOW)
				GPIO.output(LED_G, GPIO.LOW)
				GPIO.output(LED_Y, GPIO.HIGH)
				photo_increment-=1
				if photo_increment<0:
					photo_increment=max_photo_increment
				display_photo(photo_array, photo_increment)
				print(str(photo_increment))
		
		#Auto-scroll thorugh photos every 30 seconds
		elif menu_selection==3:
			display_photo(photo_array, photo_increment)
			photo_increment+=1
			if photo_increment>len(photo_array):
				photo_increment=0
			time.sleep(3000)

		# PURGE ALL PHOTOS!
		if menu_selection==6:
			print("Purging all photos")	
			GPIO.output(LED_R, GPIO.LOW)
			GPIO.output(LED_G, GPIO.LOW)
			GPIO.output(LED_Y, GPIO.LOW)
			GPIO.output(LED_R, GPIO.HIGH)
			GPIO.output(LED_Y, GPIO.HIGH)
			purge_photo_dir(image_folder)
			GPIO.output(LED_R, GPIO.LOW)
			GPIO.output(LED_Y, GPIO.LOW)
			photo_increment=0
			epd.Clear()

except KeyboardInterrupt:
    GPIO.cleanup() # Clean up GPIO

# Close the camera
camera.close()
