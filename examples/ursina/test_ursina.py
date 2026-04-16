from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe
import numpy as np

app = Ursina()

def create_agent_vision(width=64, height=64):
    # 1. Setup Buffer Properties
    win_props = WindowProperties.size(width, height)
    fb_props = FrameBufferProperties()
    fb_props.set_rgb_color(True)
    fb_props.set_rgba_bits(8, 8, 8, 0)
    fb_props.set_depth_bits(24)

    # 2. Create Offscreen Buffer
    buffer = base.graphics_engine.make_output(
        base.pipe, "agent_buffer", -100,
        fb_props, win_props, GraphicsPipe.BF_refuse_window,
        base.win.get_gsg(), base.win
    )

    if not buffer:
        print("Failed to create offscreen buffer!")
        return None, None

    # 3. Create the Agent Eye (The Ursina Entity we move)
    # CRITICAL: We explicitly set scale to 1 to avoid "singular LMatrix4"
    agent_eye = Entity(model=None, scale=1, add_to_scene_entities=True)
    agent_eye.y = 1.5

    # 4. Create the Panda3D Camera Node
    cam_node = PandaCamera('agent_cam')
    # Ensure FOV is NOT 0
    cam_node.get_lens().set_fov(90)
    cam_node.get_lens().set_near_far(0.1, 1000)

    # Attach camera node to the eye entity
    cam_np = base.render.attach_new_node(cam_node)
    cam_np.reparent_to(agent_eye)

    # 5. Link Texture for Matrix Extraction
    tex = Texture()
    buffer.add_render_texture(tex, GraphicsOutput.RTM_copy_ram)

    dr = buffer.make_display_region()
    dr.set_camera(cam_np)

    return agent_eye, tex

# --- Scene Setup ---
Sky()
ground = Entity(model='plane', scale=64, texture='white_cube', texture_scale=(64,64), color=color.light_gray)
target_cube = Entity(model='cube', color=color.red, z=10, y=1, scale=2)

# Initialize Vision
agent_eye, vision_tex = create_agent_vision(64, 64)

# Optional: Make the Main Editor Camera follow the agent eye so you see what it sees
camera.parent = agent_eye
camera.position = (0, 0, 0)
camera.rotation = (0, 0, 0)

def update():
    # 1. Keyboard Movement (Arrows)
    move_speed = 5
    rot_speed = 100

    if held_keys['up arrow']:
        agent_eye.position += agent_eye.forward * move_speed * time.dt
    if held_keys['down arrow']:
        agent_eye.position += agent_eye.back * move_speed * time.dt
    if held_keys['left arrow']:
        agent_eye.rotation_y -= rot_speed * time.dt
    if held_keys['right arrow']:
        agent_eye.rotation_y += rot_speed * time.dt

    # 2. Extract 2D Matrix
    if vision_tex and vision_tex.has_ram_image():
        data = vision_tex.get_ram_image_as("RGB")
        v_matrix = np.frombuffer(data, dtype=np.uint8).reshape((64, 64, 3))
        # v_matrix is now ready for your EvoNetwork!
        # (Note: Panda3D/Ursina matrices might be flipped vertically)

# Handle Exit Keys
def input(key):
    if key == 'escape' or key == 'tab':
        app.quit()

app.run()
