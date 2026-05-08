import os
import requests
import customtkinter as ctk
from tkinter import filedialog, messagebox, Menu
import threading

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AfandiLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Afandi Online Fix Launcher")
        self.geometry("600x620")
        self.raw_base = "https://raw.githubusercontent.com/857seif/online-fix-for-steam/main/"
        
        self.setup_ui()

    def setup_ui(self):
        self.title_label = ctk.CTkLabel(self, text="AFANDI ONLINE FIX", font=("Orbitron", 24, "bold"), text_color="#3b8ed0")
        self.title_label.pack(pady=(20, 5))

        self.frame = ctk.CTkFrame(self)
        self.frame.pack(pady=10, padx=40, fill="x")
        
        self.path_entry = ctk.CTkEntry(self.frame, placeholder_text="Paste Game Path here...", width=350)
        self.path_entry.grid(row=0, column=0, padx=10, pady=20)
        self.bind_shortcuts(self.path_entry) # ربط الاختصارات

        self.btn_browse = ctk.CTkButton(self.frame, text="BROWSE", width=100, command=self.browse_folder)
        self.btn_browse.grid(row=0, column=1, padx=10)


        self.id_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.id_frame.pack(pady=10)
        
        self.og_id_entry = ctk.CTkEntry(self.id_frame, placeholder_text="Paste AppID (Ctrl+V)", width=200)
        self.og_id_entry.pack(side="left", padx=10)
        self.bind_shortcuts(self.og_id_entry) 
        self.overlay_var = ctk.BooleanVar(value=True)
        self.overlay_check = ctk.CTkCheckBox(self, text="Enable Steam Overlay", variable=self.overlay_var)
        self.overlay_check.pack(pady=5)

        self.progress = ctk.CTkProgressBar(self, width=400)
        self.progress.set(0)
        self.progress.pack(pady=20)

        self.apply_btn = ctk.CTkButton(self, text="INSTALL FIX", font=("Segoe UI", 16, "bold"), height=45, command=self.start_installation)
        self.apply_btn.pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="Ready...", text_color="gray")
        self.status_label.pack()


    def bind_shortcuts(self, widget):
   
        widget.bind("<Control-v>", lambda e: self.force_paste(widget))
        widget.bind("<Control-V>", lambda e: self.force_paste(widget))
        
   
        widget.bind("<Control-c>", lambda e: self.force_copy(widget))
        widget.bind("<Control-C>", lambda e: self.force_copy(widget))

   
        menu = Menu(self, tearoff=0, bg="#2b2b2b", fg="white", borderwidth=0)
        menu.add_command(label="Paste", command=lambda: self.force_paste(widget))
        menu.add_command(label="Copy", command=lambda: self.force_copy(widget))
        widget.bind("<Button-3>", lambda e: menu.tk_popup(e.x_root, e.y_root))

    def force_paste(self, widget):
        try:
            
            text = self.clipboard_get()
            if text:
  
                try:
                    if widget.selection_get():
                        widget.delete("sel.first", "sel.last")
                except:
                    pass
                widget.insert("insert", text)
        except:
            pass
        return "break" 

    def force_copy(self, widget):
        try:
            selected_text = widget.selection_get()
            self.clipboard_clear()
            self.clipboard_append(selected_text)
        except:
            pass
        return "break"

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.path_entry.delete(0, 'end')
            self.path_entry.insert(0, folder)

    def find_locations(self, start_dir):
        api_dir, is_64, exe_dir = None, None, None
        for root, dirs, files in os.walk(start_dir):
            if "steam_api64.dll" in files:
                api_dir, is_64 = root, True
            elif "steam_api.dll" in files:
                api_dir, is_64 = root, False
            
            for f in files:
                if f.lower().endswith(".exe") and all(x not in f.lower() for x in ["crash", "launcher", "unity"]):
                    exe_dir = root
        return api_dir, is_64, exe_dir

    def start_installation(self):
        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self):

        root_path = self.path_entry.get().strip()
        og_id = self.og_id_entry.get().strip()
        
        if not root_path or not og_id:
            messagebox.showerror("Error", "Missing Path or AppID!")
            return

        self.apply_btn.configure(state="disabled")
        api_dir, is_64, exe_dir = self.find_locations(root_path)

        if not api_dir or not exe_dir:
            messagebox.showerror("Error", "Could not find locations!")
            self.apply_btn.configure(state="normal")
            return

   
        branch = "x64" if is_64 else "x32"
        exe_files = ["version.dll", "afandi.ini"]
        if self.overlay_var.get(): exe_files.append("SteamOverlay64.dll")
        exe_files.append(f"Afandi%20online%20fix-{'64' if is_64 else '32'}.dll")
        
        try:
            for i, f_name in enumerate(exe_files):
                clean_name = f_name.replace("%20", " ")
                url = f"{self.raw_base}{branch}/{f_name}"
                r = requests.get(url, timeout=10)
                with open(os.path.join(exe_dir, clean_name), 'wb') as f: f.write(r.content)
            

            api_name = "steam_api64.dll" if is_64 else "steam_api.dll"
            r = requests.get(f"{self.raw_base}{branch}/{api_name}", timeout=10)
            with open(os.path.join(api_dir, api_name), 'wb') as f: f.write(r.content)

            with open(os.path.join(exe_dir, "afandi.ini"), "w") as f:
                f.write(f"[Settings]\nAppId=480\nogAppId={og_id}\nPluginsFolder=plugins\nGetStubbedLol=false\n")
            
            messagebox.showinfo("Success", "Applied Successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        
        self.apply_btn.configure(state="normal")

if __name__ == "__main__":
    app = AfandiLauncher()
    app.mainloop()