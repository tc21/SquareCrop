import wx

class ImageDropTarget(wx.FileDropTarget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def OnDropFiles(self, x, y, filenames):
        """ Gets the file dropped and sets it. """
        if len(filenames) != 1:  # since it can be challenging to show 2 images
            return
        self.parent.setImage(filenames[0])