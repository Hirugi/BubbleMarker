import json
import platform
from pathlib import Path
import os


class UnknownPlatformException(Exception):
    pass


class Config(object):

    APP_NAME = 'BubbleMarker'
    SAVE_CONFIG_KEYS = [
        'max_width', 'max_height', 'app_title', 'window_min_size_y', 'window_min_size_x', 'menu_block_width',
        'resize_image_height', 'resize_image_width'
    ]

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):

        match platform.system().lower():
            case 'darwin' | 'linux':
                conf_path = f'{Path.home()}/.{self.APP_NAME}'
            case 'windows':
                conf_path = f'{Path.home()}/AppData/Roaming/{self.APP_NAME}'
            case _:
                raise UnknownPlatformException(f'Unsupported platform: {platform.system()}')

        if not os.path.exists(conf_path):
            os.makedirs(conf_path)

        self.file_path = f'{conf_path}/config.json'

        self.max_width = 1000
        self.max_height = 1000
        self.app_title = 'Bubble Marker'
        self.window_min_size_y = 500
        self.window_min_size_x = 800
        self.menu_block_width = 150
        self.menu_block_upper_height = 150
        self.resize_image_height = 1000
        self.resize_image_width = 1000

    def load_config(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r') as _f:
                data = json.loads(_f.read())
                for k, v in data:
                    setattr(self, k, v)

    def save_config(self):
        with open(self.file_path, 'w+') as _f:
            _f.write(json.dumps(self.get_data_to_save()))

    def get_data_to_save(self):
        return {k: getattr(self, k) for k in self.SAVE_CONFIG_KEYS}


config = Config()
config.load_config()

if __name__ == '__main__':
    Config().load_config()
