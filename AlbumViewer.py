# -*- coding: utf-8 -*-
# Last update: Oct 27, 2025 (Refactored for clarity)
#
# A simple image viewer for files, folders, and zip archives.
# Supports fit-to-window, pan-and-scan, and 2-page view modes.
# Note: May have issues running from some IDEs like PyCharm;
# recommended to run from a standard terminal.

import os
import sys
import zipfile
from io import BytesIO
from PIL import Image, ImageTk

import tkinter as tk
import tkinter.filedialog as tkFD
from tkinter import messagebox as mbox


class App(tk.Tk):
    # Class constant for supported image types
    IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Image Viewer")
        self.is_initialized = False

        # --- Initialize State Variables ---
        self.current_image_index = 0
        self.filename = ""
        self.file_mode = ""  # e.g., 'File', 'Folder', 'Zipped'
        self.foldername = ""
        self.is_fullscreen = False
        self.show_info = True
        self.fit_to_window = True
        self.view_mode = 0  # 0: one view, 1: two (odd left), 2: two (even left)

        self.image_list = []
        self.zip_file = None  # ZipFile object
        self.resize_job = None
        self.photo_references = []  # Prevents image garbage collection

        # --- Setup UI ---
        self.setup_widgets()
        self.setup_canvas()
        self.setup_hotkeys()

        # --- Load Initial Help Image ---
        self.file_mode = 'File'
        self.foldername = os.getcwd()
        if "HotKeys.png" in os.listdir(self.foldername):
            self.image_list.append("HotKeys.png")

        # Set this flag last.
        # The <Configure> event on the canvas will trigger the first on_resize,
        # which will then safely call show_image() for the first time.
        self.is_initialized = True

    def quit_app(self, event=None):
        """Exits the application."""
        self.quit()

    def setup_widgets(self):
        """Creates the top button bar."""
        self.btnframe = tk.Frame(self)
        self.btnframe.pack(side="top", fill="x", pady=5)

        tk.Button(self.btnframe, text="QUIT", command=self.quit_app, fg="red").pack(side="left", padx=5)
        tk.Button(self.btnframe, text="Load Zip", command=self.load_zip).pack(side="left", padx=5)
        tk.Button(self.btnframe, text="Load Folder", command=self.load_folder).pack(side="left", padx=5)
        tk.Button(self.btnframe, text="Load File", command=self.load_file).pack(side="left", padx=5)
        tk.Button(self.btnframe, text="Previous", command=self.previous_image).pack(side="left", padx=5)
        tk.Button(self.btnframe, text="Next", command=self.next_image).pack(side="left", padx=5)

    def setup_canvas(self):
        """Creates and binds the main image canvas."""
        self.canvas = tk.Canvas(self, bg="gray")
        self.canvas.pack(side="top", fill="both", expand=True)
        # Bind mouse events for panning
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan_image)
        # Bind window resize event
        self.canvas.bind("<Configure>", self.on_resize)

    def setup_hotkeys(self):
        """Binds all keyboard hotkeys."""
        # Image Navigation
        self.bind('<a>', self.previous_image)
        self.bind('<d>', self.next_image)

        # Smart arrow key navigation (pan or change image)
        self.bind('<Left>', lambda e: self.previous_image() if self.fit_to_window else self.pan_with_arrows(e))
        self.bind('<Right>', lambda e: self.next_image() if self.fit_to_window else self.pan_with_arrows(e))
        self.bind('<Up>', self.pan_with_arrows)
        self.bind('<Down>', self.pan_with_arrows)

        # App Controls
        self.bind('<f>', self.toggle_fullscreen)
        self.bind('<Escape>', self.quit_app)
        self.bind('<q>', self.quit_app)
        self.bind('<r>', self.load_folder)
        self.bind('<o>', self.load_file)
        self.bind('<z>', self.load_zip)
        self.bind('<t>', self.toggle_mode)
        self.bind('<p>', self.toggle_fit)  # Hotkey for pan/zoom
        self.bind('<BackSpace>', self.delete_file)
        self.bind('<i>', self.toggle_information)

    # --- Event Handlers & Toggles ---

    def on_resize(self, event=None):
        """
        Handles the window resize event by scheduling show_image()
        after a short delay (debounce).
        """
        if not self.is_initialized:
            return

        # Filter out tiny, invalid resize events during initialization
        if event and (event.width < 10 or event.height < 10):
            return

        if self.resize_job:
            self.after_cancel(self.resize_job)
        self.resize_job = self.after(100, self.show_image)

    def start_pan(self, event):
        """Records the starting point for a mouse pan."""
        if not self.fit_to_window:
            self.canvas.scan_mark(event.x, event.y)

    def pan_image(self, event):
        """Moves the canvas based on mouse motion."""
        if not self.fit_to_window:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

    def pan_with_arrows(self, event):
        """Scrolls the canvas using arrow keys in pan mode."""
        if not self.fit_to_window:
            if event.keysym == 'Up':
                self.canvas.yview_scroll(-1, "units")
            elif event.keysym == 'Down':
                self.canvas.yview_scroll(1, "units")
            elif event.keysym == 'Left':
                self.canvas.xview_scroll(-1, "units")
            elif event.keysym == 'Right':
                self.canvas.xview_scroll(1, "units")
            return "break"  # Prevents event from propagating

    def toggle_fit(self, event=None):
        """Toggles between 'Fit to Window' and 'Original Size' (pan) modes."""
        self.fit_to_window = not self.fit_to_window
        self.canvas.config(cursor="arrow" if self.fit_to_window else "fleur")
        self.show_image()

    def toggle_information(self, event=None):
        """Toggles the on-screen image information."""
        self.show_info = not self.show_info
        self.show_image()

    def delete_file(self, event=None):
        """Permanently deletes the currently viewed file (from disk)."""
        if not self.image_list:
            return
        if self.file_mode == 'Zipped':
            mbox.showerror("Error", "Cannot delete files from a zip archive.")
            return

        filename = self.image_list[self.current_image_index]
        if mbox.askokcancel(title="Delete", message=f"Permanently delete {filename}?", icon="warning"):
            try:
                filepath = os.path.join(self.foldername, filename)
                os.remove(filepath)
                self.image_list.pop(self.current_image_index)
                if self.current_image_index >= len(self.image_list):
                    self.current_image_index = len(self.image_list) - 1

                if not self.image_list:
                    self.canvas.delete("all")
                    self.title("Image Viewer")
                else:
                    self.show_image()
            except Exception as e:
                mbox.showerror("Error", f"Could not delete file: {e}")

    def toggle_mode(self, event=None):
        """Cycles between 1-page, 2-page (odd left), 2-page (even left)."""
        self.view_mode = (self.view_mode + 1) % 3
        self.show_image()

    def toggle_fullscreen(self, event=None):
        """Toggles fullscreen mode."""
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)
        if not self.is_fullscreen:
            # Show buttons again when exiting fullscreen
            self.btnframe.pack(side="top", fill="x", pady=5)
        else:
            self.btnframe.pack_forget()

    # --- File Loading ---

    def load_zip(self, event=None):
        """Opens a zip archive and loads all supported image files."""
        filepath = tkFD.askopenfilename(filetypes=[("Zip Archives", "*.zip")])
        if not filepath: return
        if not zipfile.is_zipfile(filepath):
            mbox.showerror("Error", "Selected file is not a valid zip archive.")
            return

        self.file_mode = 'Zipped'
        self.zip_file = zipfile.ZipFile(filepath, "r")
        all_files = self.zip_file.namelist()
        self.image_list = [f for f in all_files if self.check_ext(f)]
        self.image_list.sort()

        if self.image_list:
            self.current_image_index = 0
            self.show_image()
        else:
            mbox.showinfo("No Images", "No supported image files found in the zip archive.")

    def load_folder(self, event=None):
        """Opens a folder and loads all supported image files."""
        folder = tkFD.askdirectory()
        if not folder: return

        self.foldername = folder
        self.process_folder()
        self.file_mode = 'Folder'

        if self.image_list:
            self.current_image_index = 0
            self.show_image()
        else:
            mbox.showinfo("No Images", "No supported image files found in the selected folder.")

    def process_folder(self):
        """Helper function to scan a folder for images."""
        all_files = os.listdir(self.foldername)
        self.image_list = [f for f in all_files if self.check_ext(f)]
        self.image_list.sort()

    def load_file(self, event=None):
        """Opens a single file, but also loads all other images in its folder."""
        filetypes = [("Image Files", "*.jpg *.jpeg *.png *.gif *.webp"), ("All Files", "*.*")]
        filepath = tkFD.askopenfilename(filetypes=filetypes)
        if not filepath: return

        self.file_mode = 'File'
        self.foldername, self.filename = os.path.split(filepath)
        self.process_folder()

        if self.filename in self.image_list:
            self.current_image_index = self.image_list.index(self.filename)
            self.show_image()

    # --- Image Display Logic ---

    def show_image(self):
        """
        The main drawing function.
        Clears the canvas and redraws the current image(s).
        """
        if self.resize_job:
            self.after_cancel(self.resize_job)
            self.resize_job = None

        self.update_idletasks()
        self.canvas.delete("all")
        self.photo_references.clear()  # Clear old image references

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        # --- State 1: No Images Loaded ---
        if not self.image_list:
            self.title("Image Viewer")
            self.canvas.create_text(
                canvas_w / 2, canvas_h / 2, anchor=tk.CENTER,
                text=f"Welcome! (Canvas: {canvas_w}x{canvas_h})\nLoad a file, folder, or zip to begin.",
                font=("Arial", 14), fill="white"
            )
            return

        # --- State 2: Bad Index (e.g., after deleting last file) ---
        if self.current_image_index >= len(self.image_list):
            self.title(f"Image Viewer - Bad Index")
            self.canvas.create_text(
                canvas_w / 2, canvas_h / 2, anchor=tk.CENTER,
                text=f"Error: Image index {self.current_image_index} is out of bounds.",
                font=("Arial", 14), fill="red"
            )
            return

        # --- State 3: Load and Display Image(s) ---
        current_filename = self.image_list[self.current_image_index]
        self.title(f"Loading: {current_filename} [Canvas: {canvas_w}x{canvas_h}]")

        try:
            img = self.get_image_data(self.current_image_index)
            if not img:
                raise ValueError("Could not load image data.")

            img2 = None
            if self.view_mode != 0:
                index2 = -1
                if self.view_mode == 1 and self.current_image_index > 0:
                    index2 = self.current_image_index - 1
                elif self.view_mode == 2 and self.current_image_index < len(self.image_list) - 1:
                    index2 = self.current_image_index + 1

                if index2 != -1:
                    img2 = self.get_image_data(index2)

            # --- Call display helpers ---
            if self.fit_to_window:
                self.display_fit(img, img2, canvas_w, canvas_h)
            else:
                self.display_original(img, img2, canvas_w, canvas_h)

            if self.show_info:
                self.draw_information(img)
            else:
                self.title(f"[{self.current_image_index + 1}/{len(self.image_list)}] - {current_filename}")

        except Exception as e:
            # General error handling
            self.title(f"ERROR loading: {self.image_list[self.current_image_index]}")
            self.canvas.create_text(
                canvas_w / 2, canvas_h / 2, anchor=tk.CENTER,
                text=f"Error loading image:\n{self.image_list[self.current_image_index]}\n\n{e}",
                fill="red", font=("Arial", 12)
            )

    def display_fit(self, img, img2, canvas_w, canvas_h):
        """Displays image(s) resized to fit the canvas."""
        if self.view_mode == 0:
            photo = self.ratio_resize(img, canvas_w, canvas_h)
            if photo:
                self.canvas.create_image(canvas_w / 2, canvas_h / 2, image=photo)
                self.photo_references.append(photo)
        else:
            photo1 = self.ratio_resize(img, canvas_w / 2, canvas_h)
            if img2:
                photo2 = self.ratio_resize(img2, canvas_w / 2, canvas_h)
                if self.view_mode == 1:
                    self.canvas.create_image(0, 0, image=photo2, anchor=tk.NW)
                    self.canvas.create_image(canvas_w / 2, 0, image=photo1, anchor=tk.NW)
                else:
                    self.canvas.create_image(0, 0, image=photo1, anchor=tk.NW)
                    self.canvas.create_image(canvas_w / 2, 0, image=photo2, anchor=tk.NW)
                self.photo_references.extend([photo1, photo2])
            elif photo1:
                self.canvas.create_image(canvas_w / 2, canvas_h / 2, image=photo1)
                self.photo_references.append(photo1)

    def display_original(self, img, img2, canvas_w, canvas_h):
        """Displays image(s) at original size and enables panning."""
        photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, image=photo, anchor=tk.NW)
        self.photo_references.append(photo)

        if img2 and self.view_mode != 0:
            photo2 = ImageTk.PhotoImage(img2)
            w1, h1 = img.size
            if self.view_mode == 1:  # Odd left (img2, img)
                self.canvas.create_image(img2.size[0], 0, image=photo, anchor=tk.NW)
                self.canvas.create_image(0, 0, image=photo2, anchor=tk.NW)
            else:  # Even left (img, img2)
                self.canvas.create_image(w1, 0, image=photo2, anchor=tk.NW)
            self.photo_references.append(photo2)

        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    # --- Utility Functions ---

    def get_image_data(self, index):
        """Loads a single PIL.Image object from either a zip or file path."""
        try:
            if self.file_mode == 'Zipped':
                imagedata = self.zip_file.read(self.image_list[index])
                return Image.open(BytesIO(imagedata))
            else:
                filepath = os.path.join(self.foldername, self.image_list[index])
                return Image.open(filepath)
        except Exception as e:
            print(f"Error in get_image_data for {self.image_list[index]}: {e}")
            return None

    def draw_information(self, img):
        """Draws the info text (size, filename) on the canvas."""
        info_text = f"{img.size[0]}x{img.size[1]}  |  {self.image_list[self.current_image_index]}"

        # Create a text element first to get its bounding box
        text_id = self.canvas.create_text(10, 10, anchor="nw",
                                          font=("Arial", 12), fill="white", text=info_text)
        bbox = self.canvas.bbox(text_id)

        # Create a filled rectangle *behind* the text
        self.canvas.create_rectangle(bbox, fill="black", outline="black")

        # Raise the text to the top
        self.canvas.tag_raise(text_id)

        # Set the main window title
        self.title(f"[{self.current_image_index + 1}/{len(self.image_list)}] - Image Viewer")

    def ratio_resize(self, img, max_w, max_h):
        """Resizes a PIL.Image to fit max_w/max_h, returns a PhotoImage."""
        w, h = img.size
        if w == 0 or h == 0: return None

        # Robustness: Prevent division by zero or resizing to zero
        if max_w <= 0 or max_h <= 0:
            max_w, max_h = 1, 1

        ratio = min(max_w / w, max_h / h)
        new_size = (int(w * ratio), int(h * ratio))

        # Robustness: Ensure new size is at least 1x1
        if new_size[0] == 0 or new_size[1] == 0:
            new_size = (1, 1)

        try:
            img_resized = img.resize(new_size, Image.LANCZOS)
            return ImageTk.PhotoImage(img_resized)
        except ValueError as e:
            print(f"Error resizing image to {new_size}: {e}")
            return None

    def previous_image(self, event=None):
        """Goes to the previous image."""
        if not self.image_list: return
        step = 2 if self.view_mode != 0 else 1
        self.current_image_index = max(0, self.current_image_index - step)
        self.show_image()

    def next_image(self, event=None):
        """Goes to the next image."""
        if not self.image_list: return
        step = 2 if self.view_mode != 0 else 1
        self.current_image_index = min(len(self.image_list) - 1, self.current_image_index + step)
        self.show_image()

    def check_ext(self, filename):
        """Checks if a filename has a supported image extension."""
        return any(filename.lower().endswith(ext) for ext in App.IMAGE_EXTENSIONS)


if __name__ == "__main__":
    app = App()
    app.mainloop()
    
