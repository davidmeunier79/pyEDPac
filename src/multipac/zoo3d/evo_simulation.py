from ursina import *
from panda3d.core import GraphicsOutput, Texture, Camera as PandaCamera, FrameBufferProperties, WindowProperties, GraphicsPipe
import numpy as np
import random
import sys
import pathlib
import os

# Ensure your src is in path
sys.path.insert(0, '../src')

from edpac.config.ga_config import PopulationConfigMulti
from edpac.config.config_manager import save_configs
from edpac.config.constants import VISIO_SQRT_NB_NEURONS, AREA_SIZE

from edpac.config.zoo_config import MultiPacmanConfig, UrsinaConfig

zoo_config = MultiPacmanConfig()

# QT components
from edpac.visualisation.multi_input_visualizer import MultiInputVisualizer


from multipac.parallel.parallel_zoo3d import ParallelZoo3D
from multipac.zoo3d.agent import Agent


from PySide6 import QtWidgets
import sys

def add_wall_crosses(parent_wall, is_horizontal=True, x_density=0.5, wall_height=5.0):
    # Create a thin plane slightly offset from the wall surface to avoid z-fighting

    cross_overlay = Entity(
        parent=parent_wall,
        model='quad',
        texture='close.png', # Ensure you have a cross.png or use 'close_button'
        color=color.white,
        # Scale the texture so it repeats based on the wall dimensions
        texture_scale=(parent_wall.scale_x * x_density if is_horizontal else parent_wall.scale_z * x_density,
                       wall_height * x_density),
        double_sided=True
    )
    return cross_overlay


# --- 2. Simulation Manager ---
class EvoSimulation(Entity):
    def __init__(self, stats_path, ursina_config : UrsinaConfig = None, pop_config : PopulationConfigMulti = None):
        super().__init__()


        self.ursina_config = ursina_config or UrsinaConfig()

        self.stats_path = stats_path
        self.time_step = 0

        self.zoo = ParallelZoo3D(pop_config)
        self.zoo.init_3D_zoo()

        self.zoo.deploy()
        self.zoo.distribute_chromosomes()
        self.zoo.initialize_all_inputs()

        # Create 3D bodies for all individuals
        self._init_all_agents()

        ####################################### MultiInputVisualizer ########################
        # multi_input_viz.setAttribute(Qt.WA_DeleteOnClose)
        # multi_input_viz.destroyed.connect(stop_everything)

        self.multi_input_viz = MultiInputVisualizer(self.zoo.population, title = "EDPac inputs", scale=2)
        self.multi_input_viz.show()

    def _init_all_agents(self):
        self.agents = []

        for i, indiv in enumerate(self.zoo.population.individuals):
            print(indiv)

            if indiv is not None and indiv != 0:
                start_x, start_z = indiv.get_position()
                rot_body = random.uniform(0, 360)
                self.agents.append(Agent(i, start_pos=(start_x, 1, start_z), start_rot = rot_body, proximity_range=self.ursina_config.PROXIMITY_RANGE))
            else:
                self.agents.append(0)

    def _init_new_agent(self, new_agent_index):
        #TODO use with _init_all_agents
        assert 0 <= new_agent_index and new_agent_index < len(self.zoo.population.individuals),\
            f"***Error with 0 <= {new_agent_index} < {len(self.zoo.population.individuals)=} "

        assert 0 <= new_agent_index and new_agent_index < len( self.agents),\
            f"***Error with 0 <= {new_agent_index} < {len(self.agents)=} "

        indiv = self.zoo.population.individuals[new_agent_index]

        if indiv != 0:
            start_x, start_z = indiv.get_position()
            if self.agents[new_agent_index] == 0:
                self.agents[new_agent_index] = Agent(new_agent_index, start_pos=(start_x, 1, start_z))
            else:
                print(f"**Error, Agent {new_agent_index} should be 0 (not inited)")
        else:
            print(f"**Error, {indiv=} should not be 0")

    def update(self):
        verbose = 0

        print(f"******************** {self.time_step=} ***********************")

        if verbose > 0:
            print("[EvoSimulation] init_stats")

        self.zoo.init_stats()
        self.zoo.stats["time"][-1] = self.time_step

        if verbose > 0:
            print("[EvoSimulation] _receive_motor_outputs")

        # 1. Collect Vision from 3D world and feed it to Zoo
        motor_outputs = self.zoo._receive_motor_outputs(verbose = verbose-1)

        if verbose > 0:
            print("[EvoSimulation] compute_movements")

        self.compute_movements(motor_outputs, verbose=1)

        if verbose > 0:
            print("[EvoSimulation] All test_all_contacts")

        self._test_all_contacts(verbose= 1)

        #TODO
        if verbose > 0:
            print("[EvoSimulation] compute_perceptions")

        results = self.compute_perceptions(verbose=0)
        #
        # if self.time_step % 5 == 0:

        if verbose > 0:
            print("[EvoSimulation] display_all_color_inputs")

        qt_app = QtWidgets.QApplication.instance()
        if qt_app :
            self.multi_input_viz.display_all_color_inputs(results, verbose=verbose-1)
            self.multi_input_viz.update_display()
            qt_app.processEvents()


        nb_alive_indiv = self.zoo.compute_all_stats()

        self.time_step += 1

        if nb_alive_indiv==0:
            on_destroy()
            quit()
            return

    def compute_movements(self, motor_outputs, verbose=0):

        # 3. Apply Neural Outputs to 3D Movement

        dt = min(time.dt, self.ursina_config.MAX_REF_FRAME_REFRESH)
        #dt = time.dt
        #print(f"{time.dt=}, {dt=}")

        if verbose > 1:
            print(f"{motor_outputs=}")

        assert len(motor_outputs)==len(self.agents), f"Error with {len(motor_outputs)=} and {len(self.agents)=} "

        for i, (agent, out, pac) in enumerate(zip(self.agents, motor_outputs, self.zoo.population.individuals)):
        #
            if out is None or agent == 0 or pac == 0:
                if verbose > 1:
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
                hit_info = raycast(origin, agent.forward, distance=self.ursina_config.RAY_CAST_DISTANCE, debug=True)

                # LOOK AHEAD: check if moving forward hits a wall
                # origin = agent.world_position + (0, 0.5, 0)
                # hit_info = raycast(origin, agent.forward, distance=1, ignore=(agent,))


                if verbose > 1:
                    print(f"[compute_movements] Worker {i}:  {hit_info=}")

                if not hit_info.hit:

                    #if verbose > 0:
                    print(f"[compute_movements] *** Worker {i} move forward (no obstacle)")
                    move_vec = agent.forward * self.ursina_config.URSINA_MOVE_SPEED * dt
                    agent.x += move_vec.x
                    agent.y = 1  # Force it to stay above the plane
                    agent.z += move_vec.z
                    pac.eat_pacgum()
                    self.zoo.stats["nb_eaten_pacgums"][-1] += 1


                else:

                    no_wall = True

                    for other in hit_info.entities:

                        if isinstance(other, Agent):

                            ## other pac
                            assert 0 <= other.agent_id and other.agent_id < len(self.zoo.population.individuals), f"*Error with {other.agent_id=}"
                            other_pac = self.zoo.population.individuals[other.agent_id]

                            assert other_pac != 0, f"*Error, find agent {other.agent_id=} but no {other_pac=}"

                            if pac.get_nature == "-1" and other_pac.get_nature() == "1":

                                print(f"[compute_movements] *** Worker {i} eating prey {other.agent_id}")
                                pac.eat_prey(other_pac.get_life_points())
                                self._process_death(other.agent_id)
                                self.zoo.stats["nb_eaten_preys"][-1] += 1


                        else:
                            #if verbose > 0:
                            print(f"*[compute_movements] Worker {i} hitting a wall, no move")
                            no_wall = False

                    if no_wall == True:

                        #if verbose > 0:
                        print(f"[compute_movements] *** Worker {i} move forward")
                        move_vec = agent.forward * self.ursina_config.URSINA_MOVE_SPEED * dt
                        agent.x += move_vec.x
                        agent.y = 1  # Force it to stay above the plane
                        agent.z += move_vec.z

                        pac.eat_pacgum()
                        self.zoo.stats["nb_eaten_pacgums"][-1] += 1

            elif out[0] > zoo_config.MOTOR_THRESHOLD: # Rotate Left

                if verbose > 0:
                    print(f"[compute_movements] Worker {i} rotate left")
                agent.rotation_y -= self.ursina_config.URSINA_ROT_SPEED * dt
                agent.head.rotation_y -= self.ursina_config.URSINA_ROT_SPEED * dt

            elif out[1] > zoo_config.MOTOR_THRESHOLD: # Rotate Right

                if verbose > 0:
                    print(f"[compute_movements] Worker {i} rotate right")
                agent.rotation_y += self.ursina_config.URSINA_ROT_SPEED * dt
                agent.head.rotation_y += self.ursina_config.URSINA_ROT_SPEED * dt

            #### Moving head direction as well
            if out[2] > zoo_config.MOTOR_THRESHOLD and out[3] > zoo_config.MOTOR_THRESHOLD: # Realign dir head to dir body
                if verbose > 0:
                    print(f"[compute_movements] Worker {i} received align head order")
                agent.head.rotation_y = 0

            elif out[2] > zoo_config.MOTOR_THRESHOLD: # Rotate Head Left

                if verbose > 0:
                    print(f"[compute_movements] Worker {i} head rotate left")
                agent.head.rotation_y -= self.ursina_config.URSINA_ROT_SPEED * dt

            elif out[3] > zoo_config.MOTOR_THRESHOLD: # Rotate Head Right

                if verbose > 0:
                    print(f"[compute_movements] Worker {i} head rotate right")
                agent.head.rotation_y += self.ursina_config.URSINA_ROT_SPEED * dt


    def _test_all_contacts(self, verbose = 0):

        for agent_id, (agent, pac) in enumerate(zip(self.agents, self.zoo.population.individuals)):

            if (agent == 0 or pac == 0):

                if agent != pac :
                    print(f"***Error [_test_all_contacts] Agent and Indiv {agent_id} are not dead together {agent=} != {pac=}")

                continue

            # Check for overlaps with other agents
            hit_info = agent.intersects()

            if hit_info.hit:

                if verbose > 1:
                    print(f"[_test_all_contacts] Agent {agent_id} {hit_info=}")

                other = hit_info.entity
                if isinstance(other, Agent):


                    if verbose > 1:
                        print(f"[_test_all_contacts] Agent {agent.agent_id} intersect Agent {other.agent_id}!")
                    # Logic: Predator (-1) hits Prey (1)

                    if agent.animal_nature == "-1" and other.animal_nature == "1":
                        if verbose > 0:
                            print(f"[_test_all_contacts] Predator {agent.agent_id} biting Prey {other.agent_id}!")
                        pac.bite_prey()

                    elif agent.animal_nature == "1" and other.animal_nature == "-1":
                        if verbose > 0:
                            print(f"[_test_all_contacts] Prey {agent.agent_id} contact Predator {other.agent_id}!")
                        pac.predator_contact()


                    elif agent.animal_nature == "1" and other.animal_nature == "1":
                        if verbose > 1:
                            print(f"[_test_all_contacts] Testing reproduction between preys: {agent.agent_id} and {other.agent_id}!")
                        new_agent_index = self.zoo.test_prey_reproduction(agent.agent_id, other.agent_id)
                        if new_agent_index != -1:
                            self._init_new_agent(new_agent_index)

                    elif agent.animal_nature == "-1" and other.animal_nature == "-1":
                        if verbose > 1:
                            print(f"[_test_all_contacts] Testing reproduction between predators: {agent.agent_id} and {other.agent_id}!")
                        new_agent_index = self.zoo.test_predator_reproduction(agent.agent_id, other.agent_id)
                        if new_agent_index != -1:
                            self._init_new_agent(new_agent_index)

            # naturally losing life each time points
            pac.add_life_points(-1)

            if pac.get_life_points() < 0:
                self._process_death(agent_id)
                continue

            # test if position is outside the zoo3d
            position = agent.get_position()

            if position[1] == 1 and \
                    (-AREA_SIZE//2 <= position[0] and position[0] <= AREA_SIZE//2) and \
                    (-AREA_SIZE//2 <= position[2] and position[2] <= AREA_SIZE//2):

                if verbose > 2:
                    print(f"Position {position=} is acceptable")

            else:
                print(f"**Error, {position=}, killing individual {agent_id=}")
                self._process_death(agent_id)


    def compute_perceptions(self, verbose=0):

        results = [None] * self.zoo.num_agents

        assert len(self.zoo.pipes) == len(self.agents), f"Error with {len(self.zoo.pipes)=} !=  {len(self.agents)=}"

        for i, (pipe, agent) in enumerate(zip(self.zoo.pipes, self.agents)):
            # poll(timeout) checks if data is waiting
            # timeout=0 makes it an instantaneous check

            pac = self.zoo.population.individuals[i]

            if pac == 0 or agent == 0:

                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} is empty, continue")
                continue

            if verbose > 0:
                print(f"[ParallelZoo] Worker {i} integrate_visio_outputs")


            input_percept = agent.get_vision_matrix()


            if verbose > 0:
                print(f"[ParallelZoo] Worker {i} {input_percept.shape=}")

            results[i] = [input_percept]

            try:

                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} sending input_percept")

                pipe.send({'type': 'TASK', 'data': input_percept})
            except BrokenPipeError:

                print(f"BrokenPipeError, {input_percept=}")

        return results

    def _process_death(self, pacman_index, verbose=0):

        assert 0 <= pacman_index and pacman_index < len(self.agents), f"Error, wrong {pacman_index=} {len(self.agents)=}"

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

        self.zoo.stats["nb_deads"][-1] += 1

    def on_destroy(self):
        # Shutdown logic when window closes
        self.zoo.shutdown()
        self.zoo.save_stats(self.stats_path)
        self.zoo.population.save_individuals(self.stats_path)
        save_configs(self.stats_path)

        if hasattr(self, 'multi_input_viz'):
            self.multi_input_viz.close()

        print("Simulation Saved and Shutdown.")
