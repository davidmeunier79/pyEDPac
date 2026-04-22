from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe
import numpy as np
import sys

# Ensure your src is in path
sys.path.insert(0, '../src')

from edpac.config.ga_config import PopulationConfigMultiTest
from edpac.config.config_manager import save_configs
from edpac.config.constants import VISIO_SQRT_NB_NEURONS, AREA_SIZE

from edpac.config.zoo_config import MultiPacmanConfig

zoo_config = MultiPacmanConfig()

# QT components
from edpac.visualisation.multi_input_visualizer import MultiInputVisualizer


from multipac.parallel.parallel_zoo3d import ParallelZoo3D
from multipac.zoo3d.agent import Agent


from PySide6 import QtWidgets
import sys

# 1. Setup the Qt Application context
qt_app = QtWidgets.QApplication.instance()
if not qt_app:
    qt_app = QtWidgets.QApplication(sys.argv)


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
        #
            if out is None or agent == 0:
                if verbose > 0:
                    print(f"[compute_movements] Worker {i} motor_output is None, skipping")
                continue

            if len(out) == 0:
                #if verbose > 0:
                print(f"[compute_movements] Worker {i} _process_death")
                self._process_death(i)
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


            #### Moving head direction as well

            if out[2] > zoo_config.MOTOR_THRESHOLD and out[3] > zoo_config.MOTOR_THRESHOLD: # Realign dir head to dir body

                #if verbose > 0:
                print(f"[compute_movements] Worker {i} received align head order")
                agent.head.rotation_y = 0


            elif out[2] > zoo_config.MOTOR_THRESHOLD: # Rotate Head Left
                print(f"[ParallelZoo] Worker {i} rotate left")
                agent.head.rotation_y -= rot_speed * time.dt

            elif out[3] > zoo_config.MOTOR_THRESHOLD: # Rotate Head Right
                print(f"[ParallelZoo] Worker {i} rotate right")
                agent.head.rotation_y += rot_speed * time.dt


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

    def _process_death(self, pacman_index, verbose=0):

        assert 0 < pacman_index and pacman_index < len(self.agents), f"Error, wrong {pacman_index=} {len(self.agents)=}"

        agent = self.agents[pacman_index]
        if agent == 0:
            print(f"*Agent {pacman_index} is already set to 0")

        else:
            destroy(agent)

        # 3. Reference cleanup
        # We set it to 0 to maintain the list indices (matching worker IDs)
        self.agents[pacman_index] = 0

        if verbose > 0:
            print(f"Agent {pacman_index} has been removed from the simulation.")

        self.zoo._remove_individual(pacman_index, verbose=verbose-1)

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

