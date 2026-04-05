
import os

import seaborn as sns

import pandas as pd
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def plot_evo_stats(indiv_path)

    file_stats = os.path.join(indiv_path, f"Stats_evo.csv")

    df = pd.read_csv(file_stats)
    df = df.set_index("time")

    print(df)

    # plot nb indiv
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(df.index, df["nb_preys"], color = "blue")

    ax.plot(df.index, df["nb_predators"], color = "red")

    ax.grid()
    plt.show()

    fig.savefig(os.path.join(indiv_path, "Nb_indiv.png"))

    # plot mean fitness
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(df.index, df["mean_prey_fitness"], color = "blue")
    ax.plot(df.index, df["mean_predator_fitness"], color = "red")

    ax.grid()
    plt.show()

    fig.savefig(os.path.join(indiv_path, "Mean_fitness.png"))



    # plot mean fitness
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.plot(df.index, df["nb_deads"], color = "blue")
    ax.plot(df.index, df["nb_added_pacgums"], color = "red")

    ax.grid()
    plt.show()

    fig.savefig(os.path.join(indiv_path, "Mean_Growth.png"))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process a specific individual genome/path.")

    # Define the parameter
    parser.add_argument(
        "--indiv_path",
        type=str,
        required=True,
        help="Path to the individual .npy or chromosome file"
    )

    # Parse and execute
    args = parser.parse_args()

    start_time = time.time()
    plot_evo_stats(args.indiv_path)
    print("--- %s seconds ---" % (time.time() - start_time))
