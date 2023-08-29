# pyinstaller --noconfirm --noconsole --onefile --hidden-import plyer.platforms.win.notification --add-data 'background.png;.' --add-data 'ico.ico;.' --icon=ico.ico PantsuParser.py
import requests
from qbittorrent import Client
import time
import ttkbootstrap as tb
from config import get_config, write_config
from settings import settings, on_closing
from data import (
    update_or_get_parser_data,
    path_choice,
    update_raw_select,
)
from utilitss import resource_path, set_geometry
from parse import parse_erai_raws_or_subsplease, parse_nyaapantsu_xml
import os
import tkinter
from threading import Thread
from PIL import Image, ImageTk
import tkinter.messagebox
import pystray
from plyer import notification
from ttkbootstrap import Style
from tkinter import TclError
from qb_finder import qb_finder
from const import NAME, VERSION, SLEEP_TIME
from models import Downloader
import locale


def on_close(icon: pystray.Icon, master: tkinter.Tk):
    icon.stop()
    master.destroy()
    os._exit(1)


def on_open(icon: pystray.Icon, master: tkinter.Tk):
    icon.stop()
    master.after(0, master.deiconify)


def go_to_tray(master: tkinter.Tk):
    master.withdraw()
    image = Image.open(resource_path('ico.ico'))
    menu = (
        pystray.MenuItem('Open', lambda: on_open(icon, master)),
        pystray.MenuItem('Close', lambda: on_close(icon, master)),
    )
    icon = pystray.Icon(master.wm_title(), image, master.wm_title(), menu)
    try:
        on_closing(master.nametowidget('settings_toplevel'), master)
    except KeyError:
        pass
    icon.run()


def if_rus_keys(event: tkinter.Event):
    try:
        if event.state == 4:
            if event.keycode == 86:
                if ttl_entry.selection_present():
                    ttl_entry.delete(tkinter.SEL_FIRST, tkinter.SEL_LAST)
                    ttl_entry.insert(tkinter.INSERT, master.clipboard_get())
                else:
                    ttl_entry.insert(
                        ttl_entry.index(tkinter.INSERT),
                        master.clipboard_get()
                    )
            elif event.keycode == 65:
                ttl_entry.selection_range(0, tkinter.END)
            elif event.keycode == 67:
                if ttl_entry.selection_present():
                    master.clipboard_clear()
                    master.clipboard_append(ttl_entry.selection_get())
                    master.update()
    except TclError:
        pass


def parse():
    while get_config()['USER'].getboolean('status'):
        try:
            downloader = Downloader()
            locale.setlocale(locale.LC_TIME, 'en_US')
            parse_erai_raws_or_subsplease('erai_raws', downloader)
            parse_erai_raws_or_subsplease('subsplease', downloader)
            parse_nyaapantsu_xml('nyaapantsu', downloader)
        except Exception:
            # tkinter.messagebox.showerror('Ошибка', traceback.format_exc())
            pass
        finally:
            time.sleep(SLEEP_TIME)


def toggle_switch():
    if switch_var.get():
        write_config('status', True)
        thread = Thread(target=parse)
        thread.start()
    else:
        write_config('status', False)


master = tkinter.Tk()
master.title(f'{NAME} v{VERSION:.2f}')
master.geometry(set_geometry(master))
master.resizable(False, False)
master.iconbitmap(default=resource_path('ico.ico'))
master.protocol('WM_DELETE_WINDOW', lambda: go_to_tray(master))

style = Style(theme='journal')

img = Image.open(resource_path('background.png'))
raw_img = ImageTk.PhotoImage(img)
background_label = tkinter.Label(
    master,
    name='background_pic',
    image=raw_img,
)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

switch_var = tb.BooleanVar()
switch = tb.Checkbutton(
    master,
    variable=switch_var,
    bootstyle='success-round-toggle',
    name='"on / off" switch',
    command=toggle_switch,
)
switch.place(relx=1.0, rely=1.0, anchor='se', x=-8, y=-10)
switch_lbl = tb.Label(master, text='ON / OFF', name='"on / off" label')
switch_lbl.place(relx=1.0, rely=1.0, anchor='se', x=-40, y=-9)

ttl_entry = tb.Entry(
    master,
    bootstyle='info',
    name='title name entry',
    width=35,
)
ttl_entry.place(relx=0, rely=0, anchor='nw', x=10, y=10)
ttl_entry.bind('<Key>', if_rus_keys)

add_ttl_bttn = tb.Button(
    master,
    bootstyle='info',
    text='Add Title',
    name='add title',
    width=10,
    command=lambda: update_or_get_parser_data(
        'relations',
        f'{ttl_entry.get().strip()}->{raw_select.get()}',
        master=master
    ),
)
add_ttl_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=10)

raw_select = update_raw_select(master)

save_bttn = tb.Button(
    master,
    bootstyle='info',
    text='Save to...',
    name='save_to',
    width=10,
    command=lambda: path_choice(ttl_entry.get(), master=master),
)
save_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=50)

sttngs_bttn = tb.Button(
    master,
    bootstyle='primary',
    text='Settings',
    name='settings',
    width=10,
    command=lambda: settings(master),
)
sttngs_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=90)

if __name__ == '__main__':
    qb_finder(master)
    master.focus_force()
    master.mainloop()
