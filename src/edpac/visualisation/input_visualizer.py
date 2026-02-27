import numpy as np
from edpac.visualisation.pixel_visualizer import PixelVisualizer

from edpac.config.constants import NB_VISIO_INPUTS, VISIO_SQRT_NB_NEURONS

class InputVisualizer(PixelVisualizer):
    def __init__(self, scale=2):
        # 5 squares of 20x20. With 5px padding, we need ~130px width.
        # Height 30px to accommodate a 20x20 square with padding.
        super().__init__(width=130, height=30, scale=scale)
        self.square_size = VISIO_SQRT_NB_NEURONS
        self.padding = 5

    def _draw_filled_square(self, x_start, y_start, color):
        """Helper to fill a 20x20 area in the buffer."""
        for y in range(y_start, y_start + self.square_size):
            for x in range(x_start, x_start + self.square_size):
                self.set_pixel(x, y, color)

    def display_inputs(self, sensor_values):
        """
        Takes a list/array of 5 values (0.0 to 1.0 or category IDs).
        Displays them as a horizontal bar of colored squares.
        """
        self.clear_canvas((255, 255, 255))  # Dark gray background

        for i, pattern in enumerate(sensor_values):

            if pattern is None:
                continue

            print(pattern)

            base_x = i * self.square_size
            base_y = self.padding

            for px, py in pattern:
                self.set_pixel(base_x + px, base_y + py, (0, 0, 0))

        self.update_display()
