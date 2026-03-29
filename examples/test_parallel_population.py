#import multiprocessing as mp
#import numpy as np
#import time

import sys
sys.path.insert(0, '../src')

from multipac.parallel.parallel_zoo import ParallelPopulation
from edpac.config.ga_config import PopulationConfigTest

#from edpac.genetic_algorithm.chromosome import Chromosome



if __name__ == "__main__":
    # 1. Initialize the Master
    config = PopulationConfigTest()
    pop = ParallelPopulation(config=config)

    # 2. Start the remote processes
    pop.deploy()

    # 3. Transfer the genetic data from Master to Workers
    pop.distribute_chromosomes()

    # 4. Verify workers can compute using their new networks
    pop.run_test_step()

    # 5. Clean exit
    pop.shutdown()
