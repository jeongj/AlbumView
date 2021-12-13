# Last update Dec,13, 2021 by JJ
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

class App(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        self.SetWigets()
        self.SetCanvas()
        self.SetHotKey() # bind

        self.color = '#000000'
        self.nCurrnetImage = 0
        self.filename = ""
        self.filemod = ""
        self.foldername = ""
        self.bFullScreen, self.bInformation = False, False
        self.lImageExts = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        self.nMode = 0 # 0:one view,1:two view(odd left),2:two view(even left)

        self.lImages = []
        #self.foldername = os.getcwd()
        #print(self.foldername)
        self.lImages.append("HotKeys.png")
        #self.ShowImage()

    def Quit(self,event=None):
        self.root.quit()

    def SetWigets(self):
        self.btnframe = tk.Frame(self.root)
        self.btnframe.pack({"side": "top"})

        self.btnQuit = tk.Button(self.btnframe,text="QUIT",command=self.Quit)
        self.btnQuit["fg"] = "red"
        self.btnQuit.pack({"side": "left"})
        self.btnZip = tk.Button(self.btnframe,text="Load Zip File",command=self.LoadZip)
        self.btnZip.pack({"side": "left"})
        self.btnLoadFolder = tk.Button(self.btnframe,text="Choose a Folder",command=self.LoadFolder)
        self.btnLoadFolder.pack({"side": "left"})
        self.btnLoadFile = tk.Button(self.btnframe,text="Load A File",command=self.LoadFile)
        self.btnLoadFile.pack({"side": "left"})
        self.btnPrev = tk.Button(self.btnframe,text="Previous",command=self.PreviousImage)
        self.btnPrev.pack({"side": "left"})
        self.btnNext = tk.Button(self.btnframe,text="Next",command=self.NextImage)
        self.btnNext.pack({"side": "left"})

    def SetCanvas(self,W=640,H=480):
        self.canvas = tk.Canvas(self.root, width=W, height=H)
        self.canvas.pack(expand=True)
        #self.canvas.create_text()   # for initial help for shortcut

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

    def ToggleInformation(self,event=None):
        self.bInformation = not self.bInformation

    def Delete(self,event=None):

        if self.bFullScreen: # tkinter lose focus after askokcancel when fullscreen
            self.ToggleFullScreen() # full to normal
            WasFullScreen = True
        else :
            WasFullScreen = False

        if mbox.askokcancel(title="Delete", message="Sure?",  icon="warning"):
            os.remove(self.foldername + '/' + self.lImages[self.nCurrnetImage])
            self.lImages.remove(self.lImages[self.nCurrnetImage])
            self.ShowImage()

        #if WasFullScreen:
        #    self.ToggleFullScreen()

    def ToggleMode(self,event=None):
        _,self.nMode=divmod(self.nMode+1,3)

    def LoadZip(self, event=None): # deal with zip file
        self.filename = tkFD.askopenfilename()
        if len(self.filename) < 1: # when cancel chosen from the dialog
            return
        if not zipfile.is_zipfile(self.filename):
            self.canvas.create_text("Loaded file is not a zipfile.")
            return
        self.filemod = 'Zipped'
        self.zf = zipfile.ZipFile(self.filename,"r") # open zipfile
        self.lImages = self.zf.namelist() # get filelist from zipfile
        for filename in self.lImages:
            if self.CheckExt(filename) == False:
                self.lImages.remove(filename)
        self.lImages.sort() # sort the filelist
        self.nCurrnetImage = 0 # number for current image # image indexes
        self.ShowImage() # call show image for first image
        print('%d image(s) found'%len(self.lImages))
        for filename in self.lImages:
            print(filename)

    def LoadFolder(self, event=None): # deal with zip file
        self.foldername = tkFD.askdirectory()
        if self.foldername :
            self.ProcessFolder()
            self.filemod = 'Folder'
            self.nCurrnetImage = 0  # number for current image # image indexes
            self.ShowImage()  # call show image for first image

    def ProcessFolder(self): # list a directory, remove non-readables then sort
        self.lImages = os.listdir(self.foldername)
        for filename in self.lImages:
            if self.CheckExt(filename) == False:
                self.lImages.remove(filename)
        self.lImages.sort()  # sort the filelist

    def LoadFile(self): # just load an image file with PIL and Tkinter
        filename = tkFD.askopenfilename()
        if len(filename) < 1: # when cancel chosen from the dialog
            return
        if self.CheckExt(filename) == False:
            print('%s:Not a supported file'%filename)
            return
        self.filemod = 'File'
        self.foldername = os.path.split(filename)[0]
        self.filename = os.path.split(filename)[1]
        self.ProcessFolder()
        self.nCurrnetImage = self.lImages.index(self.filename)
        self.ShowImage()

    def ShowImage(self):
        w, h = self.root.winfo_width(),self.root.winfo_height()
        wc,hc = self.canvas.winfo_width(),self.canvas.winfo_height()
        self.canvas.delete("all") # clear canvas
        if self.bFullScreen == True:
            self.canvas.config(width=w-6,height=h-6)
        else :
            self.canvas.config(width=w-6,height=h-28) # if not smaller it frame expands on next image
        #self.canvas.create_rectangle(3,3,w-4,h-28) # for measuring canvas size

        if self.filemod == 'Zipped':
            imagedata = self.zf.read(self.lImages[self.nCurrnetImage])
            obj = BytesIO(imagedata) # image data convert to BytesIO
            img = Image.open(obj)  # open pil image
            if self.nMode != 0:
                if self.nMode == 1:
                    tFilename = self.lImages[self.nCurrnetImage-1]
                else:# self.nMode == 2:
                    tFilename = self.lImages[self.nCurrnetImage+1]
                imagedata2 = self.zf.read(tFilename)
                obj2 = BytesIO(imagedata2)
                img2 = Image.open(obj2)

        else:# self.filemod == 'Folder' or 'File':
            fullpathfilename = self.foldername + '/' if len(self.foldername) > 0 else ""
            fullpathfilename += self.lImages[self.nCurrnetImage]
            try:
                fullpathfilename = self.foldername + '/' if len(self.foldername)>0 else ""
                fullpathfilename += self.lImages[self.nCurrnetImage]
                print(fullpathfilename)
                img = Image.open(fullpathfilename)
            except:
                self.lImages.remove(self.lImages[self.nCurrnetImage])
                return
            if self.nMode != 0:
                if self.nMode == 1:
                    img2 = Image.open(self.foldername + '/' + self.lImages[self.nCurrnetImage-1])
                elif self.nMode == 2:
                    img2 = Image.open(self.foldername + '/' + self.lImages[self.nCurrnetImage+1])

        if self.nMode == 0 : # one view mode
            self.photo = self.RatioResize(img,wc,hc)
            self.canvas.create_image(w/2, h/2, image=self.photo, anchor=tk.CENTER)
        else :
            self.photo = self.RatioResize(img,wc/2,hc)
            self.photo2 = self.RatioResize(img2,wc/2,hc)
            if self.nMode == 1 : # two view mode, img2 on left
                self.canvas.create_image(wc/2,0,image=self.photo, anchor=tk.NW)
                self.canvas.create_image(0,0,image=self.photo2, anchor=tk.NW)
            else : # two view mode, img2 on right
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.canvas.create_image(wc / 2, 0, image=self.photo2, anchor=tk.NW)
        if self.bInformation:
            self.canvas.create_text(5, 5, anchor="nw", font=("Purisa", 12), text="%dx%d" % (img.size[0], img.size[1]))
            self.canvas.create_text(5, 15, anchor="nw", font=("Purisa", 12), text=self.lImages[self.nCurrnetImage])
            self.root.title("[%d/%d]"%(self.nCurrnetImage,len(self.lImages)))

    def RatioResize(self,img,wc,hc):
        ratiow, ratioh = float(wc) / img.size[0], float(hc) / img.size[1]
        ratio = ratioh if ratiow > ratioh else ratiow
        img_resized = img.resize((int(img.size[0] * ratio), int(img.size[1] * ratio)), Image.ANTIALIAS)
        return ImageTk.PhotoImage(img_resized)

    def PreviousImage(self, event=None):
        if self.filemod == "Zipped" and self.filename == "":
            return
        elif self.filemod == "" :
            return
        self.nCurrnetImage= self.nCurrnetImage-1 if self.nMode==0 else self.nCurrnetImage-2
        if self.nCurrnetImage < 0:  # bounded at first image
            self.nCurrnetImage = 0
        self.ShowImage()

    def NextImage(self, event=None):
        if self.filemod == "Zipped" and self.filename == "":
            return
        elif self.filemod == "" :
            return
        self.nCurrnetImage= self.nCurrnetImage+1 if self.nMode==0 else self.nCurrnetImage+2
        if self.nCurrnetImage >= len(self.lImages):  # bounded at last image
            self.nCurrnetImage = len(self.lImages)-1    # list ends with len-1
        self.ShowImage()

    def ToggleFullScreen(self, event=None):
        if self.bFullScreen : # full to normal
            self.canvas.pack_forget()
            self.btnframe.pack()
            self.canvas.pack()
        else: # normal to full
            self.btnframe.pack_forget()  # hide button frame
            # self.root.state('zoomed') # Windows and Mac only, Not X11
            self.root.overrideredirect(True) # for mac, cover the dock area
            self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
            #self.root.wm_attributes("-zoomed", False) # once effected, top menu bar stays
            self.root.update_idletasks()
        self.bFullScreen = not self.bFullScreen
        self.root.wm_attributes("-fullscreen", self.bFullScreen)
        self.ShowImage()

    def CheckExt(self,filename):
        for ext in self.lImageExts:
            if filename.lower().endswith(ext):
                return True
        return False

app = App()
app.root.mainloop()