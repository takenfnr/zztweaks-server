import os
import sys
import uuid
import json

import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("dark")

# ===== HWID =====
def get_hwid():
    return str(uuid.getnode())

# ===== SERVER (ÄNDRA DENNA) =====
SERVER_URL = "https://din-app.onrender.com/check"

# ===== LICENSE CHECK =====
def license_check(key):
    hwid = get_hwid()

    try:
        r = requests.post(SERVER_URL, json={
            "key": key,
            "hwid": hwid
        }, timeout=5)

        data = r.json()

        if data.get("status") == "ok":
            with open("license.json", "w") as f:
                json.dump({"hwid": hwid}, f)
            return True

        elif data.get("status") == "locked":
            messagebox.showerror("Error", "Key already used on another PC")
            return False

        else:
            messagebox.showerror("Error", "Invalid key")
            return False

    except Exception as e:
        print("Server error:", e)
        messagebox.showerror("Error", "Server offline")
        return False

# ===== LICENSE GUI =====
def license_gui():
    if os.path.exists("license.json"):
        return True

    result = {"ok": False}

    win = ctk.CTk()
    win.geometry("400x200")
    win.title("Activate ZZTweaks")

    def activate():
        key = entry.get().strip()

        if not key:
            messagebox.showerror("Error", "Enter key")
            return

        if license_check(key):
            result["ok"] = True
            win.destroy()

    ctk.CTkLabel(win, text="Enter License Key",
                 font=("Consolas", 18)).pack(pady=20)

    entry = ctk.CTkEntry(win, width=250)
    entry.pack(pady=10)

    ctk.CTkButton(win, text="Activate", command=activate).pack(pady=10)

    win.mainloop()
    return result["ok"]

# 🔒 STOP APP IF FAIL
if not license_gui():
    sys.exit()

# ===== MAIN GUI =====
app = ctk.CTk()
app.geometry("900x500")
app.title("ZZTweaks")

def set_status(t):
    status_label.configure(text=t)

# ===== DELAY TWEAKS =====
def delay1():
    os.system("powercfg -setactive SCHEME_MIN")
    set_status("Power Plan Applied")

def delay2():
    os.system("bcdedit /set disabledynamictick yes")
    set_status("Dynamic Tick Disabled")

def delay3():
    os.system("bcdedit /set useplatformclock true")
    set_status("Platform Clock Enabled")

def delay4():
    os.system("bcdedit /set useplatformtick yes")
    set_status("Platform Tick Enabled")

def delay5():
    os.system("reg add HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl /v Win32PrioritySeparation /t REG_DWORD /d 26 /f")
    set_status("CPU Priority Tweaked")

# ===== NETWORK TWEAKS =====
def net1():
    os.system("netsh int tcp set global autotuninglevel=disabled")
    set_status("AutoTuning Disabled")

def net2():
    os.system("netsh int tcp set global ecncapability=disabled")
    set_status("ECN Disabled")

def net3():
    os.system("netsh int tcp set global timestamps=disabled")
    set_status("Timestamps Disabled")

def net4():
    os.system("netsh int tcp set global rss=enabled")
    set_status("RSS Enabled")

def net5():
    os.system("netsh int tcp set global chimney=enabled")
    set_status("Chimney Enabled")

def net6():
    os.system("netsh int tcp set global dca=enabled")
    set_status("DCA Enabled")

def net7():
    os.system("ipconfig /flushdns")
    os.system("netsh winsock reset")
    set_status("Network Reset Done")

# ===== GUI =====
sidebar = ctk.CTkFrame(app, width=200)
sidebar.pack(side="left", fill="y")

ctk.CTkLabel(sidebar, text="ZZTweaks",
             font=("Consolas", 22, "bold")).pack(pady=20)

def show_page(page):
    delay_frame.pack_forget()
    network_frame.pack_forget()

    if page == "delay":
        delay_frame.pack(fill="both", expand=True)
    else:
        network_frame.pack(fill="both", expand=True)

ctk.CTkButton(sidebar, text="0 Delay",
              command=lambda: show_page("delay")).pack(pady=10)

ctk.CTkButton(sidebar, text="Network",
              command=lambda: show_page("network")).pack(pady=10)

main = ctk.CTkFrame(app)
main.pack(fill="both", expand=True)

delay_frame = ctk.CTkFrame(main)
network_frame = ctk.CTkFrame(main)

# ===== DELAY PAGE =====
ctk.CTkLabel(delay_frame, text="0 Delay Tweaks",
             font=("Consolas", 20)).pack(pady=10)

ctk.CTkButton(delay_frame, text="Power Plan", command=delay1).pack(pady=5)
ctk.CTkButton(delay_frame, text="Disable Dynamic Tick", command=delay2).pack(pady=5)
ctk.CTkButton(delay_frame, text="Enable Platform Clock", command=delay3).pack(pady=5)
ctk.CTkButton(delay_frame, text="Enable Platform Tick", command=delay4).pack(pady=5)
ctk.CTkButton(delay_frame, text="CPU Priority", command=delay5).pack(pady=5)

# ===== NETWORK PAGE =====
ctk.CTkLabel(network_frame, text="Network Tweaks",
             font=("Consolas", 20)).pack(pady=10)

ctk.CTkButton(network_frame, text="AutoTuning Off", command=net1).pack(pady=5)
ctk.CTkButton(network_frame, text="ECN Off", command=net2).pack(pady=5)
ctk.CTkButton(network_frame, text="Timestamps Off", command=net3).pack(pady=5)
ctk.CTkButton(network_frame, text="RSS On", command=net4).pack(pady=5)
ctk.CTkButton(network_frame, text="Chimney On", command=net5).pack(pady=5)
ctk.CTkButton(network_frame, text="DCA On", command=net6).pack(pady=5)
ctk.CTkButton(network_frame, text="Reset Network", command=net7).pack(pady=5)

# ===== STATUS =====
status_label = ctk.CTkLabel(app, text="Ready")
status_label.pack(side="bottom", pady=10)

show_page("delay")

app.mainloop()
