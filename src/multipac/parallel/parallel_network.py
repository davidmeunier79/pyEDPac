
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
        print(f"[Worker {self.agent_id}] Building chromosome {chromosome}")
        self.network = EvoNetwork(chromosome)
        print(f"[Worker {self.agent_id}] Network built {self.network}")

def worker_loop(pipe, agent_id):
    """The main loop for the worker process."""
    net_process = ParallelNetwork(agent_id)

    while True:

        try:
            msg = pipe.recv()

            # 1. Check if the message is a string (simple signal)
            # or a dictionary (command + data)
            if isinstance(msg, str):
                cmd = msg
                data = None
            else:
                cmd = msg.get('type')
                #data = msg.get('data')


            if cmd == 'SET_CHROMOSOME':
                # RECEIVE: Chromosome from Zoo
                chromosome = msg['data']
                #SEND: Acknowledgment back to Zoo
                pipe.send({'type': 'READY', 'id': net_process.agent_id})

                net_process.build_from_chromosome(chromosome)


            elif cmd == 'DEAD_CHROMOSOME':
                # RECEIVE: Chromosome from Zoo
                agent_id = msg['data']

                assert agent_id == net_process.agent_id, \
                    f"***[Worker {net_process.agent_id}] Error, receives DEAD_CHROMOSOME for {agent_id=}"

                print(f"[Worker {net_process.agent_id}] receives DEAD_CHROMOSOME")

                net_process.network = 0

                # #SEND: Acknowledgment back to Zoo
                # pipe.send({'type': 'READY', 'id': agent_id})

            elif cmd == 'INIT_INPUTS':
                # RECEIVE: Chromosome from Zoo
                net_process.network.initialize_inputs()
                # SEND: Acknowledgment back to Zoo
                #pipe.send({'type': 'READY', 'id': agent_id})

                #print("Receiving empty inputs")
                result = net_process.network.compute_one_wave()
                #
                # #print("Sending outputs")
                # pipe.send({'type': 'READY', 'id': agent_id})

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

                print(f"[Worker {net_process.agent_id}] shutdown")
                net_process.network = 0
                del(net_process.network)

                break

        except EOFError:
            print("EOFError: pipe is closed by master")
            break # Pipe was closed by the Master
