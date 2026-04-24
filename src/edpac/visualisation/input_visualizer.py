import numpy as np
from edpac.visualisation.pixel_visualizer import PixelVisualizer

from edpac.config.constants import NB_VISIO_INPUTS, VISIO_SQRT_NB_NEURONS

class InputVisualizer(PixelVisualizer):
    def __init__(self, height = 0, width = 0,  title = "EDPac inputs", scale = 1):
        # 5 squares of 20x20. With 5px padding, we need ~130px width.
        # Height 30px to accommodate a 20x20 square with padding.

        self.nb_input_patterns = NB_VISIO_INPUTS
        self.square_size = VISIO_SQRT_NB_NEURONS
        self.padding = 5

        if not height:
            height = VISIO_SQRT_NB_NEURONS + 2*self.padding

        if not width:
            width = NB_VISIO_INPUTS*(VISIO_SQRT_NB_NEURONS+self.padding) + self.padding

        super().__init__(height, width,  title=title, scale=scale)

        self.set_background_color((10, 10, 20))


    def draw_empty_inputs(self, root_x = 0 , root_y = 0):
        """Draw all neurons as DIM dots in the background."""

        for i in range(self.nb_input_patterns):

            base_x = self.padding + i*(self.square_size + self.padding)
            base_y = self.padding

            self.set_pattern(root_y + base_y,root_x + base_x, np.ones(shape = (self.square_size, self.square_size)),
                             (0, 0, 0))

    def draw_background(self, root_x = 0 , root_y = 0):
        """Draw all neurons as DIM dots in the background."""

        for i in range(self.nb_input_patterns):

            base_x = self.padding + i*(self.square_size + self.padding)
            base_y = self.padding

            self.set_pattern(root_y + base_y,root_x + base_x, np.ones(shape = (self.square_size, self.square_size)),
                             (60, 60, 60), target_buffer=self.background)

        #self.update_display()

    def display_inputs(self, sensor_values, root_x = 0 , root_y = 0):
        """
        Takes a list/array of 5 values (0.0 to 1.0 or category IDs).
        Displays them as a horizontal bar of colored squares.
        """
        #self.clear_canvas((255, 255, 255))  # Dark gray background

        #self.refresh_from_background()

        for i, pattern in enumerate(sensor_values):

            if pattern is None:
                continue

            base_x = self.padding +( i * (self.square_size + self.padding))
            base_y = self.padding

            self.set_pattern(root_y + base_y, root_x + base_x, pattern, (255, 255, 255))

        #self.update_display()

    def display_color_inputs(self, sensor_values, root_x = 0 , root_y = 0, verbose = 0):
        """
        Takes a list/array of 5 values (0.0 to 1.0 or category IDs).
        Displays them as a horizontal bar of colored squares.
        """
        #self.clear_canvas((255, 255, 255))  # Dark gray background

        #self.refresh_from_background()

        for i, pattern in enumerate(sensor_values):

            if verbose > 0:
                print(i, pattern)

            if pattern is None:
                continue

            base_x = self.padding +( i * (self.square_size + self.padding))
            base_y = self.padding

            self.set_color_pattern(root_y + base_y, root_x + base_x, pattern)

        #self.update_display()
