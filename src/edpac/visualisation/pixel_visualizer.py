import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore

class PixelVisualizer(QtWidgets.QLabel):
    """
    A simple pixel-based visualizer.
    Acts like a canvas where you can set individual pixel colors.
    """
    def __init__(self, width=800, height=600, scale=1, title = "pyEDPac Pixel View"):
        super().__init__()
        self.w = width
        self.h = height
        self.scale = scale # Zoom factor (e.g., 2 makes 1 pixel look like 2x2)

        # Create a black background buffer (RGBA)
        self.buffer = np.zeros((self.h, self.w, 4), dtype=np.uint8)
        self.buffer[:, :, 3] = 255  # Set Alpha channel to opaque

        self.setFixedSize(self.w * self.scale, self.h * self.scale)
        self.setWindowTitle(title)

    def clear_canvas(self, color=(0, 0, 0)):
        """Resets the whole buffer to a specific color."""
        self.buffer[:, :, 0] = color[0]
        self.buffer[:, :, 1] = color[1]
        self.buffer[:, :, 2] = color[2]


    def set_pattern(self, base_x, base_y,  narr, color=(255, 255, 255)):
        """Directly sets a pixel color at (x, y)."""
        x, y = np.where (narr == True)
        self.buffer[base_y + y, base_x +x, :3] = color

    def set_pixel(self, x, y, color=(255, 255, 255)):
        """Directly sets a pixel color at (x, y)."""
        if 0 <= x < self.w and 0 <= y < self.h:
            self.buffer[y, x, :3] = color

    def update_display(self):
        """Converts the NumPy buffer to a QImage and displays it."""
        image = QtGui.QImage(
            self.buffer.data,
            self.w, self.h,
            QtGui.QImage.Format_RGBA8888
        )
        pixmap = QtGui.QPixmap.fromImage(image)

        # If scale > 1, resize the pixmap to make pixels visible
        if self.scale > 1:
            pixmap = pixmap.scaled(self.w * self.scale, self.h * self.scale, QtCore.Qt.KeepAspectRatio)

        self.setPixmap(pixmap)

    def closeEvent(self, event):
        QtWidgets.QApplication.quit()
        event.accept()
