import configparser


def status_change(status: bool):
    config = get_config()
    config['USER']['status'] = str(status)
    with open('PANTSUPARSER.ini', 'w', encoding='utf-8') as config_file:
        config.write(config_file)


def get_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read('PANTSUPARSER.ini', encoding='utf-8')
    if 'USER' not in config:
        config['USER'] = {}
    if 'URLS' not in config:
        config['URLS'] = {}
    return config


if __name__ == '__main__':
    pass
