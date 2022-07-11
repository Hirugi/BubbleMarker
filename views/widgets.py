import math
import tkinter as tk

from tkinter import ttk
from typing import List, Optional, Tuple

from PIL import Image, ImageTk


class AutoScrollbar(ttk.Scrollbar):
    """ A scrollbar that hides itself if it's not needed. Works only for grid geometry manager """

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
            ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError('Cannot use pack with the widget ' + self.__class__.__name__)

    def place(self, **kw):
        raise tk.TclError('Cannot use place with the widget ' + self.__class__.__name__)


class ZoomCanvas(tk.Canvas):
    """ With help from https://stackoverflow.com/a/48137257 """

    def __init__(self, image_frame: tk.Frame, *args, **kwargs):
        self.image_tk = None
        self.container: int = 0
        self.__pyramid: List = []
        self.__min_side: int = 0
        self.img_height: int = 0
        self.img_width: int = 0
        self.__image: Optional[Image] = None

        self.img_scale = 1.0  # scale for the canvas image zoom, public for outer classes
        self.__delta = 1.3  # zoom magnitude
        self.__filter = Image.LANCZOS

        # Vertical and horizontal scrollbars for canvas
        h_bar = AutoScrollbar(image_frame, orient='horizontal')
        v_bar = AutoScrollbar(image_frame, orient='vertical')
        h_bar.grid(row=1, column=0, sticky='we')
        v_bar.grid(row=0, column=1, sticky='ns')

        super(ZoomCanvas, self).__init__(
            image_frame, *args, highlightthickness=0, xscrollcommand=h_bar.set, yscrollcommand=v_bar.set, **kwargs)

        h_bar.configure(command=self.__scroll_x)  # bind scrollbars to the canvas
        v_bar.configure(command=self.__scroll_y)

        self.__band_width = 1024  # width of the tile band

        # Set ratio coefficient for image pyramid
        self.__ratio = 1.0
        self.__curr_img = 0  # current image from the pyramid
        self.__scale = self.img_scale * self.__ratio  # image pyramid scale
        self.__reduction = 2  # reduction degree of image pyramid

    # noinspection PyUnusedLocal
    def __scroll_x(self, *args, **kwargs):
        """ Scroll canvas horizontally and redraw the image """
        self.xview(*args)  # scroll horizontally
        self.show_image()  # redraw the image

    # noinspection PyUnusedLocal
    def __scroll_y(self, *args, **kwargs):
        """ Scroll canvas vertically and redraw the image """
        self.yview(*args)  # scroll vertically
        self.show_image()  # redraw the image

    def show_image(self):
        if not self.container:
            return
        """ Show image on the Canvas. Implements correct image zoom almost like in Google Maps """
        box_image = self.coords(self.container)  # get image area
        box_canvas = (self.canvasx(0),  # get visible area of the canvas
                      self.canvasy(0),
                      self.canvasx(self.winfo_width()),
                      self.canvasy(self.winfo_height()))
        box_img_int = tuple(map(int, box_image))  # convert to integer or it will not work properly
        # Get scroll region box
        box_scroll = [min(box_img_int[0], box_canvas[0]), min(box_img_int[1], box_canvas[1]),
                      max(box_img_int[2], box_canvas[2]), max(box_img_int[3], box_canvas[3])]
        # Horizontal part of the image is in the visible area
        if box_scroll[0] == box_canvas[0] and box_scroll[2] == box_canvas[2]:
            box_scroll[0] = box_img_int[0]
            box_scroll[2] = box_img_int[2]
        # Vertical part of the image is in the visible area
        if box_scroll[1] == box_canvas[1] and box_scroll[3] == box_canvas[3]:
            box_scroll[1] = box_img_int[1]
            box_scroll[3] = box_img_int[3]
        # Convert scroll region to tuple and to integer
        self.configure(scrollregion=tuple(map(int, box_scroll)))  # set scroll region
        x1 = max(box_canvas[0] - box_image[0], 0)  # get coordinates (x1,y1,x2,y2) of the image tile
        y1 = max(box_canvas[1] - box_image[1], 0)
        x2 = min(box_canvas[2], box_image[2]) - box_image[0]
        y2 = min(box_canvas[3], box_image[3]) - box_image[1]
        if int(x2 - x1) > 0 and int(y2 - y1) > 0:  # show image if it in the visible area
            image = self.__pyramid[max(0, self.__curr_img)].crop(  # crop current img from pyramid
                (int(x1 / self.__scale), int(y1 / self.__scale),
                 int(x2 / self.__scale), int(y2 / self.__scale)))
            image_tk = ImageTk.PhotoImage(image.resize((int(x2 - x1), int(y2 - y1)), self.__filter))
            image_id = self.create_image(
                max(box_canvas[0], box_img_int[0]),
                max(box_canvas[1], box_img_int[1]),
                anchor='nw', image=image_tk)
            self.lower(image_id)  # set image into background
            self.image_tk = image_tk  # keep an extra reference to prevent garbage-collection

    def load_image(self, image: Image, update_current: bool = False):
        self.__image = image
        # Create image pyramid
        self.__pyramid = [self.__image]
        w, h = self.__pyramid[-1].size
        while w > 512 and h > 512:  # top pyramid image is around 512 pixels in size
            w /= self.__reduction  # divide on reduction degree
            h /= self.__reduction  # divide on reduction degree
            self.__pyramid.append(self.__pyramid[-1].resize((int(w), int(h)), self.__filter))
        # Put image into container rectangle and use it to set proper coordinates to the image
        if not update_current:
            self.img_scale = 1.0  # scale for the canvas image zoom, public for outer classes
            self.__curr_img = 0  # current image from the pyramid
            self.__scale = self.img_scale * self.__ratio  # image pyramid scale
            # Create new container for new image
            self.img_width, self.img_height = self.__image.size  # public for outer classes
            self.__min_side = min(self.img_width, self.img_height)  # get the smaller image side
            self.container = self.create_rectangle((0, 0, self.img_width, self.img_height), width=0)
        self.show_image()  # show image on the canvas
        self.focus_set()  # set focus on the canvas

    def is_outside(self, x, y):
        """ Checks if the point (x,y) is outside the image area """
        if not self.container:
            return True
        bbox = self.coords(self.container)  # get image area
        # point (x,y) is inside (False) or outside (True) the image area
        return not (bbox[0] < x < bbox[2] and bbox[1] < y < bbox[3])

    def wheel(self, event):
        """ Zoom with mouse wheel """
        x = self.canvasx(event.x)  # get coordinates of the event on the canvas
        y = self.canvasy(event.y)
        if self.is_outside(x, y):
            return  # zoom only inside image area
        scale = 1.0
        # Respond to Linux (event.num) or Windows / MacOS (event.delta) wheel event
        if event.num == 5 or event.delta == -120 or (event.state == 0 and event.delta == -1):  # scroll down, smaller
            if round(self.__min_side * self.img_scale) < 30:
                return  # image is less than 30 pixels
            self.img_scale /= self.__delta
            scale /= self.__delta
        if event.num == 4 or event.delta == 120 or (event.state == 0 and event.delta == 1):  # scroll up, bigger
            i = min(self.winfo_width(), self.winfo_height()) >> 1
            if i < self.img_scale:
                return  # 1 pixel is bigger than the visible area
            self.img_scale *= self.__delta
            scale *= self.__delta
        # Take appropriate image from the pyramid
        k = self.img_scale * self.__ratio  # temporary coefficient
        self.__curr_img = min((-1) * int(math.log(k, self.__reduction)), len(self.__pyramid) - 1)
        self.__scale = k * math.pow(self.__reduction, max(0, self.__curr_img))

        self.scale('all', x, y, scale, scale)  # rescale all objects
        # Redraw some figures before showing image on the screen
        self.show_image()

    def get_image_coords(self, x: int, y: int) -> Tuple[int, int]:
        bbox = self.coords(self.container)  # get image area
        x1 = round((x - bbox[0]) / self.img_scale)  # get real (x,y) on the image without zoom
        y1 = round((y - bbox[1]) / self.img_scale)
        return x1, y1
    
    def move_from(self, event):
        """ Remember previous coordinates for scrolling with the mouse """
        self.scan_mark(event.x, event.y)

    def move_to(self, event):
        """ Drag (move) canvas to the new position """
        self.scan_dragto(event.x, event.y, gain=1)
        self.show_image()  # zoom tile and show it on the canvas
