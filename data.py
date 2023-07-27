import json
import os
from tkinter import filedialog
import ttkbootstrap as ttk


def draw_buttons(frame):
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
        ttl_lbl = ttk.Label(row_frame, text=f'{title[:38]}...')
        ttl_lbl.pack(side='left', padx=10, pady=10)
        button = ttk.Button(
            row_frame,
            width=8,
            command=lambda title=title: path_choice(title, frame),
            **kwargs
        )
        button.pack(side='right', padx=10)


def save_download_path(title: str, path: str, frame):
    with open('parser_data.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    data['downloads'][title] = path
    with open('parser_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file)
    draw_buttons(frame)


def path_choice(title, frame):
    kwargs = {}
    parser_data = update_or_get_parser_data(get=True)
    if title in parser_data['downloads']:
        kwargs['initialdir'] = parser_data['downloads'][title]
    path = filedialog.askdirectory(**kwargs)
    if path:
        save_download_path(title, path, frame)


def update_or_get_parser_data(
        key: str = None,
        value: str = None,
        get: bool = False
        ):
    if not os.path.exists('parser_data.json'):
        with open('parser_data.json', 'w', encoding='utf-8') as json_file:
            parser_data = {
                'titles': [],
                'raws': [],
                'relations': [],
                'nyaapantsu': [],
                'erai-raws': [],
                'subsplease': [],
                'downloads': {},
            }
            json.dump(parser_data, json_file)
    with open('parser_data.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    if get:
        return data
    if value and value != '->' and value[-2:] != '->' and value[:2] != '->':
        if value not in data[key]:
            data[key].append(value)
        if key == 'relations':
            if value.split('->')[0] not in data['titles']:
                data['titles'].append(value.split('->')[0])
        with open('parser_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file)


if __name__ == '__main__':
    pass
