# pyinstaller --noconfirm --noconsole --onefile --add-data 'background.png;.' --add-data 'ico.ico;.' --icon=ico.ico PantsuParser.py
import requests
from qbittorrent import Client
import time
import xml.dom.minidom as xml
import ttkbootstrap as ttk
from config import get_config, status_change
from settings import settings
from data import (
    update_or_get_parser_data,
    path_choice,
    update_raw_select,
    RESOLUTIONS_DICT,
)
from utilitss import resource_path, set_geometry
import os
import tkinter
from threading import Thread
from ttkbootstrap.toast import ToastNotification
from PIL import Image, ImageTk
import tkinter.messagebox
import traceback
import pystray


SLEEP_TIME = 60 * 5
VERSION = 0.36
NAME = 'PantsuParser'


def on_close(icon: pystray.Icon, master: ttk.Window):
    icon.stop()
    master.destroy()
    os._exit(1)


def on_open(icon: pystray.Icon, master: ttk.Window):
    icon.stop()
    master.after(0, master.deiconify)


def go_to_tray(master: ttk.Window):
    master.withdraw()
    image = Image.open(resource_path('ico.ico'))
    menu = (
        pystray.MenuItem('Open', lambda: on_open(icon, master)),
        pystray.MenuItem('Close', lambda: on_close(icon, master)),
    )
    icon = pystray.Icon(master.wm_title(), image, master.wm_title(), menu)
    icon.run()


def remove_torrent(qb: Client, title):
    time.sleep(1)
    flag = False
    while not flag:
        for i in qb.torrents():
            if title in i['name']:
                if i['progress'] != 1:
                    break
                else:
                    qb.delete(i['hash'])
                    flag = True
        time.sleep(3)


def get_magnet(
        magnet: str,
        episode: str,
        title: str,
        number: str,
        ):
    qb = Client('http://127.0.0.1:8080/')
    qb.login('admin')
    parser_data = update_or_get_parser_data(get=True)
    kwargs = {'link': magnet}
    if title in parser_data['downloads']:
        path = f'{parser_data["downloads"][title]}/{number}'
        os.makedirs(path, exist_ok=True)
        kwargs['savepath'] = path
    qb.download_from_link(**kwargs)
    toast = ToastNotification(
        title=NAME,
        message=f'Качаю {episode}',
        duration=6000,
        )
    toast.show_toast()
    thread = Thread(target=remove_torrent, args=(qb, title))
    thread.start()


def parse_nyaapantsu_xml(key: str, master: ttk.Window):
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
                if torrent not in parser_data['nyaapantsu']:
                    for relation in parser_data['relations']:
                        if relation.split('->')[-1] in torrent:
                            if relation.split('->')[0] in torrent:
                                number = torrent.replace(title, '').split()
                                number = number[1]
                                update_or_get_parser_data(
                                    key,
                                    torrent,
                                    master=master,
                                )
                                get_magnet(
                                    torrents[torrent],
                                    torrent,
                                    title,
                                    number,
                                )


def parse_erai_raws_or_subsplease(key: str, master: ttk.Window):
    parser_data = update_or_get_parser_data(get=True)
    url = get_config()['URLS'][f'{key}_xml']
    try:
        if '_' in key:
            resolution = parser_data['resolutions'][key.replace('_', '-')]
            res = RESOLUTIONS_DICT[resolution]
            url = url.replace('?res=720p', f'?res={res}')
        else:
            resolution = parser_data['resolutions'][key]
            res = RESOLUTIONS_DICT[resolution]
            url = url.replace('?r=720', f'?r={res.replace("p", "").lower()}')
    except KeyError:
        res = '720p'
    response = requests.get(url)
    doc = xml.parseString(response.text)
    title_tags = doc.getElementsByTagName('title')
    link_tags = doc.getElementsByTagName('link')
    if key == 'erai_raws':
        tag_1 = '[Magnet] '
        tag_2 = f' [{res}]'
        author = 'erai-raws'
        name = 'Erai-raws'
    elif key == 'subsplease':
        tag_1 = '[SubsPlease] '
        tag_2 = f' ({res})'
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
                if torrent not in parser_data[author]:
                    for relation in parser_data['relations']:
                        if relation.split('->')[-1] == name:
                            if relation.split('->')[0] == title:
                                number = torrent.replace(title, '').split()
                                number = number[1]
                                update_or_get_parser_data(
                                    author,
                                    torrent,
                                    master=master,
                                )
                                get_magnet(
                                    torrents[torrent],
                                    torrent,
                                    title,
                                    number,
                                )


def parse(master: ttk.Window):
    while get_config()['USER'].getboolean('status'):
        try:
            parse_erai_raws_or_subsplease('erai_raws', master)
            parse_erai_raws_or_subsplease('subsplease', master)
            parse_nyaapantsu_xml('nyaapantsu', master)
        except Exception:
            tkinter.messagebox.showerror('Ошибка', traceback.format_exc())
        finally:
            time.sleep(SLEEP_TIME)


def toggle_switch(master: ttk.Window):
    if switch_var.get():
        status_change(True)
        thread = Thread(target=parse, args=(master,))
        thread.start()
    else:
        status_change(False)


master = ttk.Window(themename='journal')
master.title(f'{NAME} v{VERSION:.2f}')
master.geometry(set_geometry(master))
master.resizable(False, False)
master.iconbitmap(resource_path('ico.ico'))
master.protocol("WM_DELETE_WINDOW", lambda: go_to_tray(master))

img = Image.open(resource_path('background.png'))
raw_img = ImageTk.PhotoImage(img)
background_label = tkinter.Label(
    master,
    name='background_pic',
    image=raw_img,
)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

switch_var = ttk.BooleanVar()
switch = ttk.Checkbutton(
    master,
    variable=switch_var,
    bootstyle='success-round-toggle',
    name='"on / off" switch',
    command=lambda: toggle_switch(master),
)
switch.place(relx=1.0, rely=1.0, anchor='se', x=-8, y=-10)
switch_lbl = ttk.Label(master, text='ON / OFF', name='"on / off" label')
switch_lbl.place(relx=1.0, rely=1.0, anchor='se', x=-40, y=-9)

ttl_entry = ttk.Entry(
    master,
    bootstyle='info',
    name='title name entry',
    width=35,
)
ttl_entry.place(relx=0, rely=0, anchor='nw', x=10, y=10)

add_ttl_bttn = ttk.Button(
    master,
    bootstyle='info',
    text='Add Title',
    name='add title',
    width=10,
    command=lambda: update_or_get_parser_data(
        'relations',
        f'{ttl_entry.get()}->{raw_select.get()}',
        master=master
    ),
)
add_ttl_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=10)

raw_select = update_raw_select(master)

save_bttn = ttk.Button(
    master,
    bootstyle='info',
    text='Save to...',
    name='save_to',
    width=10,
    command=lambda: path_choice(ttl_entry.get(), master=master),
)
save_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=50)

sttngs_bttn = ttk.Button(
    master,
    bootstyle='primary',
    text='Settings',
    name='settings',
    width=10,
    command=lambda: settings(master),
)
sttngs_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=90)


if __name__ == '__main__':
    master.focus_force()
    master.mainloop()
