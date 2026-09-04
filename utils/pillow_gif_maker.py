# pillow_gif_maker.py 

# i need gif > 500 frames  
# mouse on black solid = perfect

TOOL_NAME = "Pillow Gif Maker"

CUST_SEQPATH = "./cursors_seq/cursors_0000.png" 
CUST_FILENAME = "cursors"

# 25 FPS = 40 ms 
# 30 FPS = 33 ms
CUST_COLOR = 64 
USE_DITHER = False # seq with color, set True
TARGET_MS = 33 
DROPFRAME = 0 # 0 = disable

import os, sys, re
from PIL import Image


# 2. Config for AutoGUI (based on tinker)
GUI_CONFIGS = [
    {"id": "seqpath", "label": "Sequence File:", "type": "file", "default": ""},
    {"id": "outpath", "label": "Save Folder:", "type": "path", "default": ""},
    {"id": "filename", "label": "Output GIF Name:", "type": "text", "default": "animation"},
    {"id": "max_colors", "label": "Max Colors (2-256):", "type": "text", "default": "64"},
    {"id": "frame_duration", "label": "Frame Duration (ms):", "type": "text", "default": "33"},
    {"id": "drop_frame", "label": "Drop Frame Step (0-X):", "type": "text", "default": "0"},
]


def png_to_gif(seqpath, outpath=None, filename="default", max_colors="64", frame_duration="33", drop_frame="0",  progress_callback=None):
    
    if not seqpath or not os.path.exists(seqpath):
        raise ValueError("Please select a valid file first.")

    try:
        colors = int(max_colors)
        duration = int(frame_duration)
        drop = int(drop_frame)
    except ValueError:
        raise ValueError("Colors, Duration, and Drop Frame must be valid numbers.")

    # Логика определения папки сохранения (задел на будущее):
    # Если путь не передан или пустой, сохраняем в папку запуска скрипта ("./")
    final_outpath = outpath if outpath and outpath.strip() else "./"
    
    output_name = filename + ".gif"
    output_path = os.path.join(final_outpath, output_name)


    folder = os.path.dirname(seqpath)
    selected_filename = os.path.basename(seqpath)
    selected_name_no_ext, extension = os.path.splitext(selected_filename)
    match_digits = re.search(r"(\d+)\s*$", selected_name_no_ext)
    if not match_digits:
        raise ValueError("The selected file is not part of a sequence (no digits at the end of the name).")
    
    digits_part = match_digits.group(1)
    base_prefix = selected_name_no_ext[:-len(digits_part)] 

    # 3. Сканируем папку и собираем ВСЮ секвенцию, похожую на этот файл
    png_files = []
    for f_name in os.listdir(folder):
        if f_name.lower().endswith(extension.lower()):
            name_no_ext, _ = os.path.splitext(f_name)
            
            # Проверяем, начинается ли файл с той же базы и заканчивается ли цифрами
            if name_no_ext.startswith(base_prefix):
                end_digits = re.search(r"(\d+)\s*$", name_no_ext)
                if end_digits:
                    png_files.append({
                        "filename": f_name,
                        "sort_number": int(end_digits.group(1))
                    })

    if not png_files:
        raise ValueError("No sequence files found matching this pattern.")

    # Сортируем файлы строго по порядку номеров
    png_files.sort(key=lambda x: x["sort_number"])

    # Применяем шаг дроп-кадров, если он задан
    drop_step = drop if drop > 0 else 1
    png_files = png_files[::drop_step]
    total_frames = len(png_files)

    print(f"[{TOOL_NAME}] Sequence Detected: {total_frames} frames.")

    # 4. Обработка кадров через Pillow
    frames = []
    first_img_path = os.path.join(folder, png_files[0]["filename"])
    
    try:
        ref_img = Image.open(first_img_path).convert("RGB")
        palette_img = ref_img.quantize(colors=colors, method=Image.Quantize.MAXCOVERAGE)
    except Exception as e:
        raise ValueError(f"Failed to initialize palette from first image: {e}")

    dither_mode = Image.Dither.FLOYDSTEINBERG if USE_DITHER else 0

    for index, file_info in enumerate(png_files):
        file_path = os.path.join(folder, file_info["filename"])
        img = Image.open(file_path).convert("RGB")

        img_quantized = img.quantize(palette=palette_img, dither=dither_mode)
        frames.append(img_quantized)

        if progress_callback:
            progress_callback(file_info["filename"], output_name, index + 1, total_frames)
        elif (index + 1) % 100 == 0:
            print(f"[{TOOL_NAME}] Completed: {index + 1}/{total_frames} frames...")

    print(f"[{TOOL_NAME}] Saving GIF via Pillow...")
    

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration * drop_step,
        loop=0,
        optimize=False,
    )

    return total_frames



# 5. Блок запуска с поддержкой хака путей и заглушки MagicMock
os.chdir(os.path.dirname(os.path.abspath(__file__)))


try:
    from modules.tinker import AutoGUI
except ImportError:
    from unittest.mock import MagicMock
    print(f"[!] {TOOL_NAME} not found AutoGUI. Running headless...")
    AutoGUI = MagicMock()

if __name__ == "__main__":
    app = AutoGUI(TOOL_NAME, GUI_CONFIGS, png_to_gif) 
    app.run()

    if 'MagicMock' in str(type(app)):
        print(f"\n[{TOOL_NAME}] Headless Mode Active...")
        try:
            total = png_to_gif(
                seqpath=CUST_SEQPATH, 
                filename=CUST_FILENAME, 
                max_colors=CUST_COLOR,
                frame_duration=TARGET_MS,
                drop_frame=DROPFRAME
            )
            print(f"[{TOOL_NAME}] Success! GIF saved in sequence folder (Total frames: {total})")
        except ValueError as err:
            print(f"[{TOOL_NAME}] [Warning] {err}")
        except Exception as err:
            print(f"[{TOOL_NAME}] [Critical Error] {err}")
            
        input("\nPress Enter to exit...")
