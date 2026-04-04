
import os

import seaborn as sns

import pandas as pd
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

if __name__ == "__main__":


    indiv_path = os.path.abspath("test_stats")

    file_stats = os.path.join(indiv_path, f"Stats_evo.csv")

    df = pd.read_csv(file_stats)
    df = df.set_index("time")

    print(df)

    plt.figure(figsize=(12, 6))

    sns.set_theme(style="dark")

    # Plot each year's time series in its own facet

    sns.lineplot(data=df, x="time", y="nb_preys")


    plt.title('EvoStats')
    plt.xlabel('time')
    plt.ylabel("nb_preys")
    plt.show()
#
#     g = sns.relplot(
#         data=df,
#         x="time", y="nb_preys", linewidth=4, zorder=5,
#         col_wrap=3, height=2, aspect=1.5, legend=False,
#     )
    #
    # # Iterate over each subplot to customize further
    # for year, ax in g.axes_dict.items():
    #
    #     # Add the title as an annotation within the plot
    #     ax.text(.8, .85, year, transform=ax.transAxes, fontweight="bold")
    #
    #     # Plot every year's time series in the background
    #     sns.lineplot(
    #         data=flights, x="month", y="passengers", units="year",
    #         estimator=None, color=".7", linewidth=1, ax=ax,
    #     )
    #
    # # Reduce the frequency of the x axis ticks
    # ax.set_xticks(ax.get_xticks()[::2])
    #
    # # Tweak the supporting aspects of the plot
    # g.set_titles("")
    # g.set_axis_labels("", "Passengers")
    # g.tight_layout()
    #
    #
