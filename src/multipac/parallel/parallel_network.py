
import sys
sys.path.insert(0, '../src')

from edpac.ed_network.evo_network import EvoNetwork



# --- The Brain Implementation ---
class ParallelNetwork():
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
    net_process = ParallelNetwork(agent_id)

    while True:

        msg = pipe.recv()
        cmd = msg.get('type')

        if cmd == 'SET_CHROMOSOME':
            # RECEIVE: Chromosome from Zoo
            chromosome = msg['data']
            net_process.build_from_chromosome(chromosome)

            # SEND: Acknowledgment back to Zoo
            #pipe.send({'type': 'READY', 'id': agent_id})

        elif cmd == 'INIT_INPUTS':
            # RECEIVE: Chromosome from Zoo
            net_process.network.initialize_inputs()
            # SEND: Acknowledgment back to Zoo
            #pipe.send({'type': 'READY', 'id': agent_id})

            #print("Receiving empty inputs")
            result = net_process.network.compute_one_wave()

            #print("Sending outputs")
            pipe.send({'type': 'RESULT', 'data': result})

        elif cmd == 'TASK':

            if msg['data'] == -1:
                #print("Receiving Dead visio inputs")
                #print("Sending empty outputs")
                pipe.send({'type': 'RESULT', 'data': []})

            elif msg['data'] == 1:

                #print("Receiving empty inputs")
                result = net_process.network.compute_one_wave()

                #print("Sending outputs")
                pipe.send({'type': 'RESULT', 'data': result})

            else:
                # Simulate a sensory-motor cycle

                #print("Receiving visio inputs")
                result = net_process.network.compute_one_wave(msg['data'])

                #print("Sending outputs")
                pipe.send({'type': 'RESULT', 'data': result})

        elif cmd == 'TERMINATE':
            break
