# pillow gif maker 
# support any length size 

import os
from PIL import Image

source_folder = "./cursors_seq"
gif_name = "cursors.gif"

target_color = 64
target_ms = 33 
# 40 ms = 25 FPS
# 33 ms = 30 FPS

print(f"Collect png images...")

png_files = sorted(
    [f for f in os.listdir(source_folder) if f.lower().endswith(".png")]
)

if not png_files:
    print("In targe folder no png images!")
    exit()

print(f"Collect png images: {len(png_files)}")

frames = []

for i, file_name in enumerate(png_files):
    file_path = os.path.join(source_folder, file_name)
    img = Image.open(file_path).convert("RGB")

    img_64_colors = img.quantize(colors=target_color, dither=0)
    frames.append(img_64_colors)

    if (i + 1) % 100 == 0:
        print(f"Completed: {i + 1} frames...")

print("Making gif by pillow...")

frames[0].save(
    gif_name,
    save_all=True,
    append_images=frames[1:],
    duration=target_ms,
    loop=0,
    optimize=False,
)

print(f"Succes! File save as: {gif_name}")
