import numpy as np

from edpac.genetic_algorithm.individual import Individual

from edpac.config.ga_config import ChromosomeConfig
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

class AnimalNature(IntEnum):
    """
    Énumération des Natures Animales


    Convention:
    - 0 = UP (Haut, y diminue)
    - 1 = DOWN (Bas, y augmente)
    - 2 = LEFT (Gauche, x diminue)
    - 3 = RIGHT (Droite, x augmente)
    """
    PREY = 1
    PREDATOR = -1
    NEUTRAL = 0

    def to_string(self) -> str:
        """Convertir Direction en string"""
        names = {
            AnimalNature.PREY: "PREY",

            AnimalNature.PREDATOR: "PREDATOR",

            AnimalNature.NEUTRAL: "NEUTRAL",
        }
        return names[self]

class Pacman(Individual):
    def __init__(self , x=0, y=0, pacman_config : PacmanConfig = None, chromo_config : ChromosomeConfig = None,  genes: np.ndarray = None):


        self.pacman_config = pacman_config or PacmanConfig()

        #self.chromo_config = chromo_config or ChromosomeConfig()

        self.animal_nature = 0

        super().__init__(chromo_config, genes)
        self.x = x
        self.y = y

        self.motor_threshold = self.pacman_config.MOTOR_THRESHOLD

        self.life_points = self.pacman_config.INITIAL_LIFE_POINTS
        #self.zoo = zoo

        # Directions: 0: Up, 1: Down, 2: Left, 3: Right
        self.dir_body = Direction.RIGHT  # Default Right
        self.dir_head = Direction.RIGHT  # Default Right

        self.stats = {"nb_eaten_preys": 0, "nb_eaten_pacgums": 0, "nb_contact_predators": 0,
                      "nb_move_forward": 0, "nb_body_turns": 0,
                      "nb_head_forward": 0, "nb_head_turns": 0,
                      'nb_bites': 0
                      }

    def set_animal_nature(self, animal_nature):
        self.animal_nature = animal_nature

    def get_animal_nature(self):
        return self.animal_nature

    def get_position(self):
        return (self.x, self.y)

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
        if self.animal_nature == "1":
            self.life_points -= self.pacman_config.NB_LIFE_POINTS_PER_PREDATOR_CONTACT
            self.stats["nb_contact_predators"] += 1

        else:
            print(f"!!!!!! Warning, animal with nature = {self.animal_nature} is having predator_contact")

    def eat_pacgum(self):
        if self.animal_nature == "1":
            self.life_points += self.pacman_config.NB_LIFE_POINTS_PER_PACGUM_PREY
            
        elif self.animal_nature == "-1":
            self.life_points += self.pacman_config.NB_LIFE_POINTS_PER_PACGUM_PREY

        self.stats["nb_eaten_pacgums"] += 1

    def eat_prey(self):
        if animal_nature == "-1":
            self.life_points += self.pacman_config.NB_LIFE_POINTS_PER_PREY
            self.stats["nb_eaten_preys"] += 1
        else:
            print(f"!!!!!! Warning, animal with nature = {animal_nature} eats a prey")

    def is_bitten(self):
        if self.animal_nature == "1":
            self.life_points -= self.pacman_config.NB_LIFE_POINTS_PER_BITE
            self.stats["nb_bites"] += 1
        else:
            print(f"!!!!!! Warning, animal with nature = {self.animal_nature} is bitten")

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


        # --- 1. HEAD CONTROL ---
        # m0 = Turn Left, m1 = Turn Right
        h_left = motor_values[0] > self.motor_threshold
        h_right = motor_values[1] > self.motor_threshold

        if h_left and not h_right:
            # Turn head left
            self.dir_head = self._get_turn(self.dir_head, -1)
            new_dir_head = Direction(self.dir_head).to_string()
            #print(f"Turn head left")
            self.stats["nb_head_turns"] += 1

        elif h_right and not h_left:
            # Turn head right
            self.dir_head = self._get_turn(self.dir_head, 1)
            new_dir_head = Direction(self.dir_head).to_string()
            #print(f"Turn head right ")
            self.stats["nb_head_turns"] += 1

        elif h_left and h_right:
            # Both active: Realign head to body
            self.dir_head = self.dir_body
            #print("Realign head to body")
            self.stats["nb_head_forward"] += 1

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
            #print(f"Turn body left ")
            self.stats["nb_body_turns"] += 1

        elif b_right and not b_left:
            # Turn body right
            self.dir_body = self._get_turn(self.dir_body, 1)

            new_dir_body = Direction(self.dir_body).to_string()
            #print(f"Turn body right")
            self.stats["nb_body_turns"] += 1

        elif b_left and b_right:
            # Both active: Move forward

            print("**** Move Forward **** ")
            self.stats["nb_move_forward"] += 1
            return 1

        return 0

    def save_stats(self,indiv_path=0):
        import json
        import os

        if indiv_path==0:
            indiv_path = os.path.abspath("")

        file_stats = os.path.join(indiv_path, "Stats_pacman.json")

        with open(file_stats, 'w+') as fp:
            json.dump(self.stats, fp, indent=4)
