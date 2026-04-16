from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe
import numpy as np
import sys

# Ensure your src is in path
sys.path.insert(0, '../src')

from edpac.config.ga_config import PopulationConfigMultiTest
from multipac.parallel.parallel_zoo import ParallelZoo
from edpac.config.config_manager import save_configs
from edpac.config.constants import VISIO_SQRT_NB_NEURONS

from edpac.config.zoo_config import MultiPacmanConfig

zoo_config = MultiPacmanConfig()



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
            add_to_scene_entities=True
        )

        self.agent_id = agent_id

        # Setup the "Neural Eye" (Offscreen)
        self.vision_tex = self.setup_offscreen_vision()

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

        self.zoo = ParallelZoo(pop_config)
        self.zoo.init_empty_zoo()
        self.zoo.deploy()
        self.zoo.distribute_chromosomes()
        self.zoo.initialize_all_inputs()

        # Create 3D bodies for all individuals
        self.agents = []
        for i, indiv in enumerate(self.zoo.population.individuals):
            print(indiv)

            if indiv:
                start_x, start_z = indiv.get_position()
                # Randomly scatter agents on the plane
                #start_x = np.random.uniform(-20, 20)
                #start_z = np.random.uniform(-20, 20)
                self.agents.append(Agent(i, start_pos=(start_x, 1, start_z)))
            else:
                self.agents.append(0)

    def update(self):
        # This mirrors your "while SIMULATION_ACTIVE" loop
        print(f"Step: {self.time_step}")


        self.zoo.init_stats()

        # 1. Collect Vision from 3D world and feed it to Zoo
        motor_outputs = self.zoo._receive_motor_outputs(verbose = 1)

        #print(motor_outputs )

        self.compute_movements(motor_outputs, verbose=1)

        #TODO
        # if verbose > 0:
        #     print("[ParallelZoo] All test_all_contacts")
        #
        # self._test_all_contacts(verbose=verbose-1)

        self.compute_perceptions(verbose=1)


        self.time_step += 1

        if self.time_step > 1000:
            sim.on_destroy()
            return

    def compute_movements(self, motor_outputs, verbose=0):

        # 3. Apply Neural Outputs to 3D Movement
        move_speed = 10
        rot_speed = 150

        if verbose > 0:
            print(f"{motor_outputs=}")

        assert len(motor_outputs)==len(self.agents), f"Error with {len(motor_outputs)=} and {len(self.agents)=} "

        for i, (agent, out) in enumerate(zip(self.agents, motor_outputs)):

            if out is None:
                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} motor_output is None, skipping")
                continue

            if out[0] > zoo_config.MOTOR_THRESHOLD and out[1] > zoo_config.MOTOR_THRESHOLD: # Forward
                print(f"[ParallelZoo] Worker {i} move forward")
                agent.position += agent.forward * move_speed * time.dt

            elif out[0] > zoo_config.MOTOR_THRESHOLD: # Rotate Left
                print(f"[ParallelZoo] Worker {i} rotate left")
                agent.rotation_y -= rot_speed * time.dt

            elif out[1] > zoo_config.MOTOR_THRESHOLD: # Rotate Right
                print(f"[ParallelZoo] Worker {i} rotate right")
                agent.rotation_y += rot_speed * time.dt





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
        print("Simulation Saved and Shutdown.")

# --- 3. Run Script ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats_path", type=str, required=True)
    args = parser.parse_args()

    app = Ursina()

    # Environment Setup
    Sky()
    Entity(model='plane', scale=100, texture='white_cube', texture_scale=(100,100), color=color.light_gray)

    # Start Simulation
    sim = EvoSimulation(args.stats_path)

    def input(key):
        if key == 'escape':
            sim.on_destroy()
            app.quit()


    app.run()
