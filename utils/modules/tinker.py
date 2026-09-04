#modules/tinker.py

import tkinter as tk
from tkinter import filedialog, messagebox

class AutoGUI:
    def __init__(self, title, schema, func):
        self.root = tk.Tk() 
        self.root.title(title)
        self.root.geometry("500x350")
        self.schema = schema
        self.func = func
        
        self.inputs = {} 

        for item in self.schema:
            frame = tk.Frame(self.root)
            frame.pack(fill="x", padx=15, pady=5)

            lbl = tk.Label(frame, text=item["label"], width=22, anchor="w")
            lbl.pack(side="left")

            entry = tk.Entry(frame)
            entry.insert(0, item["default"]) 
            entry.pack(side="left", expand=True, fill="x", padx=5)
            
            self.inputs[item["id"]] = entry

            if item["type"] == "path":
                btn = tk.Button(frame, text="Open...", command=lambda e=entry: self.choose_dir(e))
                btn.pack(side="right")
                
            elif item["type"] == "file":
                btn = tk.Button(frame, text="Open...", command=lambda e=entry: self.choose_file(e))
                btn.pack(side="right")


        self.run_btn = tk.Button(
            self.root, 
            text="PROCESS!", 
            bg="green", 
            fg="white", 
            font=("Arial", 12, "bold"), 
            command=self.start_process
        )
        self.run_btn.pack(pady=20)

    def choose_dir(self, entry_field):
        dir_path = filedialog.askdirectory()
        if dir_path:
            entry_field.delete(0, tk.END)
            entry_field.insert(0, dir_path)

    def choose_file(self, entry_field):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry_field.delete(0, tk.END)
            entry_field.insert(0, file_path)

    def start_process(self):
        user_params = {field_id: entry.get() for field_id, entry in self.inputs.items()}
        try:
            total = self.func(**user_params)
            messagebox.showinfo("Success", f"Success: {total} files")
        except ValueError as err:
            messagebox.showwarning("Warning", str(err))
        except Exception as err:
            messagebox.showerror("Error", f"Critical Error:\n{str(err)}")

    def run(self):
        self.root.mainloop()
