import multiprocessing as mp
import numpy as np
import random

import sys
sys.path.insert(0, '../src')


from edpac.config.constants import AREA_SIZE, VISIO_SQRT_NB_NEURONS

from edpac.config.network_config import NetworkConfig
from edpac.config.ga_config import PopulationConfig

#from edpac.genetic_algorithm.population import Population

from edpac.zoo.pacman_population import PacmanPopulation

from edpac.zoo.pacman import Direction

from edpac.zoo.chars import char_to_index, index_to_char

from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe

class Agent(Entity):
    def __init__(self, agent_id, start_pos=(0, 1, 0), start_rot=0, proximity_range=3.0):
        self.animal_nature = "1" if agent_id % 2 == 0 else "-1"
        ac_color = color.orange if self.animal_nature == "-1" else color.cyan

        super().__init__(
            model='cube',  # The body
            color=ac_color,
            position=start_pos,
            rotation_y=start_rot,  # Sets the initial facing direction
            scale=(1.2, 1, 1.2), # Slightly flatter body
            collider='box',
            add_to_scene_entities=True
        )

        # Proximity Sensor (Invisible but detects overlaps)
        # We make it a child of the agent so it moves with them
        self.sensor = Entity(
            parent=self,
            model='wireframe_cube', # Use wireframe for debugging, None for production
            scale=proximity_range,  # This defines the "distance" of detection
            collider='box',
            color=color.rgba(1, 1, 1, 0.1), # Faintly visible
            add_to_scene_entities=False    # Keep it out of the main entity list
        )
        self.sensor.visible = False # Usually hidden

        self.agent_id = agent_id

        # --- The Head ---
        # Child of self, so it moves with the body
        self.head = Entity(
            parent=self,
            model='sphere',
            color=color.light_gray,
            scale=(0.5, 0.5, 0.5),
            position=(0, 0.7, 0) # On top of the body
        )

        # --- The Nose/Direction Indicator ---
        # Helps see where the head is facing
        self.nose = Entity(
            parent=self.head,
            model='cube',
            color=color.black,
            scale=(0.2, 0.2, 0.5),
            position=(0, 0, 0.4) # Pointing forward from head
        )


        # Add a simple indicator on the front of the body
        self.front_stripe = Entity(
            parent=self,
            model='cube',
            color=color.white,
            scale=(1.0, 0.1, 0.1),
            position=(0, 0, 0.5) # Placed on the forward face
        )

        # Setup the "Neural Eye" (Attach it to the HEAD now)
        self.vision_tex = self.setup_offscreen_vision()

    def get_vision_matrix(self):
        if self.vision_tex.has_ram_image():
            data = self.vision_tex.get_ram_image_as("RGB")
            return np.frombuffer(data, dtype=np.uint8).reshape((VISIO_SQRT_NB_NEURONS, VISIO_SQRT_NB_NEURONS, 3))
        return np.zeros((VISIO_SQRT_NB_NEURONS, VISIO_SQRT_NB_NEURONS, 3), dtype=np.uint8)

    def setup_offscreen_vision(self, width=VISIO_SQRT_NB_NEURONS, height=VISIO_SQRT_NB_NEURONS):
        win_props = WindowProperties.size(width, height)
        fb_props = FrameBufferProperties()
        fb_props.set_rgb_color(True)
        fb_props.set_rgba_bits(8, 8, 8, 0)
        fb_props.set_depth_bits(24)

        buffer = base.graphics_engine.make_output(
            base.pipe, f"agent_buffer_{self.agent_id}", -100,
            fb_props, win_props, GraphicsPipe.BF_refuse_window,
            base.win.get_gsg(), base.win
        )

        tex = Texture()
        buffer.add_render_texture(tex, GraphicsOutput.RTM_copy_ram)





        cam_node = PandaCamera(f'cam_{self.agent_id}')
        cam_node.get_lens().set_fov(90)

        # ATTACH CAMERA TO HEAD instead of self (the body)
        cam_np = self.head.attach_new_node(cam_node)

        # Position camera at the "eyes"
        cam_np.setPos(0, 0, 0.2)

        dr = buffer.make_display_region()
        dr.set_camera(cam_np)
        return tex
