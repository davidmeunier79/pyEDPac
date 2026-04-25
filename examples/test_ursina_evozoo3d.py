from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe
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

from multipac.zoo3d.evo_simulation import EvoSimulation

from PySide6 import QtWidgets
import sys

# 1. Setup the Qt Application context
qt_app = QtWidgets.QApplication.instance()
if not qt_app:
    qt_app = QtWidgets.QApplication(sys.argv)

# --- 3. Run Script ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats_path", type=str, required=True)
    args = parser.parse_args()



    # --- Example Usage ---
    app = Ursina()

    # Environment Setup
    Sky()


    Entity(model='plane', scale=AREA_SIZE, texture='white_cube', texture_scale=(AREA_SIZE,AREA_SIZE), color=color.light_gray)
    # Simple wall setup in your EvoSimulation or __main__
    wall_thickness = 2


    area_size = 50

    # Create walls
    Wall_N = Entity(model='cube', scale=(AREA_SIZE, 5, wall_thickness), y=2, z=AREA_SIZE/2, color=color.gray, collider='box')
    Wall_S = Entity(model='cube', scale=(AREA_SIZE, 5, wall_thickness), y=2, z=-AREA_SIZE/2, color=color.gray, collider='box')
    Wall_E = Entity(model='cube', scale=(wall_thickness, 5, area_size), y=2, x=AREA_SIZE/2, color=color.gray, collider='box')
    Wall_W = Entity(model='cube', scale=(wall_thickness, 5, area_size), y=2, x=-AREA_SIZE/2, color=color.gray, collider='box')


    pop_config=PopulationConfigMultiTest()
    pop_config.POPULATION_SIZE=16
    pop_config.INIT_PREY_POPULATION_SIZE=8
    pop_config.INIT_PREDATOR_POPULATION_SIZE=8

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

