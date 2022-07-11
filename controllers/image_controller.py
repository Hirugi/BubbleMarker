from PIL import ImageTk
from PIL import Image
from PIL.ImageDraw import ImageDraw

from models import MarkedImage, CircledNumberMark


class ImageMarkingController:

    def __init__(self, image_path: str, resize_height: int = None, resize_width: int = None):
        self.image = MarkedImage(image_path, resize_height, resize_width)

    def add_mark(self, x: int, y: int):
        mark_number = self.image.mark_count + 1
        mark = CircledNumberMark(x, y, mark_number)
        if self.image.is_on_image(x, y):
            self.image.add_mark(mark)

    def remove_mark(self, clear_all: bool = False):
        if self.image.mark_count <= 0:
            return
        if clear_all:
            self.image.clear_marks()
        else:
            self.image.remove_last_mark()

    def render_image(self) -> Image:
        self.image.open()
        temp_image = self.image.image_instance.copy()
        draw_on = ImageDraw(temp_image)
        for mark in self.image.mark_list:
            mark.draw(draw_on)
        return temp_image

    def render_tk_image(self) -> ImageTk.PhotoImage:
        return ImageTk.PhotoImage(self.render_image())
