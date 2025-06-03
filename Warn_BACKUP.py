# Display warnings/notices that prompt the user for a button press, etc.
class Warn():
	def __init__(self):
		self.epd=epd2in7_V2.EPD()
		self.config=Config().load()
		self.home_dir=Path(__file__).parent.resolve() # Current directory
		self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])
		self.fontsize=int(self.config['fontsize'])
 
	# -- CAMERA MESSAGE
	def camera_msg(self, data):
		if data[2]==False:
			whitebalance=str(self.config['whitebalance'])
			brightness=str(self.config['brightness'])
			timestampphoto=str(self.config['timestampphoto'])
			contrast=str(self.config['contrast'])
			menu_text="Press photo button\nor menu button\n"
			menu_text+=f"White Balance: {whitebalance}\n"
			menu_text+=f"Brightness: {brightness}\n"
			menu_text+=f"Add Timestamp: {timestampphoto}\n"
			menu_text+=f"Contrast: {contrast}\n"
			Display().text_with_header(10, 5, "Camera Ready ", menu_text)
			return [0, 'Camera', True, 0]
		else:
			return data 

	# -- AUTOSCROLL MESSAGE
	def autoscroll_msg(self, data, photo_list):
		if len(photo_list)>0:
			if data[2]==False:
				dur=Calc().convert_time_text(int(self.config['autoscrollduration']))
				display_text=f"Wait time = {dur} \nPhoto button = Start\nMenu button = Cancel"
				Display().text_with_header(10, 40, "START AUTOSCROLL", display_text)
				data=[0,'Autoscroll', True, 0]
		else:
			data=Warn().no_photos(data) #   data=[0, 'Autoscroll', True, 0]
		return data
	
	# -- ARCHIVE MESSAGE
	def archive_msg(self, data, photo_list):
		s=''
		num_photos=len(photo_list)
		if num_photos>0:
			if data[2]==False:
				if num_photos==1: s='s'
				display_text=f"This will create a zip file\ncontaining {len(photo_list)} photo{s} currently on file.\n"
				display_text+="Files will then be deleted from \n the 'Photos' directory\nPhoto button = Confirm\nMenu button = Cancel"
				Display().text_with_header(10, 40, "ARCHIVE PHOTOS", display_text)
				data=[0,'Archive Photos', True, 0]
		else:
			data=Warn().no_photos(data)
		return data

	# -- TIMELAPSE MESSAGE
	def timelapse_msg(self, data):
		if data[2]==False:
			dur=self.config['timelapseduration']
			dur=Calc().convert_time_text(int(dur))
			menu_text=f"Time-lapse Wait = {dur}\nPhoto button = Start\nMenu button = Cancel"
			Display().text_with_header(10, 40, "START TIME-LAPSE", menu_text)
			data=[0, 'Time-Lapse Photography', True, 0]
		return data

	# -- WARNING - DELETE SINGLE PHOTO
	def delete_warning(self, data, photo_list):
		num=data[3]
		if data[2]==False:
			filename=photo_list[num]
			Log().info(f"Check delete: {filename}")
			"""
			image=Image.open(filename)
			# !!!!!!! NEW RESIZING use "thumbnail" because it will keep image ratio
#			resized_image = image.copy() # thumbnail() modifies the image in place
#			resized_image.thumbnail((self.epd.height/2, self.epd.height/2), Image.LANCZOS) # LANCZOS = method for resampling or interpolating digital signals
#			resized_image.thumbnail((50, 50), Image.LANCZOS) # LANCZOS = method for resampling or interpolating digital signals
#			resized_image=resized_image.resize((500,500), Image.LANCZOS) 
#			image=resized_image
			draw=ImageDraw.Draw(image)
			draw.rectangle([(0, 0), (int(self.epd.width)*2, 70)], fill=0)
			font=ImageFont.truetype(self.font_path, self.fontsize+4)
			draw.text((10, 2), "DELETE PHOTO?", font=font, fill=255)
			font=ImageFont.truetype(self.font_path, self.fontsize-1)
			draw.text((10, self.fontsize+8), "Menu button = Cancel\nPhoto button = Confirm", font=font, fill=255)
			self.epd.display(self.epd.getbuffer(image))
			"""
			Display().photo_text_with_header()

			data=[0, 'Delete', True, num]
		else:
			data=[0, 'Delete', True, num]
		return data

	# -- WARNING - PURGE ALL
	def purge_warning(self, data, photo_list):
		if data[2]==False:
			if len(photo_list)>0:
				Log().warning('Purge ALL Warning')
				menu_text=f"Menu button = Cancel\nPhoto button = Confirm"
				Display().text_with_header(10, 40, f"DELETE {len(photo_list)} PHOTOS?", menu_text)
				data=[0, 'Purge', True, 0]
			else:
				data=Warn().no_photos(data)
		return data

	def no_photos(self, data):
		if data[2]==False:
			Log().error("List selected, but no photos on file.")
			LEDs.LEDs(0, 0, 1)
			menu_text="There are no photos\non file to show.\n\nPress menu button...."
			Display().text_with_header(10, 40, "NO PHOTOS", menu_text)
			data=[0, 'Main Menu', True, 0]
		return data
