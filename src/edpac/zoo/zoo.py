import os
import re
import random
from math import floor
import numpy as np

from edpac.config.constants import NB_LIFE_POINTS_PER_PREY, VISIO_SQRT_NB_NEURONS, NB_LIFE_POINTS_PER_PREDATOR

from .pacman import Pacman
class Zoo:
    def __init__(self, data_dir, cell_size=VISIO_SQRT_NB_NEURONS):
        self.cell_size = cell_size
        self.rows = 0
        self.cols = 0
        self.grid = None  # Now a NumPy array
        self.pacman = None

        #self.shapes = {}
        #self.danger = {}
        self.animals = {}

        self.data_dir = data_dir

        # Mapping for clarity
        self.WALL = 'X'
        self.EMPTY = ' '
        self.DOT = '.'


    def set_pacman(self, pac):
        self.pacman = pac
        pac.zoo = self

    def _set_pacman_pos(self):
        """Locates Pacman ('0') on the grid."""
        x, y = np.where(self.grid == b'0')

        if len(x) == 1 and len(y) == 1:
            self.pacman.set_position(x, y)
        else:
            print("Warning, could not find pacman in zoo")
            self.pacman.set_position(0, 0)

    def _get_pacman_pos(self):
        """Locates Pacman ('0') on the grid."""
        x, y = np.where(self.grid == b'0')

        if len(x) == 1 and len(y) == 1:
            return x[0], y[0]
        else:
            print("Warning, could not find pacman in zoo")
            print(self.grid)
            0/0
            return 0, 0

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

        return coords

    def load_menagerie(self,  menagerie_file= "menagerie.txt"):
        # 1. Load the '.' (dot)
        self.animals['.'] = {
            "shape": self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "dot")),
            "danger": 0}


        # 2. Load Pacman directions ('0')
        # We store them in a dict inside shapes or specific attributes
        # 0: Up, 1: Down, 2: Left, 3: Right
        self.pacman_shapes = {
            0:  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userup")),
            1:  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userdown")),
            2:  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userleft")),
            3:  self._parse_xbm_hex(os.path.join(self.data_dir, "formes", "userright")),
        }

        print(self.pacman_shapes)

        #self.shapes['0'] = self.pacman_shapes["right"] # Default
        #self.danger['0'] = 0

        # 3. Load Menagerie ()
        men_path = os.path.join(self.data_dir, "menagerie", menagerie_file)
        with open(men_path, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) == 3:
                    char, rel_path = parts[0], parts[1]
                    self.animals[char] = {
                        "shape": self._parse_img_file(os.path.join(self.data_dir, "menagerie", rel_path)),
                        "danger": parts[2]
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
            self.grid = np.zeros((self.rows, self.cols), dtype=bytes)

            for r, line in enumerate(f.readlines()):
                for c, char in enumerate(line.strip()):
                    if char == '0':
                        # Pacman starting position
                        if self.pacman is not None:
                            self.pacman.set_position(c,r)
                        else:
                            print("warning, pacman in not instanciated yet...")

                    self.grid[r, c] = char
    #
    # def is_wall(self, x, y):
    #     """Vectorized boundary and wall check."""
    #     if 0 <= x < self.cols and 0 <= y < self.rows:
    #         return self.grid[y, x] == self.WALL
    #     return True
    #
    # def get_vision_slice(self, x, y, size=5):
    #     """
    #     Extracts a sub-array of the grid for Pacman's vision.
    #     Very fast using numpy slicing.
    #     """
    #     # Calculate bounds for a centered crop
    #     half = size // 2
    #     # Note: Padding might be needed if Pacman is near the edge
    #     # For simplicity, returning a slice:
    #     return self.grid[max(0, y-half):y+half+1, max(0, x-half):x+half+1]

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
        nature = self.animals[char]["danger"]

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
        elif nature == "0":
            pass
            #print("Neutral no move")
            #print( self.animals[char])
        else:
            print(f"Error with nature {nature}")

        return weights

    def live_one_step(self):
        """
        Main simulation tick.
        Inspired by the 'vivre' function in EDPac C++.
        """

        rows, cols = self.grid.shape


        entities = []

        for code in np.unique(self.grid):
            char = code.decode("utf-8")

            if char == 'X' or char == " " or char == '.':
                continue

            pos_x, pos_y = np.where(self.grid == code)
            for (x, y) in zip(pos_x, pos_y):
                entities.append((x , y , char))

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (0, 0)]

        for x, y, char in entities:
            #print(x, y, char)

            if char == '0':
                for dir_x, dir_y in directions[:-1]:
                    if 0 <= x + dir_x < cols and 0 <= y + dir_y < rows:
                        char = self.grid[y + dir_y][x + dir_x]

                        if self.animals[char]["danger"] == "-1":
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
            if 0 <= nx < rows and 0 <= ny < cols :
                if self.grid[nx][ny] in [b" ", b"."]: # Not a pacgum or empty
                    self._move_actor(x, y, nx, ny, char)
            else:
                print(f"Error with 0 <= {nx} < {rows} or 0 <= {ny} < {cols } ")



    def _move_actor(self, old_x, old_y, new_x, new_y, char):
        """Helper to update grid and leave a dot behind if necessary."""
        # In EDPac, usually, when an animal moves, it leaves the floor ('.') behind.
        tmp_char = self.grid[new_x][new_y]

        self.grid[old_x][old_y] = tmp_char
        self.grid[new_x][new_y] = char
