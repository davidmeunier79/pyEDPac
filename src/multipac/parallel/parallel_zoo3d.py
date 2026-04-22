

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
            p = mp.Process(target=worker_loop, args=(child_conn, i))
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


    def run_one_blocking_step(self, timeout=0.001, verbose=0):
        """
        Collects outputs from all workers without
        locking the Master process.
        """

        if verbose > 0:
            print("[ParallelZoo] All receive_poll_inputs")

        self._receive_poll_inputs(timeout=0.001, verbose=verbose-1)

        if verbose > 0:
            print("[ParallelZoo] All test_all_contacts")

        self._test_all_contacts(verbose=verbose-1)

        if verbose > 0:
            print("[ParallelZoo] All send_all_outputs")

        results = self._send_all_outputs(verbose=verbose-1)

        if verbose > 0:
            print("[ParallelZoo] All compute_all_stats")

        self._compute_all_stats(verbose=verbose-1)

        nb_added_pacgums = self.add_random_pacgums()
        self.stats["nb_added_pacgums"][-1] += nb_added_pacgums

        return results


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

                    if len(msg['data']):

                        if verbose > 0:
                            print(f"[ParallelZoo] Worker {i} integrate_motor_outputs {msg=}")
                        pos = msg['data']

                    else:
                        if verbose > 0:
                            print(f"[ParallelZoo] Worker {i} process_death")
                        self.process_death(i)


                except EOFError:
                    print(f"[ParallelZoo] Worker {i} pipe closed unexpectedly!")

            motor_outputs.append(pos)

        return motor_outputs

    def _receive_poll_inputs(self, timeout = 0.001, verbose=0):

        for i, pipe in enumerate(self.pipes):
            # poll(timeout) checks if data is waiting
            # timeout=0 makes it an instantaneous check

            pac = self.population.individuals[i]

            if pac == 0:

                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} is empty, continue")
                continue
            #
            # if verbose > 0:
            #     print(f"[ParallelZoo] Worker {i} polling message")

            if pipe.poll(timeout):

                try:

                    if verbose > 0:
                        print(f"[ParallelZoo] Worker {i} receiving message")

                    msg = pipe.recv()

                    if verbose > 0:
                        print(f"[ParallelZoo] Worker {i} integrate_motor_outputs {msg=}")

                    if msg['type'] != 'RESULT':
                        continue

                    if len(msg['data']):

                        if verbose > 0:
                            print(f"[ParallelZoo] Worker {i} integrate_motor_outputs {msg['data']=}")
                        pos = pac.integrate_motor_outputs(msg['data'])

                        if pos:
                            if verbose > 0:
                                print(f"[ParallelZoo] Worker {i} Move forward")
                            self._move_forward(i)
                    else:
                        if verbose > 0:
                            print(f"[ParallelZoo] Worker {i} process_death")
                        self.process_death(i)
                        continue

                except EOFError:
                    print(f"[ParallelZoo] Worker {i} pipe closed unexpectedly!")


    def _send_all_outputs(self, verbose=0):

        results = [None] * self.num_agents

        for i, pipe in enumerate(self.pipes):
            # poll(timeout) checks if data is waiting
            # timeout=0 makes it an instantaneous check

            pac = self.population.individuals[i]

            if pac == 0:

                if verbose > 0:
                    print(f"[ParallelZoo] Worker {i} is empty, continue")
                continue

            if verbose > 0:
                print(f"[ParallelZoo] Worker {i} integrate_visio_outputs")


            input_percept = self.integrate_visio_outputs(pac)
            #
            # if verbose > 0:
            #     print(f"[ParallelZoo] Worker {i} {input_percept=}")

            if input_percept:
                results[i] = input_percept

                try:
                    pipe.send({'type': 'TASK', 'data': input_percept})
                except BrokenPipeError:
                    print(f"{input_percept=}")

        return results

    def shutdown(self):
        print("\n[ParallelZoo] Terminating simulation.")
        for pipe in self.pipes:
            pipe.send({'type': 'TERMINATE'})
        for p in self.processes:
            p.join()





