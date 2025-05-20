from camera_classes import Config, Warn, Action, Menu, Log
import time, datetime, os, sys
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from gpiozero import LED, Button
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from PIL import Image, ImageDraw, ImageFont

def main():
	now=datetime.datetime.now()
	todays_date=now.strftime("%Y-%M-%D")
	with open("/home/pi/ePaper-Pi-Cam/log.log", "w") as file:
		file.write('####### '+todays_date+' #######\n')
		file.close()

	# Initialize the display
	epd=epd2in7_V2.EPD()
	epd.init()

	image_dir="/home/pi/ePaper-Pi-Cam/photos/"
	font_dir="/home/pi/ePaper-Pi-Cam/Fonts"
	font_list=[]
	for f in os.listdir(font_dir):
		if os.path.isfile:
			os.path.join(font_dir, f)
			font_list.append(f)

	"""
	# Show startup on screen
	splash_photo=["/home/pi/ePaper-Pi-Cam/Resources/splash.jpg"]
	Action.display_photo(epd, splash_photo, 0)
	image=Image.new("1", (epd.height, epd.width), 255)
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype(font_path, fontsize+4)
	draw.text((20,50),"Starting up...",font=font,fill=0)
	epd.display(epd.getbuffer(image))
	"""
	action_list=["Take Photos", "Time-lapse Camera", "Autoscroll", "Manual Scroll", "Delete All"]
	warn_list=["Camera", "Delete All", "Delete Single Photo", "Camera", "Time-Lapse Camera"]

#	C=Config
#	config=C.load()
	config=Config().load()

	font_path="/home/pi/ePaper-Pi-Cam/Fonts/"+config["font"]
	fontsize=int(config["fontsize"])
	home_dir=os.environ['HOME'] # set home dir
	print(home_dir)
	cam=Camera() # Start camera
	cam.greyscale=True # Take photos in black & white
	cam.still_size=(264, 176) # resolution of the 2.7 GPIO display
	cam.brightness=int(config["brightness"]) # can be -1.0 - 1.0
	cam.whitebalance=str(config["whitebalance"]) # see variable above for options
	image_dir="/home/pi/ePaper-Pi-Cam/photos/" # Where photos will be saved

	# Build a list of saved photos already on file. 
	# New photos will appended to the end of list.
	Log().log("Building list of previously saved photos", 1)
	photo_list=[]
	for filename in os.listdir(image_dir):
		if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
			img_path=str(os.path.join(image_dir, filename))
			photo_list.append(img_path)
	Log().log(f"Photos currently on file: {len(photo_list)}.",1)

	p=Button(5, pull_up=True) # used to take photo or select a menu item
	m=Button(19, pull_up=True) # opens the menu/goes back
	u=Button(13, pull_up=True) # menu selection +1
	d=Button(6, pull_up=True) # menu selection -1

	data=[0, "Main Menu", False]
	scroll_data=[0, False]

	while True:
		h=data[0]
		sel=data[1]
		drawn=data[2]

		if m.is_pressed:
			data=[0,"Main Menu", False]
			scroll_data=[0, False]
		elif sel in warn_list:
#			Log().log("-- Warning...", 1)
			data=Warn().warn(sel, photo_list, scroll_data[0])
		elif sel in action_list:
			if sel=="Take Photos":
				photo_list=Action().take_photo(p, cam, photo_list, image_dir)

			elif sel=="Manual Scroll":
				scroll_data=Action.manual_scroll(u, d, photo_list, scroll_data)
				if p.is_pressed:
					data=[0,"Delete Single Photo",False]

			elif sel=="Autocroll":
				scroll_data=Action().autoscroll(epd, photo_list, scroll_data)
		else:
			if drawn==False:
#				Menu.build(h, sel, photo_list)
				Menu().build(h, sel, photo_list)
				drawn=True
			data=Menu().select(h, p, m, u, d, sel)

if __name__ == "__main__":
    main()
