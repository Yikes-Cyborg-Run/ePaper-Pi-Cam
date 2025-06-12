import os
from PIL import Image, ImageDraw
 
# config
input_folder = r"C:/path/to/folder/"  # <<<<<<<<<<< change
output_name = "label_collage_30"
dpi = 300
 
# A4 at 300 DPI
a4_width_px = int(11.69 * dpi)    # 3507
a4_height_px = int(8.27 * dpi)    # 2480
 
# Grid
cols = 5
rows = 6
max_cards = cols * rows
 
# load cards
card_images = []
for filename in sorted(os.listdir(input_folder)):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        img_path = os.path.join(input_folder, filename)
        card = Image.open(img_path).convert("RGB")
        card_images.append(card)
    if len(card_images) >= max_cards:
        break
 
if len(card_images) < max_cards:
    raise ValueError(f"Only {len(card_images)} card(s) found. You need at least {max_cards} images in the folder.")
 
# create canvas
cell_width = a4_width_px // cols
cell_height = a4_height_px // rows
 
collage = Image.new("RGB", (a4_width_px, a4_height_px), "white")
draw = ImageDraw.Draw(collage)
 
# place cards on grid
for idx, card in enumerate(card_images[:max_cards]):
    row = idx // cols
    col = idx % cols
 
    # scale to fit within cell
    ratio = min(cell_width / card.width, cell_height / card.height)
    new_size = (int(card.width * ratio), int(card.height * ratio))
    resized = card.resize(new_size, Image.Resampling.LANCZOS)
 
    # center inside cell
    x = col * cell_width + (cell_width - new_size[0]) // 2
    y = row * cell_height + (cell_height - new_size[1]) // 2
 
    collage.paste(resized, (x, y))
 
    # grid border
    draw.rectangle([
        col * cell_width,
        row * cell_height,
        (col + 1) * cell_width,
        (row + 1) * cell_height
    ], outline="black", width=1)
 
# save
output_png = f"{output_name}.png"
output_pdf = f"{output_name}.pdf"
collage.save(output_png, dpi=(dpi, dpi))
collage.save(output_pdf, dpi=(dpi, dpi))
 
print(f"Collage saved as: {output_png} and {output_pdf}")