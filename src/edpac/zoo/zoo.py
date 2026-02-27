import os
import re

class Zoo:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.shapes = {}  # char -> list of (x, y), dangerosity
        self.grid = []    # 2D list of characters
        self.cell_size = 20
        self.danger = {}

    def _parse_xbm_hex(self, full_path):
        """Unpacks C-style XBM hex data into coordinates."""
        coords = []
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
                            coords.append(((byte_idx * 8) + bit + 2, row + 2))

        except Exception as e:
            print(f"Error parsing {full_path}: {e}")



        return coords

    def _parse_img_file(self, full_path):
        """Parses the 16x16 '0/1' text files."""
        coords = []
        try:
            with open(full_path, 'r') as f:
                for y, line in enumerate(f):
                    for x, bit in enumerate(line.strip()):
                        if bit == '.': coords.append((x, y))
        except Exception: pass

        print(coords)

        return coords

    def load_everything(self, screen_file="screen.0", menagerie_file= "menagerie.txt"):
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

        # 3. Load Menagerie (animals)
        men_path = os.path.join(self.data_dir, "menagerie", menagerie_file)
        with open(men_path, 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) == 3:
                    char, rel_path = parts[0], parts[1]
                    self.shapes[char] = self._parse_img_file(os.path.join(self.data_dir, "menagerie", rel_path))
                    self.danger[char] = parts[2]

        # 4. Load Screen
        screen_path = os.path.join(self.data_dir, "screens", f"{screen_file}")
        with open(screen_path, 'r') as f:
            self.grid = [list(line.strip()) for line in f]
