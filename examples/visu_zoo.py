import os
import sys
sys.path.insert(0, '../src')

# from PySide6 import QtWidgets, QtCore
#from edpac.visualisation.zoo_visualizer import ZooVisualizer
#
# def main():
#     import sys
#     from PySide6 import QtWidgets
#
#     app = QtWidgets.QApplication(sys.argv)
#
#     # Initialize with a scale of 1 (1:1 pixels)
#     zoo = ZooVisualizer(width=1024, height=768, scale=1, data_dir="/home/INT/meunier.d/Tools/Packages/pyEdPac/data")
#
#     # 1. Load the "Library" of animal shapes
#     zoo.load_menagerie("menagerie/menagerie_tmp.txt")
#
#     # 2. Draw the specific screen layout
#     zoo.draw_screen("screens/screen.tmp")
#
#     zoo.show()
#     sys.exit(app.exec())
import sys
from PySide6 import QtWidgets
from edpac.zoo.zoo import Zoo

from edpac.visualisation.zoo_visualizer import ZooVisualizer

def main():
    app = QtWidgets.QApplication(sys.argv)

    # 1. Initialize Data
    zoo = Zoo(data_dir="/home/INT/meunier.d/Tools/Packages/pyEdPac/data")
    zoo.load_everything(screen_file="screen.0", menagerie_file= "menagerie.txt")

    # 2. Initialize Visualiser
    # Original EDPac screens were often around 40x25 characters
    # 40 * 16 = 640px, 25 * 16 = 400px
    viz = ZooVisualizer(width=800, height=500, scale=2)
    viz.show()

    # 3. Initial Draw
    viz.draw_zoo(zoo)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
