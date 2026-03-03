import os
import re
import random
from math import floor
import numpy as np

from edpac.config.constants import NB_LIFE_POINTS_PER_PREY, VISIO_SQRT_NB_NEURONS, NB_LIFE_POINTS_PER_PREDATOR

from .pacman import Pacman

class Zoo:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.shapes = {}  # char -> list of (x, y), dangerosity
        self.grid = []    # 2D list of characters
        self.cell_size = 20
        self.danger = {}

        self.pacman = None # The dedicated Pacman object


    def set_pacman(self, pac):
        self.pacman = pac
        pac.zoo = self

    def _set_pacman_pos(self):
        """Locates Pacman ('0') on the grid."""
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                if char == '0':
                    self.pacman.set_position(x, y)

    def _get_pacman_pos(self):
        """Locates Pacman ('0') on the grid."""
        for y, row in enumerate(self.grid):
            for x, char in enumerate(row):
                if char == '0':
                    return x, y
        return None

    def _parse_xbm_hex(self, full_path):
        """Unpacks C-style XBM hex data into coordinates."""
        coords = np.zeros(shape = (VISIO_SQRT_NB_NEURONS,VISIO_SQRT_NB_NEURONS), dtype = int)

        try:
            with open(full_path, 'r') as f:
                content = f.read()
            match = re.search(r'\{(.*?)\}', content, re.DOTALL)
            if not match: return []

            hex_data = match.group(1).replace('\n', '').split(',')
            bytes_list = [int(h.strip(), 16) for h in hex_data if h.strip()]

            for row in range(16):
                for byte_idx in range(2):
                    byte_val = bytes_list[row * 2 + byte_idx]
                    for bit in range(8):
                        if (byte_val >> bit) & 1:

                            assert 0 <= (byte_idx * 8) + bit and (byte_idx * 8) + bit < VISIO_SQRT_NB_NEURONS
                            assert 0 <= row + bit and row < VISIO_SQRT_NB_NEURONS

                            coords[(byte_idx * 8) + bit , row ] = 1

        except Exception as e:
            print(f"Error parsing {full_path}: {e}")

        return coords

    def _parse_img_file(self, full_path):
        """Parses the 16x16 '0/1' text files."""
        coords = np.zeros(shape = (VISIO_SQRT_NB_NEURONS,VISIO_SQRT_NB_NEURONS), dtype = int)
        try:
            with open(full_path, 'r') as f:
                # first line
                firstl = f.readline().strip().split(":")
                nb_lines = int(firstl[1])

                # second line
                secondl = f.readline().strip().split(":")
                nb_cols = int(secondl[1])

                #empty line
                void = f.readline()

                for y, line in enumerate(f.readlines()):
                    line_ = line.replace("\"", "").replace(",", "")

                    for x, bit in enumerate(line_):

                        if bit == '.':

                            assert 0 <= int(x) and int(x) < nb_lines, f"Error with x: {x}"
                            assert 0 <= int(y) and int(y) < nb_cols, f"Error with x: {x}"

                            coords[int(y), int(x)] = 1
        except Exception as e:
            print(e)

        return coords

    def load_menagerie(self,  menagerie_file= "menagerie.txt"):
        # 1. Load the '.' (dot)
        self.shapes['.'] = self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "dot"))
        self.danger['.'] = 0

        # 2. Load Pacman directions ('0')
        # We store them in a dict inside shapes or specific attributes
        self.pacman_shapes = {
            "right": self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userright")),
            "left":  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userleft")),
            "up":    self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userup")),
            "down":  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userdown")),
        }

        self.shapes['0'] = self.pacman_shapes["right"] # Default
        self.danger['0'] = 0

        # Mapping for dir_body to specific shape names
        self.pacman_images = {
            0: "up",
            1: "down",
            2: "left",
            3: "right"
        }

        # 3. Load Menagerie (animals)
        men_path = os.path.join(self.data_dir, "menagerie", menagerie_file)
        with open(men_path, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) == 3:
                    char, rel_path = parts[0], parts[1]
                    self.shapes[char] = self._parse_img_file(os.path.join(self.data_dir, "menagerie", rel_path))
                    self.danger[char] = parts[2]


    def load_screen(self, screen_file="screen.0"):

        # Load the screen and find the initial '0' to place Pacman
        screen_path = os.path.join(self.data_dir, "screens",  f"{screen_file}")

        if len(self.grid):
            del self.grid

        self.grid = []
        with open(screen_path, 'r') as f:
            for y, line in enumerate(f):
                for x, el in enumerate(line.strip()):
                    if el == '0':
                        self.pacman.set_position(x, y)

                row = list(line.rstrip('\n'))
                self.grid.append(row)

    def get_move_probabilities(self, animal_x, animal_y, char):
        """
        Inspired by Zoo::probasAnimaux.
        Returns weights for [Up, Down, Left, Right, Stay].
        """
        pac_pos = self._get_pacman_pos()
        if not pac_pos:
            return [0.2, 0.2, 0.2, 0.2, 0.2] # Random if no Pacman

        px, py = pac_pos
        dx = px - animal_x
        dy = py - animal_y

        # Danger nature: 1 (Prey -> Avoid), -1 (Predator -> Approach)
        nature = self.danger[char]

        # Base weights (Equal chance)
        # Order: 0:Up (0,-1), 1:Down (0,1), 2:Left (-1,0), 3:Right (1,0), 4:Stay (0,0)
        weights = [1.0, 1.0, 1.0, 1.0, 0.5]
        #weights = [0.0, 0.0, 0.0, 0.0, 0.0]

        # Strength of attraction/repulsion (equivalent to COEF_ATTR in C++)
        bias = 1.0

        if nature == "-1": # PREDATOR: Wants to decrease distance
            if dy < 0: weights[0] += bias # Up
            if dy > 0: weights[1] += bias # Down
            if dx < 0: weights[2] += bias # Left
            if dx > 0: weights[3] += bias # Right

        elif nature == "1": # PREY: Wants to increase distance
            if dy < 0: weights[1] += bias # Move Down if Pacman is Up
            if dy > 0: weights[0] += bias # Move Up if Pacman is Down
            if dx < 0: weights[3] += bias # Move Right if Pacman is Left
            if dx > 0: weights[2] += bias # Move Left if Pacman is Right

        return weights

    def live_one_step(self):
        """
        Main simulation tick.
        Inspired by the 'vivre' function in EDPac C++.
        """
        rows = len(self.grid)
        cols = len(self.grid[0])

        # 1. Find all active entities (Pacman and Animals)
        # so we don't move the same entity twice in one tick.
        entities = []
        for y in range(rows):
            for x in range(cols):
                char = self.grid[y][x]
                if char in self.shapes and char not in ('.', 'X', " "):
                    entities.append((x, y, char))

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]

        for x, y, char in entities:
            if char == '0':

                for dir_x, dir_y in directions[:-1]:
                    if 0 <= x + dir_x < cols and 0 <= y + dir_y < rows:

                        char = self.grid[y + dir_y][x + dir_x]

                        if self.danger[char] == "-1":

                            self.pacman.life_points = self.pacman.life_points - NB_LIFE_POINTS_PER_PREDATOR

                            print("Contact with predator ", char, " Life points: " , self.pacman.life_points)

                continue

            # Calculate biased probabilities
            weights = self.get_move_probabilities(x, y, char)

            # Choose a move based on weights
            choice_idx = random.choices(range(5), weights=weights, k=1)[0]
            dx, dy = directions[choice_idx]
            nx, ny = x + dx, y + dy

            # Bounds and Wall Check
            if 0 <= nx < cols and 0 <= ny < rows:
                if self.grid[ny][nx] in [" ", "."]: # Not a pacgum or empty
                    self._move_actor(x, y, nx, ny, char)

    def _move_actor(self, old_x, old_y, new_x, new_y, char):
        """Helper to update grid and leave a dot behind if necessary."""
        # In EDPac, usually, when an animal moves, it leaves the floor ('.') behind.
        tmp_char = self.grid[new_y][new_x]

        self.grid[old_y][old_x] = tmp_char
        self.grid[new_y][new_x] = char


