import os
from typing import Optional, List

from PIL import Image
from PIL.Image import Resampling

from models import ImageMark


class MarkNotOnImageException(Exception):
    pass


class MarkedImage:

    def __init__(self, file_path: str, resize_height: int = None, resize_width: int = None):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.resize_height = resize_height
        self.resize_width = resize_width
        self.mark_list: List[Optional[ImageMark]] = []
        self.image_instance: Optional[Image] = None
        self.open()
        self.size = self.image_instance.size
        self.close()

    def is_on_image(self, x: int, y: int) -> bool:
        return (0 <= x <= self.size[0]) and (0 <= y <= self.size[1])

    def add_mark(self, mark: 'ImageMark'):
        if not self.is_on_image(mark.x, mark.y):
            raise MarkNotOnImageException(f'Mark coords is {mark.x, mark.y}, however image size is {self.size}')
        self.mark_list.append(mark)

    def remove_mark(self, position: int):
        if self.mark_list and (self.mark_count > position >= 0):
            self.mark_list.pop(position)

    def remove_last_mark(self):
        if self.mark_count > 0:
            return self.remove_mark(self.mark_count - 1)

    def clear_marks(self):
        self.mark_list.clear()

    @property
    def mark_count(self):
        return len(self.mark_list)

    def open(self):
        if not self.image_instance:
            temp_image = Image.open(self.file_path)
            if self.resize_width and self.resize_height:
                width, height = temp_image.size
                if width > height:
                    scaling_factor = self.resize_width / width
                    width = self.resize_width
                    height = int(height * scaling_factor)
                else:
                    scaling_factor = self.resize_height / height
                    height = self.resize_height
                    width = int(width * scaling_factor)
                temp_image = temp_image.resize((width, height), Resampling.LANCZOS)
            self.image_instance = temp_image
        return self.image_instance

    def close(self):
        if self.image_instance:
            self.image_instance.close()
            self.image_instance = None

    def __del__(self):
        self.close()
        del self
