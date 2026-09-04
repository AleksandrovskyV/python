# batch_renamer.py

# i need rename A_#### > B_#### 
# without Adobe Bridge


TOOL_NAME = "Batch Renamer"

CUST_FILEPATH  =  "./SEQ/A_00.png"
CUST_NEW_NAME =  "B"
CUST_DELIMITER  = "_"

import os, sys, re


# 2. Config for AutoGUI (based on tinker)
GUI_CONFIGS = [
    {"id": "filepath", "label": "Sequence:", "type": "file", "default": ""},
    {"id": "new_name", "label": "New Name:", "type": "text", "default": ""},
    {"id": "delimiter", "label": "Delimiter:", "type": "text", "default": "_"}
]


def batch_rename(filepath, new_name, delimiter="_", progress_callback=None):
    if not filepath or not os.path.exists(filepath):
        raise ValueError("Please select a valid file first.")

    folder = os.path.dirname(filepath)
    selected_filename = os.path.basename(filepath)
    
    selected_name_no_ext, extension = os.path.splitext(selected_filename)

    match_digits = re.search(r"(\d+)\s*$", selected_name_no_ext)
    if not match_digits:
        raise ValueError("The selected file is not part of a sequence (no digits at the end of the name).")
    
    digits_part = match_digits.group(1)
    base_prefix = selected_name_no_ext[:-len(digits_part)] 

    files_to_process = []
    for f_name in os.listdir(folder):
        if f_name.endswith(extension):
            name_no_ext, _ = os.path.splitext(f_name)
            
            if name_no_ext.startswith(base_prefix):
                end_digits = re.search(r"(\d+)\s*$", name_no_ext)
                if end_digits:
                    files_to_process.append({
                        "old_filename": f_name,
                        "sort_number": int(end_digits.group(1))
                    })

    if not files_to_process:
        raise ValueError(f"No sequence files found matching this pattern.")

    files_to_process.sort(key=lambda x: x["sort_number"])
    padding = max(2, len(str(len(files_to_process) - 1)) + 1)

    if not new_name.strip():
        final_base = base_prefix.rstrip(delimiter)
    else:
        final_base = new_name.strip()


    first_file = files_to_process[0]["old_filename"]
    first_new = f"{final_base}{delimiter}{str(0).zfill(padding)}{extension}"
    print(f"[Sequence Detected] Total files: {len(files_to_process)}")
    print(f"[Preview] Transform: {first_file}  --->  {first_new}")


    for index, file_info in enumerate(files_to_process):
        old_path = os.path.join(folder, file_info["old_filename"])
        formatted_index = str(index).zfill(padding)
        new_filename = f"{final_base}{delimiter}{formatted_index}{extension}"
        new_path = os.path.join(folder, new_filename)

        os.rename(old_path, new_path)

        if progress_callback:
            progress_callback(file_info["old_filename"], new_filename, index + 1, len(files_to_process))

    return len(files_to_process)




# 4. Блок запуска с поддержкой хака путей и заглушки MagicMock
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    from modules.tinker import AutoGUI
except ImportError:
    from unittest.mock import MagicMock
    print(f"[!] {TOOL_NAME} not found AutoGUI. Running headless...")
    AutoGUI = MagicMock()

if __name__ == "__main__":
    app = AutoGUI(TOOL_NAME, GUI_CONFIGS, batch_rename) 
    app.run()

    if 'MagicMock' in str(type(app)):
        print(f"\n[{TOOL_NAME}] Starting...")
        try:
            total = batch_rename(
                filepath=CUST_FILEPATH, 
                new_name=CUST_NEW_NAME, 
                delimiter=CUST_DELIMITER
            )
            print(f"[{TOOL_NAME}] Complete!")
        except ValueError as err:
            print(f"[{TOOL_NAME}] {err}")
        except Exception as err:
            print(f"[{TOOL_NAME}] {err}")

    input("\nPress Enter to exit...")