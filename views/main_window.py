import tkinter as tk
from functools import partial
from tkinter import ttk

from config import config
from controllers import ImageMarkingFileManager, ImageMarkingController
from views.widgets import ZoomCanvas


class MainWindow(tk.Tk):

    def __init__(self, *args, **kwargs):
        super().__init__('MainWindow', *args, **kwargs)

        self.file_manager = ImageMarkingFileManager()

        self.title(config.app_title)
        self.minsize(config.window_min_size_x, config.window_min_size_y)

        self.style = ttk.Style()

        # Menu frames / blocks
        self.menu_block = ttk.Frame(
            self, width=config.menu_block_width)
        self.menu_block_upper = ttk.Frame(
            self.menu_block, width=config.menu_block_width, height=config.menu_block_upper_height)
        self.menu_block_lower = ttk.Frame(
            self.menu_block, width=config.menu_block_width)

        # Buttons
        ttk.Button(
            self.menu_block_upper, text='Select input folder',
            command=self.select_folder
        ).grid(row=0, column=0, sticky='news', pady=10, padx=10)
        ttk.Button(
            self.menu_block_upper, text='Select output folder',
            command=self.file_manager.select_output_folder
        ).grid(row=1, column=0, sticky='news', pady=10, padx=10)
        ttk.Button(
            self.menu_block_lower, text='Save and go next',
            command=partial(self.next_file, save_current=True, index_modifier=1)
        ).grid(
            row=3, column=0, sticky='news', pady=10, padx=10)
        ttk.Button(
            self.menu_block_lower, text='Save',
            command=partial(self.next_file, save_current=True, index_modifier=0)
        ).grid(
            row=4, column=0, sticky='news', pady=10, padx=10)
        ttk.Button(
            self.menu_block_lower, text='Go next',
            command=partial(self.next_file, save_current=False, index_modifier=1)
        ).grid(
            row=5, column=0, sticky='news', pady=10, padx=10)
        ttk.Button(
            self.menu_block_lower, text='Go back',
            command=partial(self.next_file, save_current=False, index_modifier=-1)
        ).grid(
            row=6, column=0, sticky='news', pady=10, padx=10)
        ttk.Button(
            self.menu_block_lower, text='Remove last mark',
            command=partial(self.remove_mark, clear_all=False)
        ).grid(
            row=7, column=0, sticky='news', pady=10, padx=10)
        ttk.Button(
            self.menu_block_lower, text='Remove all marks',
            command=partial(self.remove_mark, clear_all=True)
        ).grid(
            row=8, column=0, sticky='news', pady=10, padx=10)

        self.image_frame = tk.Frame(self)

        self.canvas_block = ZoomCanvas(self.image_frame)
        self.canvas_block.grid(row=0, column=0, sticky='nswe')
        self.canvas_block.update()  # wait till canvas is created

        # Bind key actions
        self.canvas_block.bind('<Configure>', lambda event: self.canvas_block.show_image())  # canvas is resized

        self.canvas_block.bind('<MouseWheel>', self.canvas_block.wheel)  # zoom for Windows and macOS, but not Linux
        self.canvas_block.bind('<Button-5>', self.canvas_block.wheel)  # zoom for Linux, wheel scroll down
        self.canvas_block.bind('<Button-4>', self.canvas_block.wheel)  # zoom for Linux, wheel scroll up

        self.canvas_block.bind('<ButtonPress-1>', self.canvas_block.move_from)  # remember canvas position
        self.canvas_block.bind('<B1-Motion>', self.canvas_block.move_to)  # move canvas to the new position

        self.canvas_block.bind('<Double-Button-1>', self.place_mark)  # place a mark under the cursor
        self.bind('<BackSpace>', lambda event: self.remove_mark(clear_all=False))
        self.bind('<Shift-BackSpace>', lambda event: self.remove_mark(clear_all=True))

        # status bar
        self.status_frame = tk.Frame(self)
        self.status = ttk.Label(self.status_frame, text="0 / 0")
        self.status_second = ttk.Label(self.status_frame, text='© by Hirugi, 2021')

        # Pack everything
        self.menu_block_upper.pack(side="top", fill="both", expand=True)
        self.menu_block_lower.pack(side="top", fill="both", expand=True)
        self.menu_block.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.image_frame.grid(row=1, column=1, sticky="nsew")
        self.image_frame.grid_rowconfigure(0, weight=1)
        self.image_frame.grid_columnconfigure(0, weight=1)
        self.status.pack(fill="both", expand=False, side='left', ipadx=10)
        self.status_second.pack(fill="both", expand=True)
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    def update_status(self):
        self.status.configure(text=f'{self.file_manager.selected_file_index + 1} / {len(self.file_manager.files_list)}')

    def select_folder(self):
        self.file_manager.select_input_folder()
        current_file: ImageMarkingController = self.file_manager.get_current_file()
        if current_file:
            self.canvas_block.load_image(current_file.render_image())
            self.update_status()

    def next_file(self, save_current: bool, index_modifier: int):
        new_file: ImageMarkingController = self.file_manager.get_next_file(
            save_current=save_current, index_modifier=index_modifier)
        if new_file:
            self.canvas_block.load_image(new_file.render_image())
            self.update_status()

    def place_mark(self, event):
        if not self.file_manager.files_list:
            return
        x = self.canvas_block.canvasx(event.x)
        y = self.canvas_block.canvasy(event.y)
        current_file: ImageMarkingController = self.file_manager.get_current_file()
        current_file.add_mark(*self.canvas_block.get_image_coords(x, y))
        self.canvas_block.load_image(current_file.render_image(), update_current=True)

    def remove_mark(self, clear_all=False):
        if not self.file_manager.files_list:
            return
        current_file: ImageMarkingController = self.file_manager.get_current_file()
        current_file.remove_mark(clear_all=clear_all)
        self.canvas_block.load_image(current_file.render_image(), update_current=True)
