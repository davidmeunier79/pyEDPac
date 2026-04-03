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

        self._grid = None  # Now a NumPy array

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

    def _move_forward(self, pacman_index):
        """Calculates movement based on dir_body and updates grid."""
        # Map dir_body to coordinate changes
        #move_map = {Direction.UP: (0, -1), Direction.DOWN: (0, 1), Direction.LEFT: (-1, 0), Direction.RIGHT: (1, 0)}
        move_map = {Direction.DOWN: (0, -1), Direction.UP: (0, 1), Direction.LEFT: (-1, 0), Direction.RIGHT: (1, 0)}

        pac = self.population.individuals[pacman_index]

        dx, dy = move_map[pac.dir_body]

        new_x = pac.x + dx
        new_y = pac.y + dy

        target_char = self._in_grid(new_x, new_y)

        if not target_char:
            print(f"******* could not move {pacman_index=} forward, {new_x=}, {new_y=} leads to error")
            return

        if target_char == 'X': # Not a wall

            print(f"******* could not move {pacman_index=} forward, {new_x=}, {new_y=} is a wall")
            return

        # Update grid data: old position becomes a dot
        # if this a pacgum, increase life
        if target_char == ".":
            print("Eating pacgum, Life points: " , pac.life_points)
            pac.eat_pacgum()

        elif target_char != " ":

            index = char_to_index(target_char)
            animal = index % 2

            print(f"**** Pacman {pacman_index } in contact with {target_char} ({index=})")

            if self.animals[animal]["danger"] == "1" and pac.animal_nature == "-1":
                #
                # print("Biting prey ", self.animals[animal]["name"], ", Life points: " , pac.life_points)
                # self.population.individuals[index].is_bitten()

                print("Before Eating prey ", self.animals[animal]["name"], ", Life points: " , pac.life_points)
                pac.eat_prey(self.population.individuals[index].life_points)
                print("Eating prey ", self.animals[animal]["name"], ", Life points: " , pac.life_points)
                self.process_death(index)



            else:
                print("Same nature animal , cannot be eaten , we are no cannibals! "
                return

        self._set_in_grid(pac.x, pac.y, ' ')

        # New position becomes Pacman
        self._set_in_grid(new_x, new_y, index_to_char(pacman_index))

        pac.set_position(new_x, new_y)


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


    def all_move_forward(self, turn_dir = 1):

        for pacman_index, pac in enumerate(self.population.individuals):
            #print(pac)
            if pac==0:
                continue

            self._move_forward(pacman_index)

    def turn_all_body(self, turn_dir = 1):

        for pacman_index, pac in enumerate(self.population.individuals):
            #print(pac)
            if pac == 0:
                continue

            pac.dir_body = pac._get_turn(pac.dir_body, turn_dir)


    def turn_all_heads(self, turn_dir = 1):

        for pacman_index, pac in enumerate(self.population.individuals):
            #print(pac)
            if pac==0:
                continue

            pac.dir_head = pac._get_turn(pac.dir_head, turn_dir)


    def _in_grid(self, pos_x, pos_y):
        if 0 <= pos_x < self.cols and 0 <= pos_y < self.rows:
            char = self._grid[pos_y][pos_x].decode("utf-8")
            return char
        #
        # elif 0 <= pos_y < self.cols and 0 <= pos_x < self.rows:
        #     print(f"**** Warning, accessing {pos_x=},{pos_y=} in reverse order in grid ****")
        #     char = self._grid[pos_x][pos_y].decode("utf-8")
        #     return char

        #print(f"Error, could not find position {pos_x} {pos_y}")
        return 0


    def _set_in_grid(self, pos_x, pos_y, char):
        if 0 <= pos_x < self.cols and 0 <= pos_y < self.rows:
            self._grid[pos_y][pos_x] = char
        else:
            print(f"Error, could not add {char} at position {pos_x} {pos_y}")
        #
        # elif 0 <= pos_y < self.cols and 0 <= pos_x < self.rows:
        #     print(f"**** Warning, accessing {pos_x=},{pos_y=} in reverse order in grid ****")
        #     self._grid[pos_x][pos_y] = char

    def _where_in_grid(self, char):
        if char in np.unique(self._grid):
            yy, xx = np.where(self._grid == char)
            return yy, xx
        else:
            print(f"Error, {char=} could not be found in _grid")
            return (-1, -1)

    def _compute_test_contats(self, pair_contacts):

        print(pair_contacts)

        # remove if one_indiv is dead in the pair
        checked_pair_contacts = [pair for pair in pair_contacts if (self.population.individuals[pair[0]]!= 0 and self.population.individuals[pair[1]]!=0)]

        checked_pair_contacts.sort(key=lambda pair: self.population.individuals[pair[0]].get_fitness() + self.population.individuals[pair[0]].get_fitness(), reverse=True)

        print(checked_pair_contacts)

        for pac1, pac2, nature in pair_contacts:
            if nature == "1":
                self.test_prey_reproduction(pac1, pac2)

            elif nature == "-1":
                self.test_predator_reproduction(pac1, pac2)

    def test_pacman_contacts(self):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1)]

        pair_contacts = []


        for pacman_index, pac in enumerate(self.population.individuals):
            if pac==0:
                continue

            #print(pac)

            x, y = pac.get_position()

            for dir_x, dir_y in directions:

                char_contact = self._in_grid(x + dir_x,  y + dir_y)
                if not char_contact:
                    continue

                if char_contact in (".", " ", 'X') :
                    continue

                else:
                    contact_index = char_to_index(char_contact)

                animal = contact_index % 2

                if self.animals[animal]["danger"] == "-1" and pac.animal_nature == "1":
                    #print(f"Contact with predator {self.animals[animal]["name"]}, Life points: {pac.life_points}")
                    pac.predator_contact()

                elif self.animals[animal]["danger"] == "-1" and pac.animal_nature == "-1":
                    #print(f"Testing reproduction between predators {contact_index} and {pacman_index}")
                    pair_contacts.append((contact_index, pacman_index, "-1"))

                    #self.test_predator_reproduction(contact_index, pacman_index)

                elif self.animals[animal]["danger"] == "1" and pac.animal_nature == "1":
                    #print(f"Testing reproduction between preys {contact_index} and {pacman_index}")

                    pair_contacts.append((contact_index, pacman_index, "1"))
                    #self.test_prey_reproduction(contact_index, pacman_index)
                else:
                    pass
                    #print(f"Nothing particular between  {self.animals[animal]["danger"]} and {pac.animal_nature}")


            # naturally losing life each time points
            pac.life_points -= 1

            if pac.life_points < 0:
                #self.init_new_individual(pacman_index)
                self.process_death(pacman_index)
            else:
                pac.fitness = pac.life_points
                pac.fitness_evaluated = True


        self._compute_test_contats(pair_contacts)


        return len([pac for pac in self.population.individuals if pac])

    def process_death(self, pacman_index):
        #print(f"process_death of indiv {pacman_index=}")
        if self.population.individuals[pacman_index] == 0:
            #print(f"Pacman {pacman_index=} is already removed")
            return

        # remove from zoo
        x, y = self.population.individuals[pacman_index].get_position()
        self._set_in_grid(x, y, " ")

        #remove from list_indivuals
        self.population.individuals[pacman_index] = 0

        # increment nb_deads
        self.nb_deads += 1

