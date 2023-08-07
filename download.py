from qbittorrent import Client
import time
import os
from data import update_or_get_parser_data
from utilitss import resource_path
from plyer import notification
from threading import Thread
from const import NAME, LOCALHOST


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
        name: str,
        title: str,
        number: str,
        ):
    qb = Client(LOCALHOST)
    qb.login('admin')
    parser_data = update_or_get_parser_data(get=True)
    kwargs = {'link': magnet}
    if title in parser_data['downloads']:
        path = f'{parser_data["downloads"][title]}/{number}'
        os.makedirs(path, exist_ok=True)
        kwargs['savepath'] = path
    qb.download_from_link(**kwargs)
    notification.notify(
        app_name=NAME,
        title=NAME,
        message=f'Качаю {name}',
        timeout=10,
        app_icon=resource_path('ico.ico')
    )

    thread = Thread(target=remove_torrent, args=(qb, title))
    thread.start()


if __name__ == '__main__':
    pass
