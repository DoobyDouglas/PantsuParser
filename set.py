import ttkbootstrap as ttk
from data import update_or_get_parser_data, path_choice
import sys


def on_closing(window, master):
    window.destroy()
    master.nametowidget('settings').configure(state='normal')


def settings(master: ttk.Window):

    def on_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))
        canvas.unbind_all("<MouseWheel>")
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def on_mousewheel(event):
        canvas.yview_scroll(-1 * (event.delta // 120), 'units')

    master.nametowidget('settings').configure(state='disabled')
    parser_data = update_or_get_parser_data(get=True)
    master_geometry_x = master.geometry().split('+')[0].split('x')[0]
    master_geometry_y = master.geometry().split('+')[0].split('x')[1]
    master_position = master.geometry().split('x')[1].split('+')[1:]
    x = int(master_position[0]) + int(master_geometry_x) + 6
    y = master_position[1]

    window = ttk.Toplevel()
    window.title('Settings')
    window.geometry(f'{master_geometry_x}x{master_geometry_y}+{x}+{y}')
    window.resizable(False, False)
    window.protocol("WM_DELETE_WINDOW", lambda: on_closing(window, master))

    notebook = ttk.Notebook(window, bootstyle='primary', width=369, height=200)
    notebook.pack(pady=0, expand=True)
    rsltns_frame = ttk.Frame(notebook, width=400, height=280)
    dwnlds_frame = ttk.Frame(notebook, width=400, height=280)
    dt_frame = ttk.Frame(notebook, width=400, height=280)
    rsltns_frame.pack(fill='both', expand=True)
    dwnlds_frame.pack(fill='both', expand=True)
    dt_frame.pack(fill='both', expand=True)

    notebook.add(dwnlds_frame, text='Downloads')
    notebook.add(dt_frame, text='Data Manager')
    notebook.add(rsltns_frame, text='Resolutions')

    # erai_raws = ttk.Label(rsltns_frame, text='Erai-raws')
    # erai_raws.grid(column=0, row=0)

    canvas = ttk.Canvas(dwnlds_frame, width=200, height=280)
    canvas.pack(side='left', fill='both', expand=True)
    scrollbar = ttk.Scrollbar(
        dwnlds_frame,
        orient='vertical',
        bootstyle='primary',
        command=canvas.yview,
    )
    scrollbar.pack(side='right', fill='y', padx=10)
    canvas.configure(yscrollcommand=scrollbar.set)
    frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor='nw')
    frame.bind('<Configure>', on_configure)

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
    window.focus_force()
    window.mainloop()


if __name__ == '__main__':
    pass
