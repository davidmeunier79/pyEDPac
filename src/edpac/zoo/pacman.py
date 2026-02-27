from edpac.genetic_algorithm.individual import Individual
from edpac.config.constants import NB_VISIO_INPUTS, VISIO_COLUMN_DEPTH

class Pacman(Individual):
    def __init__(self, x=0, y=0, zoo=None):

        self.x = x
        self.y = y

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

    def integrate_visio_outputs(self):
        """
        Scans the zoo grid in a fan shape based on dir_head.
        Returns a list of 5 shapes (lists of pixel coordinates).
        """
        rows = len(self.zoo.grid)
        cols = len(self.zoo.grid[0])

        # 1. Define directional vectors based on dir_head
        # dirX/Y = Forward, dirPerX/Y = Side-step (Perpendicular)
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

                char = self.zoo.grid[ny][nx]

                if char == '.' or char == ' ' :
                    continue

                # 4. Check for Objects (Walls or Animals)
                found_shape = self.zoo.shapes[char]
                break

            # If nothing found in this column, it's an empty sensor
            visio_patterns.append(found_shape)

        return visio_patterns
