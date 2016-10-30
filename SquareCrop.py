import wx

import ImagePanel

# There is very minimal optimization in the scaling of the program.
# I found the one setting that worked best for my monitor, and just
# scaled everything.

# TODOs (Improvement)
#  Pass to waifu2x on save
#  2D Image Zooming
#  Configurations other than default

imageSize, frameWidth, frameHeight = \
    map(lambda x: x * wx.ScreenDC().GetPPI()[0] // 192,
        (1000, 1026, 1111))

app = wx.App(False)

frame = ImagePanel.ImagePanel(title="Square Crop", imageSize=imageSize)
frame.SetSize((frameWidth, frameHeight))
frame.Show()

# frame.setImage(None)
# frame.setImage("C:/image.jpg")

app.MainLoop()