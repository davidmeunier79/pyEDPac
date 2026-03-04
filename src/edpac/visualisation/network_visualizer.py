import numpy as np
from math import sqrt

from edpac.ed_network.network import Network # Assuming your repo structure
from edpac.config.constants import *

from .pixel_visualizer import PixelVisualizer

class NetworkVisualizer(PixelVisualizer):
    def __init__(self, height, width):
        super().__init__(height, width, title="Neural Activity")
        self.neuron_mask = np.ones((1, 1), dtype=np.uint8) # 1x1 pixel or larger

    def setup_topology(self, neuron_positions):
        """Draw all neurons as DIM dots in the background."""
        self.set_background_color((10, 10, 20))
        for x, y in neuron_positions:
            self.set_pattern(y, x, self.neuron_mask, (60, 60, 60), target_buffer=self.background)

    def display_spikes(self, spike_indices, neuron_positions):
        """
        Clean the frame using the background (dim neurons)
        then draw ONLY current spikes in bright yellow.
        """
        self.refresh_from_background()

        yellow = (255, 255, 0)
        for idx in spike_indices:
            if idx < len(neuron_positions):
                x, y = neuron_positions[idx]
                self.set_pattern(y, x, self.neuron_mask, yellow)

        self.update_display()
