from edpac.genetic_algorithm.individual import Individual
from edpac.config.constants import NB_VISIO_INPUTS, VISIO_COLUMN_DEPTH, INITIAL_LIFE_POINTS, NB_LIFE_POINTS_PER_PACGUM, NB_LIFE_POINTS_PER_PREY, MOTOR_THRESHOLD

class Pacman(Individual):
    def __init__(self, x=0, y=0, zoo=None):

        self.x = x
        self.y = y

        self.motor_threshold = MOTOR_THRESHOLD
        self.life_points = INITIAL_LIFE_POINTS
        self.zoo = zoo

        # Directions: 0: Up, 1: Down, 2: Left, 3: Right
        self.dir_body = 3  # Default Right
        self.dir_head = 3  # Default Right

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
            0: (2, 3), # Up -> Left is LEFT, Right is RIGHT
            1: (3, 2), # Down -> Left is RIGHT, Right is LEFT
            2: (1, 0), # Left -> Left is DOWN, Right is UP
            3: (0, 1)  # Right -> Left is UP, Right is DOWN
        }
        left, right = rotation_map[current_dir]
        return left if turn_type == -1 else right

    def integrate_motor_outputs(self, motor_values):
        """
        m0, m1: Head control
        m2, m3: Body control
        """
        if len(motor_values) < 4: return

        # --- 1. HEAD CONTROL ---
        h1 = motor_values[0] > self.motor_threshold
        h2 = motor_values[1] > self.motor_threshold

        if h1 and not h2: # One active: Turn Left
            self.dir_head = self._get_turn(self.dir_head, -1)
        elif h2 and not h1: # One active: Turn Right
            self.dir_head = self._get_turn(self.dir_head, 1)
        elif h1 and h2: # Both active: Realign to Body
            self.dir_head = self.dir_body

        # --- 2. BODY CONTROL ---
        b1 = motor_values[2] > self.motor_threshold
        b2 = motor_values[3] > self.motor_threshold

        if b1 and not b2: # One active: Turn Left
            self.dir_body = self._get_turn(self.dir_body, -1)
        elif b2 and not b1: # One active: Turn Right
            self.dir_body = self._get_turn(self.dir_body, 1)
        elif b1 and b2: # Both active: Move Forward
            self._move_forward()

    def _move_forward(self):
        """Calculates movement based on dir_body and updates grid."""
        # Map dir_body to coordinate changes
        move_map = {0: (0, -1), 1: (0, 1), 2: (-1, 0), 3: (1, 0)}
        dx, dy = move_map[self.dir_body]

        new_x = self.x + dx
        new_y = self.y + dy

        # Check for walls in the Zoo grid before moving
        if 0 <= new_x < len(self.zoo.grid[0]) and 0 <= new_y < len(self.zoo.grid):
            if self.zoo.grid[new_y][new_x] != 'X': # Not a wall
                # Update grid data: old position becomes a dot

                #TODO if this a pacgum, increase life; also contacts with prey and predator?
                if self.zoo.grid[new_y][new_x] == ".":
                    self.life_points = self.life_points + NB_LIFE_POINTS_PER_PACGUM

                    print("Eating pacgum, Life points: " , self.life_points)

                if self.zoo.grid[new_y][new_x] != " ":

                    char = self.zoo.grid[new_y][new_x].decode("utf-8")

                    if self.zoo.animals[char]["danger"] == "1":
                        print("Eating prey, Life points: " , self.life_points)
                        self.life_points = self.life_points + NB_LIFE_POINTS_PER_PREY


                self.zoo.grid[self.y][self.x] = ' '



                self.x, self.y = new_x, new_y
                # New position becomes Pacman
                self.zoo.grid[self.y][self.x] = '0'


    def integrate_visio_outputs(self):
        """
        Scans the zoo grid in a fan shape based on dir_head.
        Returns a list of 5 shapes (lists of pixel coordinates).
        """
        rows = len(self.zoo.grid)
        cols = len(self.zoo.grid[0])

        # 1. Define directional vectors based on dir_head
        # dirX/Y = Forward, dirPerX/Y = Side-step (Perpendicular)

        #0: Up, 1: Down, 2: Left, 3: Right

        # 0: UP, 1: DOWN, 2: LEFT, 3: RIGHT
        if self.dir_head == 0: # HAUT (UP)
            df, ds = (0, -1), (1, 0)
        elif self.dir_head == 1: # BAS (DOWN)
            df, ds = (0, 1), (-1, 0)
        elif self.dir_head == 2: # GAUCHE (LEFT)
            df, ds = (-1, 0), (0, -1)
        elif self.dir_head == 3: # DROITE (RIGHT)
            df, ds = (1, 0), (0, 1)
        else:
            df, ds = (0, 0), (0, 0)

        visio_patterns = []

        # 2. Iterate through each sensory column (i)
        for i in range(NB_VISIO_INPUTS):
            # Calculate column index relative to center (e.g., -2, -1, 0, 1, 2)
            rel_col = i - (NB_VISIO_INPUTS - 1) // 2


            found_shape = None

            # 3. Scan depth (j) in the current column
            # Start depth at abs(rel_col) to create a "V" shaped fan
            for j in range(max(abs(rel_col), 1), VISIO_COLUMN_DEPTH):
                # Calculate grid coordinates: Start + (depth * Forward) + (offset * Side)
                nx = self.x + (j * df[0]) + (rel_col * ds[0])
                ny = self.y + (j * df[1]) + (rel_col * ds[1])

                if (0<=ny and ny < len(self.zoo.grid)) and (0<=ny and nx < len(self.zoo.grid[0])):

                    char = self.zoo.grid[ny][nx].decode("utf-8")

                    if char == '.' or char == ' ' :
                        continue

                    # 4. Check for Objects (Walls or Animals)
                    assert char in self.zoo.animals.keys(), f"Error with {char}"
                    found_shape = self.zoo.animals[char]["shape"].T
                    break

            # If nothing found in this column, it's an empty sensor
            visio_patterns.append(found_shape)

        return visio_patterns
