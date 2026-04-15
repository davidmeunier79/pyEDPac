import os
import re
import string
import random
from math import floor
import numpy as np
import pathlib

from edpac.config.constants import VISIO_SQRT_NB_NEURONS, NB_VISIO_INPUTS, REGROWTH_PACGUM_RATE

from .chars import char_to_index, index_to_char
from .pacman import Pacman, Direction

class Zoo:
    def __init__(self,
                 cell_size=VISIO_SQRT_NB_NEURONS):

        self.cell_size = cell_size
        self.rows = 0
        self.cols = 0

        self._grid = None  # Now a NumPy array

        #self.shapes = {}
        #self.danger = {}
        self.animals = {}

        self.data_dir = self._get_data_dir()


        self.stats = {"time": [] , "nb_predators": [], "nb_preys" : [], "mean_predator_fitness" : [], "mean_prey_fitness": [], "generation" : [], "nb_deads": [], "nb_added_pacgums": []}

        #
        # # Mapping for clarity
        # self.WALL = 'X'
        # self.EMPTY = ' '
        # self.DOT = '.'

    def init_stats(self):

        self.stats["time"].append(0)
        self.stats["nb_predators"].append(0)
        self.stats["nb_preys"].append(0)
        self.stats["mean_predator_fitness"].append(0)
        self.stats["mean_prey_fitness"].append(0)

        self.stats["generation"].append(0)
        self.stats["nb_deads"].append(0)
        self.stats["nb_added_pacgums"].append(0)

    def _get_data_dir(self):

        # 1. Get the absolute path of constants.py
        current_file = pathlib.Path(__file__).resolve()

        # 2. Go up the folder tree to find the project root
        # (In your case: constants.py -> config/ -> edpac/ -> src/ -> ROOT)
        # Adjust the number of .parent calls to match your actual structure
        PROJECT_ROOT = current_file.parent.parent.parent.parent

        data_dir = os.path.join(PROJECT_ROOT, "data")
        return data_dir

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

                            coords[(byte_idx * 8) + bit +2, row +2] = 1

        except Exception as e:
            print(f"Error parsing {full_path}: {e}")

        return coords.T

    def _parse_img_file(self, full_path):
        """Parses the 16x16 '0/1' text files."""

        with open(full_path, 'r') as f:
            # first line
            firstl = f.readline().strip().split(":")
            nb_lines = int(firstl[1])

            # second line
            secondl = f.readline().strip().split(":")
            nb_cols = int(secondl[1])

            #empty line
            void = f.readline()


            coords = np.zeros(shape = (nb_lines, nb_cols), dtype = int)

            for x, line in enumerate(f.readlines()):
                line_ = line.replace("\"", "").replace(",", "")

                for y, bit in enumerate(line_):

                    if bit == '.':

                        assert 0 <= int(x) and int(x) < nb_lines, f"Error with x: {x}"
                        assert 0 <= int(y) and int(y) < nb_cols, f"Error with x: {x}"

                        #coords[int(y), int(x)] = 1
                        coords[ int(x), int(y)] = 1

        return np.flipud(coords)

    def load_menagerie(self,  menagerie_file= "menagerie.txt"):
        # 1. Load the '.' (dot)
        self.animals['.'] = {
            "shape": self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "dot")),
            "danger": 0,
            "name" : "dot"}

        # 2. Load Pacman directions ('0')
        # We store them in a dict inside shapes or specific attributes
        # 0: Up, 1: Down, 2: Left, 3: Right
        self.pacman_shapes = {
            0:  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userup")),
            1:  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userdown")),
            2:  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userleft")),
            3:  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userright")),
        }

        # 3. Load Menagerie ()
        men_path = os.path.join(self.data_dir, "menagerie", menagerie_file)
        with open(men_path, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) == 3:
                    char, rel_path = parts[0], parts[1]
                    if char == "X":
                        index = "X"
                    else:
                        print(char.lower())
                        index = string.ascii_lowercase.index(char.lower())

                    print(index)
                    self.animals[index] = {
                        "shape": self._parse_img_file(os.path.join(self.data_dir, "menagerie", rel_path)),
                        "danger": parts[2],
                        "name" : rel_path.split("/")[0]
                        }

    def load_screen(self, screen_file):
        """Loads level and converts to a numpy grid."""
        # ... logic to get lines from file ...
        # Assume lines is a list of strings from the .txt file

        # Load the screen and find the initial '0' to place Pacman
        screen_path = os.path.join(self.data_dir, "screens", screen_file)

        with open(screen_path, 'r') as f:
            # first line
            firstl = f.readline().strip().split(":")
            nb_lines = int(firstl[1])

            # second line
            secondl = f.readline().strip().split(":")
            nb_cols = int(secondl[1])

            self.rows = nb_lines
            self.cols = nb_cols

            # Create a numeric numpy grid
            self._grid = np.zeros((self.rows, self.cols), dtype=bytes)

            for r, line in enumerate(f.readlines()):
                for c, char in enumerate(line.strip()):
                    self._set_in_grid(c, r, char)

    def integrate_visio_outputs(self, pac):
        """
        Scans the zoo grid in a fan shape based on dir_head.
        Returns a list of 5 shapes (lists of pixel coordinates).
        """

        ## scanning laterally from higher to lower if dir_head = UP or LEFT ds > 0
        ## scanning laterally from lower to higher if dir_head = DOWN or RIGHT ds < 0

        ### scanning depth from lower to higher if dir_head = UP or RIGHT: df > 0
        ### scanning depth from higher to lower if dir_head = DOWN or LEFT df < 0

        # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        if pac.dir_head == Direction.UP: # HAUT (UP)
            df, ds = (0, 1), (1, 0)
        elif pac.dir_head == Direction.DOWN: # BAS (DOWN)
            df, ds = (0, -1), (-1, 0)
        elif pac.dir_head == Direction.LEFT: # GAUCHE (LEFT)
            df, ds = (-1, 0), (0, 1)
        elif pac.dir_head == Direction.RIGHT: # DROITE (RIGHT)
            df, ds = (1, 0), (0, -1)

        visio_patterns = []

        # 2. Iterate through each sensory column (i)
        for i in range(NB_VISIO_INPUTS):

            # Calculate column index relative to center (e.g., -2, -1, 0, 1, 2)
            rel_col = i - (NB_VISIO_INPUTS - 1) // 2

            found_shape = None
            #np.zeros(shape = (VISIO_SQRT_NB_NEURONS, VISIO_SQRT_NB_NEURONS), dtype = 'int64')

            # 3. Scan depth (j) in the current column
            # Start depth at abs(rel_col) to create a "V" shaped fan
            for j in range(max(abs(rel_col), 1), pac.pacman_config.VISIO_COLUMN_DEPTH+1):
                # Calculate grid coordinates: Start + (depth * Forward) + (offset * Side)
                nx = pac.x + (j * df[0]) + (rel_col * ds[0])
                ny = pac.y + (j * df[1]) + (rel_col * ds[1])

                char = self._in_grid(nx, ny)

                if not char:
                    continue

                if char == '.' or char == ' ':
                    continue

                elif char == 'X':
                    animal = 'X'
                else:
                    index = char_to_index(char)
                    animal = self.get_animal_from_index(index)

                # 4. Check for Objects (Walls or Animals)
                assert animal in self.animals.keys(), f"Error with {animal}, not in {self.animals.keys()}"

                found_shape = self.blur_pattern(self.animals[animal]["shape"], float(abs(j))/pac.pacman_config.VISIO_COLUMN_DEPTH * pac.pacman_config.BLURRED_FACTOR)

                break

            # If nothing found in this column, it's an empty sensor
            visio_patterns.append(found_shape)

        return visio_patterns


    def blur_pattern(self, pattern, noise):
        import numpy as np

        new_pattern = pattern.copy()
        mask = np.random.rand(*pattern.shape) < noise
        rand_values = np.random.randint(2, size=pattern.shape)
        new_pattern[mask] = rand_values[mask]

        return new_pattern

    def _in_grid(self, pos_x, pos_y):
        if 0 <= pos_x < self.cols and 0 <= pos_y < self.rows:
            char = self._grid[pos_y][pos_x].decode("utf-8")
            return char
        return 0


    def _set_in_grid(self, pos_x, pos_y, char):
        if 0 <= pos_x < self.cols and 0 <= pos_y < self.rows:
            self._grid[pos_y][pos_x] = char
        else:
            print(f"Error, could not add {char} at position {pos_x} {pos_y}")

    def _where_in_grid(self, char):
        if char in np.unique(self._grid):
            yy, xx = np.where(self._grid == char)
            return yy, xx
        else:
            #print(f"Error, {char=} could not be found in _grid")
            return ([-1], [-1])

    def add_random_pacgums(self):
        """
        Adding some pacgums in empty locations
        """
        xx, yy = self._where_in_grid(b" ")

        if xx[0] == -1 and yy[0] == -1:
            #print("No empy space found, skipping")
            return 0

        #print(f"Found {len(xx)} empty locations in zoo")
        assert len(xx) == len(yy), f"Error with _where_in_grid,  {len(xx)=} != {len(yy)=}"
        keep =  np.random.uniform(size = len(xx)) < REGROWTH_PACGUM_RATE

        nb_added_pacgums = np.sum(keep)

        #print(f"Adding {nb_added_pacgums} pacgums")

        self._grid[xx[keep], yy[keep]] = "."

        return nb_added_pacgums

    def get_animal_from_index(self, index):
        return index % 2

    def save_stats(self, indiv_path=0):

        import json
        import os
        import pandas as pd

        if indiv_path == 0:
            indiv_path = os.path.abspath("")
        else:
            try:
                os.makedirs(os.path.abspath(indiv_path))
            except OSError:
                print(f"{os.path.abspath(indiv_path)} already exists")

        file_stats = os.path.join(indiv_path, f"Stats_evo.csv")

        df = pd.DataFrame(self.stats)
        df = df.set_index("time")

        df.to_csv(file_stats , header = True)
