from edpac.genetic_algorithm.individual import Individual

from edpac.config.constants import NB_VISIO_INPUTS

from edpac.config.zoo_config import PacmanConfig
from enum import IntEnum

class Direction(IntEnum):
    """
    Énumération des 4 directions cardinales

    Convention:
    - 0 = UP (Haut, y diminue)
    - 1 = DOWN (Bas, y augmente)
    - 2 = LEFT (Gauche, x diminue)
    - 3 = RIGHT (Droite, x augmente)
    """
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    def to_string(self) -> str:
        """Convertir Direction en string"""
        names = {
            Direction.UP: "UP",
            Direction.DOWN: "DOWN",
            Direction.LEFT: "LEFT",
            Direction.RIGHT: "RIGHT"
        }
        return names[self]





class Pacman(Individual):
    def __init__(self, x=0, y=0, zoo=None, config : PacmanConfig = None):

        self.config = config or PacmanConfig()
        self.x = x
        self.y = y

        self.motor_threshold = self.config.MOTOR_THRESHOLD
        self.life_points = self.config.INITIAL_LIFE_POINTS
        self.zoo = zoo

        # Directions: 0: Up, 1: Down, 2: Left, 3: Right
        self.dir_body = Direction.RIGHT  # Default Right
        self.dir_head = Direction.RIGHT  # Default Right

        self.stats = {"nb_eaten_preys": 0, "nb_eaten_pacgums": 0, "nb_contact_predators": 0,
                      "nb_move_forward": 0, "nb_body_turns": 0,
                      "nb_head_forward": 0, "nb_head_turns": 0
                      }

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_directions(self, body, head):
        self.dir_body = body
        self.dir_head = head

    def _get_turn(self, current_dir, turn_type):
        """
        Calculates 90-degree turn.
        turn_type: -1 for Left, 1 for Right
        Directions: 0:UP, 1:DOWN, 2:LEFT, 3:RIGHT
        """
        # Mapping: {current: (turn_left, turn_right)}
        rotation_map = {
            Direction.UP: (Direction.LEFT, Direction.RIGHT), # Up -> Left is LEFT, Right is RIGHT
            Direction.DOWN: (Direction.RIGHT, Direction.LEFT), # Down -> Left is RIGHT, Right is LEFT
            Direction.LEFT: (Direction.DOWN, Direction.UP), # Left -> Left is DOWN, Right is UP
            Direction.RIGHT: (Direction.UP, Direction.DOWN)  # Right -> Left is UP, Right is DOWN
        }
        left, right = rotation_map[current_dir]
        return left if turn_type == -1 else right

    def predator_contact(self):
        self.life_points -= self.config.NB_LIFE_POINTS_PER_PREDATOR

        self.stats["nb_eaten_preys"] += 1

    def eat_pacgum(self):
        self.life_points += self.config.NB_LIFE_POINTS_PER_PACGUM
        self.stats["nb_eaten_pacgums"] += 1

    def eat_prey(self):
        self.life_points += self.config.NB_LIFE_POINTS_PER_PREY
        self.stats["nb_eaten_preys"] += 1


    def integrate_motor_outputs(self, motor_values):
        """
        Traiter les outputs moteurs du réseau

        motor_values[0] (m0): Head LEFT control
        motor_values[1] (m1): Head RIGHT control
        motor_values[2] (b1): Body LEFT control
        motor_values[3] (b2): Body RIGHT control

        ✅ FIXED: Indexing et logique correcte
        """
        if len(motor_values) < 4:
            return

        # --- 2. BODY CONTROL ---
        # b1 = Turn Left, b2 = Turn Right
        b_left = motor_values[2] > self.motor_threshold
        b_right = motor_values[3] > self.motor_threshold

        old_dir_body = Direction(self.dir_body).to_string()
        old_dir_head = Direction(self.dir_head).to_string()

        if b_left and not b_right:
            # Turn body left

            self.dir_body = self._get_turn(self.dir_body, -1)
            new_dir_body = Direction(self.dir_body).to_string()
            #print(f"Turn body left from {old_dir_body} to {new_dir_body}")

            self.stats["nb_body_turns"] += 1

        elif b_right and not b_left:
            # Turn body right
            self.dir_body = self._get_turn(self.dir_body, 1)

            new_dir_body = Direction(self.dir_body).to_string()
            #print(f"Turn body right from {old_dir_body} to {new_dir_body}")

            self.stats["nb_body_turns"] += 1

        elif b_left and b_right:
            # Both active: Move forward

            self._move_forward()
            #print("Move Forward")
            self.stats["nb_move_forward"] += 1

        # --- 1. HEAD CONTROL ---
        # m0 = Turn Left, m1 = Turn Right
        h_left = motor_values[0] > self.motor_threshold
        h_right = motor_values[1] > self.motor_threshold

        if h_left and not h_right:
            # Turn head left
            self.dir_head = self._get_turn(self.dir_head, -1)
            new_dir_head = Direction(self.dir_head).to_string()
            #print(f"Turn head left from {old_dir_head} to {new_dir_head}")
            self.stats["nb_head_turns"] += 1

        elif h_right and not h_left:
            # Turn head right
            self.dir_head = self._get_turn(self.dir_head, 1)
            new_dir_head = Direction(self.dir_head).to_string()
            #print(f"Turn head right from {old_dir_head} to {new_dir_head}")
            self.stats["nb_head_turns"] += 1

        elif h_left and h_right:
            # Both active: Realign head to body
            self.dir_head = self.dir_body
            #print("Realign head to body")
            self.stats["nb_head_forward"] += 1

    def _move_forward(self):
        """Calculates movement based on dir_body and updates grid."""
        # Map dir_body to coordinate changes
        move_map = {Direction.UP: (0, -1), Direction.DOWN: (0, 1), Direction.LEFT: (-1, 0), Direction.RIGHT: (1, 0)}
        dx, dy = move_map[self.dir_body]

        new_x = self.x + dx
        new_y = self.y + dy

        #print(f"Testing Moves from ({self.y}, {self.x}) to ({new_y}, {new_x})")

        rows, cols = self.zoo.grid.shape

        # Check for walls in the Zoo grid before moving
        if 0 <= new_x < cols and 0 <= new_y < rows:

            if self.zoo.grid[new_y][new_x] != b'X': # Not a wall

                # Update grid data: old position becomes a dot
                # if this a pacgum, increase life
                if self.zoo.grid[new_y][new_x] == b".":
                    self.eat_pacgum()
                    #print("Eating pacgum, Life points: " , self.life_points)

                elif self.zoo.grid[new_y][new_x] == b" ":
                    pass
                    #print("Moving forward in empty space")

                else:
                    char = self.zoo.grid[new_y][new_x].decode("utf-8")

                    if self.zoo.animals[char]["danger"] == "1":
                        self.eat_prey()
                        print("Eating prey ", self.zoo.animals[char]["name"], ", Life points: " , self.life_points)

                    elif self.zoo.animals[char]["danger"] == "-1":
                        print("Predator ", self.zoo.animals[char]["name"], "cannot be eaten !!!! ")
                        return

                self.zoo.grid[self.y][self.x] = b' '
                self.x, self.y = new_x, new_y

                # New position becomes Pacman
                self.zoo.grid[self.y][self.x] = b'0'


    def integrate_visio_outputs(self):
        """
        Scans the zoo grid in a fan shape based on dir_head.
        Returns a list of 5 shapes (lists of pixel coordinates).
        """

        rows, cols = self.zoo.grid.shape
            ## scanning laterally from higher to lower if dir_head = UP or LEFT ds > 0
            ## scanning laterally from lower to higher if dir_head = DOWN or RIGHT ds < 0

        ### scanning depth from lower to higher if dir_head = UP or RIGHT: df > 0
        ### scanning depth from higher to lower if dir_head = DOWN or LEFT df < 0

        # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        if self.dir_head == Direction.UP: # HAUT (UP)
            df, ds = (0, 1), (1, 0)
        elif self.dir_head == Direction.DOWN: # BAS (DOWN)
            df, ds = (0, -1), (-1, 0)
        elif self.dir_head == Direction.LEFT: # GAUCHE (LEFT)
            df, ds = (-1, 0), (0, 1)
        elif self.dir_head == Direction.RIGHT: # DROITE (RIGHT)
            df, ds = (1, 0), (0, -1)

        visio_patterns = []

        # 2. Iterate through each sensory column (i)
        for i in range(NB_VISIO_INPUTS):

            # Calculate column index relative to center (e.g., -2, -1, 0, 1, 2)
            rel_col = i - (NB_VISIO_INPUTS - 1) // 2

            found_shape = None

            # 3. Scan depth (j) in the current column
            # Start depth at abs(rel_col) to create a "V" shaped fan
            for j in range(max(abs(rel_col), 1), self.config.VISIO_COLUMN_DEPTH+1):
                # Calculate grid coordinates: Start + (depth * Forward) + (offset * Side)
                nx = self.x + (j * df[0]) + (rel_col * ds[0])
                ny = self.y + (j * df[1]) + (rel_col * ds[1])

                if (0<=ny and ny < rows) and (0<=nx and nx < cols):

                    char = self.zoo.grid[ny][nx].decode("utf-8")

                    if char == '.' or char == ' ' :
                        continue

                    # 4. Check for Objects (Walls or Animals)
                    assert char in self.zoo.animals.keys(), f"Error with {char}"

                    found_shape = self.blur_pattern(self.zoo.animals[char]["shape"], float(abs(j))/self.config.VISIO_COLUMN_DEPTH * self.config.BLURRED_FACTOR)

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

    def save_stats(self,indiv_path=0):
        import json

        self.stats["fitness"] = self.get_fitness()
        self.stats["nb_genes"] = self.get_nb_genes()

        if indiv_path==0:
            indiv_path = os.path.abspath("")

        file_stats = os.path.joint(indiv_path, "Stats_pacman.json")

        with open(file_stats, 'w+') as fp:
            json.dump(self.stats, fp, indent=4)

