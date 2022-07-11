from PIL import ImageFont
from PIL.ImageDraw import ImageDraw


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

    def draw(self, draw_on: ImageDraw) -> ImageDraw:
        bound_box = (self.x - 15, self.y - 15, self.x + 15, self.y + 15)
        draw_on.ellipse(bound_box, fill='white', outline='red', width=2)
        text = str(self.number)
        ascent, descent = self.font.getmetrics()
        w = self.font.getmask(text).getbbox()[2]
        h = self.font.getmask(text).getbbox()[3] + descent
        # TODO Fix circle centering
        draw_on.text(
            (self.x - (w - 4), self.y - (h - 4)), text,
            fill='black', font=self.font, anchor=None, spacing=0, align='center', stroke_width=1)
        return draw_on
