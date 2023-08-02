import ttkbootstrap as ttk
from data import (
    update_or_get_parser_data,
    update_downloads,
    update_data_manager,
    update_resolutions,
)
from utilitss import resource_path
from functools import partial
import json
import tkinter


def on_closing(window, master):
    window.destroy()
    master.nametowidget('settings').configure(state='normal')


def settings(master: tkinter.Tk):

    def dwnlds_config(event):
        dwnlds_canvas.configure(scrollregion=dwnlds_canvas.bbox('all'))
        dwnlds_canvas.unbind_all("<MouseWheel>")
        dwnlds_canvas.bind_all("<MouseWheel>", dwnlds_mousewheel)

    def dt_mngr_config(event):
        dt_mngr_canvas.configure(scrollregion=dt_mngr_canvas.bbox('all'))
        dt_mngr_canvas.unbind_all("<MouseWheel>")
        dt_mngr_canvas.bind_all("<MouseWheel>", dt_mngr_mousewheel)

    def dwnlds_mousewheel(event):
        dwnlds_canvas.yview_scroll(-1 * (event.delta // 120), 'units')

    def dt_mngr_mousewheel(event):
        dt_mngr_canvas.yview_scroll(-1 * (event.delta // 120), 'units')

    def on_tab_change(event):
        try:
            tab_index = notebook.index(notebook.select())
            scroll_handlers[tab_index](None)
        except KeyError:
            pass

    def on_open_window(event):
        try:
            tab_index = notebook.index(notebook.select())
            scroll_handlers[tab_index](None)
        except KeyError:
            pass

    scroll_handlers = {0: dwnlds_config, 1: dt_mngr_config}

    master.nametowidget('settings').configure(state='disabled')
    parser_data = update_or_get_parser_data(get=True)
    if 'resolutions' not in parser_data:
        with open('parser_data.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        data['resolutions'] = {}
        with open('parser_data.json', 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file)
        parser_data = update_or_get_parser_data(get=True)
    master_geometry_x = master.geometry().split('+')[0].split('x')[0]
    master_geometry_y = master.geometry().split('+')[0].split('x')[1]
    master_position = master.geometry().split('x')[1].split('+')[1:]
    x = int(master_position[0]) + int(master_geometry_x) + 6
    y = master_position[1]

    window = tkinter.Toplevel(master=master, name='settings_toplevel')
    window.title('Settings')
    window.geometry(f'{master_geometry_x}x{master_geometry_y}+{x}+{y}')
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window, master))
    window.bind("<Map>", on_open_window)

    notebook = ttk.Notebook(window, bootstyle='primary', width=369, height=200)
    notebook.pack(expand=True)
    notebook.bind("<<NotebookTabChanged>>", on_tab_change)

    dwnlds_frame = ttk.Frame(notebook, width=400, height=280)
    dwnlds_frame.pack(fill='both', expand=True)
    notebook.add(dwnlds_frame, text='Downloads')
    dwnlds_canvas = ttk.Canvas(dwnlds_frame, width=200, height=280)
    dwnlds_canvas.pack(side='left', fill='both', expand=True)
    dwnlds_scrollbar = ttk.Scrollbar(
        dwnlds_frame,
        orient='vertical',
        bootstyle='primary',
        command=dwnlds_canvas.yview,
    )
    dwnlds_scrollbar.pack(side='right', fill='y', padx=10)
    dwnlds_canvas.configure(yscrollcommand=dwnlds_scrollbar.set)
    frame_4_dwnlds = ttk.Frame(dwnlds_canvas, name='frame_4_dwnlds')
    dwnlds_canvas.create_window((0, 0), window=frame_4_dwnlds, anchor='nw')
    frame_4_dwnlds.bind('<Configure>', dwnlds_config)
    update_downloads(frame_4_dwnlds)

    dt_mngr_frame = ttk.Frame(notebook, width=400, height=280)
    dt_mngr_frame.pack(fill='both', expand=True)
    notebook.add(dt_mngr_frame, text='Data Manager')
    dt_mngr_canvas = ttk.Canvas(dt_mngr_frame, width=200, height=280)
    dt_mngr_canvas.pack(side='left', fill='both', expand=True)
    dt_mngr_scrollbar = ttk.Scrollbar(
        dt_mngr_frame,
        orient='vertical',
        bootstyle='primary',
        command=dt_mngr_canvas.yview,
    )
    dt_mngr_scrollbar.pack(side='right', fill='y', padx=10)
    dt_mngr_canvas.configure(yscrollcommand=dt_mngr_scrollbar.set)
    frame_4_dt_mngr = ttk.Frame(dt_mngr_canvas, name='frame_4_dt_mngr')
    dt_mngr_canvas.create_window((0, 0), window=frame_4_dt_mngr, anchor='nw')
    frame_4_dt_mngr.bind('<Configure>', dt_mngr_config)

    menu = ttk.Combobox(
        frame_4_dt_mngr,
        values=list(parser_data.keys()),
        name='menu',
        state='readonly',
        width=10,
    )
    menu.pack(side='top', padx=10, pady=10, anchor='w')
    menu.set(list(parser_data.keys())[0])
    menu.bind(
        "<<ComboboxSelected>>",
        partial(update_data_manager, frame=frame_4_dt_mngr, master=master)
    )
    update_data_manager(None, frame_4_dt_mngr)

    rsltns_raws_frame = ttk.Frame(notebook, width=400, height=280)
    rsltns_raws_frame.pack(fill='both', expand=True)
    notebook.add(rsltns_raws_frame, text='Raws and Resolutions')
    rsltns_raws_canvas = ttk.Canvas(rsltns_raws_frame, width=200, height=280)
    rsltns_raws_canvas.pack(side='left', fill='both', expand=True)
    frame_4_rsltns_raws = ttk.Frame(
        rsltns_raws_canvas,
        name='frame_4_rsltns_raws',
    )
    rsltns_raws_canvas.create_window(
        (0, 0), window=frame_4_rsltns_raws, anchor='nw'
    )

    raw_entry = ttk.Entry(
        frame_4_rsltns_raws,
        name='entry_raw',
        bootstyle='info',
        width=18,
    )
    raw_entry.pack(side='left', padx=7, pady=10)
    add_raw_bttn = ttk.Button(
        frame_4_rsltns_raws,
        bootstyle='info',
        text='Add Raw',
        name='add_raw',
        width=8,
        command=lambda: update_or_get_parser_data(
            'raws',
            raw_entry.get(),
            master=master,
        ),
    )
    add_raw_bttn.pack(side='right', padx=10)

    resolutions_frame = ttk.Frame(rsltns_raws_frame, name='resolutions_frame')
    resolutions_frame.place(x=10, y=45)
    update_resolutions(resolutions_frame, master)

    window.focus_force()
    window.mainloop()


if __name__ == '__main__':
    pass
