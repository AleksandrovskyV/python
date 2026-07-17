# pillow gif maker 
# support any length size 

import os
from PIL import Image

source_folder = "./cursors_seq"
gif_name = "cursors.gif"

# mouse on black solid = perfect
target_color = 64 
use_dither = False # seq with color, set True

# 25 FPS = 40 ms 
# 30 FPS = 33 ms
target_ms = 33 
dropframe = 0 # 0 = disable

print(f"Collect png images...")
png_files = sorted(
    [f for f in os.listdir(source_folder) if f.lower().endswith(".png")]
)

if not png_files:
    print("In targe folder no png images!")
    exit()

drop_step = dropframe if dropframe > 0 else 1
png_files = png_files[::drop_step]
print(f"Collect png images: {len(png_files)}")

frames = []
first_img_path = os.path.join(source_folder, png_files[0])
ref_img = Image.open(first_img_path).convert("RGB")
palette_img = ref_img.quantize(colors=target_color, method=Image.Quantize.MAXCOVERAGE)

for i, file_name in enumerate(png_files):
    file_path = os.path.join(source_folder, file_name)
    img = Image.open(file_path).convert("RGB")

    if use_dither:
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
    gif_name,
    save_all=True,
    append_images=frames[1:],
    duration=target_ms * drop_step,
    loop=0, # = infinity
    optimize=False, # not recomned this opt
)

print(f"Succes! File save as: {gif_name}")