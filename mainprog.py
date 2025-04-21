import RPi.GPIO as GPIO
import time, datetime, os
from picamzero import Camera
from waveshare_epd import epd2in7_V2
from PIL import Image,ImageDraw,ImageFont

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for the button
TAKE_PIC_PIN=5
PIC_UP_PIN=6
PIC_DOWN_PIN=13

PIC_UP_PIN_2=18
# PIC_DOWN_PIN_2=23

# BUZZ_PIN=18

CLEAR_SCREEN_PIN= 19
TAKE_PIC_PIN_2=21
LED_R=20
LED_G=16
LED_Y=12

# Set up the button pin as an input with a pull-up resistor
GPIO.setup(TAKE_PIC_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIC_UP_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PIC_DOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(PIC_UP_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(PIC_DOWN_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(TAKE_PIC_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CLEAR_SCREEN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_G,GPIO.OUT)
GPIO.setup(LED_Y,GPIO.OUT)
GPIO.setup(LED_R,GPIO.OUT)
GPIO.setwarnings(False) # ?

# Initialize the display
epd = epd2in7_V2.EPD()
epd.init()
epd.Clear()

# Display options
white_balance=["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"]
image_folder = '/home/pi/camapp/photos/'
home_dir = os.environ['HOME'] #set the location of home directory
cam = Camera()
cam.greyscale = True # make it black and white
cam.still_size = (264, 176) # resolution of the display
#cam.still_size = (132, 88) # resolution of the display
cam.brightness=0 # can be -1.0 - 1.0
cam.preview_size=(264, 176)
cam.whitebalance=white_balance[4]

# cam.start_preview()

# Build an array of the current files 
photo_array=[]
for filename in os.listdir(image_folder):
	if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
		img_path=str(os.path.join(image_folder, filename))
		photo_array.append(img_path)
photo_increment=0
max_photo_increment=len(photo_array)
max_photo_increment-=1

def display_photo(photo_array, key):
	epd.Clear()
	filename=photo_array[key]
	image=Image.open(filename)
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
	draw.text((5, 160), filename, font=font, fill=1)
#	draw.rectangle((0, 160, 300, 190), fill=000, outline = epd.GRAY1)
	epd.display(epd.getbuffer(image))

# Create a new image with a white background
image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)

# Load a font and draw some text
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
draw.text((10, 10), 'Ready to Take Photo', font=font, fill=0)

# Display the image
epd.display(epd.getbuffer(image))

GPIO.output(LED_G, GPIO.HIGH)
GPIO.output(LED_Y, GPIO.LOW)
GPIO.output(LED_R, GPIO.LOW)

try:
	while True:
		# Read the button conditions
		take_pic_state=GPIO.input(TAKE_PIC_PIN)
		take_pic_state_2=GPIO.input(TAKE_PIC_PIN_2)
		clear_screen_state=GPIO.input(CLEAR_SCREEN_PIN)
		btn_up_state=GPIO.input(PIC_UP_PIN)
		btn_down_state=GPIO.input(PIC_DOWN_PIN)
#		btn_up_state_2=GPIO.input(PIC_UP_PIN_2)
#		btn_down_state_2=GPIO.input(PIC_DOWN_PIN_2)

		# Check buttons conditions
		if btn_up_state==False: #or btn_up_state_2==False:
			GPIO.output(LED_R, GPIO.LOW)
			GPIO.output(LED_G, GPIO.LOW)
			GPIO.output(LED_Y, GPIO.HIGH)
			photo_increment+=1					# !!!!!!! CHECK FOR THE PLUS SIGN here!
			if photo_increment>max_photo_increment:
				photo_increment=0
			display_photo(photo_array, photo_increment)
		elif btn_down_state==False: # or btn_down_state_2==False:
			GPIO.output(LED_R, GPIO.LOW)
			GPIO.output(LED_G, GPIO.LOW)
			GPIO.output(LED_Y, GPIO.HIGH)
			photo_increment-=1
			if photo_increment<0:
				photo_increment=max_photo_increment
			display_photo(photo_array, photo_increment)	

		elif clear_screen_state==False:
			epd.Clear() 
			image=Image.new('1', (epd.height, epd.width), 255)
			draw=ImageDraw.Draw(image)
			draw.text((10, 10), 'Ready', font=font, fill=0)
			epd.display(epd.getbuffer(image)) # Display the image

		# If the take photo button is pressed (LOW)
		elif take_pic_state==False or take_pic_state_2==False:
			GPIO.output(LED_G,GPIO.LOW)
			GPIO.output(LED_Y,GPIO.LOW)
			GPIO.output(LED_R,GPIO.HIGH)
			timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # Get the current timestamp
			filename=f'{timestamp}.jpg' # Construct the filename
#			cam.annotate(filename, 'plain-small', 'white', 1, 2, [5,170]) # add a timestamp to photo
			cam.take_photo("home/pi/camapp/photos/"+timestamp+".jpg") #save the image to your desktop  !!!!!!! CHECK FOR PLUS SIGN HERE!!!!!!!
			img_path=os.path.join(image_folder, filename)
			image=Image.open(img_path)
#			image=image.convert('1')  # Convert to black and white (already B&W as default
			image=image.resize((epd.height, epd.width))
			epd.display(epd.getbuffer(image)) # Display the final image
			GPIO.output(LED_R, GPIO.LOW)
			GPIO.output(LED_Y, GPIO.LOW)
			GPIO.output(LED_G, GPIO.HIGH)
			photo_array.append(img_path)
			max_photo_increment=len(photo_array)
			max_photo_increment-=1
except KeyboardInterrupt:
    GPIO.cleanup() # Clean up GPIO

# Close the camera
camera.close()
