import os
import re
import numpy as np
from PIL import Image
from edpac.visualisation.pixel_visualizer import PixelVisualizer

from edpac.zoo.zoo import Zoo
from edpac.zoo.pacman import Pacman

class ZooVisualizer(PixelVisualizer):
    def draw_zoo(self, zoo: Zoo):
        self.clear_canvas((255, 255, 255)) # Deep black background

        for row_idx, row in enumerate(zoo.grid):
            for col_idx, char in enumerate(row):
                if char in zoo.shapes:
                    base_x = col_idx * zoo.cell_size
                    base_y = row_idx * zoo.cell_size

                    #color = (0, 0, 0)

                    # Color Logic
                    if char == '.' or char == 'X':
                        color = (80, 80, 80)    # Dim gray for dots
                    elif char == '0':
                        color = (255, 255, 0)   # Yellow for Pacman
                    elif zoo.danger[char] == '1':
                        color = (0, 0, 255) # Blue for preys
                    elif zoo.danger[char] == '-1':
                        color = (255, 0, 0) # Red for predators

                    self.set_pattern(base_x, base_y , zoo.shapes[char].T, color)

        # 3. Draw Pacman (The Body and the Head Bar)
        self._draw_pacman(zoo)

        self.update_display()

    def _draw_pacman(self, zoo):
        p = zoo.pacman
        bx = p.x * zoo.cell_size
        by = p.y * zoo.cell_size

        # A. Draw Body Sprite
        direction_name = zoo.pacman_images[p.dir_body]
        body_shape = zoo.pacman_shapes[direction_name]
        self.set_pattern(bx, by ,body_shape,  (255, 255, 0)) # Yellow

        # B. Draw Head Bar (Blue Line)
        # We draw a 2-pixel thick blue line on the edge of the 16x16 cell
        blue = (50, 50, 255)
        cs = zoo.cell_size - 1

        if p.dir_head == 0: # Up: Top edge
            for i in range(16):
                self.set_pixel(bx + i, by, blue)
                self.set_pixel(bx + i, by + 1, blue)
        elif p.dir_head == 1: # Down: Bottom edge
            for i in range(16):
                self.set_pixel(bx + i, by + cs, blue)
                self.set_pixel(bx + i, by + cs - 1, blue)
        elif p.dir_head == 2: # Left: Left edge
            for i in range(16):
                self.set_pixel(bx, by + i, blue)
                self.set_pixel(bx + 1, by + i, blue)
        elif p.dir_head == 3: # Right: Right edge
            for i in range(16):
                self.set_pixel(bx + cs, by + i, blue)
                self.set_pixel(bx + cs - 1, by + i, blue)
