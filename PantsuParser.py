# pyinstaller --noconfirm --noconsole --onefile --add-data 'background.png;.' --add-data 'ico.ico;.' --icon=ico.ico PantsuParser.py
import requests
from qbittorrent import Client
import os
import time
import xml.dom.minidom as xml
import ttkbootstrap as ttk
from conf import get_config, status_change
from set import settings
from data import update_or_get_parser_data
import sys
import tkinter
from threading import Thread
from ttkbootstrap.toast import ToastNotification
from PIL import Image, ImageTk
import tkinter.messagebox
import traceback


SLEEP_TIME = 60 * 5
VERSION = 0.17
NAME = 'PantsuParser'


def on_closing(master):
    master.destroy()
    sys.exit()


def resource_path(path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, path)


def get_magnet(magnet: str, episode: str, title: str):
    qb = Client('http://127.0.0.1:8080/')
    qb.login('admin')
    parser_data = update_or_get_parser_data(get=True)
    kwargs = {'link': magnet}
    print(title)
    print(parser_data['downloads'])
    if title in parser_data['downloads']:
        kwargs['savepath'] = parser_data['downloads'][title]
    qb.download_from_link(**kwargs)
    toast = ToastNotification(
        title=NAME,
        message=f'Качаю {episode}',
        duration=6000,
        alert=True,
        )
    toast.show_toast()


def parse_nyaapantsu_xml(key):
    parser_data = update_or_get_parser_data(get=True)
    url = get_config()['URLS'][f'{key}_xml']
    response = requests.get(url)
    doc = xml.parseString(response.text)
    title_tags = doc.getElementsByTagName('title')
    link_tags = doc.getElementsByTagName('link')
    torrents = {}
    for i in range(len(link_tags)):
        title = title_tags[i].firstChild.nodeValue.split('[GJ.Y] ')[-1]
        if 'nyaa pantsu' not in title.lower():
            torrents[title] = link_tags[i].firstChild.nodeValue
    for torrent in torrents:
        for title in parser_data['titles']:
            if title in torrent:
                flag = False
                if torrent not in parser_data['nyaapantsu']:
                    for relation in parser_data['relations']:
                        if relation.split('->')[-1] in torrent:
                            if relation.split('->')[0] in torrent:
                                update_or_get_parser_data(
                                    key,
                                    torrent
                                )
                                get_magnet(torrents[torrent], torrent, title)
                                flag = True
                    if not flag:
                        for raw in parser_data['raws']:
                            if raw in torrent:
                                update_or_get_parser_data(
                                    key,
                                    torrent
                                )
                                get_magnet(torrents[torrent], torrent, title)
                                flag = True


def parse_erai_raws_or_subsplease(key: str):
    parser_data = update_or_get_parser_data(get=True)
    url = get_config()['URLS'][f'{key}_xml']
    response = requests.get(url)
    doc = xml.parseString(response.text)
    title_tags = doc.getElementsByTagName('title')
    link_tags = doc.getElementsByTagName('link')
    if key == 'erai_raws':
        tag_1 = '[Magnet] '
        tag_2 = ' [720p]'
        author = 'erai-raws'
        name = 'Erai-raws'
    elif key == 'subsplease':
        tag_1 = '[SubsPlease] '
        tag_2 = ' (720p)'
        author = 'subsplease'
        name = 'SubsPlease'
    torrents = {}
    for i in range(len(link_tags)):
        title = title_tags[i].firstChild.nodeValue.split(tag_1)[-1]
        title = title.split(tag_2)[0]
        if author not in title.lower():
            torrents[title] = link_tags[i].firstChild.nodeValue
    for torrent in torrents:
        for title in parser_data['titles']:
            if title in torrent:
                flag = False
                if torrent not in parser_data[author]:
                    for relation in parser_data['relations']:
                        if relation.split('->')[-1] == name:
                            if relation.split('->')[0] == title:
                                update_or_get_parser_data(
                                    author,
                                    torrent
                                )
                                get_magnet(torrents[torrent], torrent, title)
                                flag = True
                    if not flag:
                        if name in parser_data['raws']:
                            update_or_get_parser_data(
                                author,
                                torrent
                            )
                            get_magnet(torrents[torrent], torrent, title)
                            flag = True


def parse():
    while get_config()['USER'].getboolean('status'):
        try:
            parse_erai_raws_or_subsplease('erai_raws')
            parse_erai_raws_or_subsplease('subsplease')
            parse_nyaapantsu_xml('nyaapantsu')
        except Exception:
            tkinter.messagebox.showerror('Ошибка', traceback.format_exc())
        finally:
            time.sleep(SLEEP_TIME)


def toggle_switch():
    if switch_var.get():
        status_change(True)
        thread = Thread(target=parse)
        thread.start()
    else:
        status_change(False)


def set_geometry(master: ttk.Window):
    width = 369
    height = 200
    to_right = master.winfo_screenwidth() // 8
    x = (master.winfo_screenwidth() - width) // 2
    y = (master.winfo_screenheight() - height) // 2
    return f'{width}x{height}+{x + to_right}+{y}'


master = ttk.Window(themename='journal')
master.title(f'{NAME} v{VERSION:.2f}')
master.geometry(set_geometry(master))
master.resizable(False, False)
master.iconbitmap(resource_path('ico.ico'))
master.protocol("WM_DELETE_WINDOW", lambda: on_closing(master))

img = Image.open(resource_path('background.png'))
raw_img = ImageTk.PhotoImage(img)
background_label = tkinter.Label(master, image=raw_img)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

#frame = ttk.Frame(master, width=94, height=120, bootstyle='warning')
#frame.place(relx=1.0, rely=1.0, anchor='se', x=-5, y=-75)

switch_var = ttk.BooleanVar()
switch = ttk.Checkbutton(
    master,
    variable=switch_var,
    bootstyle='success-round-toggle',
    command=toggle_switch,
)
switch.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

ttl_entry = ttk.Entry(master, bootstyle='info', width=40)
ttl_entry.place(relx=0, rely=0, anchor='nw', x=10, y=10)

add_ttl_bttn = ttk.Button(
    master,
    bootstyle='info',
    text='Add Title',
    width=10,
    command=lambda: update_or_get_parser_data('titles', ttl_entry.get()),
)
add_ttl_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=10)

raw_entry = ttk.Entry(master, bootstyle='info', width=15)
raw_entry.place(relx=0, rely=0, anchor='nw', x=160, y=50)

add_raw_bttn = ttk.Button(
    master,
    bootstyle='info',
    text='Add Raw',
    width=10,
    command=lambda: update_or_get_parser_data('raws', raw_entry.get()),
)
add_raw_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=50)

relation_bttn = ttk.Button(
    master,
    bootstyle='success',
    text='Relation',
    width=10,
    command=lambda: update_or_get_parser_data(
        'relations', f'{ttl_entry.get()}->{raw_entry.get()}'
        ),
)
relation_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=90)

sttngs_bttn = ttk.Button(
    master,
    bootstyle='primary',
    text='Settings',
    name='settings',
    width=10,
    command=lambda: settings(master),
)
sttngs_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=130)

if __name__ == '__main__':
    master.focus_force()
    master.mainloop()
