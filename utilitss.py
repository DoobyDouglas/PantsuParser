import os
import sys
import tkinter
import time
import subprocess


def wait():
    pass


def qb_strt_and_main_wndw_rtrn(master: tkinter.Tk, path: str):
    subprocess.Popen(path)
    time.sleep(1)
    master.wm_attributes('-topmost', 1)
    master.wm_attributes('-topmost', 0)
    master.focus_force()


def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, path)


def set_geometry(master: tkinter.Tk):
    width = 338
    height = 160
    to_right = master.winfo_screenwidth() // 8
    x = (master.winfo_screenwidth() - width) // 2
    y = (master.winfo_screenheight() - height) // 2
    return f'{width}x{height}+{x + to_right}+{y}'


if __name__ == '__main__':
    pass
