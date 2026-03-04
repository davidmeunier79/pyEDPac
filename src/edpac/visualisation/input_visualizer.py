import numpy as np
from edpac.visualisation.pixel_visualizer import PixelVisualizer

from edpac.config.constants import NB_VISIO_INPUTS, VISIO_SQRT_NB_NEURONS

class InputVisualizer(PixelVisualizer):
    def __init__(self, title = "EDPac inputs", scale = 1):
        # 5 squares of 20x20. With 5px padding, we need ~130px width.
        # Height 30px to accommodate a 20x20 square with padding.

        self.nb_input_patterns = NB_VISIO_INPUTS
        self.square_size = VISIO_SQRT_NB_NEURONS
        self.padding = 5

        height = VISIO_SQRT_NB_NEURONS + 2*self.padding
        width = NB_VISIO_INPUTS*(VISIO_SQRT_NB_NEURONS+self.padding) + self.padding
        print(width, height)

        super().__init__(height, width,  title=title, scale=scale)

    def draw_background(self):
        """Draw all neurons as DIM dots in the background."""
        self.set_background_color((10, 10, 20))

        for i in range(self.nb_input_patterns):

            x = self.padding + i*(self.square_size + self.padding)
            y = self.padding
            self.set_pattern(y, x, np.ones(shape = (self.square_size, self.square_size)),
                             (60, 60, 60), target_buffer=self.background)

        self.update_display()

    def display_inputs(self, sensor_values):
        """
        Takes a list/array of 5 values (0.0 to 1.0 or category IDs).
        Displays them as a horizontal bar of colored squares.
        """
        #self.clear_canvas((255, 255, 255))  # Dark gray background

        self.refresh_from_background()

        for i, pattern in enumerate(sensor_values):

            if pattern is None:
                continue

            base_x = self.padding +( i * (self.square_size + self.padding))
            base_y = self.padding

            self.set_pattern(base_y, base_x  ,pattern,  (255, 255, 255))

        self.update_display()
