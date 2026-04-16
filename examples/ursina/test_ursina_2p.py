from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe
import numpy as np

app = Ursina()

class Individual(Entity):
    def __init__(self, color=color.red, start_pos=(0, 1.5, 0), controls={}, view_region=(0, 0.5, 0, 1)):
        super().__init__(
            model='cube',
            color=color,
            position=start_pos,
            scale=(1, 2, 1) # A simple "humanoid" block
        )
        self.controls = controls

        # 1. Setup the Vision (Offscreen buffer for the Matrix/Neural Input)
        self.vision_tex = self.setup_offscreen_vision()

        # 2. Setup the Viewport (Split-screen for the USER to see)
        # view_region is (left, right, bottom, top) from 0.0 to 1.0
        self.cam_node = PandaCamera(f'cam_{color}')
        self.cam_node.get_lens().set_fov(90)
        self.cam_np = base.render.attach_new_node(self.cam_node)
        self.cam_np.reparent_to(self)
        self.cam_np.setY(0.4) # Position at "head" height

        # Create the display region on the main window
        dr = base.win.make_display_region(*view_region)
        dr.set_camera(self.cam_np)

    def setup_offscreen_vision(self, width=64, height=64):
        win_props = WindowProperties.size(width, height)
        fb_props = FrameBufferProperties()
        fb_props.set_rgb_color(True)
        fb_props.set_rgba_bits(8, 8, 8, 0)
        fb_props.set_depth_bits(24)

        buffer = base.graphics_engine.make_output(
            base.pipe, f"buffer_{self.color}", -100,
            fb_props, win_props, GraphicsPipe.BF_refuse_window,
            base.win.get_gsg(), base.win
        )

        tex = Texture()
        buffer.add_render_texture(tex, GraphicsOutput.RTM_copy_ram)

        # Internal camera for the buffer
        inner_cam = PandaCamera('inner_cam')
        inner_cam_np = self.attach_new_node(inner_cam)
        inner_cam_np.setY(0.4)

        dr = buffer.make_display_region()
        dr.set_camera(inner_cam_np)
        return tex

    def update(self):
        # Movement logic
        move_speed = 5
        rot_speed = 100

        # Translation
        if held_keys[self.controls['up']]:
            self.position += self.forward * move_speed * time.dt
        if held_keys[self.controls['down']]:
            self.position += self.back * move_speed * time.dt

        # Rotation
        if held_keys[self.controls['left']]:
            self.rotation_y -= rot_speed * time.dt
        if held_keys[self.controls['right']]:
            self.rotation_y += rot_speed * time.dt

# --- Environment Setup ---
Sky()
ground = Entity(model='plane', scale=64, texture='white_cube', texture_scale=(64,64), color=color.gray)

# Initialize Player 1 (Red) - Left side of screen
p1 = Individual(
    color=color.red,
    start_pos=(-5, 1, 0),
    controls={'up': 'up arrow', 'down': 'down arrow', 'left': 'left arrow', 'right': 'right arrow'},
    view_region=(0, 0.5, 0, 1) # Left half
)

# Initialize Player 2 (Blue) - Right side of screen
p2 = Individual(
    color=color.blue,
    start_pos=(5, 1, 0),
    controls={'up': 'q', 'down': 'w', 'left': 's', 'right': 'd'},
    view_region=(0.5, 1, 0, 1) # Right half
)

# Disable the default main camera so it doesn't overlap our split-screen
camera.enabled = False

def input(key):
    if key == 'escape' or key == 'tab':
        application.quit()

app.run()
