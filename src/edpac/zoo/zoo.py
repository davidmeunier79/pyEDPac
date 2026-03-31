import os
import re
import string
import random
from math import floor
import numpy as np
import pathlib

from edpac.config.constants import VISIO_SQRT_NB_NEURONS, NB_VISIO_INPUTS

from .chars import char_to_index, index_to_char
from .pacman import Pacman, Direction

class Zoo:
    def __init__(self,
                 cell_size=VISIO_SQRT_NB_NEURONS):

        self.cell_size = cell_size
        self.rows = 0
        self.cols = 0
        self.grid = None  # Now a NumPy array

        #self.shapes = {}
        #self.danger = {}
        self.animals = {}

        self.data_dir = self._get_data_dir()

        self.nb_deads = 0

        #
        # # Mapping for clarity
        # self.WALL = 'X'
        # self.EMPTY = ' '
        # self.DOT = '.'


    def _get_data_dir(self):

        # 1. Get the absolute path of constants.py
        current_file = pathlib.Path(__file__).resolve()

        # 2. Go up the folder tree to find the project root
        # (In your case: constants.py -> config/ -> edpac/ -> src/ -> ROOT)
        # Adjust the number of .parent calls to match your actual structure
        PROJECT_ROOT = current_file.parent.parent.parent.parent

        data_dir = os.path.join(PROJECT_ROOT, "data")
        return data_dir
    #
    # def _get_pacman_pos(self):
    #     """Locates Pacman ('0') on the grid."""
    #     x, y = np.where(self.grid == b'0')
    #
    #     if len(x) == 1 and len(y) == 1:
    #         return x[0], y[0]
    #     else:
    #         print("Warning, could not find pacman in zoo")
    #         print(self.grid)
    #         0/0
    #         return 0, 0

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
            self.grid = np.zeros((self.rows, self.cols), dtype=bytes)

            for r, line in enumerate(f.readlines()):
                for c, char in enumerate(line.strip()):
                    self.grid[r, c] = char

    def _move_forward(self, pacman_index):
        """Calculates movement based on dir_body and updates grid."""
        # Map dir_body to coordinate changes
        move_map = {Direction.UP: (0, -1), Direction.DOWN: (0, 1), Direction.LEFT: (-1, 0), Direction.RIGHT: (1, 0)}

        pac = self.population.individuals[pacman_index]

        dx, dy = move_map[pac.dir_body]


        new_x = pac.x + dx
        new_y = pac.y + dy

        #print(f"Testing Moves from ({self.y}, {self.x}) to ({new_y}, {new_x})")

        #rows, cols = self.grid.shape

        # Check for walls in the Zoo grid before moving

        if 0 <= new_y < self.rows and 0 <= new_x < self.cols:

        #if 0 <= new_x < cols and 0 <= new_y < rows: # old version

            target_char = self.grid[new_y][new_x].decode("utf-8")

            if target_char != 'X': # Not a wall

                # Update grid data: old position becomes a dot
                # if this a pacgum, increase life
                if target_char == ".":
                    print("Eating pacgum, Life points: " , pac.life_points)
                    pac.eat_pacgum()

                elif target_char == " ":
                    pass
                    #print("Moving forward in empty space")

                else:
                    index = char_to_index(target_char)
                    animal = index % 2

                    print(f"**** Pacman {pacman_index } in contact with {target_char} ({index=})")

                    if self.animals[animal]["danger"] == "1" and pac.animal_nature == "-1":

                        print("Biting prey ", self.animals[animal]["name"], ", Life points: " , pac.life_points)
                        self.population.individuals[index].is_bitten()

                        if self.population.individuals[index].life_points < 0:
                            print("Eating prey ", self.animals[animal]["name"], ", Life points: " , pac.life_points)
                            pac.eat_prey()
                            self.population.individuals[index].process_death()



                    elif self.animals[animal]["danger"] == "-1" and pac.animal_nature == "1":
                        print("Predator ", self.animals[animal]["name"], "cannot be eaten !!!! ")
                        return

                self.grid[pac.y][pac.x] = b' '
                pac.x, pac.y = new_x, new_y

                # New position becomes Pacman
                self.grid[pac.y][pac.x] = pacman_index

    def integrate_visio_outputs(self, pac):
        """
        Scans the zoo grid in a fan shape based on dir_head.
        Returns a list of 5 shapes (lists of pixel coordinates).
        """
        #rows, cols = self.grid.shape

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

                if (0<=ny and ny < self.rows) and (0<=nx and nx < self.cols):

                    char = self.grid[ny][nx].decode("utf-8")

                    if char == '.' or char == ' ' or char == 'X':
                        continue

                    else:
                        index = char_to_index(char)

                    animal = index % 2
                    #print(self.animals.keys())

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


    def test_pacman_contacts(self):

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for pacman_index, pac in enumerate(self.population.individuals):
            #print(pac)
            if pac==0:
                continue

            x, y = pac.get_position()

            rows, cols = self.grid.shape

            for dir_x, dir_y in directions:
                if 0 <= x + dir_x < rows and 0 <= y + dir_y < cols:

                    char_contact = self.grid[x + dir_x][y + dir_y].decode("utf-8")

                    if char_contact in (".", " ", 'X') :
                        continue

                    else:
                        contact_index = char_to_index(char_contact)

                    animal = contact_index % 2

                    if self.animals[animal]["danger"] == "-1" and pac.animal_nature == "1":
                        pac.predator_contact()
                        print("Contact with predator ", self.animals[animal]["name"], " Life points: " , pac.life_points)

                    elif self.animals[animal]["danger"] == "-1" and pac.animal_nature == "-1":
                        print(f"Testing reproduction between predators {contact_index} and {pacman_index}")
                        self.test_predator_reproduction(contact_index, pacman_index)


                    elif self.animals[animal]["danger"] == "1" and pac.animal_nature == "1":
                        print(f"Testing reproduction between preys {contact_index} and {pacman_index}")
                        self.test_prey_reproduction(contact_index, pacman_index)

            if pac.life_points < 0:
                #self.init_new_individual(pacman_index)
                self.process_death(pacman_index)

        print(f"******************** {self.nb_deads=} ***********************")


    def process_death(self, pacman_index):
        #TODO
        print(f"TODO process_death of indiv {pacman_index=}")
        if self.population.individuals[pacman_index] == 0:
            print(f"Pacman {pacman_index=} is already removed")
            return

        # remove from zoo
        x, y = self.population.individuals[pacman_index].get_position()
        self.grid[y, x] = " "
        #remove from list_indivuals
        self.population.individuals[pacman_index] = 0
        #print(self.population.individuals)

        self.nb_deads += 1
        print(f"******************** {self.nb_deads=} ***********************")
