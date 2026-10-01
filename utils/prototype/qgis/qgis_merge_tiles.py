import os
from PIL import Image

#работа из директории где лежит
source_dir = "./2X" # в этой папке у меня лежат тайлы
output_file = "./merged.png" # запишет по месту где лежит скрипт

TILE = 2 # 2x2
WIDTH_TILE = 2900 # px 
# Если тайлы разной ширины, он просто растянет 
# меньшие к этому "target" значению



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if source_dir.startswith("."):
    source_dir = os.path.normpath(os.path.join(BASE_DIR, source_dir))

if output_file.startswith("."):
    output_file = os.path.normpath(os.path.join(BASE_DIR, output_file))

first_tile_path = os.path.join(source_dir, "tile_0_0.png")
if not os.path.exists(first_tile_path):
    raise FileNotFoundError(f"not found start: {first_tile_path}")


with Image.open(first_tile_path) as img:
    aspect_ratio = img.size[1] / img.size[0] 
    tile_h = int(WIDTH_TILE * aspect_ratio)


total_w = WIDTH_TILE * TILE
total_h = tile_h * TILE
assembled_image = Image.new("RGBA", (total_w, total_h))

for row in range(TILE):
    for col in range(TILE):
        file_name = f"tile_{row}_{col}.png"
        file_path = os.path.join(source_dir, file_name)
        
        if os.path.exists(file_path):
            with Image.open(file_path) as tile:
                if tile.size != (WIDTH_TILE, tile_h):
                    tile = tile.resize((WIDTH_TILE, tile_h), Image.Resampling.LANCZOS)
                
                pos_x = col * WIDTH_TILE
                pos_y = row * tile_h
                assembled_image.paste(tile, (pos_x, pos_y))
        else:
            print(f"file not found {file_name}")

assembled_image.save(output_file, "PNG")
print(f"succes: {output_file} ===")
