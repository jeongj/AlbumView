
README
Last Update Nov23 2021

AlbumView by JJ

This python program is for opening a group of zipped image files, an image folder.
The function with 2 images in one view is also supported.
Gif animation and stopper will be added on the next version.
  

1. Required modules are as follows

	import sys
	import os
	import screeninfo
	from PIL import Image, ImageTk # Pillow module
	import zipfile
	if sys.version_info[0] == 2: # not tested yet
	    import Tkinter as tk  # Tkinter -> tkinter in Python3, Tkinter in python2
	    from BytesIO import BytesIO  # import StringIO #Python2
	    import tkFileDialog as tkFD
	else:
	    import tkinter as tk # Tkinter -> tkinter in Python3, Tkinter in python2
	    from io import BytesIO
	    import tkinter.filedialog as tkFD
	    from tkinter import messagebox as mbox


2. Supported image formats are as follows

	self.lImageExts = ['.jpg', '.jpeg', '.png', '.gif', '.webp']


3. Hot Keys are as follows

	def SetHotKey(self):
		self.root.bind('<a>', self.PreviousImage)
		self.root.bind('<d>', self.NextImage)
		self.root.bind('<f>', self.ToggleFullScreen)
		self.root.bind('<e>', self.LoadFile)
		self.root.bind('<q>', self.Quit)
		self.root.bind('<r>', self.LoadFolder)
		self.root.bind('<o>', self.LoadFile)
		self.root.bind('<z>', self.LoadZip)
		self.root.bind('<t>', self.ToggleMode)
		self.root.bind('<BackSpace>', self.Delete)
		self.root.bind('<i>', self.ToggleInformation)
