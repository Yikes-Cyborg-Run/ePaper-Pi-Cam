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

### Install git
```
sudo apt install git
```

### Install picamera
```
sudo apt install python3-picamzero
```

### Extra Resources
[Picamera Docs](https://projects.raspberrypi.org/en/projects/getting-started-with-picamera/0)

[Run Python script on Startup](https://www.youtube.com/watch?v=Gl9HS7-H0mI)

### To-Do
- [x] Buttons to navigate through past photos.
- [ ] Button to delete single images
- [ ] Button to delete ALL images

