import os
import re
import numpy as np
from PIL import Image
from edpac.visualisation.pixel_visualizer import PixelVisualizer

from edpac.zoo.zoo import Zoo
from edpac.zoo.pacman import Pacman, Direction
from edpac.zoo.chars import char_to_index, index_to_char

from edpac.config.zoo_config import ZooVisualizerConfig

class ZooVisualizer(PixelVisualizer):

    def __init__(self, zoo, scale = 1, title="Zoo Display", config : ZooVisualizerConfig = None):

        self.config = config or ZooVisualizerConfig()
        self.cell_size = self.config.ZOO_CELL_SIZE

        self.zoo = zoo
        self.rows, self.cols = self.zoo.grid.shape

        #self.zoo = None
        super().__init__(self.rows * self.cell_size, self.cols * self.cell_size,title=title , scale=scale)

    def draw_static_grid(self, wall_color=(100, 100, 100)):
        """
        Draw walls into the BACKGROUND buffer so they don't need
        to be recalculated every frame.
        """
        self.set_background_color((255, 255, 255))
        wall_mask = np.ones((self.cell_size, self.cell_size), dtype=np.uint8)

        # Find walls in grid_array (assuming grid_array is a numpy array)
        yy, xx = np.where(self.zoo.grid == b'X')
        for y, x in zip(yy, xx):
            self.set_pattern(y * self.cell_size, x * self.cell_size,
                             wall_mask, wall_color, target_buffer=self.background)

    def draw_zoo(self):
        """
        1) Clear frame with background (walls)
        2) Draw Pacman and animals on active buffer
        """
        self.refresh_from_background()

        # Draw Animals
        for code in np.unique(self.zoo.grid):
            char = code.decode("utf-8")

            if char == 'X' or char == " ":
                continue

            elif char == ".":

                color = (80, 80, 80)    # Dim gray for dots
                val = self.zoo.animals["."]
                pos_y, pos_x = np.where(self.zoo.grid == code)
                for y, x in zip(pos_y, pos_x):
                    self.set_pattern(y * self.cell_size, x * self.cell_size, val["shape"], color )

                continue

            pacman_index = char_to_index(char)
            animal = pacman_index % 2

            assert animal in self.zoo.animals.keys(), f"Error with {animal} ands {self.zoo.animals.keys()}"

            val = self.zoo.animals[animal]
            if val["danger"] == "-1":
                color = (255, 0, 0) # Red for predators

            elif val["danger"] == "1":
                color = (0, 0, 255) # Blue for preys

            else:
                color = (80, 80, 80)    # Dim gray for dots

            self._draw_pacman(pacman_index, color)

        self.update_display()
#
#     def _turn(self, body_shape, dir_body):
#         # shapes are normallly looking RIGHT
#         if dir_body ==
    def _draw_pacman(self, pacman_index, color):

        if not self.zoo.population.individuals[pacman_index]:
            return

        pacman = self.zoo.population.individuals[pacman_index]

        x, y = pacman.get_position()

        bx = x * self.cell_size
        by = y * self.cell_size

        # A. Draw Body Sprite
        animal = pacman_index % 2

        body_shape = self.zoo.animals[animal]["shape"]
        #body_shape = self._turn(body_shape, pacman.dir_body)
        self.set_pattern(by, bx ,body_shape,  color)

        # B. Draw Head Bar (Blue Line)
        # We draw a 2-pixel thick blue line on the edge of the 16x16 cell
        blue_bar = np.zeros(shape = (self.cell_size, self.cell_size))

        if pacman.dir_head == Direction.UP: # Up: Top edge
            blue_bar[-2:, 2:19] = 1
        elif pacman.dir_head == Direction.DOWN: # Down: Bottom edge
            blue_bar[:2, 2:19] = 1
        elif pacman.dir_head == Direction.LEFT: # Left: Left edge
            blue_bar[2:19, :2] = 1
        elif pacman.dir_head == Direction.RIGHT: # Right: Right edge
            blue_bar[2:19, -2:] = 1
        self.set_pattern(by, bx ,blue_bar, color)
        #self.update_display()


