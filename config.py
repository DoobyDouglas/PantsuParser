import configparser


erai_raws_xml = (
    'https://www.erai-raws.info/feed/?res=720p'
    '&type=magnet&0879fd62733b8db8535eb1be24e23f6d'
)
subsplease_xml = 'https://subsplease.org/rss/?r=720'
nyaapantsu_xml = 'https://ouo.si/feed/magnet'


def write_config(key: str, value: str or bool) -> None:
    config = get_config()
    config['USER'][key] = str(value)
    with open('PANTSUPARSER.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read('PANTSUPARSER.ini', encoding='utf-8')
    if 'USER' not in config:
        config['USER'] = {'status': False}
    if 'URLS' not in config:
        config['URLS'] = {
            'erai_raws_xml': erai_raws_xml,
            'subsplease_xml': subsplease_xml,
            'nyaapantsu_xml': nyaapantsu_xml,
        }
    return config


if __name__ == '__main__':
    pass
