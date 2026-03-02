
from edpac.ed_network.network import Network # Assuming your repo structure
from edpac.config.constants import *
from math import sqrt

from .pixel_visualizer import PixelVisualizer

class NetworkVisualizer(PixelVisualizer):
    def __init__(self,  width, height, scale, title):
        super().__init__( width, height, scale, title)
        # Performance: Use one ScatterPlotItem for all neurons
        #self.neuron_scatter = pg.ScatterPlotItem(pxMode=True)
        #self.addItem(self.neuron_scatter)

#         if not QtWidgets.QApplication.instance():
#             self.app = QtWidgets.QApplication([])
#         else:
#             self.app = QtWidgets.QApplication.instance()
#
#         super().__init__()
#         self.setBackground('w')
#         self.setWindowTitle(title)
#
#
#         # Store lines (synapses)
#         self.synapses = []
#
#         # Mapping to store neuron positions for synapse drawing
#         self.neuron_positions = {} # {neuron_id: (x, y)}

    def draw_assembly(self, assembly, x_offset, y_offset ):

        for i, neuron_id in enumerate(assembly.get_neuron_ids()):

            sqrt_num_neurons = sqrt(assembly.get_nb_neurons())

            x =  int(x_offset + i%sqrt_num_neurons) # Slight jitter for visibility
            y =  int(y_offset + (i // sqrt_num_neurons))
            self.neuron_positions[neuron_id] = (x, y)

    def init_network(self, network: Network):
        """Processes the Network object and lays it out in columns."""
        #self.clear()
        self.neuron_positions = {}

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


            y_offset = a * (sqrt_num_neurons + GAP_INPUT_ASSEMBLY)

            self.draw_assembly(assembly, x_base, y_offset )

            #print(self.neuron_positions)

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

            y_offset = a * (sqrt_num_neurons + GAP_OUTPUT_ASSEMBLY)

            self.draw_assembly(assembly, x_base, y_offset )

    def display_empty_network(self):

        self._init_buffer()

        all_pos = list(self.neuron_positions.values())

        self.clear_canvas((255, 255, 255)) # White

        for x,y in all_pos:
            self.set_pixel(x, y, (0, 0, 0)) # Black

        self.update_display()

    def update_visu(self, spike_neuron_ids):

        all_pos_spikes = []

        for neuron_id in spike_neuron_ids:

            if neuron_id in self.neuron_positions.keys():
                pos = self.neuron_positions[neuron_id]
                all_pos_spikes.append(pos)

        for x,y in all_pos_spikes:
            self.set_pixel(x, y, (255, 255, 0)) # Yellow

        self.update_display()

