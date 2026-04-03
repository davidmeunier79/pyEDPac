import multiprocessing as mp
import numpy as np
import time

import sys
sys.path.insert(0, '../src')


#from visualizer import BaseVisualizer,PatternVisualizer
#
# from edpac.zoo.zoo import Zoo
# #from network import Network
#
# from edpac.ed_network.ed_synapse import EDSynapse
#
#


from edpac.ed_network.evo_network import EvoNetwork
#

from edpac.config.constants import NB_VISIO_INPUTS, MINIMAL_TIME

from edpac.config.ga_config import PopulationConfigTest, PopulationConfig
from edpac.config.network_config import NetworkConfig
# from edpac.config.physiology_config import NeuronConfig
#
#
# from PySide6.QtCore import QEventLoop, QTimer, Qt
# from PySide6 import QtWidgets, QtCore
#
# from edpac.visualisation.network_visualizer import NetworkVisualizer
# from edpac.visualisation.input_visualizer import InputVisualizer
# #from edpac.visualisation.pixel_visualizer import PixelVisualizer
#
# from edpac.tracer.neuron_tracer import NeuronTracer

from edpac.genetic_algorithm.chromosome import Chromosome

from edpac.genetic_algorithm.population import Population







# --- The Brain Implementation ---
class MPINetwork():
    """
    This class lives inside the worker process.
    It builds the network only when it receives a chromosome.
    """
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.network = 0

    def build_from_chromosome(self, chromosome):
        # In your real code: self.network = EvoNetwork(chromosome)
        # Here we simulate the complexity of building a network
        self.network = EvoNetwork(chromosome)
        print(f"[Worker {self.agent_id}] Network built with {len(chromosome.genes)} genes.")



def worker_loop(pipe, agent_id):
    """The main loop for the worker process."""
    brain = MPINetwork(agent_id)

    while True:
        msg = pipe.recv()
        cmd = msg.get('type')

        if cmd == 'SET_CHROMOSOME':
            # RECEIVE: Chromosome from Zoo
            chromosome = msg['data']
            brain.build_from_chromosome(chromosome)
            # SEND: Acknowledgment back to Zoo
            pipe.send({'type': 'READY', 'id': agent_id})

        elif cmd == 'TASK':
            # Simulate a sensory-motor cycle
            result = brain.network.compute_one_wave(msg['data'])
            pipe.send({'type': 'RESULT', 'data': result})

        elif cmd == 'TERMINATE':
            break

# --- The Centralized Zoo ---
class MasterZoo(Population):
    def __init__(self, num_agents=5, config : PopulationConfig = None):
        self.num_agents = num_agents
        self.pipes = []
        self.processes = []
        # Centralized Genomes (each is a random array of 20 values)
        #self.chromosomes = [np.random.rand(20) for _ in range(num_agents)]
        super().__init__(config)

    def deploy(self):
        print(f"[Zoo] Deploying {self.num_agents} individuals...")
        for i in range(self.num_agents):
            parent_conn, child_conn = mp.Pipe()
            p = mp.Process(target=worker_loop, args=(child_conn, i))
            p.start()
            self.pipes.append(parent_conn)
            self.processes.append(p)

    def distribute_chromosomes(self):
        print("[Zoo] Sending chromosomes to workers...")
        for i, pipe in enumerate(self.pipes):
            # Pass the specific chromosome for this ID
            pipe.send({'type': 'SET_CHROMOSOME', 'data': self.individuals[i]})

        # Synchronize: Wait for all "READY" signals
        for i, pipe in enumerate(self.pipes):
            response = pipe.recv()
            if response['type'] == 'READY':
                print(f"[Zoo] Confirmed: Worker {response['id']} is initialized.")

    def run_test_step(self):
        print("\n[Zoo] Running a test neural computation step...")
        test_input = [np.zeros(shape=(NetworkConfig.VISIO_SQRT_NB_NEURONS, NetworkConfig.VISIO_SQRT_NB_NEURONS)) for i in range(NB_VISIO_INPUTS)]

        for pipe in self.pipes:
            pipe.send({'type': 'TASK', 'data': test_input})

        for i, pipe in enumerate(self.pipes):
            res = pipe.recv()
            print(f"[Zoo] Agent {i} computed result: {res['data']}")

    def shutdown(self):
        print("\n[Zoo] Terminating simulation.")
        for pipe in self.pipes:
            pipe.send({'type': 'TERMINATE'})
        for p in self.processes:
            p.join()

if __name__ == "__main__":
    # 1. Initialize the Master
    config = PopulationConfigTest()
    zoo = MasterZoo(num_agents=5, config=config)

    # 2. Start the remote processes
    zoo.deploy()

    # 3. Transfer the genetic data from Master to Workers
    zoo.distribute_chromosomes()

    # 4. Verify workers can compute using their new networks
    zoo.run_test_step()

    # 5. Clean exit
    zoo.shutdown()
