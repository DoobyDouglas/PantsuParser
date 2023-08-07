from datetime import datetime as dt
from datetime import timedelta
import requests
from data import update_or_get_parser_data
from const import RESOLUTIONS_DICT, TIMEDELTA
from download import get_magnet
from config import get_config
import xml.dom.minidom as xml
import locale


class Torrent:

    def __init__(self, name, link) -> None:
        self.name = name
        self.link = link
        self.number = None

    def get_number(self, title):
        self.number = self.name.replace(title, '').split()[1]

    def update_db(self, author):
        update_or_get_parser_data(author, self.name)

    def __str__(self) -> str:
        return self.name


def parse_erai_raws_or_subsplease(key: str):
    locale.setlocale(locale.LC_TIME, 'en_US')
    parser_data = update_or_get_parser_data(get=True)
    url = get_config()['URLS'][f'{key}_xml']
    try:
        if key == 'erai_raws':
            resolution = parser_data['resolutions'][key.replace('_', '-')]
            res = RESOLUTIONS_DICT[resolution]
            url = url.replace('?res=720p', f'?res={res}')
        elif key == 'subsplease':
            resolution = parser_data['resolutions'][key]
            res = RESOLUTIONS_DICT[resolution]
            url = url.replace('?r=720', f'?r={res.replace("p", "").lower()}')
    except KeyError:
        res = '720p'
    response = requests.get(url)
    doc = xml.parseString(response.text)
    title_tags = doc.getElementsByTagName('title')
    link_tags = doc.getElementsByTagName('link')
    date_tags = doc.getElementsByTagName('pubDate')
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
    torrents = []
    count = 0
    for i in range(len(link_tags)):
        title = title_tags[i].firstChild.nodeValue.split(tag_1)[-1]
        title = title.split(tag_2)[0]
        if author not in title.lower():
            date = date_tags[count].firstChild.nodeValue
            date = date.replace(' +0000', '')
            date = dt.strptime(date, "%a, %d %b %Y %H:%M:%S")
            now = dt.now().strftime("%Y-%m-%d %H:%M:%S")
            now = dt.strptime(now, "%Y-%m-%d %H:%M:%S")
            if not now - date > timedelta(days=TIMEDELTA):
                link = link_tags[i].firstChild.nodeValue
                torrent = Torrent(title, link)
                torrents.append(torrent)
            count += 1
    torrents = [i for i in torrents if i.name not in parser_data[author]]
    for torrent in torrents:
        for title in parser_data['titles']:
            if title in torrent.name:
                for relation in parser_data['relations']:
                    if relation.split('->')[-1] == name:
                        if relation.split('->')[0] == title:
                            torrent.get_number(title)
                            torrent.update_db(author)
                            get_magnet(
                                torrent.link, torrent.name,
                                title, torrent.number
                            )


def parse_nyaapantsu_xml(key: str):
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
                                )
                                get_magnet(
                                    torrents[torrent],
                                    torrent,
                                    title,
                                    number,
                                )


if __name__ == '__main__':
    pass
