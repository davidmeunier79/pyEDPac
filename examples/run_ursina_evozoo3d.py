from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe, get_model_path
import numpy as np
import sys

# Ensure your src is in path
sys.path.insert(0, '../src')

from edpac.config.ga_config import PopulationConfigMulti, PopulationConfigMultiTest

from edpac.config.config_manager import save_configs
from edpac.config.constants import VISIO_SQRT_NB_NEURONS, AREA_SIZE

from edpac.config.zoo_config import MultiPacmanConfig, UrsinaConfig

#zoo_config = MultiPacmanConfig()

# QT components
from edpac.visualisation.multi_input_visualizer import MultiInputVisualizer


from multipac.parallel.parallel_zoo3d import ParallelZoo3D
#from multipac.zoo3d.agent import Agent

from multipac.zoo3d.evo_simulation import EvoSimulation, add_wall_crosses

from PySide6 import QtWidgets
import sys

# 1. Setup the Qt Application context
qt_app = QtWidgets.QApplication.instance()
if not qt_app:
    qt_app = QtWidgets.QApplication(sys.argv)

# --- Wall Decoration Setup ---
wall_height = 5
# Define how many crosses per unit (e.g., 1 cross every 2 units)
x_density = 0.5

wall_thickness = 2




# Get the path to your package level 'data/texture' folder
# Adjust the number of '.parent' calls depending on where main.py is relative to /data
package_root = Path(__file__).resolve().parent.parent # Example: goes up to package level
print(package_root)

texture_dir = package_root / 'data' / 'textures'

print(texture_dir)

# Add this directory to the global search path
#get_model_path().prepend_directory(str(texture_dir))


# --- 3. Run Script ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats_path", type=str, required=True)
    args = parser.parse_args()



    # --- Example Usage ---
    app = Ursina()
    application.asset_folder = texture_dir

    # Environment Setup
    Sky()

    Entity(model='plane', scale=AREA_SIZE, texture='white_cube', texture_scale=(AREA_SIZE,AREA_SIZE), color=color.light_gray)


    # Create walls with textures
    Wall_N = Entity(model='cube', scale=(AREA_SIZE, wall_height, wall_thickness), y=2, z=AREA_SIZE/2, color=color.gray, collider='box')
    # Overlay on the inner side (facing -Z)
    inner_N = add_wall_crosses(Wall_N, True, x_density, wall_height)
    inner_N.z = -0.51 # Move slightly inward from the wall center
    inner_N.scale_x = 1 # Matches parent width

    Wall_S = Entity(model='cube', scale=(AREA_SIZE, wall_height, wall_thickness), y=2, z=-AREA_SIZE/2, color=color.gray, collider='box')
    # Overlay on the inner side (facing +Z)
    inner_S = add_wall_crosses(Wall_S, True, x_density, wall_height)
    inner_S.z = 0.51
    inner_S.rotation_y = 180

    Wall_E = Entity(model='cube', scale=(wall_thickness, wall_height, AREA_SIZE), y=2, x=AREA_SIZE/2, color=color.gray, collider='box')
    # Overlay on the inner side (facing -X)
    inner_E = add_wall_crosses(Wall_E, False, x_density, wall_height)
    inner_E.x = -0.51
    inner_E.rotation_y = 90

    Wall_W = Entity(model='cube', scale=(wall_thickness, wall_height, AREA_SIZE), y=2, x=-AREA_SIZE/2, color=color.gray, collider='box')
    # Overlay on the inner side (facing +X)
    inner_W = add_wall_crosses(Wall_W, False, x_density, wall_height)
    inner_W.x = 0.51
    inner_W.rotation_y = -90


    pop_config=PopulationConfigMulti()
    #pop_config.POPULATION_SIZE=16
    #pop_config.INIT_PREY_POPULATION_SIZE=10
    #pop_config.INIT_PREDATOR_POPULATION_SIZE=10

    # Start Simulation
    sim = EvoSimulation(args.stats_path, ursina_config = None, pop_config = pop_config)

    # Use the Ursina wrapper 'camera', NOT a NodePath
    camera.orthographic = True
    camera.position = (0, 40, 0)
    camera.rotation_x = 90
    camera.fov = 50  # In ortho mode, FOV acts as the zoom level

    # Increase the range of what the camera can see
    camera.clip_plane_far = 500  # Default is often 100
    camera.clip_plane_near = 0.1


    def input(key):
        if key == 'escape':
            sim.on_destroy()
            quit()

    app.run()

