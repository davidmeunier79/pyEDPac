import os
import sys
sys.path.insert(0, '../src')

import numpy as np

from PySide6 import QtWidgets
#from visualizer import BaseVisualizer,PatternVisualizer
from edpac.visualisation.visualizer import ZooVisualizer, NetworkVisualizer

from edpac.zoo.zoo import Zoo
#from network import Network

from edpac.ed_network.ed_synapse import EDSynapse


from edpac.ed_network.network import Network
from edpac.ed_network.network_builder import create_simple_network

from edpac.config.constants import *


#
# def main():
#     app = QtWidgets.QApplication(sys.argv)
#
#     viz_zoo = ZooVisualizer()
#     viz_zoo.show()
#
#     # Draw a 200x200 rectangle at (0,0)
#     viz_zoo.draw_enclosure(0, 0, 200, 200)
#
#     # Load an XBM from your directory and place it in the middle (100, 100)
#     # Update this path to your actual file location
#     viz_zoo.draw_xbm_pattern("../data/menagerie/cochon/cochon.XBM", 100, 100)
#     sys.exit(app.exec())


def main():
    # Create objects
    net = create_simple_network()

#     # Initialize GUI
    app = QtWidgets.QApplication(sys.argv)
    viz_net = NetworkVisualizer()

    viz_net.display_network(net)
#
    viz_net.show()

    print("Before injections:" , EDSynapse.event_manager.get_nb_events())
    ### add random stim to event_manager
    pattern_float = np.random.random(size=(VISIO_SQRT_NB_NEURONS*  VISIO_SQRT_NB_NEURONS))

    net.inject_input_float(assembly_idx=0, time=0, pattern_float=pattern_float)

    while True:
        events = EDSynapse.event_manager.run_one_step()
        if events is not None:
            print(events)

            viz_net.update_visu(events)

            viz_net.show()
        else:
            break



    # Run the loop
    exit_code = app.exec()

    # Force a hard exit of the Python interpreter
    # to kill any dangling background threads
    print("Process finished.")
    os._exit(exit_code) # This is a 'harder' exit than sys.exit()

    #sys.exit(app.exec())
#

#
# def main():
#     # 1. YOU MUST CREATE THIS FIRST
#     # This initializes the Qt event loop and display connection.
#     app = QtWidgets.QApplication(sys.argv)
#
#     # 1. Initialize Visualizer
#     viz_zoo = PatternVisualizer(title="Zoo Simulation")
#     viz_zoo.draw_pattern_in_rect("../../../data/menagerie/cochon/cochon.XBM", 100, 100, 200, 200)
#     viz_zoo.show()
#
#     viz_net = BaseVisualizer(title="Network Simulation")
#     viz_net.show()
#     sys.exit(app.exec())
#

if __name__ == "__main__":
    main()
