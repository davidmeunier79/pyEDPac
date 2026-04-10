import multiprocessing as mp
import numpy as np

import sys
sys.path.insert(0, '../src')


from edpac.config.constants import NB_VISIO_INPUTS, MINIMAL_TIME
from edpac.config.network_config import NetworkConfig
from edpac.config.ga_config import PopulationConfig

#from edpac.genetic_algorithm.pacman_population import PacmanParallelZoo

from edpac.zoo.evo_zoo import EvoZoo

from multipac.parallel.parallel_network import worker_loop

# --- The Centralized ParallelZoo ---
class ParallelZoo(EvoZoo):
    def __init__(self, pop_config : PopulationConfig = None):
        self.pop_config = pop_config or PopulationConfig()
        super().__init__(self.pop_config)

        self.num_agents = self.pop_config.POPULATION_SIZE
        self.pipes = []
        self.processes = []


    def deploy(self):
        print(f"[ParallelZoo] Deploying {self.num_agents} individuals...")
        for i in range(self.num_agents):
            parent_conn, child_conn = mp.Pipe()
            p = mp.Process(target=worker_loop, args=(child_conn, i))
            p.start()
            self.pipes.append(parent_conn)
            self.processes.append(p)

    def distribute_chromosomes(self):
        print("[ParallelZoo] Sending chromosomes to workers...")
        for i, pipe in enumerate(self.pipes):
            # Pass the specific chromosome for this ID
            if not self.population.individuals[i]:
                continue

            print(f"[ParallelZoo] sending chrosomose to Worker {i} ")
            pipe.send({'type': 'SET_CHROMOSOME', 'data': self.population.individuals[i]})

        #
        # # Synchronize: Wait for all "READY" signals
        # for i, pipe in enumerate(self.pipes):
        #
        #     if not self.population.individuals[i]:
        #         continue
        #
        #     response = pipe.recv()
        #     if response['type'] == 'READY':
        #         print(f"[ParallelZoo] Confirmed: Worker {response['id']} chromosome is ready.")


    def initialize_all_inputs(self):
        print("[ParallelZoo] Sending INIT_INPUTS to workers...")
        for i, pipe in enumerate(self.pipes):
            if not self.population.individuals[i]:
                continue

            # Pass the specific chromosome for this ID
            pipe.send({'type': 'INIT_INPUTS'})

            print(f"[ParallelZoo] Waiting Worker {i} INIT_INPUTS")
        #
        # # Synchronize: Wait for all "READY" signals
        # for i, pipe in enumerate(self.pipes):
        #     if not self.population.individuals[i]:
        #         continue
        #
        #     response = pipe.recv()
        #     if response['type'] == 'READY':
        #         print(f"[ParallelZoo] Confirmed: Worker {response['id']} is initialized.")
        #

    def send_death_signal(self, pacman_index):
        assert 0 <= pacman_index and pacman_index < len(self.pipes), f"Error with {pacman_index=} in pipes"

        pipe = self.pipes[pacman_index]
        pipe.send({'type': 'DEAD_CHROMOSOME', 'data': pacman_index})

        print(f"[ParallelZoo] Waiting Worker {pacman_index} DEAD_CHROMOSOME")

        wait_response = True

        while wait_response:
            print(f"[ParallelZoo] Confirmed: Worker {pacman_index} waiting DEAD_CHROMOSOME response.")
            response = pipe.recv()
            if response['type'] == 'READY':
                print(f"[ParallelZoo] Confirmed: Worker {response['id']} is DEAD_CHROMOSOME.")
                wait_response = False
            else:
                print(f"*[ParallelZoo] Not Confirmed DEAD_CHROMOSOME: Worker send {response=} ")

    def send_chromosome(self, pacman_index):
        assert 0 <= pacman_index and pacman_index < len(self.pipes), f"Error with {pacman_index=} in pipes"
        assert  self.population.individuals[pacman_index], f"Error, sending empty chromosome {pacman_index}"

        pipe = self.pipes[pacman_index]
        pipe.send({'type': 'SET_CHROMOSOME', 'data': self.population.individuals[pacman_index]})

        print(f"[ParallelZoo] sending chrosomose to Worker {pacman_index} ")

        #
        # wait_response = True
        #
        # while wait_response:
        #     print(f"[ParallelZoo] Confirmed: Worker {pacman_index} waiting SET_CHROMOSOME response.")
        #     response = pipe.recv()
        #     if response['type'] == 'READY':
        #         print(f"[ParallelZoo] Confirmed: Worker {response['id']} is SET_CHROMOSOME.")
        #         wait_response = False
        #     else:
        #         print(f"*[ParallelZoo] Not Confirmed SET_CHROMOSOME: Worker send {response=} ")

    # def send_init_input(self, pacman_index):
    #     assert 0 <= pacman_index and pacman_index < len(self.pipes), f"Error with {pacman_index=} in pipes"
    #
    #     assert  self.population.individuals[pacman_index], f"Error, empty individual {pacman_index} sending INIT_INPUTS "

        print(f"[ParallelZoo] Sending New Worker {pacman_index} INIT_INPUTS")
        pipe = self.pipes[pacman_index]
        pipe.send({'type': 'INIT_INPUTS'})

#
#         response = pipe.recv()
#         if response['type'] == 'READY':
#             print(f"[ParallelZoo] Confirmed: New Worker {response['id']} is initialized.")
#

    def run_one_non_blocking_step(self, timeout=0.001):
        """
        Collects outputs from all workers without
        locking the Master process.
        """
        results = [None] * self.num_agents

        for i, pipe in enumerate(self.pipes):
            # poll(timeout) checks if data is waiting
            # timeout=0 makes it an instantaneous check

            percept = 0

            if pipe.poll(timeout):
                try:
                    res = pipe.recv()
                    if res['type'] != 'RESULT':
                        continue

                    if len(res['data']):

                        if self.population.individuals[i]==0:
                            percept=-1
                        else:

                            pos = self.population.individuals[i].integrate_motor_outputs(res['data'])

                            if pos:
                                print(f"**** Move forward for agent {i}")
                                self._move_forward(i)
                    else:
                        self.process_death(i)
                        percept = -1

                    if percept != -1:

                        # computing contacts
                        res = self.test_contacts(i)

                        if not res:
                            continue

                        percept = self.compute_percept(i)

                        results[i] = percept

                    if percept:
                        try:
                            pipe.send({'type': 'TASK', 'data': percept})

                        except BrokenPipeError:

                            print(f"{percept=}")


                except EOFError:
                    print(f"[Zoo] Worker {i} pipe closed unexpectedly!")
            else:
                # Optional: Handle the "Lagging Agent" case
                # Maybe use the previous frame's command or stay still
                results[i] = None

            pac = self.population.individuals[i]

            if pac:

                pac.fitness = pac.get_life_points()
                pac.fitness_evaluated = True

                if pac.get_animal_nature() == "-1":
                    self.stats["mean_predator_fitness"][-1] += pac.get_fitness()
                    self.stats["nb_predators"][-1] +=1
                elif pac.get_animal_nature() == "1":
                    self.stats["mean_prey_fitness"][-1] += pac.get_fitness()
                    self.stats["nb_preys"][-1] +=1


                # naturally losing life each time points
                pac.add_life_points(-1)

                if pac.get_life_points() < 0:
                    #self.init_new_individual(pacman_index)
                    self.process_death(i)

            nb_added_pacgums = self.add_random_pacgums()
            self.stats["nb_added_pacgums"][-1] += nb_added_pacgums

        return results

    def send_first_wave(self, visio_inputs):
        assert len(visio_inputs) == len(self.pipes), f"Error with visio_inputs {len(visio_inputs)=} == {len(self.pipes)=}"

        for pipe, visio_input in zip(self.pipes, visio_inputs):
            #print(visio_input)

            try:
                pipe.send({'type': 'TASK', 'data': visio_input})

            except BrokenPipeError:
                if visio_input == -1:
                    print("Dead visio inputs")
                elif visio_input == 1:
                    print("Empty visio inputs")

                print(f"{visio_input=}")
        #print(f"[ParallelZoo] Agent {i} moved")



    def run_one_step(self, visio_inputs):

        #print("\n[ParallelZoo] Running a test neural computation step...")

        assert len(visio_inputs) == len(self.pipes), f"Error with visio_inputs {len(visio_inputs)=} == {len(self.pipes)=}"

        for pipe, visio_input in zip(self.pipes, visio_inputs):
            #print(visio_input)

            try:
                pipe.send({'type': 'TASK', 'data': visio_input})

            except BrokenPipeError:

                print(f"{visio_input=}")

        move_pos = {}

        for i, pipe in enumerate(self.pipes):
            res = pipe.recv()
            #print(f"[ParallelZoo] Agent {i} computed result: {res['data']}")

            if len(res['data']):
                pos = self.population.individuals[i].integrate_motor_outputs(res['data'])

                if pos:
                    print(f"**** Move forward for agent {i}")
                    move_pos[i] = pos
            else:
                move_pos[i] = -1

        return move_pos

        #print(f"[ParallelZoo] Agent {i} moved")


    def shutdown(self):
        print("\n[ParallelZoo] Terminating simulation.")
        for pipe in self.pipes:
            pipe.send({'type': 'TERMINATE'})
        for p in self.processes:
            p.join()





