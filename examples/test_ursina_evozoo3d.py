from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe
import numpy as np
import sys

# Ensure your src is in path
sys.path.insert(0, '../src')

from edpac.config.ga_config import PopulationConfigMultiTest
from multipac.parallel.parallel_zoo3d import ParallelZoo3D
from edpac.config.config_manager import save_configs
from edpac.config.constants import VISIO_SQRT_NB_NEURONS, AREA_SIZE

from edpac.config.zoo_config import MultiPacmanConfig

zoo_config = MultiPacmanConfig()

# QT components
from edpac.visualisation.multi_input_visualizer import MultiInputVisualizer
from PySide6 import QtWidgets
import sys

# 1. Setup the Qt Application context
qt_app = QtWidgets.QApplication.instance()
if not qt_app:
    qt_app = QtWidgets.QApplication(sys.argv)


# --- 1. The Agent Logic ---
class Agent(Entity):
    def __init__(self, agent_id, start_pos=(0, 1, 0)):
        self.animal_nature = "-1" if agent_id % 2 == 0 else "1"

        # Assign color based on role (Predator=Red, Prey=Green/Blue)
        ac_color = color.red if self.animal_nature == "-1" else color.blue

        super().__init__(
            model='cube',
            color=ac_color,
            position=start_pos,
            scale=(1, 2, 1),
            collider='box',          # CRITICAL: Add this for .intersects() to work
            add_to_scene_entities=True
        )

        self.agent_id = agent_id

        # Setup the "Neural Eye" (Offscreen)
        self.vision_tex = self.setup_offscreen_vision()
    #
    # def get_proximity_data(self):
    #     # Cast a ray forward to see if anything is in the way
    #     # distance=5 is the range of the "smell" or "sonar"
    #     hit_info = raycast(self.world_position + self.forward*0.6, self.forward, distance=5, ignore=(self,))
    #
    #     if hit_info.hit:
    #         return hit_info.distance / 5  # Normalized 0.0 to 1.0
    #     return 1.0  # Clear path

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
        cam_np = self.attach_new_node(cam_node)

        # OFFSET: Position camera slightly forward (0.6) so it doesn't see inside the cube
        cam_np.setPos(0, 0.4, 0.6)
        #
        # # In the __main__ block, after creating 'app'
        # cam_np.setPos(0, 50, -50)  # High up and pulled back
        # cam_np.setP(-45)          # Tilt down to look at the plane
        # cam_np.orthographic = False      # Use True if you want a technical 2D-style top-down view

        dr = buffer.make_display_region()
        dr.set_camera(cam_np)
        return tex

    def get_vision_matrix(self):
        if self.vision_tex.has_ram_image():
            data = self.vision_tex.get_ram_image_as("RGB")
            return np.frombuffer(data, dtype=np.uint8).reshape((VISIO_SQRT_NB_NEURONS, VISIO_SQRT_NB_NEURONS, 3))
        return np.zeros((VISIO_SQRT_NB_NEURONS, VISIO_SQRT_NB_NEURONS, 3), dtype=np.uint8)

# --- 2. Simulation Manager ---
class EvoSimulation(Entity):
    def __init__(self, stats_path):
        super().__init__()

        self.stats_path = stats_path
        self.time_step = 0

        # Initialize Zoo (Parallel Logic)
        pop_config=PopulationConfigMultiTest()

        pop_config.POPULATION_SIZE=4

        pop_config.INIT_PREY_POPULATION_SIZE =2

        pop_config.INIT_PREDATOR_POPULATION_SIZE =2

        self.zoo = ParallelZoo3D(pop_config)
        self.zoo.init_3D_zoo()

        self.zoo.deploy()
        self.zoo.distribute_chromosomes()
        self.zoo.initialize_all_inputs()

        # Create 3D bodies for all individuals
        self.agents = []
        for i, indiv in enumerate(self.zoo.population.individuals):
            print(indiv)

            if indiv is not None and indiv != 0:
                start_x, start_z = indiv.get_position()
                # Randomly scatter agents on the plane
                #start_x = np.random.uniform(-20, 20)
                #start_z = np.random.uniform(-20, 20)
                self.agents.append(Agent(i, start_pos=(start_x, 1, start_z)))
            else:
                self.agents.append(0)


        ####################################### MultiInputVisualizer ########################
        # multi_input_viz.setAttribute(Qt.WA_DeleteOnClose)
        # multi_input_viz.destroyed.connect(stop_everything)

        self.multi_input_viz = MultiInputVisualizer(self.zoo.population, title = "EDPac inputs", scale=4)
        self.multi_input_viz.show()

    def update(self):
        verbose = 0
        # This mirrors your "while SIMULATION_ACTIVE" loop

        if verbose > 0:
            print(f"[EvoSimulation] Step: {self.time_step}")

        if verbose > 0:
            print("[EvoSimulation] init_stats")

        self.zoo.init_stats()

        if verbose > 0:
            print("[EvoSimulation] _receive_motor_outputs")

        # 1. Collect Vision from 3D world and feed it to Zoo
        motor_outputs = self.zoo._receive_motor_outputs(verbose = verbose-1)

        if verbose > 0:
            print("[EvoSimulation] compute_movements")

        self.compute_movements(motor_outputs, verbose=verbose-1)

        if verbose > 0:
            print("[EvoSimulation] All test_all_contacts")

        self._test_all_contacts(verbose= 1)

        #TODO
        if verbose > 0:
            print("[EvoSimulation] compute_perceptions")

        results = self.compute_perceptions(verbose=verbose-1)
        #
        # if self.time_step % 5 == 0:

        if verbose > 0:
            print("[EvoSimulation] display_all_color_inputs")

        self.multi_input_viz.display_all_color_inputs(results)
        self.multi_input_viz.update_display()

        qt_app.processEvents()


        self.time_step += 1

        if self.time_step > 1000:
            sim.on_destroy()
            quit()
            return

    def compute_movements(self, motor_outputs, verbose=0):

        # 3. Apply Neural Outputs to 3D Movement
        move_speed = 1
        rot_speed = 150

        if verbose > 0:
            print(f"{motor_outputs=}")

        assert len(motor_outputs)==len(self.agents), f"Error with {len(motor_outputs)=} and {len(self.agents)=} "

        for i, (agent, out) in enumerate(zip(self.agents, motor_outputs)):

            if out is None or agent == 0:
                if verbose > 0:
                    print(f"[compute_movements] Worker {i} motor_output is None, skipping")
                continue

            if out[0] > zoo_config.MOTOR_THRESHOLD and out[1] > zoo_config.MOTOR_THRESHOLD: # Forward

                if verbose > 0:
                    print(f"[compute_movements] Worker {i} received move forward order")

                origin = agent.world_position + Vec3(0, 1, 0) + (agent.forward * 0.6)
                hit_info = raycast(origin, agent.forward, distance=5, ignore=(agent,), debug=True)

                # LOOK AHEAD: check if moving forward hits a wall
                # origin = agent.world_position + (0, 0.5, 0)
                # hit_info = raycast(origin, agent.forward, distance=1, ignore=(agent,))

                print(f"[compute_movements] Worker {i}:  {hit_info=}")
                if not hit_info.hit:

                    print(f"[compute_movements] Worker {i} move forward ")
                    move_vec = agent.forward * move_speed * time.dt
                    agent.x += move_vec.x
                    agent.y = 1  # Force it to stay above the plane
                    agent.z += move_vec.z
                else:

                    print(f"[ParallelZoo] Worker {i} hitting a wall, no move")



            elif out[0] > zoo_config.MOTOR_THRESHOLD: # Rotate Left
                print(f"[ParallelZoo] Worker {i} rotate left")
                agent.rotation_y -= rot_speed * time.dt

            elif out[1] > zoo_config.MOTOR_THRESHOLD: # Rotate Right
                print(f"[ParallelZoo] Worker {i} rotate right")
                agent.rotation_y += rot_speed * time.dt

    def _test_all_contacts(self, verbose = 0):
        for agent_id, agent in enumerate(self.agents):
            if agent == 0: continue

            # Check for overlaps with other agents
            hit_info = agent.intersects()
#
#             if verbose >0:
#                 print(f"[Test all contacts] Agent {agent_id} {hit_info=}")

            if hit_info.hit:
                other = hit_info.entity
                if isinstance(other, Agent):

                    print(f"Agent {agent.agent_id} caught Agent {other.agent_id}!")
                    # Logic: Predator (-1) hits Prey (1)
                    if agent.animal_nature == "-1" and other.animal_nature == "1":
                        #if verbose > 0:
                        print(f"Predator {agent.agent_id} caught Prey {other.agent_id}!")
                        # TODO
                        #Execute zoo logic: increase fitness, reset prey position, etc.

    def compute_perceptions(self, verbose=0):

        results = [None] * self.zoo.num_agents

        assert len(self.zoo.pipes) == len(self.agents), f"Error with {len(self.zoo.pipes)=} !=  {len(self.agents)=}"

        for i, (pipe, agent) in enumerate(zip(self.zoo.pipes, self.agents)):
            # poll(timeout) checks if data is waiting
            # timeout=0 makes it an instantaneous check

            pac = self.zoo.population.individuals[i]

            if pac == 0:

                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} is empty, continue")
                continue

            if verbose > 0:
                print(f"[ParallelZoo] Worker {i} integrate_visio_outputs")


            input_percept = agent.get_vision_matrix()


            if verbose > 0:
                print(f"[ParallelZoo] Worker {i} {input_percept.shape=}")

            results[i] = input_percept

            try:

                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} sending input_percept")

                pipe.send({'type': 'TASK', 'data': input_percept})
            except BrokenPipeError:

                print(f"BrokenPipeError, {input_percept=}")

        return results

    def on_destroy(self):
        # Shutdown logic when window closes
        self.zoo.shutdown()
        self.zoo.save_stats(self.stats_path)
        self.zoo.population.save_individuals(self.stats_path)
        save_configs(self.stats_path)

        if hasattr(self, 'multi_input_viz'):
            self.multi_input_viz.close()

        print("Simulation Saved and Shutdown.")

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


    # Start Simulation
    sim = EvoSimulation(args.stats_path)

    # Use the Ursina wrapper 'camera', NOT a NodePath
    camera.orthographic = True
    camera.position = (0, 100, 0)
    camera.rotation_x = 90
    camera.fov = 100  # In ortho mode, FOV acts as the zoom level

    # Increase the range of what the camera can see
    camera.clip_plane_far = 500  # Default is often 100
    camera.clip_plane_near = 0.1


    def input(key):
        if key == 'escape':
            sim.on_destroy()
            quit()

    app.run()

