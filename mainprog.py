import RPi.GPIO as GPIO
import time, datetime, os
from picamzero import Camera
from waveshare_epd import epd4in2_V2 # epd2in7_V2  -- is for the GPIO HAT
from PIL import Image,ImageDraw,ImageFont

print("Initializing")

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin for the button
TAKE_PIC_PIN=21
PIC_UP_PIN=6
PIC_DOWN_PIN=13
LED_R=20
LED_G=16
LED_Y=12

GPIO.setwarnings(False) #  where does this need to be???? after next block?????

# Set up the button pin as an input with a pull-up resistor
GPIO.setup(TAKE_PIC_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
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
home_dir=os.environ['HOME'] # set home dir
# image_folder=home_dir+"/camapp/photos/"
image_folder="/home/pi/camapp/photos/"
# home_dir=os.environ['HOME'] #set the location of home directory
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
print("Building photo filename list...")
photo_array=[]
photo_name_array=[]
for filename in os.listdir(image_folder):
	if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
		img_path=str(os.path.join("/home/pi/camapp/photos/", filename))
		photo_array.append(img_path)
#		photo_array.append(os.path.join("/photos", filename))
		photo_name_array.append(img_path)
photo_increment=0
max_photo_increment=len(photo_array)
max_photo_increment-=1

photo_name_list=""

for photo_name in photo_name_array:
	photo_name_list+=photo_name+"\n"

def display_photo(photo_array, key):
#	epd.Clear()
	filename=photo_array[key]
	print(filename)
	image=Image.open(filename)
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
	draw.text((5, 160), filename, font=font, fill=1)
	epd.display(epd.getbuffer(image))

# Create a new image with a white background
image=Image.new("1", (epd.height, epd.width), 255)
draw=ImageDraw.Draw(image)

# Load a font and draw some text
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
draw.text((20, 50), "Ready to take photo", font=font, fill=0)
draw.text((20, 100), "Image Dir: "+image_folder, font=font, fill=0)
draw.text((20, 150), "Num Photos: "+str(max_photo_increment), font=font, fill=0)
draw.text((20, 200), "Photo List: \n"+photo_name_list, fill=0)

# Display the image
epd.display(epd.getbuffer(image))

GPIO.output(LED_G, GPIO.HIGH)
GPIO.output(LED_Y, GPIO.LOW)
GPIO.output(LED_R, GPIO.LOW)

print("Starting script...")

try:
	while True:
		# Read the button conditions
		take_pic_state=GPIO.input(TAKE_PIC_PIN)
		btn_up_state=GPIO.input(PIC_UP_PIN)
		btn_down_state=GPIO.input(PIC_DOWN_PIN)

		# Check buttons conditions
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
		# If the take photo button is pressed (LOW)
		elif take_pic_state==False:
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
except KeyboardInterrupt:
    GPIO.cleanup() # Clean up GPIO

# Close the camera
camera.close()
