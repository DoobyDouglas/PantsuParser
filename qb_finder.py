import os
import tkinter
from config import get_config, write_config
from utilitss import qb_strt_and_main_wndw_rtrn
from const import ROOTS, QB_EXE
import psutil
from threading import Thread
from utilitss import wait
import ttkbootstrap as ttk
import tkinter.messagebox


def is_qb_running(path: str = None):
    for proc in psutil.process_iter(['name', 'exe']):
        if QB_EXE in proc.name():
            if not path:
                return proc.info['exe']
            else:
                if path == proc.info['exe']:
                    return True
                return False


def find_qbittorrent(prgrss_br, srch_dir, qb_finder, master):
    prgrss_br.start()
    for i in ROOTS:
        for root, dirs, files in os.walk(f'{i.upper()}:\\'):
            srch_dir.config(text=root)
            if QB_EXE in files:
                path = os.path.join(root, QB_EXE)
                write_config('qbittorrent_path', path)
                prgrss_br.stop()
                qb_finder.destroy()
                qb_strt_and_main_wndw_rtrn(master, path)
                return
    prgrss_br.stop()
    qb_finder.destroy()
    tkinter.messagebox.showinfo(
        'qBittorrent не найден',
        'Запустите qBittorrent вручную'
    )


def qb_finder(master: tkinter.Tk):
    try:
        config = get_config()
        path = config['USER']['qbittorrent_path']
        if not is_qb_running(path):
            qb_strt_and_main_wndw_rtrn(master, path)
    except KeyError:
        path = is_qb_running()
        if path:
            write_config('qbittorrent_path', path)
        else:
            master_geometry_x = master.geometry().split('+')[0].split('x')[0]
            master_position = master.geometry().split('x')[1].split('+')[1:]
            x = int(master_position[0]) + int(master_geometry_x) - 226
            y = int(master_position[1]) + 36

            qb_finder = tkinter.Toplevel(master)
            qb_finder.title('PPqBS')
            qb_finder.resizable(False, False)
            qb_finder.protocol("WM_DELETE_WINDOW", wait)
            qb_finder.geometry(f'220x112+{x}+{y}')

            srch_lbl = ttk.Label(qb_finder, text='Searching qBittorrent...')
            srch_lbl.pack(pady=2, padx=10)

            dir_frame = ttk.Frame(qb_finder)
            dir_frame.pack()
            srch_dir = ttk.Label(dir_frame, wraplength=180)
            srch_dir.pack(pady=2, padx=10)

            prgrss_br = ttk.Progressbar(
                qb_finder,
                mode='determinate',
                length=200,
            )
            prgrss_br.place(relx=0.5, rely=0.5, anchor='center', y=40)

            thread = Thread(
                target=find_qbittorrent,
                args=(prgrss_br, srch_dir, qb_finder, master)
            )
            thread.start()

            qb_finder.wm_attributes('-topmost', 1)
            qb_finder.wm_attributes('-topmost', 0)
            qb_finder.grab_set()
            qb_finder.focus_force()
            qb_finder.mainloop()


if __name__ == '__main__':
    pass
