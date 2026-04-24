

import multiprocessing as mp
import numpy as np

import sys
sys.path.insert(0, '../src')


from edpac.config.constants import NB_VISIO_INPUTS, MINIMAL_TIME
from edpac.config.network_config import NetworkConfig
from edpac.config.ga_config import PopulationConfig

#from edpac.genetic_algorithm.pacman_population import PacmanParallelZoo

from multipac.zoo3d.evo_zoo3d import EvoZoo3D

from multipac.parallel.parallel_network import worker_loop

# --- The Centralized ParallelZoo ---
class ParallelZoo3D(EvoZoo3D):
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
            p = mp.Process(target=worker_loop, args=(child_conn, i, 0))
            p.start()
            self.pipes.append(parent_conn)
            self.processes.append(p)

    def distribute_chromosomes(self):
        print("[ParallelZoo] Sending SET_CHROMOSOME to workers...")
        for i, pipe in enumerate(self.pipes):
            # Pass the specific chromosome for this ID
            if not self.population.individuals[i]:
                continue

            print(f"[ParallelZoo] sending chrosomose to Worker {i} ")
            pipe.send({'type': 'SET_CHROMOSOME', 'data': self.population.individuals[i]})

        # Synchronize: Wait for all "READY" signals
        print("[ParallelZoo] Waiting workers to be READY...")
        for i, pipe in enumerate(self.pipes):

            if not self.population.individuals[i]:
                continue

            response = pipe.recv()
            if response['type'] == 'READY':
                print(f"[ParallelZoo] Confirmed: Worker {response['id']} chromosome is ready.")

    def initialize_all_inputs(self):
        print("[ParallelZoo] Sending INIT_INPUTS to workers...")
        for i, pipe in enumerate(self.pipes):
            if not self.population.individuals[i]:
                continue

            print(f"[ParallelZoo] Worker {i} INIT_INPUTS")
            # Pass the specific chromosome for this ID
            pipe.send({'type': 'INIT_INPUTS'})


    def _send_death_signal(self, pacman_index):
        assert 0 <= pacman_index and pacman_index < len(self.pipes), f"Error with {pacman_index=} in pipes"

        pipe = self.pipes[pacman_index]
        pipe.send({'type': 'DEAD_CHROMOSOME', 'data': pacman_index})

        print(f"[ParallelZoo] Sending Worker {pacman_index} DEAD_CHROMOSOME")


    def _send_chromosome(self, pacman_index):
        assert 0 <= pacman_index and pacman_index < len(self.pipes), f"Error with {pacman_index=} in pipes"
        assert  self.population.individuals[pacman_index], f"Error, sending empty chromosome {pacman_index}"

        pipe = self.pipes[pacman_index]
        pipe.send({'type': 'SET_CHROMOSOME', 'data': self.population.individuals[pacman_index]})

        print(f"[ParallelZoo] sending chrosomose to Worker {pacman_index} ")

        wait_response = True

        while wait_response:
            print(f"[ParallelZoo] Confirmed: Worker {pacman_index} waiting SET_CHROMOSOME response.")
            response = pipe.recv()
            if response['type'] == 'READY':
                print(f"[ParallelZoo] Confirmed: Worker {response['id']} is SET_CHROMOSOME.")
                wait_response = False
            else:
                print(f"*[ParallelZoo] Not Confirmed SET_CHROMOSOME: Worker send {response=} ")


        print(f"[ParallelZoo] Sending New Worker {pacman_index} INIT_INPUTS")
        pipe = self.pipes[pacman_index]
        pipe.send({'type': 'INIT_INPUTS'})

    def _remove_individual(self, pacman_index, verbose=0):

        assert 0 < pacman_index and pacman_index < len(self.population.individuals), \
            f"Error, wrong {pacman_index=} {len(self.population.individuals)=}"

        if self.population.individuals[pacman_index] == 0:
            if verbose > 0:
                print(f"Pacman {pacman_index=} is already removed")
            return

        #remove from list_indivuals
        self.population.store_dead_individual(self.population.individuals[pacman_index])
        self.population.individuals[pacman_index] = 0

        #if verbose > 0:
        print(f"Agent {pacman_index} has been removed from the population.")

        ## send signal to process
        self._send_death_signal(pacman_index)

        # increment nb_deads
        self.stats["nb_deads"][-1] += 1


    def _process_death(self, pacman_index, verbose=0):
        print("*Warning, _process_death should be implemented in inherited classes")

    def _receive_motor_outputs(self, timeout = 0.001, verbose=0):

        motor_outputs = []

        for i, pipe in enumerate(self.pipes):
            # poll(timeout) checks if data is waiting
            # timeout=0 makes it an instantaneous check

            pos = None


            pac = self.population.individuals[i]

            if pac == 0:

                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} is empty, continue")

                motor_outputs.append(pos)
                continue
            #
            # if verbose > 0:
            #     print(f"[ParallelZoo] Worker {i} polling message")

            if pipe.poll(timeout):

                try:

                    if verbose > 0:
                        print(f"[ParallelZoo] Worker {i} receiving message")

                    msg = pipe.recv()

                    if msg['type'] != 'RESULT':
                        motor_outputs.append(pos)
                        continue

                    if verbose > 0:
                        print(f"[ParallelZoo] Worker {i} integrate_motor_outputs {msg=}")
                    pos = msg['data']


                except EOFError:
                    print(f"[ParallelZoo] Worker {i} pipe closed unexpectedly!")

            motor_outputs.append(pos)

        return motor_outputs

    def shutdown(self):
        print("\n[ParallelZoo] Terminating simulation.")
        for pipe in self.pipes:
            pipe.send({'type': 'TERMINATE'})
        for p in self.processes:
            p.join()





