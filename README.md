<!--
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

# ePaper-Pi-Cam
Take photos with Raspberry Pi and show them on a WaveShare ePaper display.
Buttons to loop through past photos.

### Install Pi OS
**Flash the OS with Raspberry Pi Imager**  
[Download it here](https://www.raspberrypi.com/software/)

Select Raspberry Pi Zero 2W from boards selection list.  
Select PiOS64bit lite  
Select the drive where your SD card is stored

### Update Pi
```
sudo apt update && sudo apt -y full-upgrade
```

### Install Git
```
sudo apt install git
```

### Install picamzero
This project makes use of the picamzero module to take photos.
```
sudo apt install python3-picamzero
```

> [!IMPORTANT]
> * This project makes use of ePaper displays manufactured by WaveShare.  
> * Installing this project will install drivers for ALL WaveShare displays and save them into the directory "waveshare_epd".  
> * To use a particular display, you will need to edit the line in "mainprog.py" that looks like this:  
> 

### Extra Resources
[Picamera Docs](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0)

[Run Python script on Startup](https://www.youtube.com/watch?v=Gl9HS7-H0mI)

[Install Git](https://github.com/git-guides/install-git)

### To-Do
- [x] Buttons to navigate through past photos.
- [ ] Button to delete single images
- [ ] Button to delete ALL images

> [!NOTE]
> Useful information that users should know, even when skimming content.

