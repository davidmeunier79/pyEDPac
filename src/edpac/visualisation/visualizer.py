import numpy as np
import pyqtgraph as pg
from PySide6 import QtWidgets, QtCore
from PIL import Image

def load_xbm_as_coords(filepath):
    """
    Loads an XBM file and returns the (x, y) coordinates
    of all 'on' bits (black pixels).
    """
    with Image.open(filepath) as img:
        # XBM is 1-bit; convert to numpy array
        # 0 is usually white/off, 1 is black/on
        data = np.array(img)
        width, height = img.size

        # Find coordinates where the pixel is 'on'
        # Note: XBM data is often inverted depending on the viewer,
        # so we check for the foreground color.
        y_coords, x_coords = np.where(data == 0) # In PIL, 0 is often the 'ink' for XBM

        return x_coords, y_coords, width, height

class BaseVisualizer(pg.PlotWidget):
    """
    Modern replacement for the Fenetre class.
    Provides drawing primitives for pyEDPac simulations.
    """
    def __init__(self, title="pyEDPac Visualizer", background='w'):
        # Ensure QApplication exists
        if not QtWidgets.QApplication.instance():
            self.app = QtWidgets.QApplication([])
        else:
            self.app = QtWidgets.QApplication.instance()

        super().__init__()
        self.setBackground(background)
        self.setWindowTitle(title)

        # Initialize the scatter item for points/agents
        self.scatter_item = pg.ScatterPlotItem(pxMode=True)
        self.addItem(self.scatter_item) # This attaches it to the plot

        self.lines = []

    def clear_canvas(self):
        self.scatter_item.clear()
        for line in self.lines:
            self.removeItem(line)
        self.lines = []

    def draw_agent(self, x, y, size=5, color='b', symbol='o'):
        """
        Replacement for Fenetre::TraceCarre or TracePoint.
        Adds a point/agent to the scatter plot.
        """
        self.points.addPoints([{
            'pos': [x, y],
            'size': size,
            'pen': pg.mkPen(None),
            'brush': pg.mkBrush(color),
            'symbol': symbol
        }])

    def draw_connection(self, x1, y1, x2, y2, weight=1, color='k'):
        """
        Useful for the Network class to draw synapses.
        """
        line = pg.PlotCurveItem([x1, x2], [y1, y2],
                                 pen=pg.mkPen(color, width=weight))
        self.addItem(line)
        self.lines.append(line)

    def refresh(self):
        """Forces a GUI update, similar to XFlush or XNextEvent logic."""
        QtWidgets.QApplication.processEvents()


    def draw_enclosure(self, x, y, w, h):
        """Draws the fixed size rectangle (The Zoo walls)"""
        rect = QtWidgets.QGraphicsRectItem(x, y, w, h)
        rect.setPen(pg.mkPen('k', width=2))
        self.addItem(rect)

    def closeEvent(self, event):
        """This handles the 'X' button click."""
        print("Window closing, terminating process...")

        # If you have a simulation thread, stop it here!
        # self.my_thread.quit()

        # Force the application to quit
        QtWidgets.QApplication.instance().quit()
        event.accept()

class PatternVisualizer(BaseVisualizer):
    def draw_pattern_in_rect(self, xbm_path, rect_x, rect_y, rect_w, rect_h):
        """
        Draws a rectangle and centers the XBM pattern inside it.
        """
        # 1. Draw the "Zoo" enclosure (The Rectangle)
        rect = pg.QtWidgets.QGraphicsRectItem(rect_x, rect_y, rect_w, rect_h)
        rect.setPen(pg.mkPen('k', width=2))
        self.addItem(rect)

        # 2. Load the pattern bits
        px, py, p_w, p_h = load_xbm_as_coords(xbm_path)

        # 3. Calculate centering offset
        offset_x = rect_x + (rect_w - p_w) / 2
        offset_y = rect_y + (rect_h - p_h) / 2

        # 4. Draw the bits as small points
        # We flip the y-axis (py) because X11 coordinates are top-down
        # while PlotWidget is usually bottom-up.
        self.scatter_item.addPoints(
            x=px + offset_x,
            y=(p_h - py) + offset_y,
            size=2,
            brush='k'
        )

class ZooVisualizer(BaseVisualizer):
    def __init__(self):
        super().__init__(title="EDPac Zoo")

    def draw_xbm_pattern(self, xbm_path, center_x, center_y):
        try:
            with Image.open(xbm_path) as img:
                # Convert XBM bits to coordinates
                data = np.array(img)
                # In XBM/PIL, 0 is often the 'ink' (foreground)
                y_idx, x_idx = np.where(data == 0)

                # Center the pattern
                width, height = img.size
                x_coords = x_idx - (width / 2) + center_x
                # Flip Y because X11 is top-down, but PlotWidget is bottom-up
                y_coords = (height - y_idx) - (height / 2) + center_y

                # Update the scatter plot
                self.scatter_item.addPoints(x=x_coords, y=y_coords, size=2, brush='k')

        except FileNotFoundError:
            print(f"Error: Could not find {xbm_path}")
        except Exception as e:
            print(f"An error occurred: {e}")


from edpac.ed_network.network import Network # Assuming your repo structure
from edpac.config.constants import *
from math import sqrt

from edpac.ed_network.event_manager import SpikeEvent

class NetworkVisualizer(BaseVisualizer):
    def __init__(self):
        super().__init__(title="pyEDPac Network")
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

            x =  x_offset + i%sqrt_num_neurons # Slight jitter for visibility
            y =  y_offset + (i // sqrt_num_neurons)
            self.neuron_positions[neuron_id] = (x, y)

    def display_network(self, network: Network):
        """Processes the Network object and lays it out in columns."""
        #self.clear()
        self.neuron_positions = {}

        # Define column X-coordinates

        cols = {'input': 0,
                'hidden': VISIO_SQRT_NB_NEURONS+GAP_INPUT_ASSEMBLY,
                "output": VISIO_SQRT_NB_NEURONS+GAP_INPUT_ASSEMBLY + SQRT_NB_ASSEMBLIES*(SQRT_NB_NEURONS+GAP_HIDDEN_ASSEMBLY)
                }

        # 1. Calculate positions for every neuron in every assembly
        # input
        x_base = cols['input']

        print("Draw input_assemblies")
        for a, assembly in enumerate(network.input_assemblies):
            print(f"Assembly {a}")
            # Determine column based on assembly name or attribute
            # Adjust this logic if you have a specific 'type' attribute

            # Layout neurons vertically within the assembly
            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))


            y_offset = a * (sqrt_num_neurons + GAP_INPUT_ASSEMBLY)
            print("y_offset:", y_offset)

            self.draw_assembly(assembly, x_base, y_offset )

            #print(self.neuron_positions)

        # hidden
        print("Draw hidden_assemblies")
        x_base = cols['hidden']

        for a, assembly in enumerate(network.hidden_assemblies):

            print(f"Assembly {a}")
            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))

            x_a = a % SQRT_NB_ASSEMBLIES
            y_a = a // SQRT_NB_ASSEMBLIES

            x_offset = x_base + x_a * (sqrt_num_neurons + GAP_HIDDEN_ASSEMBLY)
            y_offset = y_a * (sqrt_num_neurons + GAP_HIDDEN_ASSEMBLY)

            print("x_offset:", x_offset)
            print("y_offset:", y_offset)

            self.draw_assembly(assembly, x_offset, y_offset )

        # output
        x_base = cols['output']

        print("Draw output_assemblies")
        for a, assembly in enumerate(network.output_assemblies):

            print(f"Assembly {a}")
            sqrt_num_neurons = sqrt(len(assembly.get_neurons()))

            y_offset = a * (sqrt_num_neurons + GAP_OUTPUT_ASSEMBLY)
            print("y_offset:", y_offset)

            self.draw_assembly(assembly, x_base, y_offset )


        # 3. Draw Neurons (Points)
        all_pos = list(self.neuron_positions.values())

        print("Draw Neurons")
        self.scatter_item.addPoints(
            pos=all_pos,
            #size=100,
            #brush=pg.mkBrush(50, 150, 255, 200),
            pen=pg.mkPen('k', width=0.5))

        # 2. Draw Synapses (Lines)
        # We iterate through connections.
        # Note: adjust this depending on how you store synapses in your Network class
        #
        # print("Draw input Synapses")
        # for assembly in network.input_assemblies:
        #     if assembly.get_nb_neurons() == 0:
        #         continue
        #
        #     for neuron in assembly.get_neurons():
        #
        #         # Assuming neuron has a list of outgoing synapses
        #
        #         if len(neuron.outgoing_links):
        #             start_pos = self.neuron_positions[neuron.id]
        #             #print("start_pos = ", start_pos)
        #
        #             print("Neuron ", neuron.id)
        #             for syn in neuron.outgoing_links:
        #                 end_neuron_id = syn.post_node.id
        #
        #                 if end_neuron_id in self.neuron_positions:
        #                     end_pos = self.neuron_positions[end_neuron_id]
        #                     self.draw_synapse(start_pos, end_pos, syn.weight)
        #
        # print("Draw internal Synapses")
        # for assembly in network.hidden_assemblies:
        #
        #     print("Assembly ", assembly.id)
        #     for neuron in assembly.get_neurons():
        #
        #
        #         # Assuming neuron has a list of outgoing synapses
        #         if len(neuron.outgoing_links):
        #
        #             print("Neuron ", neuron.id)
        #             start_pos = self.neuron_positions[neuron.id]
        #             #print("start_pos = ", start_pos)
        #
        #             for syn in neuron.outgoing_links:
        #                 end_neuron_id = syn.post_node.id
        #
        #                 if end_neuron_id in self.neuron_positions:
        #                     end_pos = self.neuron_positions[end_neuron_id]
        #                     self.draw_synapse(start_pos, end_pos, syn.weight)

        print("Finished drawing ")

    def draw_synapse(self, start, end, weight):
        # Scale line width by weight, cap it at 5 for visibility
        width = 0.1
        color = 'r' if weight < 0.0 else 'b' # Red for inhibitory, Blue for excitatory
        line = pg.PlotCurveItem(
            [start[0], end[0]],
            [start[1], end[1]],
            pen=pg.mkPen(color, width=width)
        )
        self.addItem(line)
        #self.synapses.append(line)

    def clear(self):
        self.neuron_scatter.clear()
        for s in self.synapses:
            self.removeItem(s)
        self.synapses = []

    def update_visu(self, events):

        all_pos_spikes = []
        for event in events:
            if isinstance(event, SpikeEvent):
                print(event.neuron)
                if event.neuron.id in self.neuron_positions.keys():
                    pos = self.neuron_positions[event.neuron.id]
                    all_pos_spikes.append(pos)

        print(all_pos_spikes)

        print("Draw Spikes")
        self.scatter_item.addPoints(
            pos=all_pos_spikes,
            #brush=pg.mkBrush(50, 150, 255, 200),
            pen=pg.mkPen('w', width=0.5))

        print("Finished Draw Spikes")
