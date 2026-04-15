

from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe
import numpy as np

app = Ursina()

def create_agent_vision(width=64, height=64):
    # 1. Buffer Setup
    win_props = WindowProperties.size(width, height)
    fb_props = FrameBufferProperties()
    fb_props.set_rgb_color(True)
    fb_props.set_rgba_bits(8, 8, 8, 0)
    fb_props.set_depth_bits(24)

    buffer = base.graphics_engine.make_output(
        base.pipe, "agent_buffer", -100,
        fb_props, win_props, GraphicsPipe.BF_refuse_window,
        base.win.get_gsg(), base.win
    )

    # 2. The "Eye" (An Ursina Entity you can move/rotate easily)
    agent_eye = Entity()

    # 3. The Camera Node (Low-level Panda3D)
    cam_node = PandaCamera('agent_cam')
    cam_node.get_lens().set_fov(180)

    # Attach the camera node TO the Ursina Entity
    cam_np = base.render.attach_new_node(cam_node)
    cam_np.reparent_to(agent_eye)

    # 4. Texture & Buffer linking
    tex = Texture()
    # RTM_copy_ram is crucial for getting data back to the CPU
    buffer.add_render_texture(tex, GraphicsOutput.RTM_copy_ram)

    dr = buffer.make_display_region()
    dr.set_camera(cam_np)

    return agent_eye, tex

# --- Environment ---
Entity(model='cube', color=color.red, z=10, y=1)
Entity(model='plane', scale=32, texture='white_cube', texture_scale=(32,32))

def update():
    # 1. Rotation (Turning Left/Right)
    # Using time.dt ensures movement speed is the same regardless of FPS
    rotation_speed = 100
    if held_keys['left arrow']:
        agent_eye.rotation_y -= rotation_speed * time.dt
    if held_keys['right arrow']:
        agent_eye.rotation_y += rotation_speed * time.dt

    # 2. Translation (Moving Forward/Backward)
    move_speed = 5
    if held_keys['up arrow']:
        # .forward is a vector pointing where the entity is looking
        agent_eye.position += agent_eye.forward * move_speed * time.dt
    if held_keys['down arrow']:
        agent_eye.position += agent_eye.back * move_speed * time.dt

    # 3. Optional: Vertical Movement (Fly up/down)
    if held_keys['page up']:
        agent_eye.y += move_speed * time.dt
    if held_keys['page down']:
        agent_eye.y -= move_speed * time.dt

# 4. Handle Escape or Tab to quit
def input(key):
    if key == 'escape' or key == 'tab':
        application.quit()

# --- Initialize and Run ---

# Initialize
agent_eye, vision_tex = create_agent_vision(64, 64)
agent_eye.y = 1.5 # Set at "head height"

app.run()
