import multiprocessing as mp
import numpy as np
import time

# --- Mock Classes for Testing ---
class MockNetwork:
    def __init__(self, genome):
        self.genome = genome

    def compute(self, inputs):
        # Dummy logic: sum inputs and add genome bias
        return np.sum(inputs) + np.mean(self.genome)

def brain_worker(pipe, agent_id):
    """The Individual process."""
    network = None
    print(f"[Brain {agent_id}] Online.")

    while True:
        msg = pipe.recv()
        cmd = msg.get('type')

        if cmd == 'SET_CHROMOSOME':
            network = MockNetwork(msg['data'])
            pipe.send({'type': 'READY'})

        elif cmd == 'SENSE':
            # Simulate 'Vision' input
            vision_data = msg['data']
            # Brain computing...
            motor_out = network.compute(vision_data)
            pipe.send({'type': 'MOTOR', 'data': motor_out})

        elif cmd == 'TERMINATE':
            print(f"[Brain {agent_id}] Shutting down.")
            break

# --- The Centralized Master ---
class TestZoo:
    def __init__(self):
        self.num_agents = 2
        self.workers = []
        self.pipes = []
        self.genomes = [np.random.rand(10), np.random.rand(10)]

    def start(self):
        print("[Zoo] Initializing agents...")
        for i in range(self.num_agents):
            parent_conn, child_conn = mp.Pipe()
            p = mp.Process(target=brain_worker, args=(child_conn, i))
            p.start()
            self.pipes.append(parent_conn)
            self.workers.append(p)

    def run_sim(self, steps=3):
        # 1. Upload Genomes
        for i, pipe in enumerate(self.pipes):
            pipe.send({'type': 'SET_CHROMOSOME', 'data': self.genomes[i]})
            pipe.recv() # Wait for READY
        print("[Zoo] All brains loaded with chromosomes.")

        # 2. Step through time
        for t in range(steps):
            print(f"\n--- Tick {t} ---")
            # Send Vision
            for pipe in self.pipes:
                fake_vision = np.random.rand(5)
                pipe.send({'type': 'SENSE', 'data': fake_vision})

            # Collect Motor Commands
            for i, pipe in enumerate(self.pipes):
                resp = pipe.recv()
                print(f"[Zoo] Agent {i} output: {resp['data']:.4f}")

    def stop(self):
        for pipe in self.pipes:
            pipe.send({'type': 'TERMINATE'})
        for w in self.workers:
            w.join()
        print("\n[Zoo] Clean exit.")

if __name__ == "__main__":
    zoo = TestZoo()
    zoo.start()
    try:
        zoo.run_sim()
    finally:
        zoo.stop()
