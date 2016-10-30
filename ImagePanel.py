import wx
import wx.adv

import ImageDropTarget
import SquareImage

class ImagePanel(wx.Frame):
    def __init__(self, parent=None, title="Image Panel", imageSize=1024):
        super().__init__(parent=parent, title=title, size=(imageSize, imageSize))
        # Create the panel to display the image, and other instance variables
        self.maxImageSize = imageSize
        self.imageView = wx.Panel(self)
        self.image = SquareImage.SquareImage(None)

        # Image dragging-related variables
        self.mouseDown = False
        self.mouseDownCoordinates = None
        self.mouseDownOffset = 0

        # Image drop handling
        self.dropTarget = ImageDropTarget.ImageDropTarget(self)
        self.imageView.SetDropTarget(self.dropTarget)

        # Create a status bar
        self.statusBar = wx.StatusBar(self)
        self.SetStatusBar(self.statusBar)
        self.statusBar.SetStatusText("Right click or drag an image into the window to get started.")

        # Create a sizer, to make sure the imageView is resized to the window
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.imageView, 1, wx.ALL | wx.EXPAND, 0)

        sizer.SetSizeHints(self)
        self.SetSizer(sizer)

        # Create bindings
        self.imageView.Bind(wx.EVT_SIZE, self.resize)
        self.imageView.Bind(wx.EVT_PAINT, self.paint)
        self.imageView.Bind(wx.EVT_RIGHT_UP, self.showContextMenu)

        self.imageView.Bind(wx.EVT_LEFT_DOWN, self.onLeftDown)
        self.imageView.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.imageView.Bind(wx.EVT_MOTION, self.onMotion)
        self.imageView.Bind(wx.EVT_LEAVE_WINDOW, self.onLeaveWindow)

        self.Bind(wx.EVT_MENU, self.showOpenImageDialog, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.saveImage, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.showAboutDialog, id=wx.ID_ABOUT)

        # Accelerator Table for keyboard shortcuts
        acceleratorTable = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord("O"), wx.ID_OPEN),
            (wx.ACCEL_CTRL, ord("S"), wx.ID_SAVE),
            (wx.ACCEL_CTRL, ord("I"), wx.ID_ABOUT)
        ])
        self.SetAcceleratorTable(acceleratorTable)

        # Required for AutoBufferedPaintDC
        self.imageView.SetBackgroundStyle(style=wx.BG_STYLE_PAINT)

    def resize(self, event):
        if self.image:
            self.imageView.Refresh()

    def paint(self, event):
        """ Retrieves the image and paints it on imageView.
            We know that the image is a square, we keep it a square. """
        width, height = self.imageView.Size
        dimension = min(width, height)

        if dimension < self.image.dimension:
            resizeQuality = wx.IMAGE_QUALITY_BICUBIC
        elif dimension < self.image.dimension * 2:
            resizeQuality = wx.IMAGE_QUALITY_BILINEAR
        else:
            resizeQuality = wx.IMAGE_QUALITY_NORMAL

        image = self.image.image().Scale(dimension, dimension, resizeQuality)

        self.imageView.Refresh()

        dc = wx.AutoBufferedPaintDC(self.imageView)
        dc.Clear()
        dc.DrawBitmap(wx.Bitmap(image),
                      (width - dimension) // 2,
                      (height - dimension) // 2)

    def setImage(self, imagePath):
        """ Sets an image, given a path. """
        if imagePath is not None:
            self.image = SquareImage.SquareImage(imagePath)
            self.statusBar.SetStatusText("Opened {}".format(imagePath))
            self.imageView.Refresh()

    def showContextMenu(self, event):
        """ Shows a right click context menu. """
        menu = wx.Menu()
        menu.Append(wx.ID_OPEN, "Open...\tCtrl+O", "Open an image...", )
        menu.Append(wx.ID_SAVE, "Save\tCtrl+S", "Save the cropped image...")
        menu.AppendSeparator()
        menu.Append(wx.ID_ABOUT, "About\tCtrl+I", "About this program...")

        menu.Bind(wx.EVT_MENU, self.showOpenImageDialog, id=wx.ID_OPEN)
        menu.Bind(wx.EVT_MENU, self.saveImage, id=wx.ID_SAVE)
        menu.Bind(wx.EVT_MENU, self.showAboutDialog, id=wx.ID_ABOUT)

        self.PopupMenu(menu, event.GetPosition())
        menu.Destroy()

    def showOpenImageDialog(self, event):
        """ Allows user to pick a file in a dialog, which will then be opened. """
        openImageDialog = wx.FileDialog(self, "Open",
                                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if openImageDialog.ShowModal() == wx.ID_CANCEL:
            return
        self.setImage(openImageDialog.GetPath())


    def saveImage(self, event):
        """ Saves an image to file. """
        fileWritten = self.image.writeFile()
        self.statusBar.SetStatusText("Saved {}".format(fileWritten))

    def showAboutDialog(self, event):
        """ Shows the about dialog. """
        info = wx.adv.AboutDialogInfo()
        info.SetName("Square Crop")
        info.SetVersion("0.0.1")
        info.SetDevelopers(["Tianyi (Tiger) Cao"])
        info.SetDescription("A program to crop a picture into a square.")

        wx.adv.AboutBox(info)

    # The following methods create basic implementation of image dragging
    # I read up on DragImage and it was too complicated.
    # TODOs: Right now, your mouse cursor always tries to focus on the same
    #        location on the image. That means, if you drag too far, it'll stop
    #        dragging. But once you reverse the direction, it doesn't immediately
    #        start dragging backwards, instead you have to drag all the way back
    #        to where it stopped dragging for it to move backwards.
    def onLeftDown(self, event):
        self.mouseDown = True
        self.mouseDownCoordinates = event.GetPosition()
        self.mouseDownOffset = self.image.offset
    def onLeftUp(self, event):
        self.mouseDown = False
    def onMotion(self, event):
        # a quick note that
        #     1. dragging requires natural scrolling,
        #        i.e dragging downwards == scrolling upwards
        #     2. your image is scaled
        #        i.e a pixel on your monitor != a pixel in the image
        if self.mouseDown:
            width, height = self.imageView.Size
            scale = self.image.dimension / min(width, height)

            newCoordinates = event.GetPosition()
            x_pixelOffset = (self.mouseDownCoordinates[0] - newCoordinates[0]) * scale
            y_pixelOffset = (self.mouseDownCoordinates[1] - newCoordinates[1]) * scale
            self.image.addOffsetCoordinates(x_pixelOffset, y_pixelOffset, self.mouseDownOffset)

            if self.image.getStatusUpdate():
                self.imageView.Refresh()
    def onLeaveWindow(self, event):
        self.mouseDown = False