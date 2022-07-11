import os
from tkinter import filedialog
from typing import Any

import filetype

from config import config
from controllers import ImageMarkingController


class FileManager:

    def __init__(self):
        self.files_list = []
        self.input_folder = None
        self.output_folder = None
        self.selected_file_index = 0

    def select_input_folder(self):
        self.files_list = []
        _input_folder = filedialog.askdirectory()
        if not _input_folder:
            return
        self.input_folder = _input_folder
        folder_items = os.listdir(self.input_folder)
        folder_items.sort()
        for item in folder_items:
            item_path = f'{self.input_folder}/{item}'
            if os.path.isfile(item_path) and self.can_add_file(item_path):
                self.files_list.append(self.prepare_file(item_path))
        self.selected_file_index = 0

    @staticmethod
    def can_add_file(item_path: str) -> bool:
        """ Add filters for the file here to decide whether to add it """
        raise NotImplementedError

    @staticmethod
    def prepare_file(item_path: str) -> Any:
        """ Wrap the file in the desired object before adding it to the list """
        raise NotImplementedError

    def select_output_folder(self):
        _output_folder = filedialog.askdirectory()
        if not _output_folder:
            return
        self.output_folder = _output_folder

    def get_current_file(self):
        return self.files_list[self.selected_file_index] if self.files_list else None

    def save_current_file(self):
        curr_file = self.get_current_file()
        if not curr_file:
            return
        if not self.output_folder:
            save_path = f'{self.input_folder}/output'
            os.makedirs(save_path, exist_ok=True)
        else:
            save_path = f'{self.output_folder}/'

        curr_file.render_image().save(f'{save_path}/{curr_file.image.file_name}')

    def get_next_file(self, save_current: bool = False, index_modifier: int = 1):
        """ Pass 1 to get next file, or -1 to get previous one, and so on """
        if save_current:
            self.save_current_file()
        next_index = self.selected_file_index + index_modifier
        if 0 <= next_index < len(self.files_list):
            self.selected_file_index = next_index
        return self.get_current_file()


class ImageMarkingFileManager(FileManager):
    
    @staticmethod
    def can_add_file(item_path: str) -> bool:
        return filetype.is_image(item_path)

    @staticmethod
    def prepare_file(item_path: str) -> Any:
        return ImageMarkingController(
            image_path=item_path, resize_height=config.resize_image_height, resize_width=config.resize_image_width)
