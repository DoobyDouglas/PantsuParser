from qbittorrent import Client
import os
from data import update_or_get_parser_data
from utilitss import resource_path
from plyer import notification
from const import NAME, LOCALHOST
import time


class Torrent:

    __slots__ = ('name', 'link', 'number', 'title')

    def __init__(self, name: str, link: str) -> None:
        self.name = name
        self.link = link
        self.number = None
        self.title = None

    def set_number_and_title(self, title: str) -> None:
        self.number = self.name.replace(title, '').split()[1]
        self.title = title

    def update_db(self, author: str) -> None:
        update_or_get_parser_data(author, self.name)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.__str__()


class Downloader:

    def __init__(self) -> None:
        self.client = Client(LOCALHOST)
        self.client.login()

    def download(self, torrent: Torrent) -> None:
        data = update_or_get_parser_data(get=True)
        kwargs = {'link': torrent.link}
        if torrent.title in data['downloads']:
            path = f'{data["downloads"][torrent.title]}'f'/{torrent.number}'
            os.makedirs(path, exist_ok=True)
            kwargs['savepath'] = path
        self.client.download_from_link(**kwargs)

    def send_notification(self, torrent: Torrent):
        notification.notify(
            app_name=NAME,
            title=NAME,
            message=f'Качаю {torrent.name}',
            timeout=10,
            app_icon=resource_path('ico.ico')
        )

    def remove_torrent(self, torrent: Torrent):
        time.sleep(1)
        flag = False
        while not flag:
            for i in self.client.torrents():
                if torrent.title.strip('?') in i['name']:
                    if i['progress'] != 1:
                        break
                    else:
                        self.client.delete(i['hash'])
                        flag = True
            time.sleep(3)
