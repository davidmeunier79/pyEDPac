import multiprocessing as mp
import numpy as np
from edpac.network.evo_network import EvoNetwork

def brain_worker(pipe, agent_id):
    """
    Independent process for one agent's brain.
    """
    network = None

    while True:
        # Wait for a message from the Zoo
        msg = pipe.recv()

        cmd = msg.get('type')

        if cmd == 'SET_CHROMOSOME':
            # Initialize/Update the network with a new genome
            network = EvoNetwork(msg['data'])
            pipe.send({'type': 'READY'})

        elif cmd == 'SENSE':
            # Perform neural computation
            vision_input = msg['data']
            motor_output = network.compute(vision_input)
            # Send motor command back to Zoo
            pipe.send({'type': 'MOTOR', 'data': motor_output})

        elif cmd == 'TERMINATE':
            break
