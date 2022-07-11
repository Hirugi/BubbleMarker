from PIL import ImageFont
from PIL.ImageDraw import ImageDraw

from config import config


class ImageMark:

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def draw(self, draw_on: ImageDraw) -> ImageDraw:
        raise NotImplementedError


class CircledNumberMark(ImageMark):

    def __init__(self, x: int, y: int, number: int):
        super().__init__(x, y)

        self.number = number
        self.font = ImageFont.truetype("Keyboard.ttf", 16)
        self.r = config.mark_circle_radius

    def draw(self, draw_on: ImageDraw) -> ImageDraw:
        bound_box = (
            self.x - self.r,
            self.y - self.r,
            self.x + self.r,
            self.y + self.r
        )
        draw_on.ellipse(bound_box, fill='white', outline='red', width=2)
        text = str(self.number)
        ascent, descent = self.font.getmetrics()
        w = self.font.getmask(text).getbbox()[2]
        h = self.font.getmask(text).getbbox()[3] + descent
        draw_on.text(
            (self.x - (w/2), self.y - (h/2) - 1), text,
            fill='black', font=self.font)
        return draw_on
