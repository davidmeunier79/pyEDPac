import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg

class PixelVisualizer(QtWidgets.QMainWindow):
    def __init__(self, height, width, title="Visualizer"):
        super().__init__()
        self.setWindowTitle(title)
        self.height = height
        self.width = width

        # Buffers: uint8 is critical for pyqtgraph RGB performance
        self.buffer = np.zeros((height, width, 3), dtype=np.uint8)
        self.background = np.zeros((height, width, 3), dtype=np.uint8)

        # UI Setup
        self.view = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.view)
        self.vb = self.view.addViewBox()
        self.vb.setAspectLocked(True)

        self.img = pg.ImageItem(axisOrder='row-major')
        self.vb.addItem(self.img)

    def refresh_from_background(self):
        """Clean the active buffer by copying the background."""
        np.copyto(self.buffer, self.background)

    def set_background_color(self, color):
        """Fill background with a solid color (R, G, B)."""
        self.background[:] = color

    def set_pattern(self, base_y, base_x, pattern_arr, color, target_buffer=None):
        """
        Draws a numpy pattern (mask of 1s) onto the buffer.
        target_buffer: if None, draws to active buffer. Else draws to background.
        """
        dest = self.buffer if target_buffer is None else target_buffer

        # Get indices where pattern is active
        rows, cols = np.where(pattern_arr > 0)

        # Shift indices
        target_rows = rows + base_y
        target_cols = cols + base_x

        # Boundary check using boolean masking
        valid = (target_rows >= 0) & (target_rows < self.height) & \
                (target_cols >= 0) & (target_cols < self.width)

        dest[target_rows[valid], target_cols[valid]] = color

    def update_display(self):
        """Push buffer to GPU."""
        self.img.setImage(self.buffer, autoLevels=False)
