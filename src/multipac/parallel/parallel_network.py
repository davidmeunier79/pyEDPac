
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
    #
    # def build_from_chromosome(self, chromosome):
    #     # In your real code: self.network = EvoNetwork(chromosome)
    #     # Here we simulate the complexity of building a network
    #     #print(f"[Worker {self.agent_id}] Building chromosome {chromosome}")
    #     self.network =
    #     #print(f"[Worker {self.agent_id}] Network built {self.network}")


def test_all_receive(pipe,timeout = 0.001, verbose=0):

    cmd = ""
    data = None

    try:

        while pipe.poll(timeout):

            msg = pipe.recv()

            # 1. Check if the message is a string (simple signal)
            # or a dictionary (command + data)
            if isinstance(msg, str):
                cmd = msg
                data = None
            else:
                cmd = msg.get('type')
                data = msg.get('data')

            if cmd in ["DEAD_CHROMOSOME", "SET_CHROMOSOME", "TERMINATE"]:
                break

    except EOFError:
        print("EOFError: pipe is closed by master for receiving")

    return cmd, data

def worker_loop(pipe, agent_id, verbose = 1):
    """The main loop for the worker process."""
    net_process = ParallelNetwork(agent_id)

    while True:
#
#         if verbose > 0
#             print(f"[Worker {net_process.agent_id}] Looping")

        result = 0

        cmd, data = test_all_receive(pipe, verbose = verbose-1)
        #
        # # 1. Check if the message is a string (simple signal)
        # # or a dictionary (command + data)
        # if isinstance(msg, str):
        #     cmd = msg
        #     data = None
        # else:
        #     cmd = msg.get('type')
        #     data = msg.get('data')
        #
        # if verbose > 0:
        #     print(f"[Worker {net_process.agent_id}] {cmd=}")
        #

        if cmd == 'SET_CHROMOSOME':

            # RECEIVE: Chromosome from Zoo
            print(f"[Worker {net_process.agent_id}] receives SET_CHROMOSOME")
            chromosome = data


            if verbose > 0:
                print(f"[Worker {net_process.agent_id}] SET_CHROMOSOME send READY")

            pipe.send({'type': 'READY', 'id': net_process.agent_id})

            if verbose > 0:
                print(f"[Worker {net_process.agent_id}] SET_CHROMOSOME EvoNetwork")
            net_process.network = EvoNetwork(chromosome)

            print(f"[Worker {net_process.agent_id}] building EvoNetwork")
            result = 0

        elif cmd == 'DEAD_CHROMOSOME':
            # RECEIVE: Chromosome from Zoo
            agent_id = data

            assert agent_id == net_process.agent_id, \
                f"***[Worker {net_process.agent_id}] Error, receives DEAD_CHROMOSOME for {agent_id=}"

            print(f"[Worker {net_process.agent_id}] receives DEAD_CHROMOSOME")
            net_process.network = 0
            result = 0

        elif cmd == 'INIT_INPUTS':
            if verbose > 0:
                print(f"[Worker {net_process.agent_id}] initialize_inputs")
            net_process.network.initialize_inputs()

            if verbose > 0:
                print(f"[Worker {net_process.agent_id}] compute_one_rgb_wave init")

            result = net_process.network.compute_one_rgb_wave()

        elif cmd == 'TASK':

            if all(pattern is None for pattern in data):
                if verbose > 0:
                    print(f"[Worker {net_process.agent_id}] compute_one_rgb_wave empty")

                result = net_process.network.compute_one_rgb_wave()

            else:

                if verbose > 0:
                    print(f"[Worker {net_process.agent_id}] compute_one_wave data")

                result = net_process.network.compute_one_rgb_wave(data)

        elif cmd == 'TERMINATE':

            print(f"[Worker {net_process.agent_id}] shutdown")
            net_process.network = 0
            del(net_process.network)
            break

        if result != 0:

            if len(result)==0:
                print(f"[Worker {net_process.agent_id}] Empty No more events in event manager, breaking")

            try:
                if verbose>0:
                    print(f"[Worker {net_process.agent_id}] Sending outputs {result=}")
                pipe.send({'type': 'RESULT', 'data': result})

            except EOFError:
                print("EOFError: pipe is closed by master for sending")
                break # Pipe was closed by the Master
