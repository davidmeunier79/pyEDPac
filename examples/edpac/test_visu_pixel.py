
import os
import sys
sys.path.insert(0, '../src')

from PySide6 import QtWidgets, QtCore
from edpac.visualisation.pixel_visualizer import PixelVisualizer

import numpy as np

def run_simulation_step(viz, network):
    """
    This replaces your old C++ while(1) loop logic.
    """
    # 1. Logic: Clear the screen
    viz.set_background_color((20, 20, 20)) # Dark gray background

    # 2. Update Network (Dummy example: random firing neurons)
    # In reality, you'd call network.step() here
    for _ in range(100):
        x = QtCore.QRandomGenerator.global_().bounded(viz.width)
        y = QtCore.QRandomGenerator.global_().bounded(viz.height)
        viz.set_pattern(x, y, np.ones(shape=(2, 2)), (255, 255, 0)) # Yellow for spike

    # 3. Render
    viz.update_display()

def main():
    app = QtWidgets.QApplication(sys.argv)

    # Create visualizer (800x600 pixels, scaled up 2x for visibility)
    viz = PixelVisualizer(width=400, height=300, scale=2)
    viz.show()

    # Use a QTimer to run the simulation at ~60 FPS
    timer = QtCore.QTimer()
    timer.timeout.connect(lambda: run_simulation_step(viz, None))
    timer.start(16) # 16ms = 60fps

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
