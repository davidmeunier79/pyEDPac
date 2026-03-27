class CentralizedZoo:
    def __init__(self, population_size=64):
        self.size = population_size
        self.pipes = []
        self.workers = []
        self.agents = [] # Physical representations in the Zoo

    def setup_workers(self):
        for i in range(self.size):
            parent_conn, child_conn = mp.Pipe()
            p = mp.Process(target=brain_worker, args=(child_conn, i))
            p.start()
            self.pipes.append(parent_conn)
            self.workers.append(p)

    def run_generation(self, genomes):
        # 1. Send chromosomes to all workers
        for i, pipe in enumerate(self.pipes):
            pipe.send({'type': 'SET_CHROMOSOME', 'data': genomes[i]})

        # Wait for all to be ready
        for pipe in self.pipes:
            pipe.recv()

        # 2. Main Simulation Loop
        for tick in range(1000):
            # A. Distribute Vision (Master -> Workers)
            for i, pipe in enumerate(self.pipes):
                vision = self.get_agent_vision(i) # From Zoo grid
                pipe.send({'type': 'SENSE', 'data': vision})

            # B. Collect Motor Commands (Workers -> Master)
            # This is the synchronization point
            for i, pipe in enumerate(self.pipes):
                response = pipe.recv()
                motor = response['data']
                self.apply_action(i, motor)

            # C. Update World Physics & Collisions
            self.resolve_physics()

            if self.all_dead():
                break

        # 3. Collect Fitness & Run GA
        scores = [a.fitness for a in self.agents]
        new_genomes = self.genetic_algorithm(genomes, scores)
        return new_genomes

    def cleanup(self):
        for pipe in self.pipes:
            pipe.send({'type': 'TERMINATE'})
        for w in self.workers:
            w.join()
