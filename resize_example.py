from PIL import Image
from waveshare_epd import epd2in13bc # Example for 2.13-inch display

desired_width = 300
desired_height = 200

# Open the image
image = Image.open("your_image.jpg")

# Resize the image to fit within the desired dimensions while maintaining aspect ratio
resized_image = image.copy() # thumbnail() modifies the image in place
resized_image.thumbnail((desired_width, desired_height), Image.LANCZOS)

# Prepare the image for your e-paper display (adjust as needed for your specific display)
black_image = resized_image.convert('1')

# Initialize the e-paper display
epd = epd2in13bc.EPD()
epd.init()

# Get the byte buffer
black_buffer = epd.getbuffer(black_image)

# Display the image
epd.display(black_buffer)

# Put the display to sleep (optional)
epd.sleep()