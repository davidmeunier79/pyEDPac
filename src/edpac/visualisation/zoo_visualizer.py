import os
import re
import numpy as np
from PIL import Image
from edpac.visualisation.pixel_visualizer import PixelVisualizer
#
# class ZooVisualizer(PixelVisualizer):
#     def __init__(self, width=800, height=600, scale=2, data_dir="data"):
#         # Scale=2 makes the 16x16 icons easier to see on modern screens
#         super().__init__(width, height, scale)
#         self.data_dir = data_dir
#         self.menagerie = {}  # Maps char -> list of (x, y) relative coords
#         self.cell_size = 16  # .img files are 16x16
#
#     def load_menagerie(self, menagerie_file="menagerie/menagerie.txt"):
#         """Reads menagerie.txt and loads the .img file for each animal."""
#         path = os.path.join(self.data_dir, menagerie_file)
#
#         if not os.path.exists(path):
#             print(f"Error: {path} not found.")
#             return
#
#         with open(path, 'r') as f:
#             for line in f:
#                 print(line)
#                 parts = line.split()
#                 if len(parts) >= 2:
#                     char = parts[0]
#                     # Convert XBM extension to .img if necessary
#                     img_rel_path = parts[1]
#                     self.menagerie[char] = self._get_img_coords(img_rel_path)
#
#         # --- Manual 'dot' assignment for the '.' character ---
#         dot_path = os.path.join(self.data_dir, "formes", "dot")
#         self.menagerie['.'] = self._parse_xbm_hex(dot_path)
#
#         print(self.menagerie)
#
#     def _parse_xbm_hex(self, full_path):
#         """
#         Skips C headers, finds the { ... } block, and
#         unpacks the hex data into (x, y) coordinates.
#         """
#         coords = []
#         try:
#             with open(full_path, 'r') as f:
#                 content = f.read()
#
#             # 1. Use regex to find everything between { and }
#             match = re.search(r'\{(.*?)\}', content, re.DOTALL)
#             if not match:
#                 return []
#
#             # 2. Extract hex strings (e.g., '0x01') and convert to integers
#             hex_data = match.group(1).replace('\n', '').split(',')
#             bytes_list = [int(h.strip(), 16) for h in hex_data if h.strip()]
#
#             # 3. Unpack bits (16x16 XBM = 2 bytes per row)
#             # Row 0 uses bytes_list[0] and [1], Row 1 uses [2] and [3], etc.
#             for row in range(16):
#                 for byte_idx in range(2):
#                     byte_val = bytes_list[row * 2 + byte_idx]
#                     for bit in range(8):
#                         # XBM bits are LSB first (Least Significant Bit)
#                         if (byte_val >> bit) & 1:
#                             x = (byte_idx * 8) + bit
#                             y = row
#                             coords.append((x, y))
#         except Exception as e:
#             print(f"Error parsing hex XBM {full_path}: {e}")
#         return coords
#
#     def _get_img_coords(self, rel_path):
#         """Parses a 16x16 text file of '0' and '1' into coordinates."""
#         full_path = os.path.join(self.data_dir, "menagerie", rel_path)
#         coords = []
#         try:
#             with open(full_path, 'r') as f:
#                 for y, line in enumerate(f):
#                     print(line)
#                     # Only process the first 16 characters to avoid newlines/spaces
#                     for x, bit in enumerate(line.strip()[:16]):
#                         if bit == '.': # '1' represents the animal pixel
#                             coords.append((x, y))
#         except Exception as e:
#             print(f"Could not load img {full_path}: {e}")
#         return coords
#
#
#     def draw_screen(self, screen_file="screens/screen.tmp"):
#         """Reads a screen file and stamps patterns into the buffer."""
#         path = os.path.join(self.data_dir, screen_file)
#         self.clear_canvas((255, 255, 255)) # Dark background
#
#         with open(path, 'r') as f:
#             for row_idx, line in enumerate(f):
#                 for col_idx, char in enumerate(line.strip()):
#                     if char in self.menagerie:
#                         # Calculate top-left pixel for this grid cell
#                         start_x = col_idx * self.cell_size
#                         start_y = row_idx * self.cell_size
#
#                         # Stamp each pixel of the animal pattern
#                         for px, py in self.menagerie[char]:
#                             self.set_pixel(start_x + px, start_y + py, (200, 200, 255))
#
#         self.update_display()

from edpac.zoo.zoo import Zoo

class ZooVisualizer(PixelVisualizer):
    def draw_zoo(self, zoo: Zoo):
        self.clear_canvas((255, 255, 255)) # Deep black background

        for row_idx, row in enumerate(zoo.grid):
            for col_idx, char in enumerate(row):
                if char in zoo.shapes:
                    base_x = col_idx * zoo.cell_size
                    base_y = row_idx * zoo.cell_size

                    #color = (0, 0, 0)

                    # Color Logic
                    if char == '.' or char == 'X':
                        color = (80, 80, 80)    # Dim gray for dots
                    elif char == '0':
                        color = (255, 255, 0)   # Yellow for Pacman
                    elif zoo.danger[char] == '1':
                        color = (0, 0, 255) # Blue for preys
                    elif zoo.danger[char] == '-1':
                        color = (255, 0, 0) # Red for predators

                    for px, py in zoo.shapes[char]:
                        self.set_pixel(base_x + px, base_y + py, color)

        self.update_display()
