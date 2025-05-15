from gpiozero import LED, Button
import time, datetime, os, logging, sys
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

log("################################################# - Initializing", 1)

def load_config():
#	global config_font, font_path, font_size, white_balance, display_rotation, autoscroll_duration, timelapse_duration, timestamp_photo, brightness
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

def take_photo():
    global image_folder, photo_list, timestamp_photo
    LEDs(0,0,1)
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

def menu_pressed(go_to):
	global h, selection, drawn
	h=0
	selection=go_to
	drawn=False
	log("Going to "+selection,1)
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

def up_font():
	global h, font_list
	limit=len(font_list)-1
	h+=1
	if(h>=limit):h=0
	log("Up pressed - h="+str(h), 1)
	font_menu()
	return None
def down_font():
	global h, font_list
	limit=len(font_list)-1
	h-=1
	if(h<0):h=limit
	log("Down pressed - h="+str(h), 1)
	font_menu()
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
	display_photo(photo_list, photo_increment)
	return photo_increment

def font_menu():
	global h, head_fs, base_fs, selection, font_list, drawn
	LEDs(0,1,0)
	y=40 # Will increment to place menu items vertically
	image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype(font_path, head_fs)
	draw.text((20,10), selection.upper(), font=font, fill=0)
	for f in font_list:
		sample_font=ImageFont.truetype("/home/pi/ePaper-Pi-Cam/Fonts/"+f, base_fs)
		if f==font_list[h]:
			f="> "+f
		draw.text((20,y),f,font=sample_font,fill=0)
		y=y+20 # Increment y position for next item
	epd.display(epd.getbuffer(image)) # Show the final output
	LEDs(1,0,0)
	drawn=True
	return None

def delete_photo_warning():
	global head_fs, base_fs, photo_increment, photo_list, font_path, drawn
	log("Delete photo warning...", 1)
	filename=photo_list[photo_increment]
	image=Image.open(filename)
	image=image.resize((epd.height/2, epd.width/2))
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype(font_path, head_fs)
	draw.text((20,10), "Are you SURE you want to \ndelete this photo?", font=font, fill=0)
	font=ImageFont.truetype(font_path, base_fs)
	draw.text((20,10), "Press Menu button to cancel\nPress Photo button to delete", font=font, fill=0)
	epd.display(epd.getbuffer(image))
	drawn="True"

def make_selection(list):
    global h, selection, drawn
    selection=list[h]
    drawn=False
    log("Selection: "+selection, 1)
    h=0
    return selection

def menu(list):
	global h, head_fs, base_fs, selection, font_path, drawn
	LEDs(0,1,0)
	y=40 # Will increment to place menu items vertically
	image=Image.new("1", (epd.height, epd.width), 255) 	# Create a new image with a white background
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype(font_path, head_fs)
	draw.text((20,10), selection.upper(), font=font, fill=0)
	font=ImageFont.truetype(font_path, base_fs)
	for i in list:
		if i==list[h]:
			i="> "+str(i)
		draw.text((20,y),str(i)+"\n",font=font,fill=0)
		y=y+20 # Increment y position for next item
	epd.display(epd.getbuffer(image)) # Show the final output
	LEDs(1,0,0)
	drawn=True
	return None

def display_photo(photo_list, key):
	global head_fs, base_fs
	log("Loading file...", 1)
	filename=photo_list[key]
	image=Image.open(filename)
	image=image.resize((epd.height, epd.width))
#	draw=ImageDraw.Draw(image)
#	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", base_fs-6)
#	draw.text((5, 280), filename, font=font, fill=1)
	epd.display(epd.getbuffer(image))
	log("Displayed file: "+filename,1)
	return None

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
	global head_fs, base_fs
	log("List selected, but no photos on file.", 0)
	LEDs(0,0,1)
	image=Image.new("1", (epd.height, epd.width), 255)
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype(font_path, head_fs)
	draw.text((20,50),"No photos to show.",font=font,fill=0)
	font=ImageFont.truetype(font_path, base_fs)
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

def future_calc():
	global now_time, now, future_time, future, drawn, autoscroll_duration
	# Get the current timestamp
	now_time=datetime.datetime.now()
	now=int(time.mktime(now_time.timetuple()))
	# Add autoscroll_duration to timestamp
	future_time=now_time+datetime.timedelta(seconds=autoscroll_duration)
	future=int(time.mktime(future_time.timetuple()))
	# Print the original and updated timestamps
	log("   NOW: "+str(now),1)
	log("FUTURE: "+str(future),1)
	drawn=True
	return None

def save_options(key_name, list):
	global h, drawn, head_fs, base_fs, selection, config
	log("Saving options....", 1)
	config[key_name]=list[h]
	# Save updated config
	with open("/home/pi/ePaper-Pi-Cam/config.txt", 'w') as file:
		for key, value in config.items():
			file.write(f"{key}={value}\n")
		image=Image.new("1", (epd.height, epd.width), 255)
		draw=ImageDraw.Draw(image)
		font=ImageFont.truetype(font_path, head_fs)
		draw.text((20,50),"Options Saved!",font=font,fill=0)
		font=ImageFont.truetype(font_path, base_fs)
		draw.text((20,75),"Restart camera for \nchanges to load.",font=font,fill=0)
		epd.display(epd.getbuffer(image))
		time.sleep(3)
	log("Options saved, rebooting now....", 1)
	drawn=False
	h=0
	os.execv(sys.executable, ['python'] + sys.argv)
#	os.system("sudo reboot")
	return None

def LEDs(green,yellow,red):
	if green==1: LED_G.on()
	else:  LED_G.off()
	if yellow==1: LED_Y.on()
	else: LED_Y.off()
	if red==1: LED_R.on()
	else: LED_R.off()

def format_timelapse_text():
	global timelapse_duration
	if(timelapse_duration<60):
		suffix="second"
		dur=timelapse_duration
	elif(timelapse_duration>60 and timelapse_duration<3600):
		suffix="minute"
		dur=timelapse_duration/60
	elif(timelapse_duration>60 and timelapse_duration<3600):
		suffix="hour"
		dur=timelapse_duration/3600
	# format the text to display
	if dur!=1:
		final=str(dur)+" "+suffix+"s"
	else:
		final=suffix
	return final

def start_timelapse():
	global timelapse_begun
	timelapse_begun=True
	return None

def options_control(back_to, list, config_key_to_save):
	global drawn
	menu_btn.when_pressed=lambda:menu_pressed(back_to)
	if drawn==True:
		up_btn.when_pressed=lambda:up_menu(list)
		down_btn.when_pressed=lambda:down_menu(list)
		photo_btn.when_pressed=lambda:save_options(config_key_to_save, list)
	else:
		menu(autoscroll_list)
	return None

# Load existing config
config=load_config()
for key, value in config.items():
	log(f"{key}: {value}", 1)
config_font=str(config["font"])
font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config_font
font_size=str(config["font_size"])
white_balance=str(config["white_balance"])
display_rotation=int(config["display_rotation"])
autoscroll_duration=int(config["autoscroll_duration"])
timelapse_duration=int(config["timelapse_duration"])
timestamp_photo=bool(config["timestamp_photo"])
brightness=int(config["brightness"])

# Set the base font size
base_fs=14
if font_size=="-4":base_fs-=4
elif font_size=="-2":base_fs-=2
elif font_size=="0":base_fs=base_fs
elif font_size=="+2":base_fs+=2
elif font_size=="+4":base_fs+=4
elif font_size=="+6":base_fs+=6
elif font_size=="+8":base_fs+=8
# Calculate header and sub font sizes
head_fs=base_fs+2
sub_fs=base_fs-2

# Define the GPIO pin #s for buttons and LEDs
photo_btn=Button(5, pull_up=True) # used to take photo or select a menu item
menu_btn=Button(19, pull_up=True) # opens the menu
up_btn=Button(13, pull_up=True)# menu selection +1
down_btn=Button(6, pull_up=True)# menu selection -1
LED_G=LED(20)
LED_Y=LED(16)
LED_R=LED(12)

# Menu & Options lists
main_menu_list=["Camera", "Time-lapse Camera", "Camera Options", "Autoscroll", "Manual Scroll", "Delete All Photos"]
options_menu_list=["Font Selection", "Font Size", "Display Rotation", "Autoscroll Duration", "Time-Lapse Duration", "White Balance", "Shut Down", "Delete Photos"]
white_balance_list=["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"]
font_size_list=["-4", "-2", "0", "+2", "+4"]
autoscroll_list=[10, 30, 60, 120, 300, 600]
timelapse_list=[1, 30, 60, 300, 600, 1800, 3600]
display_rotation_list=[90, 180, 270]
timestamp_list=["True", "False"]
font_list=[f for f in os.listdir("/home/pi/ePaper-Pi-Cam/Fonts") if os.path.isfile(os.path.join("/home/pi/ePaper-Pi-Cam/Fonts", f))]

# Set menu defaults
selection="Main Menu" # open to Main Menu when the program starts
h=0 # variable for incrementing menu selections
drawn=False # variable to stop looping over menu drawing

# Initialize the display
epd=epd2in7_V2.EPD()
epd.init()

# Show startup on screen
splash_photo=["/home/pi/ePaper-Pi-Cam/Resources/splash.jpg"]
display_photo(splash_photo, 0)
image=Image.new("1", (epd.height, epd.width), 255)
draw=ImageDraw.Draw(image)
font=ImageFont.truetype(font_path, head_fs)
draw.text((20,50),"Starting up...",font=font,fill=0)
epd.display(epd.getbuffer(image))
time.sleep(2)

# ePaper display and Camera options
home_dir=os.environ['HOME'] # set home dir
image_folder="/home/pi/ePaper-Pi-Cam/photos/" # Where photos will be saved
cam=Camera() # Start camera
cam.greyscale=True # Take photos in black & white
cam.still_size=(264, 176) # resolution of the 2.7 GPIO display
cam.brightness=int(brightness) # can be -1.0 - 1.0
cam.whitebalance=white_balance # see variable above for options

# Build a list of saved photos already on file. New photos will appended to the end of this list
log("Building list of previously saved photos", 1)
photo_list=[]
list_increment=0
for filename in os.listdir(image_folder):
	if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
		img_path=str(os.path.join(image_folder, filename))
		photo_list.append(img_path)

# Set image rotation NEED ???????
if display_rotation==90:image=image.transpose(Image.ROTATE_90)
elif display_rotation==180:image=image.transpose(Image.ROTATE_180)
elif display_rotation==270:image=image.transpose(Image.ROTATE_270)

log("Script Started", 1)
LEDs(1,0,0)

try:
	while True:
		if selection=="Main Menu":
			if drawn==True:
				up_btn.when_pressed=lambda:up_menu(main_menu_list)
				down_btn.when_pressed=lambda:down_menu(main_menu_list)
				photo_btn.when_pressed=lambda:make_selection(main_menu_list)
			else:
				menu(main_menu_list)
		elif selection=="Camera Options":
			if drawn==True:
				up_btn.when_pressed=lambda:up_menu(options_menu_list)
				down_btn.when_pressed=lambda:down_menu(options_menu_list)
				photo_btn.when_pressed=lambda:make_selection(options_menu_list)
				menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
			else:
				menu(options_menu_list)
		elif selection=="Camera":
			if drawn==True:
#				drawn==True # NEED ???????
				photo_btn.when_pressed=lambda:take_photo()
			else:
				log("Camera selected."+str(len(photo_list))+" photos onfile.",1)
				LEDs(1,0,0)
				image=Image.new("1", (epd.height, epd.width), 255)
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype(font_path, head_fs)
				draw.text((10,50),"Ready to take photos.",font=font,fill=0)
				font=ImageFont.truetype(font_path, base_fs)
				draw.text((15,85),"Push Photo button to take a photo.\nPush the Menu button to cancel",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				drawn=True
			menu_btn.when_pressed=lambda:menu_pressed("Main Menu")	
		elif selection=="Time-lapse Camera":
			if drawn==True:
				if timelapse_begun==True:
					now_time=datetime.datetime.now()
					now=int(time.mktime(now_time.timetuple()))
					if now>future:
						take_photo()
						future_calc()
				else:
					photo_btn.when_pressed=lambda:start_timelapse()
			else:
				log("Time-lapse Camera selected."+str(len(photo_list))+" photos onfile.",1)
				LEDs(1,0,0)
				timelapse_duration_text=format_timelapse_text()
				image=Image.new("1", (epd.height, epd.width), 255)
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype(font_path, head_fs)
				draw.text((10,50),"Ready to start time-lapse.",font=font,fill=0)
				draw.text((15,85),"Photos will be taken every "+timelapse_duration_text+".",font=font,fill=0)
				font=ImageFont.truetype(font_path, sub_fs)
				draw.text((15,105),"Push Photo button to begin time-lapse photography.\nPush the Menu button at any time to exit.",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				drawn=True
			menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
		elif selection=="Manual Scroll":
			if(len(photo_list)>0):
				menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
				up_btn.when_pressed=lambda:up_photo(photo_list)
				down_btn.when_pressed=lambda:down_photo(photo_list)
				photo_btn.when_pressed=lambda:menu_pressed("Delete Single Photo")
			else:
				if drawn==False:
					drawn=True
					no_photos_msg()
		elif selection=="Delete Single Photo":
			if drawn==True:
				menu_btn.when_pressed=lambda:menu_pressed("Manual Scroll")
				up_btn.when_pressed=lambda:up_photo("Manual Scroll")
				down_btn.when_pressed=lambda:down_photo("Manual Scroll")
				photo_btn.when_pressed=lambda:menu_pressed("Delete Single Photo Confirmed")
			else:
				delete_photo_warning()
		elif selection=="Delete Single Photo Confirmed":
			file_path="/home/pi/ePaper-Pi-Cam/Photos/"+photo_list[photo_increment]
			try:
				os.remove(file_path)
				log(f"Photo deleted.", 1)
				LEDs(0,1,0)
				image=Image.new("1", (epd.height, epd.width), 255)
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype(font_path, head_fs)
				draw.text((15,5),"Photo Deleted",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				time.sleep(1)
				drawn=True
				selection="Manual Scroll"
			except FileNotFoundError:
				log(f"Error: File '{file_path}' not found.",0)
			except Exception as e:
				log(f"An error occurred: {e}",0)
		elif selection=="Autoscroll":
			menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
			if len(photo_list)>0:
				if drawn==True:
					now_time=datetime.datetime.now()
					now=int(time.mktime(now_time.timetuple()))
					if now>future:
						list_increment+=1
						if list_increment>=len(photo_list)-1:
							list_increment=0
						log("Autoscroll Increment: "+str(list_increment), 1)
						display_photo(photo_list, list_increment)
						future_calc()
				else:
					display_photo(photo_list, list_increment)
					future_calc()
			else:
				if drawn==False:
					drawn=True
					no_photos_msg()
		elif selection=="Autoscroll Duration":
#			options_control("Camera Options", autoscroll_list, "autoscroll")
			menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
			if drawn==True:
				up_btn.when_pressed=lambda:up_menu(autoscroll_list)
				down_btn.when_pressed=lambda:down_menu(autoscroll_list)
				photo_btn.when_pressed=lambda:save_options("autoscroll", autoscroll_list)
			else:
				menu(autoscroll_list)
		elif selection=="Time-Lapse Duration":
#			options_control("Camera Options", timelapse_list, "timelapse_duration")
			menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
			if drawn==True:
				up_btn.when_pressed=lambda:up_menu(timelapse_list)
				down_btn.when_pressed=lambda:down_menu(timelapse_list)
				photo_btn.when_pressed=lambda:save_options("timelapse_duration",timelapse_list)
			else:
				menu(timelapse_list)
		elif selection=="Font Selection":
			if drawn==True:
				# Separate up and down functions so it can draw different fonts
				menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
				up_btn.when_pressed=lambda:up_font()
				down_btn.when_pressed=lambda:down_font()
				photo_btn.when_pressed=lambda:save_options("font", font_list)
			else:
				menu(font_list)
		elif selection=="Font Size":
#			options_control(!!!!!!!)
			menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
			if drawn==True:
				up_btn.when_pressed=lambda:up_menu(font_size_list)
				down_btn.when_pressed=lambda:down_menu(font_size_list)
				photo_btn.when_pressed=lambda:save_options("font_size", font_size_list)
			else:
				menu(font_size_list)
		elif selection=="Timestamp Photo":
#			options_control("Camera Options", timestamp_list, "timestamp")
			if drawn==True:
				menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
				up_btn.when_pressed=lambda:up_menu(timestamp_list)
				down_btn.when_pressed=lambda:down_menu(timestamp_list)
				photo_btn.when_pressed=lambda:save_options("timestamp", timestamp_list)
			else:
				menu(timestamp_list)
		elif selection=="Display Rotation":
#			options_control("Camera Options", display_rotation_list, "display_rotation")
			if drawn==True:
				menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
				up_btn.when_pressed=lambda:up_menu(display_rotation_list)
				down_btn.when_pressed=lambda:down_menu(display_rotation_list)
				photo_btn.when_pressed=lambda:save_options("display_rotation", display_rotation_list)
			else:
				menu(display_rotation_list)
		elif selection=="White Balance":
#			options_control("Camera Options", white_balance_list, "white_balance")
			if drawn==True:
				menu_btn.when_pressed=lambda:menu_pressed("Camera Options")
				up_btn.when_pressed=lambda:up_menu(white_balance_list)
				down_btn.when_pressed=lambda:down_menu(white_balance_list)
				photo_btn.when_pressed=lambda:save_options("white_balance", display_rotation_list)
			else:
				menu(white_balance_list)
		elif selection=="Delete All Photos":
			if drawn==True:
				menu_btn.when_pressed=lambda:menu_pressed("Main Menu")
				photo_btn.when_pressed=lambda:menu_pressed("Purge Confirmed")
			else:
				log("Confirming purge of all "+str(len(photo_list))+" photos.",1)
				LEDs(0,1,0)
				image=Image.new("1", (epd.height, epd.width), 255)
				draw=ImageDraw.Draw(image)
				font=ImageFont.truetype(font_path, base_fs)
				draw.text((15,5),"Are you SURE you want to \ndelete all "+str(len(photo_list))+" photos?",font=font,fill=0)
				font=ImageFont.truetype(font_path, sub_fs)
				draw.text((20,75),"Press Menu button to cancel.",font=font,fill=0)
				draw.text((20,100),"Press Photo button to confirm.",font=font,fill=0)
				epd.display(epd.getbuffer(image))
				drawn=True
		elif selection=="Purge Confirmed":
			log("Purging all photos....",1)	
			LEDs(0,0,1)
			purge_photo_dir(image_folder)
			LEDs(1,0,0)
			list_increment=0
			epd.Clear()
			selection="Main Menu"
			photo_list=[]
			log("Purge complete.",1)
			drawn=False
		elif selection=="Shut Down":
			log("Shutdown requested..... Shutting down in 3 seconds.", 1)
			image=Image.new("1", (epd.height, epd.width), 255)
			epd.display(epd.getbuffer(image))
			LEDs(0,0,0)
			os.system("sudo shutdown -h now")
except KeyboardInterrupt:
    log("Process was interrupted - shutting down.", 0)