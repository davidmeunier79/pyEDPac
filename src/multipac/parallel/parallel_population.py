import multiprocessing as mp
import numpy as np

import sys
sys.path.insert(0, '../src')


from edpac.config.constants import NB_VISIO_INPUTS, MINIMAL_TIME
from edpac.config.network_config import NetworkConfig
from edpac.config.ga_config import PopulationConfig

from edpac.genetic_algorithm.pacman_population import PacmanPopulation

from multipac.parallel.parallel_network import worker_loop

# --- The Centralized Population ---
class ParallelPopulation(PacmanPopulation):
    def __init__(self, pop_config : PopulationConfig = None):
        self.pop_config = pop_config or PopulationConfig()

        self.num_agents = self.pop_config.POPULATION_SIZE
        self.pipes = []
        self.processes = []

        super().__init__(pop_config)

    def deploy(self):
        print(f"[Population] Deploying {self.num_agents} individuals...")
        for i in range(self.num_agents):
            parent_conn, child_conn = mp.Pipe()
            p = mp.Process(target=worker_loop, args=(child_conn, i))
            p.start()
            self.pipes.append(parent_conn)
            self.processes.append(p)

    def distribute_chromosomes(self):
        print("[Population] Sending chromosomes to workers...")
        for i, pipe in enumerate(self.pipes):
            # Pass the specific chromosome for this ID
            pipe.send({'type': 'SET_CHROMOSOME', 'data': self.individuals[i]})

            print(f"[ParallelPopulation] Waiting Worker {i}")

        # Synchronize: Wait for all "READY" signals
        for i, pipe in enumerate(self.pipes):
            response = pipe.recv()
            if response['type'] == 'READY':
                print(f"[ParallelPopulation] Confirmed: Worker {response['id']} chromosome is ready.")


    def initialize_all_inputs(self):
        print("[Population] Sending INIT_INPUTS to workers...")
        for i, pipe in enumerate(self.pipes):
            # Pass the specific chromosome for this ID
            pipe.send({'type': 'INIT_INPUTS'})

            print(f"[ParallelPopulation] Waiting Worker {i} INIT_INPUTS")

        # Synchronize: Wait for all "READY" signals
        for i, pipe in enumerate(self.pipes):
            response = pipe.recv()
            if response['type'] == 'READY':
                print(f"[ParallelPopulation] Confirmed: Worker {response['id']} is initialized.")


    def send_chromosome(self, pacman_index):
        assert 0 <= pacman_index and pacman_index < len(self.pipes), f"Error with {pacman_index=} in pipes"

        pipe = self.pipes[pacman_index]
        pipe.send({'type': 'SET_CHROMOSOME', 'data': self.individuals[pacman_index]})

        print(f"***** [ParallelPopulation] Waiting New Worker {pacman_index} SET_CHROMOSOME")

        response = pipe.recv()
        if response['type'] == 'READY':
            print(f"***** [ParallelPopulation] Confirmed: New Worker {response['id']} is initialized.")


    def send_init_input(self, pacman_index):
        assert 0 <= pacman_index and pacman_index < len(self.pipes), f"Error with {pacman_index=} in pipes"

        pipe = self.pipes[pacman_index]
        pipe.send({'type': 'INIT_INPUTS'})

        print(f"***** [ParallelPopulation] Waiting New Worker {pacman_index} INIT_INPUTS")

        response = pipe.recv()
        if response['type'] == 'READY':
            print(f"***** [ParallelPopulation] Confirmed: New Worker {response['id']} is initialized.")


    def run_one_step(self, visio_inputs):
        #print("\n[ParallelPopulation] Running a test neural computation step...")
        #test_input = [np.zeros(shape=(NetworkConfig.VISIO_SQRT_NB_NEURONS, NetworkConfig.VISIO_SQRT_NB_NEURONS)) for i in range(NB_VISIO_INPUTS)]

        assert len(visio_inputs) == len(self.pipes), f"Error with visio_inputs {visio_inputs}"

        for pipe, visio_input in zip(self.pipes, visio_inputs):
            #print(visio_input)
#
#             if visio_input == -1:
#                 print("Dead visio inputs")
#             elif visio_input == 1:
#                 print("Empty visio inputs")

            #print(f"{visio_input=}")
            pipe.send({'type': 'TASK', 'data': visio_input})


        move_pos = {}

        for i, pipe in enumerate(self.pipes):
            res = pipe.recv()
            #print(f"[ParallelPopulation] Agent {i} computed result: {res['data']}")

            if len(res['data']):
                pos = self.individuals[i].integrate_motor_outputs(res['data'])

                if pos:
                    print(f"**** Move forward for agent {i}")
                    move_pos[i] = pos
            else:
                move_pos[i] = -1

        return move_pos

        #print(f"[ParallelPopulation] Agent {i} moved")


    def shutdown(self):
        print("\n[ParallelPopulation] Terminating simulation.")
        for pipe in self.pipes:
            pipe.send({'type': 'TERMINATE'})
        for p in self.processes:
            p.join()


