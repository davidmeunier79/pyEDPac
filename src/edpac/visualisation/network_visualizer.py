import numpy as np
from math import sqrt

from edpac.ed_network.network import Network # Assuming your repo structure
from edpac.config.constants import *

from .pixel_visualizer import PixelVisualizer

class NetworkVisualizer(PixelVisualizer):
    def __init__(self, title="Neural Activity", scale=1):

        width = VISIO_SQRT_NB_NEURONS+GAP_INPUT_ASSEMBLY + SQRT_NB_ASSEMBLIES*(SQRT_NB_NEURONS+GAP_HIDDEN_ASSEMBLY) + GAP_OUTPUT_ASSEMBLY+MOTOR_SQRT_NB_NEURONS

        height = max((VISIO_SQRT_NB_NEURONS+GAP_INPUT_ASSEMBLY)*NB_INPUT_ASSEMBLIES,
                     SQRT_NB_ASSEMBLIES*(SQRT_NB_NEURONS+GAP_HIDDEN_ASSEMBLY),
                     (MOTOR_SQRT_NB_NEURONS+GAP_OUTPUT_ASSEMBLY)*NB_OUTPUT_ASSEMBLIES)


        super().__init__( height=height, width=width,title=title, scale=scale)

        self.neuron_positions = {}
        self.neuron_mask = np.ones((1, 1), dtype=np.uint8) # 1x1 pixel or larger

    def draw_assembly(self, assembly, x_offset, y_offset ):

        for i, neuron_id in enumerate(assembly.get_neuron_ids()):

            sqrt_num_neurons = sqrt(assembly.get_nb_neurons())

            x =  int(x_offset + i%sqrt_num_neurons) # Slight jitter for visibility
            y =  int(y_offset + (i // sqrt_num_neurons))
            self.neuron_positions[neuron_id] = (x, y)

    def init_network(self, network: Network):
        """Processes the Network object and lays it out in columns."""
        #self.clear()

        # Define column X-coordinates
        cols = {'input': 0,
                'hidden': VISIO_SQRT_NB_NEURONS+GAP_INPUT_ASSEMBLY,
                "output": VISIO_SQRT_NB_NEURONS+GAP_INPUT_ASSEMBLY + SQRT_NB_ASSEMBLIES*(SQRT_NB_NEURONS+GAP_HIDDEN_ASSEMBLY) + GAP_OUTPUT_ASSEMBLY
                }

        # 1. Calculate positions for every neuron in every assembly
        # input
        x_base = cols['input']

        print("Draw input_assemblies")
        for a, assembly in enumerate(network.input_assemblies):
            # Determine column based on assembly name or attribute
            # Adjust this logic if you have a specific 'type' attribute

            # Layout neurons vertically within the assembly
            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))
            y_offset = a * sqrt_num_neurons
            self.draw_assembly(assembly, x_base, y_offset )

        # hidden
        print("Draw hidden_assemblies")
        x_base = cols['hidden']

        for a, assembly in enumerate(network.hidden_assemblies):

            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))

            x_a = a % SQRT_NB_ASSEMBLIES
            y_a = a // SQRT_NB_ASSEMBLIES

            x_offset = x_base + x_a * (sqrt_num_neurons + GAP_HIDDEN_ASSEMBLY)
            y_offset = y_a * (sqrt_num_neurons + GAP_HIDDEN_ASSEMBLY)

            self.draw_assembly(assembly, x_offset, y_offset )

        # output
        x_base = cols['output']

        print("Draw output_assemblies")
        for a, assembly in enumerate(network.output_assemblies):

            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))

            y_offset = a * sqrt_num_neurons

            self.draw_assembly(assembly, x_base, y_offset )

        self.create_template()

    def create_template(self):
        """Call this ONCE when the network is loaded."""
        self.background.fill(0) # Start Black

        for x, y in list(self.neuron_positions.values()):
            # Draw static neurons in a dim color
            # Draw a dim gray pixel for every neuron
            if 0 <= x and x < self.width and 0 <= y and y < self.height:
                self.background[y, x, :3] = [40, 40, 60]

    def setup_topology(self):
        """Draw all neurons as DIM dots in the background."""
        self.set_background_color((10, 10, 20))
        for x, y in list(self.neuron_positions.values()):
            self.set_pattern(y, x, self.neuron_mask, (60, 60, 60), target_buffer=self.background)

        self.update_display()

    def display_spikes(self, spike_indices):
        """
        Clean the frame using the background (dim neurons)
        then draw ONLY current spikes in bright yellow.
        """
        self.refresh_from_background()

        for idx in spike_indices:
            if idx in self.neuron_positions.keys():
                x, y = self.neuron_positions[idx]
                self.set_pattern(y, x, self.neuron_mask, (255, 255, 0))
            else:
                print(f"Error, could not find {idx} in neuron_positions {list(self.neuron_positions.keys())}")

        self.update_display()
