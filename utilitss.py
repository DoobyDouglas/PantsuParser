import os
import sys
import ttkbootstrap as ttk


def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, path)


def set_geometry(master: ttk.Window):
    width = 338
    height = 160
    to_right = master.winfo_screenwidth() // 8
    x = (master.winfo_screenwidth() - width) // 2
    y = (master.winfo_screenheight() - height) // 2
    return f'{width}x{height}+{x + to_right}+{y}'


if __name__ == '__main__':
    pass
