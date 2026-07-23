import os
import re

TARGET_DIR = "./mouth_top" 
FINAL_NAME = "mouth_top" 
TOKEN_DELIMITER = "_" 
FILE_EXTENSION = ".png"


def batch_rename():
    files_to_process = []

    for filename in os.listdir(TARGET_DIR):
        if filename.endswith(FILE_EXTENSION):

            name_without_ext, _ = os.path.splitext(filename)
            tokens = name_without_ext.split(TOKEN_DELIMITER)

            if tokens:
                last_token = tokens[-1]  # Берем последний токен

                # Извлекаем из последнего токена только цифры
                match = re.search(r"\d+", last_token)
                if match:
                    number_val = int(match.group())
                    files_to_process.append(
                        {
                            "old_filename": filename,
                            "sort_number": number_val,
                        }
                    )

    # 2. Сортируем файлы по найденному числу
    files_to_process.sort(key=lambda x: x["sort_number"])

    if not files_to_process:
        print("No files to rename")
        return

    # Определяем нужную длину паддинга (нулей), чтобы имена были красивыми
    # Например, если файлов 15, сделает 01, 02... Если 105, то 001, 002...
    max_index = len(files_to_process) - 1
    padding = max(2, len(str(max_index)))

    print(f"Search Files: {len(files_to_process)}\n")

    for index, file_info in enumerate(files_to_process):
        old_path = os.path.join(TARGET_DIR, file_info["old_filename"])

        formatted_index = str(index).zfill(padding)
        new_filename = f"{FINAL_NAME}_{formatted_index}{FILE_EXTENSION}"
        new_path = os.path.join(TARGET_DIR, new_filename)


        os.rename(old_path, new_path)
        print(f"Renamed: {file_info['old_filename']} -> {new_filename}")


if __name__ == "__main__":
    batch_rename()
