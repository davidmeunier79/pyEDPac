import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore
import pyqtgraph as pg

class PixelVisualizer(QtWidgets.QMainWindow):
#class PixelVisualizer(QtWidgets.QLabel):
    def __init__(self, height, width, scale = 1, title="Visualizer"):
        super().__init__()
        self.setWindowTitle(title)
        self.height = height
        self.width = width
        self.scale = scale

        # Buffers: uint8 is critical for pyqtgraph RGB performance
        self.buffer = np.zeros((height, width, 3), dtype=np.uint8)
        self.background = np.zeros((height, width, 3), dtype=np.uint8)

        # UI Setup
        self.setFixedSize(self.width * self.scale, self.height * self.scale)

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

    def draw_line(self, start_pos, end_pos, color, target_buffer=None, neuron_mask=np.ones(shape=(1,1))):

        dest = self.buffer if target_buffer is None else target_buffer

        x1, y1 = int(start_pos[0])*neuron_mask.shape[0], int(start_pos[1]*neuron_mask.shape[0])
        x2, y2 = int(end_pos[0])*neuron_mask.shape[1], int(end_pos[1])*neuron_mask.shape[1]

        # Bresenham's Algorithm
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            # Boundary Check: Only draw if within buffer limits
            if 0 <= x1 < self.width and 0 <= y1 < self.height:
                dest[y1, x1] = color

            if x1 == x2 and y1 == y2:
                break

            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    def update_display(self):
        """Push buffer to GPU."""
        self.img.setImage(self.buffer, autoLevels=False)
        #
        # if self.scale > 1:
        #     pixmap = pixmap.scaled(self.w * self.scale, self.h * self.scale, QtCore.Qt.KeepAspectRatio)
        #
