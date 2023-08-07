import configparser
from const import erai_raws_xml, subsplease_xml, nyaapantsu_xml


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
