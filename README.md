<!--


$${\color{red}Red}$$	$${\color{red}Red}$$
$${\color{green}Green}$$	$${\color{green}Green}$$
$${\color{lightgreen}Light \space Green}$$	$${\color{lightgreen}Light \space Green}$$
$${\color{blue}Blue}$$	$${\color{blue}Blue}$$
$${\color{lightblue}Light \space Blue}$$	$${\color{lightblue}Light \space Blue}$$
$${\color{black}Black}$$	$${\color{black}Black}$$
$${\color{white}White}$$




https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax

> [!NOTE]
> Useful information that users should know, even when skimming content.

> [!TIP]
> Helpful advice for doing things better or more easily.

> [!IMPORTANT]
> Key information users need to know to achieve their goal.

> [!WARNING]
> Urgent info that needs immediate user attention to avoid problems.

> [!CAUTION]
> Advises about risks or negative outcomes of certain actions.

-->
# ePaper-Pi-Cam #
Take photos with Raspberry Pi and show them on a WaveShare ePaper display.
Buttons to loop through past photos.

## Wire up hardware ##  
**Setup Waveshare ePaper Display**  
• If you are using the Waveshare 2.7-inch GPIO hat, all you need to do is seat the hat on your Pi.  
• If you're using a different/wired Waveshare display, refer to the wiring diagram and table below.
<br>

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/waveshare_Pi02W_setup.jpg' align='left' width='550'>  
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

 <br><br>

**Connect Camera Buttons**  
• If you are using the Waveshare 2.7-inch GPIO hat, all you need to do is seat the hat on your Pi.  
• If you're using a different Waveshare display, refer to the wiring diagram and table below.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/Waveshare_2in7_GPIOhat_pins.jpg' align='left' width='400'>  
<br>  

| Button Function | Pi GPIO Pin |
|------------|------------|  
| Take Photo/Select | 5 |  
| Up Selection | 13 |
| Down Selection | 6 |
| Open Menu/Cancel | 19 |  

<br><br>

**Optional Camera LEDs**  
• The addition of LEDs to the camera is optional but adds a little bit of flare to the camera's functionality.  
• If you are using the Waveshare 2.7-inch GPIO hat, you'll need to use a breakout board or some kind of prototype board to connect the LEDs.  
[Example of Breakout Board](https://www.amazon.com/dp/B0DMNJ17PD?ref=ppx_yo2ov_dt_b_fed_asin_title)  
[Example of Prototype Board](https://www.amazon.com/dp/B08C2XSTK2?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)  
• Refer to the wiring table below if you are adding LEDs to your camera.
| LED | Pi GPIO Pin |
|------------|------------|  
| Green | 16 |  
| Yellow | 12 |
| Red | 20 |

**Connect the Camera**  
• For this project, I used the official Raspberry Pi Camera module.  
• Others may work, but you may need to install specific device drivers.  
• Before connecting the camera (or anything for that matter) power off your Pi.
• Pay close attention to how you connect the ribbon cable to both your Pi and your camera.
• Be careful 


## Install the Raspberry Pi Operating System
**Flash the OS with Raspberry Pi Imager**  
[Download Raspberry Pi Imager here](https://www.raspberrypi.com/software/)  
• To start, select Raspberry Pi Zero 2W from boards selection list.  
<img src='' align='left' width='400'>  
<br>  
• For the operating system, select "OTHER" -- from the resulting list, select PiOS64bit lite.  
<img src='' align='left' width='400'>  
<br>  
• Select the drive where your SD card is stored.  
<img src='' align='left' width='400'>  
<br>  
• Select "Next".  

**Apply Custom Settings**  
*→ You need to configure a few custom settings so you can access WiFi and SSH into your Pi.*  
• Click on the "EDIT SETTINGS" button.  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/edit_custom_settings.png' width='500'>  

• Keep the username as "pi" and keep the default password as "raspberry" for now.  
• You can change the password later, but the username **MUST** stay as "pi".  
• Under "Configure Wireless LAN", enter your WiFi SSID and WiFi password.  
• Click "SAVE" to continue  

<img src='https://github.com/Yikes-Cyborg-Run/ePaper-Pi-Cam/blob/main/Resources/README_images/general_settings.png' width='400'>
<br>

### Get Pi's IP address  
• To create an SSH session, you need to determine your Pi's IP address.
• Connect your Pi to your computer via a USB cable.
> [!IMPORTANT]
> * It is essential that USB cable you connect to your Pi is a **DATA** cable.  
> * Some cables are strictly for charging and will not transfer data.  

• Open the terminal from your computer and enter:  
```
ping pi@local
```
• The terminal will attempt to verify the status of your Pi and return its IP address.  
• Write down the IP address, you will use this to SSH into your Pi.

### Update Pi
• After flashing, it is always recommended to update and upgrade  the OS.  
```
sudo apt update && sudo apt -y full-upgrade
```

### Install Git  
• OS Lite does not include Git, so you will need to install it for this project.
```
sudo apt install git
```


**Open Pi Configuration to enable SPI**  
• SPI must be enabled to use the ePaper display.  
• To asccess the Pi config menu, do:
'''
sudo raspi-config
'''



### Install picamzero
• This project makes use of the picamzero module to take photos.
```
sudo apt install python3-picamzero
```
• Use command line to take a test photo after picamzero has been installed.  
```
rpicam-still -o image.jpg
```
• The terminal will create an image. After it is done, use the "ls" command to verify that a file was created.



> [!IMPORTANT]
> * This project makes use of ePaper displays manufactured by WaveShare.  
> * Installing this project will install drivers for ALL WaveShare displays and save them into the directory "waveshare_epd".  
> * To use a particular display, you will need to edit the line near the top of "mainprog.py" that looks like this:  
> ``` from waveshare_epd import epd2in7_V2 ```  
edit the part "epd2in7_V2" to match the name of your display.




### Project Resources
**Picamzero Documents**  
[Getting Started](https://raspberrypifoundation.github.io/picamera-zero/)
[Picamera Project Docs](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0)  
[Using Picamera2 Functions with Picamzero](https://raspberrypifoundation.github.io/picamera-zero/picamera2/)    
[Picamzero API Documentation](https://raspberrypifoundation.github.io/picamera-zero/api_docs/)  
[ePaper Tutorials](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)  

**Waveshare ePaper Info**  
[Waveshare screen rotation -- MAYBE](https://www.waveshare.com/wiki/4.3inch_DSI_LCD)  
[More Waveshare info - Python Screen rotation / partial refresh options](https://www.waveshare.com/wiki/E-Paper_API_Analysis#Python)  
[Waveshare ePaper setup -- complete massive walk-through](https://peppe8o.com/epaper-eink-raspberry-pi/)  
[Waveshare 2.7" with buttons -- Walkthrough with Drawing examples](https://dev.to/ranewallin/getting-started-with-the-waveshare-2-7-epaper-hat-on-raspberry-pi-41m8)  

### Other Resources ###
[How to Run a Script on Startup for Raspberry Pi - by Sam Westby Tech](https://www.youtube.com/watch?v=Gl9HS7-H0mI)

[Raspberry Pi Headless Setup for ssh - by Sam Westby Tech](https://www.youtube.com/watch?v=9fEnvDgxwbI)

[Headless Pi Setup Documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#setting-up-a-headless-raspberry-pi)  

[How to Install Git](https://github.com/git-guides/install-git)

### To-Do
- [x] Buttons to navigate through past photos.
- [ ] Button to delete single images
- [ ] Button to delete ALL images
- [ ] Settings window to change indoor/outdoor brightness, whitebalance, etc.
- [ ] Possibly add a bright LED for flash?
