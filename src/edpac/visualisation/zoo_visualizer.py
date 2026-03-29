import os
import re
import numpy as np
from PIL import Image
from edpac.visualisation.pixel_visualizer import PixelVisualizer

from edpac.zoo.zoo import Zoo
from edpac.zoo.pacman import Pacman, Direction

from edpac.config.zoo_config import ZooVisualizerConfig

class ZooVisualizer(PixelVisualizer):

    def __init__(self, scale = 1, title="Zoo Display", config : ZooVisualizerConfig = None):

        self.config = config or ZooVisualizerConfig()
        self.rows, self.cols = self.config.ZOO_NB_ROWS, self.config.ZOO_NB_COLS
        self.cell_size = self.config.ZOO_CELL_SIZE
        self.zoo = None
        super().__init__(self.rows * self.cell_size, self.cols * self.cell_size,title=title , scale=scale)

    def init_zoo(self, zoo : Zoo):
        self.zoo = zoo

    def draw_static_grid(self, grid_array, wall_color=(100, 100, 100)):
        """
        Draw walls into the BACKGROUND buffer so they don't need
        to be recalculated every frame.
        """
        self.set_background_color((255, 255, 255))
        wall_mask = np.ones((self.cell_size, self.cell_size), dtype=np.uint8)

        # Find walls in grid_array (assuming grid_array is a numpy array)
        yy, xx = np.where(grid_array == b'X')
        for y, x in zip(yy, xx):
            self.set_pattern(y * self.cell_size, x * self.cell_size,
                             wall_mask, wall_color, target_buffer=self.background)

    def draw_zoo(self):
        """
        1) Clear frame with background (walls)
        2) Draw Pacman and animals on active buffer
        """
        self.refresh_from_background()

        #self._draw_pacman()
        self.update_display()

        # Draw Animals
        for code in np.unique(self.zoo.grid):
            char = code.decode("utf-8")

            if char == 'X' or char == " ":
                continue

            elif char != ".":
                print(char)
                char = int(char)

            assert char in self.zoo.animals.keys(), f"Error with {char} ands {self.zoo.animals.keys()}"

            val = self.zoo.animals[char]
            if val["danger"] == "-1":
                color = (255, 0, 0) # Red for predators

            elif val["danger"] == "1":
                color = (0, 0, 255) # Blue for preys

            else:
                color = (80, 80, 80)    # Dim gray for dots

            pos_x, pos_y = np.where(self.zoo.grid == code)
            for (x, y) in zip(pos_x, pos_y):
                self.set_pattern(x * self.cell_size,
                                 y * self.cell_size,
                                 val["shape"],
                                 color )
        self.update_display()
    #
    # def _draw_pacman(self):
    #     pacman = self.zoo.pacman
    #     x,y = self.zoo._get_pacman_pos()
    #
    #     bx = x * self.cell_size
    #     by = y * self.cell_size
    #
    #     # A. Draw Body Sprite
    #     body_shape = self.zoo.pacman_shapes[pacman.dir_body]
    #     self.set_pattern(bx, by ,body_shape,  (255, 255, 0)) # Yellow
    #
    #     # B. Draw Head Bar (Blue Line)
    #     # We draw a 2-pixel thick blue line on the edge of the 16x16 cell
    #     blue_bar = np.zeros(shape = (self.cell_size, self.cell_size))
    #
    #     if pacman.dir_head == Direction.UP: # Up: Top edge
    #         blue_bar[-2:, 2:19] = 1
    #     elif pacman.dir_head == Direction.DOWN: # Down: Bottom edge
    #         blue_bar[:2, 2:19] = 1
    #     elif pacman.dir_head == Direction.LEFT: # Left: Left edge
    #         blue_bar[2:19, :2] = 1
    #     elif pacman.dir_head == Direction.RIGHT: # Right: Right edge
    #         blue_bar[2:19, -2:] = 1
    #     self.set_pattern(bx, by ,blue_bar, (50, 50, 255)) # blue
    #
    #     self.update_display()
