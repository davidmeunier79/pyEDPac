import numpy as np
import pyqtgraph as pg
from PySide6 import QtWidgets, QtCore
from PIL import Image

def load_xbm_as_coords(filepath):
    """
    Loads an XBM file and returns the (x, y) coordinates
    of all 'on' bits (black pixels).
    """
    with Image.open(filepath) as img:
        # XBM is 1-bit; convert to numpy array
        # 0 is usually white/off, 1 is black/on
        data = np.array(img)
        width, height = img.size

        # Find coordinates where the pixel is 'on'
        # Note: XBM data is often inverted depending on the viewer,
        # so we check for the foreground color.
        y_coords, x_coords = np.where(data == 0) # In PIL, 0 is often the 'ink' for XBM

        return x_coords, y_coords, width, height

class BaseVisualizer(pg.PlotWidget):
    """
    Modern replacement for the Fenetre class.
    Provides drawing primitives for pyEDPac simulations.
    """
    def __init__(self, title="pyEDPac Visualizer", background='w'):
        # Ensure QApplication exists
        if not QtWidgets.QApplication.instance():
            self.app = QtWidgets.QApplication([])
        else:
            self.app = QtWidgets.QApplication.instance()

        super().__init__()
        self.setBackground(background)
        self.setWindowTitle(title)

        # Initialize the scatter item for points/agents
        self.scatter_item = pg.ScatterPlotItem(pxMode=True)
        self.addItem(self.scatter_item) # This attaches it to the plot

        self.lines = []

    def clear_canvas(self):
        self.scatter_item.clear()
        for line in self.lines:
            self.removeItem(line)
        self.lines = []

    def draw_agent(self, x, y, size=5, color='b', symbol='o'):
        """
        Replacement for Fenetre::TraceCarre or TracePoint.
        Adds a point/agent to the scatter plot.
        """
        self.points.addPoints([{
            'pos': [x, y],
            'size': size,
            'pen': pg.mkPen(None),
            'brush': pg.mkBrush(color),
            'symbol': symbol
        }])

    def draw_connection(self, x1, y1, x2, y2, weight=1, color='k'):
        """
        Useful for the Network class to draw synapses.
        """
        line = pg.PlotCurveItem([x1, x2], [y1, y2],
                                 pen=pg.mkPen(color, width=weight))
        self.addItem(line)
        self.lines.append(line)

    def refresh(self):
        """Forces a GUI update, similar to XFlush or XNextEvent logic."""
        QtWidgets.QApplication.processEvents()


class PatternVisualizer(BaseVisualizer):
    def draw_pattern_in_rect(self, xbm_path, rect_x, rect_y, rect_w, rect_h):
        """
        Draws a rectangle and centers the XBM pattern inside it.
        """
        # 1. Draw the "Zoo" enclosure (The Rectangle)
        rect = pg.QtWidgets.QGraphicsRectItem(rect_x, rect_y, rect_w, rect_h)
        rect.setPen(pg.mkPen('k', width=2))
        self.addItem(rect)

        # 2. Load the pattern bits
        px, py, p_w, p_h = load_xbm_as_coords(xbm_path)

        # 3. Calculate centering offset
        offset_x = rect_x + (rect_w - p_w) / 2
        offset_y = rect_y + (rect_h - p_h) / 2

        # 4. Draw the bits as small points
        # We flip the y-axis (py) because X11 coordinates are top-down
        # while PlotWidget is usually bottom-up.
        self.scatter_item.addPoints(
            x=px + offset_x,
            y=(p_h - py) + offset_y,
            size=2,
            brush='k'
        )


class ZooVisualizer(BaseVisualizer):
    def __init__(self):
        super().__init__(title="EDPac Zoo")

    def draw_xbm_pattern(self, xbm_path, center_x, center_y):
        try:
            with Image.open(xbm_path) as img:
                # Convert XBM bits to coordinates
                data = np.array(img)
                # In XBM/PIL, 0 is often the 'ink' (foreground)
                y_idx, x_idx = np.where(data == 0)

                # Center the pattern
                width, height = img.size
                x_coords = x_idx - (width / 2) + center_x
                # Flip Y because X11 is top-down, but PlotWidget is bottom-up
                y_coords = (height - y_idx) - (height / 2) + center_y

                # Update the scatter plot
                self.scatter_item.addPoints(x=x_coords, y=y_coords, size=2, brush='k')

        except FileNotFoundError:
            print(f"Error: Could not find {xbm_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def draw_enclosure(self, x, y, w, h):
        """Draws the fixed size rectangle (The Zoo walls)"""
        rect = QtWidgets.QGraphicsRectItem(x, y, w, h)
        rect.setPen(pg.mkPen('k', width=2))
        self.addItem(rect)
