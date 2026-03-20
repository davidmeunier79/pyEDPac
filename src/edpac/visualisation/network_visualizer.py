import numpy as np
from math import sqrt

from edpac.ed_network.network import Network # Assuming your repo structure
from edpac.config.network_config import ProjectionNature, NetworkConfig, NetworkVisualizerConfig
#from edpac.config.constants import
from .pixel_visualizer import PixelVisualizer

class NetworkVisualizer(PixelVisualizer):
    def __init__(self,
                 config : NetworkVisualizerConfig = None,
                 network_config : NetworkConfig = None,
                 title="Neural Activity",
                 scale=1):
        self.config = config or NetworkVisualizerConfig()
        self.network_config = network_config or NetworkConfig()

        self.neuron_mask = np.ones((2, 2), dtype=np.uint8) # 1x1 pixel or larger

        width = (self.network_config.VISIO_SQRT_NB_NEURONS+self.config.GAP_INPUT_ASSEMBLY + self.network_config.SQRT_NB_ASSEMBLIES*(self.network_config.SQRT_NB_NEURONS+self.config.GAP_HIDDEN_ASSEMBLY) + self.config.GAP_OUTPUT_ASSEMBLY+self.network_config.MOTOR_SQRT_NB_NEURONS)*self.neuron_mask.shape[0]

        height = max((self.network_config.VISIO_SQRT_NB_NEURONS+self.config.GAP_INPUT_ASSEMBLY)*self.network_config.NB_INPUT_ASSEMBLIES,
                     self.network_config.SQRT_NB_ASSEMBLIES*(self.network_config.SQRT_NB_NEURONS+self.config.GAP_HIDDEN_ASSEMBLY),
                     (self.network_config.MOTOR_SQRT_NB_NEURONS+self.config.GAP_OUTPUT_ASSEMBLY)*self.network_config.NB_OUTPUT_ASSEMBLIES)*self.neuron_mask.shape[1]


        super().__init__( height=height, width=width,title=title, scale=scale)

        self.neuron_positions = {}
        self.assembly_positions = {}

        self.set_background_color(0)


    def draw_assembly(self, assembly, x_offset, y_offset ):

        for i, neuron_id in enumerate(assembly.get_neuron_ids()):

            sqrt_num_neurons = sqrt(assembly.get_nb_neurons())

            x =  int(x_offset + i%sqrt_num_neurons) # Slight jitter for visibility
            y =  int(y_offset + (i // sqrt_num_neurons))
            self.neuron_positions[neuron_id] = (x, y)

    def init_assemblies(self, network: Network):
        """Processes the Network object and lays it out in columns."""
        #self.clear()

        # Define column X-coordinates
        cols = {'input': 0,
                'hidden': self.network_config.VISIO_SQRT_NB_NEURONS+self.config.GAP_INPUT_ASSEMBLY,
                "output": self.network_config.VISIO_SQRT_NB_NEURONS+self.config.GAP_INPUT_ASSEMBLY + self.network_config.SQRT_NB_ASSEMBLIES*(self.network_config.SQRT_NB_NEURONS+self.config.GAP_HIDDEN_ASSEMBLY) + self.config.GAP_OUTPUT_ASSEMBLY
                }

        # 1. Calculate positions for every neuron in every assembly
        # input
        x_offset = cols['input']

        #print("Draw input_assemblies")
        for a, assembly in enumerate(network.input_assemblies):
            # Determine column based on assembly name or attribute
            # Adjust this logic if you have a specific 'type' attribute

            # Layout neurons vertically within the assembly
            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))
            y_offset = a * sqrt_num_neurons
            self.draw_assembly(assembly, x_offset, y_offset )
            self.assembly_positions[assembly.id] = x_offset+int(self.network_config.VISIO_SQRT_NB_NEURONS/2), y_offset+int(self.network_config.VISIO_SQRT_NB_NEURONS/2)

        # hidden
        #print("Draw hidden_assemblies")
        x_base = cols['hidden']


        for a, assembly in enumerate(network.hidden_assemblies):

            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))

            x_a = a // self.network_config.SQRT_NB_ASSEMBLIES
            y_a = a % self.network_config.SQRT_NB_ASSEMBLIES

            x_offset = x_base + x_a * (sqrt_num_neurons + self.config.GAP_HIDDEN_ASSEMBLY)
            y_offset = y_a * (sqrt_num_neurons + self.config.GAP_HIDDEN_ASSEMBLY)

            self.draw_assembly(assembly, x_offset, y_offset )

            self.assembly_positions[assembly.id] = x_offset+int(self.network_config.SQRT_NB_NEURONS/2), y_offset+int(self.network_config.SQRT_NB_NEURONS/2)

        # output
        x_offset = cols['output']

        #print("Draw output_assemblies")
        for a, assembly in enumerate(network.output_assemblies):

            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))

            y_offset = a * sqrt_num_neurons

            self.draw_assembly(assembly, x_offset, y_offset )
            self.assembly_positions[assembly.id] = x_offset+int(self.network_config.MOTOR_SQRT_NB_NEURONS/2), y_offset+int(self.network_config.MOTOR_SQRT_NB_NEURONS/2)

    def draw_assemblies(self):

        for x, y in list(self.neuron_positions.values()):
            self.set_pattern(y*self.neuron_mask.shape[1], x*self.neuron_mask.shape[0], self.neuron_mask, (60, 60, 60), target_buffer=self.background)

    def draw_projections(self, network: Network):

        # draw projections
        for proj in network.projections:

            pre_assembly_pos = self.assembly_positions[proj.pre_node]
            post_assembly_pos = self.assembly_positions[proj.post_node]

            if proj.nature == ProjectionNature.INHIBITORY:
                color = (255, 0, 0) # blue

            elif proj.nature == ProjectionNature.EXCITATORY:
                color = (0, 0, 255) # red
            else:
                print(f"Error with proj {proj.nature}")

            self.draw_line(pre_assembly_pos, post_assembly_pos, color, target_buffer = self.background, neuron_mask=self.neuron_mask)


    def display_spikes(self, spike_indices):
        """
        Clean the frame using the background (dim neurons)
        then draw ONLY current spikes in bright yellow.
        """
        self.refresh_from_background()

        for idx in spike_indices:
            if idx in self.neuron_positions.keys():
                x, y = self.neuron_positions[idx]
                self.set_pattern(y*self.neuron_mask.shape[1], x*self.neuron_mask.shape[0], self.neuron_mask, (255, 255, 0))
            else:
                print(f"Error, could not find {idx} in neuron_positions {list(self.neuron_positions.keys())}")
