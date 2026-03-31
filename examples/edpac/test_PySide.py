import sys
import numpy as np
from PySide6 import QtWidgets, QtCore
import pyqtgraph as pyqtgraph

class EDPacWindow(QtWidgets.QMainWindow):
    def __init__(self, width=800, height=600, title="pyEDPac Visualization"):
        super().__init__()

        # 1. Setup the Central Widget and Layout
        self.setWindowTitle(title)
        self.resize(width, height)
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # 2. Setup the Plotting Widget (The "Fenetre" Canvas)
        # pyqtgraph is significantly faster than Matplotlib for simulations
        self.canvas = pyqtgraph.PlotWidget()
        self.canvas.setBackground('w')  # White background like classic X11
        self.canvas.showGrid(x=True, y=True)
        self.layout.addWidget(self.canvas)

        # Reference for drawing objects (lines, points, etc.)
        self.curve = self.canvas.plot(pen='b') # Blue line
        self.scatter = pyqtgraph.ScatterPlotItem(size=10, pen=pyqtgraph.mkPen(None), brush=pyqtgraph.mkBrush(255, 0, 0, 120))
        self.canvas.addItem(self.scatter)

        # 3. Simulation Timer (Replaces the manual X11 event loop)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_simulation)
        self.timer.start(50)  # Update every 50ms

        # Example data state
        self.ptr = 0

    def draw_point(self, x, y):
        """Replacement for Fenetre::DrawPoint"""
        self.scatter.addPoints([{'pos': [x, y]}])

    def update_simulation(self):
        """
        This is where your pyEDPac logic would hook in.
        Example: Drawing a moving sine wave.
        """
        data = np.sin(np.linspace(0, 10, 100) + self.ptr)
        self.curve.setData(data)
        self.ptr += 0.1

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = EDPacWindow()
    window.show()
    sys.exit(app.exec())
