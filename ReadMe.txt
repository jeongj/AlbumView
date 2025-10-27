======================
 Python Image Viewer
======================

A simple, fast, and feature-rich image viewer built with Python, Tkinter, and Pillow. 
It's designed to be a lightweight tool for browsing images from folders or zip archives, 
with full support for keyboard navigation.

---
Features
---
* Multiple Load Modes: Open a single file, an entire folder, or a .zip archive.
* Fit & Pan: Toggle between "Fit to Window" (default) and "Original Size" for pan-and-scan.
* Panning Controls: In pan mode, click-and-drag with the mouse or use all four arrow keys.
* 2-Page View: Cycle between single-page, 2-page (odd-left), and 2-page (even-left) for reading comics or manga.
* File Deletion: Permanently delete the currently viewed image from your disk (with confirmation).
* Toggles: Switch to fullscreen or hide/show image information (resolution, filename).
* Supported Formats: .jpg, .jpeg, .png, .gif, .webp.

---
How to Run
---

1. Requirements
   * Python 3
   * Pillow (the Python Imaging Library)

   You can install Pillow using pip:
   pip install Pillow


2. Running the App

   You can run the script directly from your terminal:
   python3 image_viewer.py

   (Use `python` or `python3` depending on your system setup)

   > Important Note
   > This application may not run correctly when launched from within some IDEs like PyCharm. 
   > It is highly recommended to run it from a standard system terminal 
   > (Command Prompt, PowerShell, or macOS Terminal) for proper event handling and resizing.

---
Controls & Hotkeys
---

   Key               Action
   ----------------- --------------------------------
   A / Left Arrow    Previous Image (or Pan Left)
   D / Right Arrow   Next Image (or Pan Right)
   Up Arrow          Pan Up (in Pan Mode)
   Down Arrow        Pan Down (in Pan Mode)
   
   O                 Open a single File
   R                 Open a Folder
   Z                 Open a Zip archive
   
   P                 Toggle Pan Mode (Fit vs. Original Size)
   T                 Toggle View Mode (1-page / 2-page)
   I                 Toggle on-screen Information
   F                 Toggle Fullscreen
   
   Backspace         Delete the current file
   Q / Escape        Quit the application
