from camera_classes import Config, Warn, Action, Menu
import os, time

def main():
	data=[0, "Main Menu"]
	photo_increment=0
	photo_list=[]
	image_folder="/home/pi/ePaper-Pi-Cam/photos/"
#	font_directory="/home/pi/ePaper-Pi-Cam/Fonts"
	font_directory=r"C:/Users/ckingsbury/OneDrive - City of Port Orange/Desktop/ePaper-Pi-Cam/Fonts"
	font_list=[]
	for f in os.listdir(font_directory):
		if os.path.isfile:
			os.path.join(font_directory, f)
			font_list.append(f)

	ignore_list=["Take Photo", "Time-lapse Camera", "Autoscroll", "Manual Scroll", "Delete All Photos", "Delete All Photos", "Delete Single", "Camera", "Time-Lapse Camera"]
	menu_list={
                "Main Menu":["Camera", "Camera Options", "Time-lapse Camera", "Autoscroll", "Manual Scroll", "Delete All Photos"],
                "Camera Options":["Font Selection", "Font Size", "Display Rotation", "Autoscroll Duration", "Time-Lapse Duration", "White Balance", "Shut Down", "Delete Photos"],
                "White Balance":["auto", "tungsten", "fluorescent", "indoor", "daylight", "cloudy"],
                "Font Size":["-4", "-2", "0", "+2", "+4"],
                "Autoscroll Duration":[10, 30, 60, 120, 300, 600],
                "Time-lapse Duration":[1, 30, 60, 300, 600, 1800, 3600],
                "Display Rotation":[90, 180, 270],
                "Timestamp Photo":["True", "False"],
                "Font Selection": font_list
    #			"Font Selection":[f for f in os.listdir(font_directory) if os.path.isfile(os.path.join(font_directory, f))]
                }
	action_list=["Take Photo", "Time-lapse Camera", "Autoscroll", "Manual Scroll", "Delete All Photos"]
	warn_list=["Delete All Photos", "Delete Single", "Camera", "Time-Lapse Camera"]
	config=Config.load()

	# Build main menu before loop begins
#	Menu.build(0, "Main Menu", menu_list)

	# Show startup on screen
	splash_photo=["/home/pi/ePaper-Pi-Cam/Resources/splash.jpg"]
	Action.display_photo(splash_photo, 0)
	image=Image.new("1", (epd.height, epd.width), 255)
	draw=ImageDraw.Draw(image)
	font=ImageFont.truetype(font_path, head_fs)
	draw.text((20,50),"Starting up...",font=font,fill=0)
	epd.display(epd.getbuffer(image))
	time.sleep(2)

	while True:
		h=data[0]
		selection=data[1]
#		print(f"{selection} - h: {h} ")
		if selection in warn_list:
			print("warn")
			data=Warn.warn(selection)
		elif selection in action_list:
			print("its an action")
			if selection =="Take Photo":
				Action.take_photo(config, photo_list, image_folder)
#				data=[0, selection]
			if selection =="Manual Scroll":
				photo_increment=Action.manual_scroll(photo_list, photo_increment)
#				data=[0, selection]
		else:
			Menu.build(h, selection, menu_list)
			data=Menu.select(h, selection, menu_list, ignore_list)

if __name__ == "__main__":
    main()
