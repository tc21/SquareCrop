""" A wrapper over wx.Image, providing functionality of Square Crop. """
import wx

class SquareImage:
    __HORIZONTAL = 0
    __VERTICAL = 1

    def __init__(self, path):
        if path is None:
            self.source = wx.Image("white.bmp")
        else:
            self.source = wx.Image(path)
        self.path = path
        self.width, self.height = self.source.GetSize()

        # In the future, there will be the ability to zoom.
        # Currently, you can't zoom in to the picture.
        # Currently, the mouse wheel also does nothing.
        # You would be able to control an image's vertical and horizontal
        # offset at the same time.
        # self.zoomFactor = 1.0
        # self.horizontalOffset = 0
        # self.verticalOffset = 0
        self.offset = 0
        if self.width >= self.height:
            self.direction = SquareImage.__HORIZONTAL
            self.dimension = self.height
        else:
            self.direction = SquareImage.__VERTICAL
            self.dimension = self.width

        self.changedSinceLastUpdate = True

    def image(self):
        """ Returns the cropped, square image. """
        if self.direction == SquareImage.__HORIZONTAL:
            left, top = self.offset, 0
        else:
            left, top = 0, self.offset
        return self.source.GetSubImage((left, top, self.dimension, self.dimension))

    def setOffset(self, offset):
        """ Sets the offset of the cropped image, ensuring the cropped
            image is within boundaries of the source. """
        if offset < 0:
            newOffset = 0
        elif self.dimension + offset > max(self.width, self.height):
            newOffset = max(self.width, self.height) - self.dimension
        else:
            newOffset = offset

        if newOffset != self.offset:
            self.changedSinceLastUpdate = True
            self.offset = newOffset

    def addOffsetCoordinates(self, x, y, original):
        """ This function provides an interface for ImagePanel
            to pass an xy-coordinate delta without knowing the orientation
            of the image. """
        if self.direction == SquareImage.__HORIZONTAL:
            offsetCoordinate = x
        else:
            offsetCoordinate = y
        self.setOffset(original + offsetCoordinate)

    def getStatusUpdate(self):
        """ Another interface for ImagePanel, which returns whether the
            image changed since the previous call the getStatusUpdate. """
        if self.changedSinceLastUpdate:
            self.changedSinceLastUpdate = False
            return True
        else:
            return False

    def writeFile(self):
        """ Simply saves the image as image~cropped.png.
            In the future, maybe can be extended to specify path or
            extension. wx.Image.SaveFile automatically parses extension,
            so all you need to do is change the output filename. """
        outputPath = self.path[:self.path.rfind(".")] + "~cropped.png"
        self.image().SaveFile(outputPath)
        return outputPath