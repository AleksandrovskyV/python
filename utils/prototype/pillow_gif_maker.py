# prototype/pillow_gif_maker.py 

# i need gif > 500 frames  
# mouse on black solid = perfect

import os
from PIL import Image

CUST_FILEPATH = "./cursors_seq"
CUST_FILENAME = "cursors.gif"

# mouse on black solid = perfect
CUST_COLOR = 64 
USE_DITHER = False # seq with color, set True

# 25 FPS = 40 ms 
# 30 FPS = 33 ms
TARGET_MS = 33 
DROPFRAME = 0 # 0 = disable

print(f"Collect png images...")
png_files = sorted(
    [f for f in os.listdir(CUST_FILEPATH) if f.lower().endswith(".png")]
)

if not png_files:
    print("In targe folder no png images!")
    exit()

drop_step = DROPFRAME if DROPFRAME > 0 else 1
png_files = png_files[::drop_step]
print(f"Collect png images: {len(png_files)}")

frames = []
first_img_path = os.path.join(CUST_FILEPATH, png_files[0])
ref_img = Image.open(first_img_path).convert("RGB")
palette_img = ref_img.quantize(colors=CUST_COLOR, method=Image.Quantize.MAXCOVERAGE)

for i, file_name in enumerate(png_files):
    file_path = os.path.join(CUST_FILEPATH, file_name)
    img = Image.open(file_path).convert("RGB")

    if USE_DITHER:
        # for colored animation
        #img_quantized = img.quantize(palette=palette_img, dither=Image.Dither.NONE)
        img_quantized = img.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG)
    else:
        # for greyscale sequence
        img_quantized = img.quantize(palette=palette_img, dither=0)

    frames.append(img_quantized)

    if (i + 1) % 100 == 0:
        print(f"Completed: {i + 1} frames...")

print("Making gif by pillow...")

frames[0].save(
    CUST_FILENAME,
    save_all=True,
    append_images=frames[1:],
    duration=TARGET_MS * drop_step,
    loop=0, # = infinity
    optimize=False, # not recomned this opt
)

print(f"Succes! File save as: {CUST_FILENAME}")