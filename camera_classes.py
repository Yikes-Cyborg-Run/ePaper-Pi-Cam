import time, datetime, os, logging, re
from gpiozero import LED, Button
from picamzero import Camera
from waveshare_epd import epd2in7_V2 # -- the 2.7inch GPIO HAT
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# If you dont like my kumkuats, dont shake my tree

# DISPLAY: Some of these arent even in use, but keep
class Display():
    def __init__(self):
        self.epd=epd2in7_V2.EPD()
        self.config=Config().load()
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])
        self.fontsize=int(self.config['fontsize'])
        self.font=ImageFont.truetype(self.font_path, self.fontsize)
        self.header_font=ImageFont.truetype(self.font_path, self.fontsize+4)
        self.image=Image.new('1', (self.epd.height, self.epd.width), 255)
        self.draw=ImageDraw.Draw(self.image)
    """
    def text(self, x, y, text):
        self.draw.text((x, y), text, font=self.font, fill=0)
        self.epd.display(self.epd.getbuffer(self.image))
    """
    def text_with_header(self, x, y, header, text):
        self.draw.text((x, y), header, font=self.header_font, fill=0)
        self.draw.text((x, y+self.fontsize+10), text, font=self.font, fill=0)
        self.epd.display(self.epd.getbuffer(self.image))

    def photo(self, image_path):
        image=Image.open(image_path)
        image=image.resize((self.epd.height, self.epd.width))
        self.epd.display(self.epd.getbuffer(image))

# Class to build, navigate through, and select menus
class Menu():
    def __init__(self):
        self.config=Config().load()
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.image_dir=self.home_dir / 'Photos'
        self.font_dir=self.home_dir / 'Fonts'
        self.font_list=[] # for font menu
        for f in os.listdir(self.font_dir):
            if os.path.isfile:
                os.path.join(self.font_dir, f)
                self.font_list.append(f)
        self.font_size=int(self.config['fontsize'])
        self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])
        self.menu_list={
                # Camera options to vflip, hflip, greyscale
                'Main Menu':['Manual Scroll', 'Camera', 'Time-Lapse Photography', 'Autoscroll', 'Camera Options', 'Display Options'],
                'Camera Options':['Time-Lapse Duration', 'White Balance', 'Shut Down', 'Contrast', 'Exposure', 'Purge'],
                'White Balance':['Auto', 'Cloudy', 'Daylight', 'Fluorescent', 'Indoor', 'Tungsten'],
                'Time-Lapse Duration':['1', '30', '60', '300', '600', '1800', '3600'],
                'Timestamp Photo':['Yes', 'No'],
                'Exposure':['None', '5', '10', '30', '60', '120'],
                'Contrast':['0', '5', '10', '15', '20', '25', '32'],
                'Display Options':['Font', 'Font Size', 'Display Rotation', 'Autoscroll Duration', 'Show Splash Screen'],
                'Font Size':['12', '14', '16', '18', '20', '22', '24'],
                'Autoscroll Duration':['10', '30', '60', '120', '300', '600'],
                'Display Rotation':['90', '180', '270'],
                'Show Splash Screen':['Yes', 'No'],
                'Font': self.font_list,
                }
        # These do not need a menu created
        self.ignore_list=['Camera', 'Take Photo', 'Time-lapse Camera', 'Autoscroll', 'Manual Scroll', 'Delete', 'Purge']

    # Build the selected menu
    # sel = selected menu to use, h = item that's highlighted, photo_list = to tally the total photos 
    def build(self, h, sel, photo_list):
        config_val='-keep_check_value-'
        if (sel in self.menu_list['Camera Options']) or (sel in self.menu_list['Display Options']):
            k=sel.lower()
            k=re.sub(r'[^a-zA-Z0-9]', '', k)
            config=Config().load()
            config_val=str(config[k])
        use_menu=self.menu_list[sel]
        Log().info(f"{sel.upper()} -- {use_menu}")
        final_menu=''
        highlighted=use_menu[h]
        for item in use_menu:
            item=str(item)
            if item==config_val: config_notch=' x ' # Mark the current saved option
            else: config_notch=''

            # Show the total number of photos for these items
            if item=='Autoscroll' or item=='Manual Scroll' or item=='Delete' or item=='Purge':
                show=item+f' - {str(len(photo_list))} photos'
            else:
                show=item+config_notch
            if item==highlighted:
                show='-- '+show # add a mark to the one that's highlighted
            final_menu+=show+'\n'
        Display().text_with_header(10, 0, sel.upper(), final_menu)
        return

#    def navigate(self, h, sel, menu_list, ignore_list, p, m, u, d):
    # Function to navigate through the menu
    # h = highlighted item, p = photo button, m = menu button, u = up button, d = down button
    # sel = selected item that is returned when p is pressed to build the menu
    def navigate(self, h, p, m, u, d, sel):
        use_menu=self.menu_list[sel]
        data=[h, sel, True, 0]
        limit=len(use_menu)-1
        if sel not in self.ignore_list:
            if p.is_pressed:
                data=[0, use_menu[h], False, 0]
                if (sel in self.menu_list['Camera Options']) or (sel in self.menu_list['Display Options']):
                    data=Config().save(sel, use_menu[h])
            elif m.is_pressed: # go to main menu
                data=[0, 'Main Menu', False, 0]
            elif u.is_pressed:
                h+=1
                if h>limit:h=0
                data=[h, sel, False, 0]
            elif d.is_pressed:
                h-=1
                if h<0:h=limit
                data=[h, sel, False, 0]
        return data

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
                dur=self.config['autoscrollduration']
                dur=Calc().convert_time_text(int(dur))
                menu_text=f"Wait time = {dur} \nPhoto button = Start\nMenu button = Cancel"
                Display().text_with_header(10, 40, "START AUTOSCROLL", menu_text)
                data=[0,'Autoscroll', True, 0]
        else:
            data=Warn().no_photos(data) #   data=[0, 'Autoscroll', True, 0]
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
            image=Image.open(filename)
            # !!!!!!! NEW RESIZING use "thumbnail" because it will keep image ratio
#            resized_image = image.copy() # thumbnail() modifies the image in place
#            resized_image.thumbnail((self.epd.height/2, self.epd.height/2), Image.LANCZOS) # LANCZOS = method for resampling or interpolating digital signals
#            resized_image.thumbnail((50, 50), Image.LANCZOS) # LANCZOS = method for resampling or interpolating digital signals
#            resized_image=resized_image.resize((500,500), Image.LANCZOS) 
#            image=resized_image
            draw=ImageDraw.Draw(image)
            draw.rectangle([(0, 0), (int(self.epd.width)+10, 70)], fill=0)
            font=ImageFont.truetype(self.font_path, self.fontsize+4)
            draw.text((10, 2), "DELETE PHOTO?", font=font, fill=255)
            font=ImageFont.truetype(self.font_path, self.fontsize-1)
            draw.text((10, self.fontsize+8), "Menu button = Cancel\nPhoto button = Confirm", font=font, fill=255)
            self.epd.display(self.epd.getbuffer(image))
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

class Action():
    def __init__(self):
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.config=Config().load()
#        self.epd=epd2in7_V2.EPD()
        self.timestamp_photo=self.config['timestampphoto']
        self.photo_flash=self.config['photoflash']
        self.image_dir=str(self.home_dir / 'Photos')
        self.fontsize=int(self.config['fontsize'])
        self.font_path=str(self.home_dir / 'Fonts' / self.config['font'])

	# Build a list of saved photos already on file.
	# New photos will appended to the end of list.
    def photo_list(self):
            Log().info("Building list of previously saved photos")
            photo_list=[]
            dir=Path(self.image_dir)
            try:
                for filename in list(dir.glob('*jpg')):
                    if Path(filename).is_file():
                        img_path=self.image_dir / filename
                        photo_list.append(img_path)
                Log().info(f"Photos currently on file: {len(photo_list)}.")
                return photo_list
            except Exception as e:
                Log().error(f"Could not create photo list.\nDetails:\n{e}")

    # p: photo button pressed, cam: initialized camera object from main(), existing photo_list
    def take_photo(self, cam, photo_list):
        LEDs().LEDs(0, 0, 1)
        timestamp=datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # Get the current timestamp
        filename=f'{timestamp}.jpg' # Construct the filename
        if self.timestamp_photo==True: # Check if timestamping is enabled in config...
            cam.annotate(timestamp, 'plain-small', 'white', 1, 2, [5, 170]) # add a timestamp to photo ??????? Any way to make the position dynamic based on the screen size?
        image_path=self.image_dir+'/'+filename
#        LEDs().flash(1)
        Log().info(f"Taking photo:{image_path}")
        cam.take_photo(image_path)
        Display().photo(image_path)
        LEDs().LEDs(1, 0, 0)
        photo_list.append(image_path)
        return photo_list

    def display_photo(self, photo):
        Log().info(f"Loading file: {photo}....")
        Display().photo(photo)
        Log().info(f"Displayed file: {photo}")
        return None

    # MANUAL SCROLL
    # Tab through existing photos with u: up button, d: down button
    # Also uses: existing photo_list and data:[photo_increment, drawn - True or False]
    def manual_scroll(self, u, d, photo_list, data):
        num=data[3]
        drawn=data[2]
        if len(photo_list)>0:
            limit=len(photo_list)-1
            if drawn==True:
                if u.is_pressed:
                    num+=1
                    if num>limit:num=0
                    data=[0, 'Manual Scroll', False, num]
                elif d.is_pressed:
                    num-=1
                    if num<0: num=limit
                    data=[0, 'Manual Scroll', False, num]
            else:
                Action().display_photo(photo_list[num])
                data=[0, 'Manual Scroll', True, num]
        else:
            data=Warn().no_photos(data)
        return data

    def delete_single_photo(self, num, file):
        Log().info(f"Attempting to delete: {file}...")
        try:
            next_num=num-1
            file.unlink()
            Log().info(f"Deleted: {file}")
            menu_text="Going back to list..."
            Display().text_with_header(10, 30, "DELETED PHOTO", menu_text)
            time.sleep(.5)
            return [0, 'Manual Scroll', False, next_num]
        except Exception as e:
            Log().error(f"There was an error deleting file: {file}.\n Details:\n{e}")

    # Function to delete ALL photos on file
    # I used the word "PURGE" to make it stand out against the word delete.
    def purge_photo_dir(self, photo_list):
        Log().info("Attempting to purge all photos...")
        num=len(photo_list)
        del_dir=Path(self.image_dir)
        for file in del_dir.iterdir():
            if file.is_file():
                try:file.unlink()
                except Exception as e:Log().error(f"Could not delete: {file}.\n Details:\n{e}")
                Log().info(f"Deleted: {file}")
        Log().info(f"Deleted All {num} photos")
        menu_text="Going back to main menu...."
        Display().text_with_header(10, 20, f"DELETED ALL\n{num}PHOTOS", menu_text)
        time.sleep(2)
        return [0, 'Main Menu', False, 0]

# Control LEDs
class LEDs():
    def __init__(self):
        self.config=Config().load()
        self.photo_flash=self.config['photoflash']
        self.show_LEDs=self.config['showleds']

    # LEDs to show camera is busy or performing an action
    # Takes 0 or 1, 0=off, 1=on
    def LEDs(self, green, yellow, red):
        if self.show_LEDs=='Yes':
            LED_G=LED(20)
            LED_Y=LED(16)
            LED_R=LED(12)
            if green==1: LED_G.on()
            else: LED_G.off()
            if yellow==1: LED_Y.on()
            else: LED_Y.off()
            if red==1: LED_R.on()
            else: LED_R.off()

    # Camera Flash
    def flash(self, on_or_off):
        if self.photo_flash=='Yes':
            LED_FLASH=LED(4) # !!!!!!! Need proper pin
            if on_or_off==1: 
                LED_FLASH.on()
            else:
                LED_FLASH.off()

class Calc():
    def __init__(self): # ??????? NEED ???????
        pass

    # Calculates a future time to reset next picture in Autoscroll
    def future(self, autoscroll_duration):
        now_time=datetime.datetime.now() # Get the current datetime
        now=int(time.mktime(now_time.timetuple())) # Make timestamp
        future_time=now_time+datetime.timedelta(seconds=autoscroll_duration) # Add autoscroll_duration to timestamp
        future=int(time.mktime(future_time.timetuple()))
        # Log the current and future timestamps
        Log().info(f"   NOW: {str(now)}")
        Log().info(f"FUTURE: {str(future)}")
        return future

    # Display the current timelapse setting
    # !!!!!!! IN PROGRESS
    def convert_time_text(self, dur):
        suffix='..'
        if(dur<60):
            suffix='second'
            dur=dur
        elif(dur>60 and dur<3600):
            suffix='minute'
            dur=dur/60
        elif(dur>60 and dur>3600):
            suffix='hour'
            dur=dur/3600
        # format the text to display
        if dur!=1: final=str(dur)+' '+suffix+'s'
        else: final=suffix
        return final

class Config():
    def __init__(self):
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.config_path=self.home_dir / 'config.txt'

    # Load config settings from txt file
    def load(self):
        config={}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as file:
                    for line in file:
                        if '=' in line:
                            key, value=line.strip().split('=', 1)
                            config[key]=value
            except Exception as e:
                Log().error(f"Could not load config.\nDetails:\n{e}")
        else:
            Log().error("No config file.")
        return config

    # Save config settings to txt file
    def save(self, k, v):
#        self.epd.init()
        # Using key names from the Camera Options menu, strip down and make all lowercase
        k=k.lower()
        k=re.sub(r'[^a-zA-Z0-9]', '', k)
        config=Config().load()
        config[k]=str(v) # Assign passed variable to item
        Log().info(f"Saving option....\n{k} - {v}")
        # Open txt file and save the updated config
        try:
            with open(self.config_path, 'w') as file:
                for key, value in config.items():
                    file.write(f'{key}={value}\n')
                time.sleep(.5)
            Log().info("Saved config")
            return [0, 'Main Menu', False, 0]
        except Exception as e:
            Log().error(f"Could not save config.\nDetails:\n{e}")

# Save info to a log file
class Log():
    def __init__(self): # ??????? NEED ???????
        self.home_dir=Path(__file__).parent.resolve() # Current directory
        self.log_path=self.home_dir / 'log.log'
        self.logger=logging.getLogger(str(self.log_path))
        logging.basicConfig(filename=self.log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)

    def info(self, msg):
        logging.basicConfig(filename=self.log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)
        print(f"INFO: {msg}")
        self.logger.info(msg)

    def warning(self, msg):
        logging.basicConfig(filename=self.log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)
        print(f"WARNING: {msg}")
        self.logger.warning(msg)

    def error(self, msg):
        logging.basicConfig(filename=self.log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)
        print(f"ERROR: {msg}")
        self.logger.info(msg)

    def critical(self, msg):
        logging.basicConfig(filename=self.log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)
        print(f"CRITICAL: {msg}")
        self.logger.critial(msg)

    def debug(self, msg):
        logging.basicConfig(filename=self.log_path, encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%I:%M:%S %p',)
        print(f"DEBUG: {msg}")
        self.logger.debug(msg)



"""
Partial UPDATES ???????
The final test is about partial updates. To say the truth, I don’t love continuously updating an e-ink display as it has a limited number of refreshes (even if very big) and I think that you can use the full power of this kind of display when you want to show a static image which changes with a very low frequency.
The test shows partial updates on the e-ink display by showing a clock that runs for 10 seconds, with an inverse progress bar.
epd.displayPartBaseImage initializes the e-ink display to partial update mode. Then, a loop is executed for 10 seconds, continuously updating the image on the display.
The elapsed time will adjust the width of the progress bar by calculating at each loop the width of the first 3 rectangles. The 4th rectangle will just cover at each run the old time characters, in order to avoid the overlapping between old characters and new ones.
The updated image is displayed using epd.displayPartial, and there’s a pause of 0.2 seconds between each update.
After the end of the while loop, the display is switched back to full update mode.

    clear_display(epd)
    draw.text((0, 0), 'Test 9) Partial Updates', font = font15, fill = black)
    epd.displayPartBaseImage(epd.getbuffer(image))
    epd.init(epd.PART_UPDATE)

    num = 0
    start_time=time.time()
    elapsed = time.time()-start_time
    while (time.time()-start_time) <= 10:
        elapsed=time.time()-start_time
        progress = int(220-int(elapsed*10))
        draw.rectangle((120, 70, progress, 75), fill = black)
        draw.rectangle((progress, 70, 220, 75), fill = white)
        draw.rectangle([(progress,70),(220,75)],outline = black)

        draw.rectangle((120, 80, 220, 105), fill = white)
        draw.text((120, 80), time.strftime('%H:%M:%S'), font = font24, fill = black)
        epd.displayPartial(epd.getbuffer(image))
        time.sleep(0.2)
    epd.init(epd.FULL_UPDATE)
    time.sleep(2)
"""