import sys

sys.path.insert(0, '../src')

from PySide6 import QtWidgets
#from visualizer import BaseVisualizer,PatternVisualizer
from edpac.visualisation.visualizer import ZooVisualizer, NetworkVisualizer

from edpac.zoo.zoo import Zoo
#from network import Network

from edpac.ed_network.network import Network
from edpac.ed_network.network_builder import create_simple_pacman_network
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
    net = create_simple_pacman_network()

#     # Initialize GUI
    app = QtWidgets.QApplication(sys.argv)
    viz_net = NetworkVisualizer()
    viz_net.show()

    viz_net.display_network(net)
#
#     viz_net.show()
#
    sys.exit(app.exec())
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
