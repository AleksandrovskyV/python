#entry_run.py

TOOL_NAME = "Python Loader"

print(f"""
{TOOL_NAME}\n
Load selected .py script from folder. Logic:

0. Checking self directory on .py and .spec files
1. If change folder > reload scanning

[auto-generate spec] > creates pure default one-exe config 
[select from]        > use selected .spec or clone (clone replaces script names)

[pack!] > package from selected .spec (and replaces names inside if cloned)
[load!] > load script
""")

import os, sys, re, webbrowser, subprocess

# WINDOWS: TO WORK DIR
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from tkinter import Tk, filedialog, Toplevel, Label, StringVar
from tkinter import ttk
from tkinter.font import Font

def user_window_gui():
    """Create ask window with target script selection"""
    result = {"selected_script": None, "dir": None}
    
    win = Toplevel()
    win.title(TOOL_NAME)
    win.geometry("320x270") 
    win.resizable(False, False)
    win.attributes("-topmost", True)
    
    # Ссылка на сайт
    link_font = Font(size=10, underline=True)
    link_label = Label(win, text="Source Code", font=link_font, cursor="hand2", anchor="w")
    link_label.pack(pady=(24, 0), padx=(15, 0), fill="x")
    
    # Блок 1: Выбор папки
    Label(win, text="Folder with .py files:", anchor="w").pack(pady=(15, 0), padx=(15, 15), fill="x")
    frame_dir = ttk.Frame(win)
    frame_dir.pack(anchor="w", padx=(15, 15), fill="x", pady=(5, 0))
    
    dir_var = StringVar(value=os.getcwd())
    result["dir"] = os.getcwd()
    
    entry_dir = ttk.Entry(frame_dir, textvariable=dir_var, state="readonly")
    entry_dir.pack(side="left", fill="x", expand=True)
    
    # Block 2: Combobox with script-names
    frame_pyname = ttk.Frame(win)
    frame_pyname.pack(anchor="w", padx=(15, 15), fill="x", pady=(15, 0))
    script_text = ttk.Label(frame_pyname, text="Script:")
    script_text.pack(side="left", padx=(0, 10))

    script_var = StringVar(value="")
    unit_combo = ttk.Combobox(frame_pyname, textvariable=script_var, state="readonly")
    unit_combo.pack(side="left", fill="x", expand=True)

    # Block 3: Combobox with spec-files
    frame_specname = ttk.Frame(win)
    frame_specname.pack(anchor="w", padx=(15, 15), fill="x", pady=(15, 0))
    spec_text = ttk.Label(frame_specname, text="Spec:  ")
    spec_text.pack(side="left", padx=(0, 10))

    spec_var = StringVar(value="")
    spec_combo = ttk.Combobox(frame_specname, textvariable=spec_var, state="readonly")
    spec_combo.pack(side="left", fill="x", expand=True)

    def refresh_py_list(folder):
        """Scan folder and return list .py files and .spec files"""
        if not folder or not os.path.exists(folder):
            unit_combo["values"] = []
            spec_combo["values"] = []
            script_var.set("")
            spec_var.set("")
            return
        
        # 1. Сканируем .py файлы (исключая сам загрузчик)
        current_file = os.path.basename(__file__)
        py_files = [f for f in os.listdir(folder) if f.endswith('.py') and f != current_file]
        
        unit_combo["values"] = py_files
        if py_files:
            script_var.set(py_files[0])  # select first file default
            result["selected_script"] = os.path.join(folder, py_files[0])
        else:
            script_var.set("No .py files found")
            result["selected_script"] = None

        # 2. Сканируем .spec файлы для сборки списка вариантов
        spec_files = [f for f in os.listdir(folder) if f.endswith('.spec')]
        
        # Формируем список: первый элемент всегда "auto-generate", затем кастомные шаблоны
        combo_spec_values = ["auto-generate"]
        for sf in spec_files:
            combo_spec_values.append(f"from {sf}")
            
        spec_combo["values"] = combo_spec_values
        
        # --- НОВОЕ ПРАВИЛО АВТОВЫБОРА ---
        if py_files:
            # Получаем базовое имя текущего выбранного скрипта (без .py)
            current_base_name = os.path.splitext(py_files[0])[0]
            expected_spec_name = f"{current_base_name}.spec"
            
            # Если такой .spec файл существует в папке
            if expected_spec_name in spec_files:
                spec_var.set(f"from {expected_spec_name}")
            else:
                spec_var.set("auto-generate")
        else:
            spec_var.set("auto-generate")


    def choose_directory():
        folder = filedialog.askdirectory(title="Select Python Scripts Folder", parent=win)
        if folder:
            dir_var.set(folder)
            result["dir"] = folder
            refresh_py_list(folder)

    ttk.Button(frame_dir, text="...", width=3, command=choose_directory).pack(side="left", padx=(5, 0))
    
    def combo_func(event=None):
        """refresh path with reload combobox"""
        selected_py = script_var.get()
        if selected_py and selected_py != "No .py files found":
            result["selected_script"] = os.path.join(result["dir"], selected_py)
            
            # Динамически проверяем правило при смене скрипта пользователем
            current_base_name = os.path.splitext(selected_py)[0]
            expected_spec_name = f"{current_base_name}.spec"
            
            # Получаем список всех spec файлов из уже загруженных в комбобокс
            all_specs = [v[5:] for v in spec_combo["values"] if v.startswith("from ")]
            
            if expected_spec_name in all_specs:
                spec_var.set(f"from {expected_spec_name}")
            else:
                spec_var.set("auto-generate")

    unit_combo.bind("<<ComboboxSelected>>", combo_func)
    
    # first init list
    refresh_py_list(result["dir"])
    
    # Блок 4: load button
    def on_confirm(event=None):
        if result["selected_script"] and os.path.exists(result["selected_script"]):
            try:
                subprocess.Popen([sys.executable, result["selected_script"]])
            except Exception as e:
                print(f"Error starting script: {e}")
            #finally:
                #win.destroy()
        else:
            print("No valid script selected.")
            win.destroy()

    def on_pack(event=None):
        script_path = result["selected_script"]
        if not script_path or not os.path.exists(script_path):
            print("Error: No script selected for packing.")
            return

        script_dir = result["dir"]
        script_name = os.path.basename(script_path)           # Например: vram_optimizer.py
        base_name = os.path.splitext(script_name)[0]          # Например: vram_optimizer
        target_spec_file = f"{base_name}.spec"                # Спек, который ожидает PyInstaller
        target_spec_path = os.path.join(script_dir, target_spec_file)
        req_path = os.path.join(script_dir, "requirements.txt")

        selected_spec_mode = spec_var.get()

        print(f"\n--- Starting Packaging for: {script_name} ---")
        
        # [1/3] Checking dependencies...
        print("[1/3] Checking dependencies...")
        if os.path.exists(req_path):
            print("   -> Found requirements.txt! Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=script_dir)
        
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], cwd=script_dir)

        # [2/3] Checking build configuration...
        print("[2/3] Checking build configuration...")
        
        # ЛОГИКА 1: Выбран режим генерации шаблона из другого .spec файла
        if selected_spec_mode.startswith("from "):
            template_spec_name = selected_spec_mode[5:].strip()  # отрезаем "from "
            template_spec_path = os.path.join(script_dir, template_spec_name)
            
            if os.path.exists(template_spec_path):
                print(f"   -> Template mode: Copying plain from {template_spec_name} and updating target to '{script_name}'...")
                try:
                    with open(template_spec_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 1. Заменяем целевой скрипт в блоке Analysis (ищет любой файл с расширением .py в кавычках)
                    # Например, ['vram_optimizer.py'] превратит в ['имя_нового_скрипта.py']
                    content = re.sub(r"['\"][^'\"]+\.py['\"]", f"'{script_name}'", content)
                    
                    # 2. Заменяем имя итогового .exe файла во всем конфиге
                    # Например, name='vram_optimizer_from_gpt_reduce' превратит в name='имя_нового_скрипта'
                    updated_content = re.sub(r"""name\s*=\s*['"][^'"]+['"]""", f"name='{base_name}'", content)
                    
                    # Сохраняем как {имя_текущего_скрипта}.spec
                    with open(target_spec_path, 'w', encoding='utf-8') as f:
                        f.write(updated_content)
                        
                    cmd = [sys.executable, "-m", "PyInstaller", "--clean", target_spec_file]
                except Exception as e:
                    print(f"   -> Error processing template spec: {e}. Falling back to default spec check...")
                    selected_spec_mode = "auto-generate"
            else:
                print(f"   -> Template {template_spec_name} not found! Falling back to auto-generate...")
                selected_spec_mode = "auto-generate"


        # ЛОГИКА 2: Стандартный авто-режим (или если сработал фолбэк)
        if selected_spec_mode == "auto-generate":
            if os.path.exists(target_spec_path):
                print(f"   -> Found existing {target_spec_file}! Building from config to keep your excludes...")
                cmd = [sys.executable, "-m", "PyInstaller", "--clean", target_spec_file]
            else:
                print("   -> Configuration not found. Creating a new one from .py file...")
                cmd = [sys.executable, "-m", "PyInstaller", "--clean", "--onefile", "--noconsole", script_name]

        # Запускаем PyInstaller в контексте выбранной папки
        subprocess.run(cmd, cwd=script_dir)

        print("[3/3] Build complete! Check 'dist' folder.")
        #win.destroy()
        refresh_py_list(script_dir)

    # Разметка кнопок в одну строку
    frame_endbtn = ttk.Frame(win)
    frame_endbtn.pack(anchor="w", padx=(15, 15), fill="x", pady=(25, 0))
    
    btn_package = ttk.Button(frame_endbtn, text="pack!", command=on_pack)
    btn_package.pack(side="left", expand=True, fill="x", padx=(0, 5))

    btn_start = ttk.Button(frame_endbtn, text="load!", command=on_confirm)
    btn_start.pack(side="left", expand=True, fill="x", padx=(5, 0))
    
    win.bind("<Return>", on_confirm)
    
    def open_url(event):
        webbrowser.open("https://github.com/AleksandrovskyV/python/")
    link_label.bind("<Button-1>", open_url)
    
    win.wait_window()
    return result["selected_script"], result["dir"]

def run_selecto_py_loader():
    root = Tk()
    root.withdraw()
    user_window_gui()

if __name__ == "__main__":
    run_selecto_py_loader()
