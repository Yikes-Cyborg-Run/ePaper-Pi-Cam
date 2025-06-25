<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/title.jpg'>  

## A Raspberry Pi Camera to show photos on an ePaper display. ##  

### Table of Contents ###
• [Main Features](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#main-features)
• [Introduction](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#introduction)
• [Hardware](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#hardware)
• [Install Raspberry Pi OS](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#install-the-raspberry-pi-operating-system)
• [Install Modules](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#install-modules)  
• [Install ePaper-Pi-Cam](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#auto-startboot-time-execution)
• [Enable SPI](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#enable-spi)
• [Auto-Start/Boot-Time Exectution](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#auto-startboot-time-execution)  
• [Questions & Troubleshooting](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam?#questions--troubleshooting)
• [Resources & To-Do](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam?#project-resources-notes--to-do)
• [About the Author](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam?#about-the-author)

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/splash_lego_enclosure.jpg' width='650'>

_Early prototype of the ePaper-Pi-Cam. Forgive the crude lego enclosure, I've no 3D printer!_  

# Main Features #
1) Use your camera to take photos and render them on-the-fly with an ePaper display.
2) Take time-lapse photos with user-defined duration.
3) Display photos you've taken on Autoscroll function with a user-defined duration.
4) Manually scroll through photos you've taken and delete photos if you wish to.
5) Archive your Photos directory to a zip file for protecting from deletion or downloading later.
6) Purge all photos.
7) Customizable Options: Display Font, Font Size, Time-Lapse Duration, Autoscroll Duration, Brightness, Contrast, Enable/Disable Flash, Exposure, Photo Resolution, White Balance, Archive Photos, Show Splash Screen, Clear Display and Shut Down, Show Photo and Shut Down, Purge Entire Photo Directory.

| Menu Name | Options/Items | 
|------------|------------|  
| Main | Camera, Time-Lapse, Manual Scroll, Autoscroll,  Camera Options, Display Options, System Options |  
| Camera Options | Brightness, Contrast, Exposure, Flash, Time-Lapse Duration, White Balance |
| Display Options | Font, Font Size, Autoscroll Duration, Photo Resolution |
| System Options | Archive Photos, Show Splash Screen, Timestamp Photo, Clear Display and Shut Down,  Show Photo and Shut Down, Purge All Photos |

# Introduction #  
<table style="width:500px;" align='right'>
<tr><td>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/TL_sunset.gif'>
</td></tr>
<tr><td><i>This is a time-lapse compilation of the sun going down <br>from my porch. I put it together with photos I downloaded <br>from the camera taken at a 30-second interval.</i>
</td></tr>
</table>

**Inspiration for this project**  
There are an increasing number of projects that take advantage of the ePaper display's functionality. I'm really drawn to these displays and the soft aesthetic they add to pretty much any project. One popular use for the ePaper display is to use it as a picture frame and I've always thought these were interesting. The Pi serves up photos that have been previously saved to an SD card, scrolling through them at an interval. Simple enough and at the same time, very cool. So I thought, why not build an actual camera that takes photos and uses an ePaper display as the screen; and then combine it with the picture frame functionality? I Googled around and didn't really find anything of the sort -- a combination of a camera AND scrolling picture frame. So I decided to see if I could build one.  

**Yeah, but... WHY?**  
I know you may be wondering, why use an ePaper display as a camera screen? Isn't it laggy with the re-drawing? To be fair, this project is a sort of [Rube Goldberg](https://en.wikipedia.org/wiki/Rube_Goldberg) macine. The screen does need to re-draw, and this was one of my major hurdles in putting this together. The ePaper display will need to refresh each time there is a change to the image. Normal displays (like LCDs and such) have a high refresh rate that makes them better suited for displaying dynamic content. But with that benefit, there comes increased power consumption that increases even more with back-lighting of the screen. With ePaper the refresh rate is very noticible (to say the least), but power consumption is quite low as a trade-off. I've set this camera out for hours taking time-lapse photos on a single 18650 lithium-ion battery. Still, the code needs to loop in order to function. In doing so, the ePaper screen will continually refresh despite not having any changes to the display. So I needed a way to let the program know that the display had drawn and to not continue to refresh it upon each iteration of the loop. I believe I did this in the most efficient way I know. But I certainly have plans to refine the code to have the display only partially refresh the changed areas.  

**Some things to keep in mind**    
I understand full well that a lot of this code could be better, and some of it is likely downright offensive to a long-time Python programmer. For that I sincerely apologize. Still, I think I'm learning and getting a little bit better; and that continuing to work on this will help me to improve on all of my shortcomings. To conclude, I would like to emphasize that I would never offer anything up to the public that didn't work for me personally. At this point, I've gone though these steps a number of times from scratch. I know what some of the possible stumbling blocks might be, and hopefully I've doucumented how to overcome them in the walk-through. If anyone has any issues, I will do my absolute best to help. And I am always open to suggestions to make this better and to hopefully learn even more.  

I hope you enjoy this project, I've had a lot of fun with it!  

# Hardware #  
**Hardware Used in This Project:**
1) Raspberry Pi Zero2 W
2) Waveshare 2.7-inch ePaper Hat with built-in GPIO buttons  
   Note: This project does NOT support multi-color ePaper displays -- ONLY black and white ones.
3) Official Raspberry Pi Camera Module V2
4) Micro SD Card (formatted to Fat32)
5) Micro USB data cable → **$${\color{red}MAKE \space SURE \space IT'S \space A \space DATA \space CABLE!}$$**
6) 3x LEDs of different colors, plus 3x 220Ω resistors → **$${\color{blue}LEDs\space optional}$$**
7) 1x extra-bright LED for camera flash, plus 1x 220Ω resistors → **$${\color{blue}LED\space optional}$$**
8) Powerbank (to make it mobile) -- I have plans to add instructions for a battery build.

**Wiring Diagram**  
• This image shows how to wire up the camera buttons if you are not using the ePaper Hat.  
• It also shows the wiring of optional LEDs.  
• IMPORTANT NOTE: The camera in the image below is for display ONLY. This is NOT the proper orientation/connection for the camera. See "Connect the Camera" below for proper connection.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/wiring_diagram.png' width='650'>  

**Setup WaveShare ePaper Display**  
• If you are using the WaveShare 2.7-inch GPIO hat, all you need to do is seat the hat on your Pi.  
• If you're using a different/wired WaveShare display, refer to the GPIO diagram and table below or the image above.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/waveshare_Pi02W_setup.jpg' width='550' align='left'>  
<br>  

| ePaper Pin | Pi GPIO Pin | 
|------------|------------|  
| VCC | 3.3V |  
| GND | GND |
| DIN | 10 (MOSI) |
| CLK | 11 (SCLK) |
| CS | 8 (CE0) |
| DC | 25 |
| RST | 17 |
| BUSY | 24 |

<br>

**Connect Camera Buttons**  
• If you are using the WaveShare 2.7-inch GPIO hat, all you need to do is seat the hat on your Pi.  
• If you're using a different WaveShare display, refer to the diagram and table below.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/Waveshare_2in7_GPIOhat_pins.jpg' align='left' width='400'>  
<br>  

| Button Function | Pi GPIO Pin |
|------------|------------|  
| Take Photo/Select | 5 |  
| Up Selection | 13 |
| Down Selection | 6 |
| Open Menu/Cancel | 19 |

<br>

**Optional Camera LEDs**  
• The addition of LEDs to the camera is optional but adds a little bit of flare to the camera's functionality.  
• The LEDs will light up to notify you that the camera is busy, or that other operations are in progress.  
• If you are using the Waveshare 2.7-inch GPIO hat, you'll need to use a breakout board or some kind of prototype board to connect the LEDs.  
[Example of Breakout Board](https://www.amazon.com/dp/B0DMNJ17PD?ref=ppx_yo2ov_dt_b_fed_asin_title)  
[Example of Prototype Board](https://www.amazon.com/dp/B08C2XSTK2?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)  
• Refer to the table below if you are adding LEDs to your camera.  
• I use these "traffic-light" LEDs as they come with built-in resistors and are simple to wire up.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/traffic_light_LEDs.png' align='left'>  

| LED | Pi GPIO Pin |
|------------|------------|  
| Green | 16 |  
| Yellow | 12 |
| Red | 20 |
| Flash | 23 |  

<br>

**Connect the Camera**  
• For this project, I used the official Raspberry Pi Camera module.  
• Others may work, but you may need to install specific device drivers.  
• Before connecting the camera (or anything for that matter) power off your Pi.  
• Be careful with the connector clips on the Pi and camera, as they are delicate and can break!  
• Pay close attention to how you connect the ribbon cable to both your Pi and your camera.  
• The copper for both ends of the ribbon cable should face as shown below.  

<img src='' align='left' width='400' alt='connect camera'>  
<br>  

# Install the Raspberry Pi Operating System #
**Flash the OS with Raspberry Pi Imager**  
[Download Raspberry Pi Imager here](https://www.raspberrypi.com/software/)  
  
• To start, select Raspberry Pi Zero 2W from the device selection list.  
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/select_board.jpg' width='400'>  

• For the operating system, select "Raspberry Pi OS (other)".  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/os_other.jpg' width='300'>  

• Then select "Raspberry Pi OS Lite (64 bit)".  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/OS_lite64.png' width='300'>  

• Now select the drive where your SD card is stored.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/storage.jpg' width='400'>  

• Click "NEXT".  

**Use OS Customization?**  
*→ You need to configure a few custom settings so you can access WiFi and SSH into your Pi.*  
• Click on the "EDIT SETTINGS" button.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/edit_custom_settings.png' width='500'>  

• Keep the username as "pi" and keep the default password as "raspberry" for now.  
• You can change the password later, but the username **MUST** remain "pi".  
• Under "Configure Wireless LAN", enter your WiFi SSID, WiFi password and select your country.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/general_settings.png' width='400'>  

• Keep the SERVICES settings to enable SSH as they are and click "SAVE" to continue.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/setup_ssh.jpg' width='500'>  

• Click "YES", and then double check the disc you'll be writing to. All data will be erased.  
• Click "CONTINUE" to begin writing the OS.  
• Once the Raspberry Pi Imager has finished, you can eject the card and insert it into your Pi.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/OS_write_complete.png' width='500'>  

### Get Your Pi's IP Address  
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/Pi_data_port.png' width='200' align='right'>  

• To create an SSH session, you need to determine your Pi's IP address.  
• There are a number of ways you can achieve this, but this method works well for me.  
• Connect your Pi to your computer via a USB **data** cable.  
• Be sure to connect to the micro-USB port that is more toward the middle of the board, as the one on the outer edge is for power only.
> [!IMPORTANT]
> * It is essential that USB cable you connect to your Pi is a **DATA** cable.  
> * Some cables are strictly for charging and will not transfer data.  

• Open the terminal from your computer and enter:  
```
ping pi -n 1
```
• The terminal will attempt to verify the status of your Pi and return its IP address.  
• Write down the IP address, you will use this to SSH into your Pi.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/ping_pi.png' width='500'>  

### SSH Into Pi  
• Once you have the IP, you can SSH into your Pi to complete the installation.  
• Replace the IP below with your IP.  
```
ssh pi@192.168.1.139
```
• Enter your password and press Enter.  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/ssh_IP_pw.png' width='500'>  

If you get a warning like the one below, approve it by typing "yes" and pressing Enter.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/ssh_warning.jpg' width='700'>  

**Alternatively....**  
• An alternate way to SSH into your Pi is to open the terminal and type:
```
ssh pi@pi
```
• Then enter your password.  
• However, if you want to download your photos using a file-transfer application like FileZilla, you will need the IP address to connect.  

### Update Pi
• After flashing, it is always recommended to update and upgrade the OS.  
(This process will likely take a couple minutes to complete.)  
```
sudo apt update && sudo apt -y full-upgrade
```

# Install Modules #  
(Installing each module will likely take a couple minutes to complete.)  

### Install picamzero
• This project makes use of the picamzero module to take photos.  
```
sudo apt install python3-picamzero -y
```

### Install Git  
• OS Lite does not include Git, so you will need to install it for this project.
```
sudo apt install git -y
```

### Install gpiozero  
• This project uses the gpiozero module to interface with buttons and LEDs.  
• gpiozero is a library that simplifies interacting with GPIO (General Purpose Input/Output) pins of the Pi.  
• OS Lite does not include gpiozero, so you will need to install it for this project.  
```
sudo apt install python3-gpiozero -y
```

# Install ePaper-Pi-Cam #  
• To get the link to clone this repo, click the green "Code" button at the top of this page.  
• Click the Copy url to clipboard icon/button.  
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/install_ePaper-Pi-Cam.png'>  
• But I've already done this for you, 😉 so you can just open the terminal and paste this in:
```
git clone https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam.git
```
**Alternatively....**  
An alternate method of installation is to download the zip file, extract it, and upload the ePaper-Pi-Cam directory to home/pi/.  

# Enable SPI #
• SPI (Serial Peripheral Interface) must be enabled to use the ePaper display.  
• To to enable this, access the Pi config menu:
```
sudo raspi-config
```
• Use the arrow keys to select option 5 "Interfacing Options".  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/SPI_1.jpg' width='400'>  

• Then select P4 "SPI".  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/SPI_2.jpg' width='400'>  

• Select "Yes" to enable SPI.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/SPI_3.jpg' width='400'>  

• Select "Yes" to reboot your Pi and apply config changes.  
• NOTE: If not prompted to reboot, select Finish from the config menu and manually reboot in the terminal - sudo reboot  
<br>
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/SPI_4.jpg' width='400'>  

> [!IMPORTANT]
> * This project makes use of ePaper displays manufactured by WaveShare.  
> * Installing this project will install drivers for ALL WaveShare displays and save them into the directory "waveshare_epd".  
> * To use a different WaveShare display, you will need to read "How do I use a different ePaper display?" under the [Questions & Troubleshooting](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam?#questions--troubleshooting) section.  

# Auto-Start/Boot-Time Execution #  
• To make the camera automatically start when the Pi boots up, facilitating mobility, you'll need to do a couple things.  
• Open the crontab from the terminal.  
```
sudo crontab -e
```
• Select the first option for the editor.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/crontab_notice.jpg' width='500'>  

• Add the folowwing to the bottom of the file.  
```
@reboot python3 /home/pi/ePaper-Pi-Cam/main.py &
```
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/crontab_setting.jpg' width='600'>  

• Ctrl-X to exit, then Y to save, and Enter to confirm.  
• Then reboot the Pi
```
sudo reboot
```

### All Done! ###  
• At this point, you have completed the installation.
• When you Pi reboots it should automatically start the ePaper-Pi-Cam app, display the splash screen and load the main menu.  
• If you encounter any issues, please check the section below or contact me. I'm glad to help!  

# Questions & Troubleshooting #
**How do I use a different ePaper display?**  
Right now, this code only supports [Waveshare ePaper displays](https://www.waveshare.com/epaper). It is written mostly for the [Waveshare HAT that includes GPIO buttons](https://www.waveshare.com/product/displays/e-paper/epaper-2/2.7inch-e-paper-hat.htm?___SID=U). The fact that the HAT has GPIO buttons built in makes it very convenient and easy to use. HOWEVER, you can use any of the displays listed in the [waveshare_epd](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/tree/main/waveshare_epd) directory. You will need to edit a couple lines of code to use your specific display. First, open the file "eppc.py" and look for this code at the top: `from waveshare_epd import epd2in7_V2`. Edit this code to match your specific display. For example, if you are using the 4.2-inch version-2 display, you would change this to be `from waveshare_epd import epd4in2_V2`. Do NOT include the .py extension. Second, in the Display class of this file, change the code `self.epd=epd2in7_V2.EPD()` to match your display. For example, if you are using the 4.2-inch version-2 display, you would change this to be `self.epd=epd4in2_V2.EPD()`. Save the file, re-upload it to the ePaper-Pi-Cam directory, and restart your Pi.

**How do I download photos from the camera?**  
The FileFilla application is a great resource for gaining access to your photos. It is a free and open-source platform that makes it easy for a user to connect to their Pi. You can [Download FileZilla here](https://filezilla-project.org/) Once you have installed and launched FileZilla, you will need to enter the host (IP address of your Pi), username (pi), and password (default is "raspberry"); then click "Quick Connect".  Navigate to the `home/pi/ePaper-Pi-Cam` directory and download the Photos directory. If you have archived photos, these will be saved in the "Archived_Photos" directory. Open that directory and download the .zip file.  

**When I download from the Photos directory they are in Black & White**  
Well, duh -- This is a black and white display! But in all candor, you can set the camera to take color photos if you wish. That way, when you download them they are in color. To do this, open the file "main.py". Find this line of code:
```
cam.greyscale=True
```
Change it to False (you can also comment it out or delete it completely) and restart your Pi.  
  
**My Pi won't connect to my computer**  
<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/Pi_data_port.png' width='100' align='right'>
The "Law of USB Cables" states: No matter how many USB cables you have, you only ever have ONE good one. 99% of the time when you can't connect it is because the cable is for power-only. You will need a data cable to connect successfully. Furthermore, you need to connect the micro USB to the proper port on the Pi (see image). The data port is the micro USB connection that is more toward the middle of the board. This port will also power the Pi. The port near the edge of the board is for power only and does not support data transfer.    

**How do I restore the original camera defaults?**  
There is a file in the Resources directory titled "default_config.txt". Copy that file into the parent directory and rename it to "config.txt".  

**My camera is not working or is not recognized**  
Make sure that you have connected your camera properly to the Serial Interface port. Refer to the image under Connect the Camera in the [Hardware](https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam#hardware) section.  

**At what resolution/size are photos taken?**  
The default resolution is set to the highest resolution for this particular camera: 3000x2000 -- Need exact number here!!!!!!! You can set the resolution to be lower from the System Options Menu. If you have a camera that will accept a higher resolution   

**How do I change the splash screen?**  
There is a file in the Resources directory named "splash.jpg". To have your own splash screen, simply overwrite this file with your own image. The file must be titled "splash.jpg". Alternatively, you can choose to disable the splash screen altogether from the System Options menu.

**Am I able to add my own fonts?**  
You sure can! You can upload your own fonts to the "Fonts" directory and select them from the Display Options menu. Fonts must be TrueType (.ttf).

# Project Resources, Notes & To-Do #
**picamzero**  
[Docs Recipes](https://picamera.readthedocs.io/en/release-1.13/)
[Getting Started](https://raspberrypifoundation.github.io/picamera-zero/)
[Picamera Project Docs](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0)  
[Using Picamera2 Functions with Picamzero](https://raspberrypifoundation.github.io/picamera-zero/picamera2/)    
[Picamzero API Documentation](https://raspberrypifoundation.github.io/picamera-zero/api_docs/)  
[PiCamzero Timelapse option](https://raspberrypifoundation.github.io/picamera-zero/camera/)

**gpiozero**  
[Install gpiozero](https://gpiozero.readthedocs.io/en/stable/installing.html)  
[gpiozero Info, Docs & Recipies](https://gpiozero.readthedocs.io/en/latest/)
[Recipies → light sensor for auto flash](https://gpiozero.readthedocs.io/en/stable/recipes.html#light-sensor)  

**Waveshare ePaper Display**  
[ePaper Tutorials](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)  
[Waveshare screen rotation -- MAYBE](https://www.waveshare.com/wiki/4.3inch_DSI_LCD)  
[More Waveshare info - Python Screen rotation / partial refresh options](https://www.waveshare.com/wiki/E-Paper_API_Analysis#Python)  
[Waveshare ePaper setup -- complete massive walk-through](https://peppe8o.com/epaper-eink-raspberry-pi/)  
[Waveshare 2.7" with buttons -- Walkthrough with Drawing examples](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)  

**Other Resources**  
[How to Run a Script on Startup for Raspberry Pi - by Sam Westby Tech](https://www.youtube.com/watch?v=Gl9HS7-H0mI)  
[Raspberry Pi Headless Setup for ssh - by Sam Westby Tech](https://www.youtube.com/watch?v=9fEnvDgxwbI)  
[Headless Pi Setup Documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-headless-raspberry-pi)  
[How to Install Git](https://github.com/git-guides/install-git)  
[Raspberry Pi Official Camera Module Documentation](https://www.raspberrypi.com/documentation/accessories/camera.html)  

### To-Do
- [ ] Audit code for efficiencey - remove/refine classes / modules -- logging
- [ ] Partial refresh of display
- [ ] Menu Config Options for: Screen Rotation, Camera Eposure, Screen & Photo Resolution
- [ ] Select a photo for splashscreen from manual scroll
- [ ] Long Term: Wifi connect to download photos?
- [ ] Long Term: Web UI?
- [ ] Long Term: Light sensor for auto-flash?
- [x] Increase flash duration for better exposure.
- [x] Buttons to navigate through past photos.
- [x] Delete single images
- [x] Delete ALL images
- [x] Settings window to change indoor/outdoor brightness, whitebalance, etc.
- [x] Possibly add a bright LED for flash?

# About the Author #  
I am a GIS Analyst currently residing in sunny Central Florida, working in local municipal government. A child of the 70's, I have been programming since the days of the Apple IIe. Although I began my career as a newspaper journalist and graphic designer, that path quickly evolved to include web design. Up until I started working in GIS in 2020, I had never programmed in the Python language. The nature of my job and the applications we use to produce paper and online maps required me to gain some experience with Python. After developing some scripts to automate the many repetitive tasks we must perform, including a couple of Python Toolboxes, I started to fall in love with the language and it's benefits. I have been interested in microcontrollers since a friend introduced me Arduino back in 2009. I put together a number of projects with Arduino before I started to investigate the Raspberry Pi. I have found that the community surrounding microcontrollers, DIY electronics and programming is very supportive and inspiring. I have wanted to contribute to the community for a long time, and I hope that this project may inspire others the same way that the community has inspired me. When I'm not working or tinkering, I enjoy spending time with my wife and family -- hanging out at the beach or simply gardening in our yard and caring for our orchids. Some of my other interests include carpentry, painting & drawing, hiking & camping, and LoRa radio communication.
