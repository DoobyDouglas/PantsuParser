import json
import os
from tkinter import filedialog
import ttkbootstrap as ttk
from tkinter import messagebox

DEFAULT_RAWS = [
    'Erai-raws',
    'SubsPlease',
    'B-Global',
    'Sentai',
    'Baha',
    'CR',
]


def update_raw_select(master: ttk.Window):
    parser_data = update_or_get_parser_data(get=True)
    raw_select = ttk.Combobox(
        master,
        values=list(parser_data['raws']),
        name='raw_select',
        state='readonly',
        width=10,
    )
    raw_select.place(relx=0, rely=0, anchor='nw', x=146, y=50)
    if len(parser_data['raws']) == 0:
        with open('parser_data.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        for raw in DEFAULT_RAWS:
            data['raws'].append(raw)
        with open('parser_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file)
        parser_data = update_or_get_parser_data(get=True)
        update_raw_select(master)
    raw_select.set(parser_data['raws'][0])
    return raw_select


def update_rsltns_raws(
    master: ttk.Window = None,
        ):
    entry = master.nametowidget(
        'settings_toplevel.'
        '!notebook.!frame3.!canvas.frame_4_rsltns_raws.entry_raw'
    )
    entry.delete(0, 'end')
    master.nametowidget('raw_select').destroy()
    update_raw_select(master)


def update_data_manager(
        event,
        frame: ttk.Frame,
        master: ttk.Window = None,
        ):
    parser_data = update_or_get_parser_data(get=True)
    for widget in frame.winfo_children():
        if widget.winfo_name() != 'menu':
            widget.destroy()
        else:
            menu = widget.get()
    for title in parser_data[menu]:
        row_frame = ttk.Frame(frame)
        row_frame.pack(fill='x')
        ttl_lbl = ttk.Label(row_frame, text=title, wraplength=200)
        ttl_lbl.pack(side='left', padx=10, pady=10)
        button = ttk.Button(
            row_frame,
            width=6,
            text='Delete',
            command=(
                lambda key=menu,
                value=title, master=master: update_or_get_parser_data(
                    key, value, delete=True, frame=frame, master=master,
                )
            ),
        )
        button.pack(side='right', padx=10)


def update_downloads(frame: ttk.Frame):
    parser_data = update_or_get_parser_data(get=True)
    for widget in frame.winfo_children():
        widget.destroy()
    for title in parser_data['titles']:
        kwargs = {}
        if title in parser_data['downloads']:
            kwargs['text'] = 'Saved to'
            kwargs['bootstyle'] = 'success'
        else:
            kwargs['text'] = 'Save to...'
            kwargs['bootstyle'] = 'primary'
        row_frame = ttk.Frame(frame)
        row_frame.pack(fill='x')
        ttl_lbl = ttk.Label(row_frame, text=title, wraplength=200)
        ttl_lbl.pack(side='left', padx=10, pady=10)
        button = ttk.Button(
            row_frame,
            width=8,
            command=lambda title=title: path_choice(title, frame=frame),
            **kwargs
        )
        button.pack(side='right', padx=10)


def update_main(master: ttk.Window, key: str):
    master.nametowidget('save_to').destroy()
    if key == 'save':
        text = 'Saved to'
        bootstyle = 'success'
    elif key == 'full':
        text = 'Save to...'
        bootstyle = 'info'
        master.nametowidget('title name entry').delete(0, 'end')
    save_bttn = ttk.Button(
        master,
        bootstyle=bootstyle,
        text=text,
        name='save_to',
        width=10,
        command=lambda: path_choice(
            master.nametowidget('title name entry').get(),
            master=master
        ),
    )
    save_bttn.place(relx=1.0, rely=0, anchor='ne', x=-10, y=50)


def save_download_path(
        title: str,
        path: str,
        frame: ttk.Frame = None,
        master: ttk.Window = None,
        ):
    with open('parser_data.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    data['downloads'][title] = path
    with open('parser_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file)
    if frame:
        update_downloads(frame)
    elif master:
        update_main(master, 'save')


def path_choice(
        title: str,
        frame: ttk.Frame = None,
        master: ttk.Window = None,
        ):
    if not title:
        messagebox.showinfo('Нет названия', 'Сначала введите название')
        return
    kwargs = {}
    parser_data = update_or_get_parser_data(get=True)
    if title in parser_data['downloads']:
        kwargs['initialdir'] = parser_data['downloads'][title]
    path = filedialog.askdirectory(**kwargs)
    if path:
        kwargs = {'title': title, 'path': path}
        if frame:
            kwargs['frame'] = frame
        elif master:
            kwargs['master'] = master
        save_download_path(**kwargs)


def update_or_get_parser_data(
        key: str = None,
        value: str = None,
        get: bool = False,
        delete: bool = False,
        frame: ttk.Frame = None,
        master: ttk.Window = None,
        ):
    if not os.path.exists('parser_data.json'):
        with open('parser_data.json', 'w', encoding='utf-8') as json_file:
            parser_data = {
                'titles': [],
                'raws': DEFAULT_RAWS,
                'relations': [],
                'downloads': {},
                'nyaapantsu': [],
                'erai-raws': [],
                'subsplease': [],
            }
            json.dump(parser_data, json_file)
    with open('parser_data.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    if get:
        return data
    elif delete:
        if isinstance(data[key], dict):
            del data[key][value]
        elif isinstance(data[key], list):
            for i, j in enumerate(data[key]):
                if j == value:
                    del data[key][i]
    else:
        if value not in data[key]:
            if key == 'relations' and value.split('->')[0] != '':
                data[key].append(value)
                if value.split('->')[0] not in data['titles']:
                    data['titles'].append(value.split('->')[0])
            elif key == 'raws' and value != '':
                data[key].append(value)
    with open('parser_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file)
    if frame:
        update_data_manager(None, frame, master=master)
    if master:
        update_main(master, 'full')
        try:
            dwnlds = master.nametowidget(
                'settings_toplevel.!notebook.!frame.!canvas.frame_4_dwnlds'
            )
            update_downloads(dwnlds)
            dt_mngr = master.nametowidget(
                'settings_toplevel.!notebook.!frame2.!canvas.frame_4_dt_mngr'
            )
            update_data_manager(None, dt_mngr, master=master)
            update_rsltns_raws(master)
        except KeyError:
            pass
        except IndexError:
            pass


if __name__ == '__main__':
    pass
