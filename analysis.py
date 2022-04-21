import matplotlib.pyplot as plt
from os import listdir, chdir
from statistics import mean
import numpy as np

sizes = [1, 5, 10, 20, 50, 100, 250, 500]

miind_sf_firing_rates = []
nest_sf_firing_rates = []

nest_balanced_exc_firing_rates = np.zeros((len(sizes), len(sizes)))
nest_balanced_inh_firing_rates = np.zeros((len(sizes), len(sizes)))

miind_balanced_exc_firing_rates = np.zeros((len(sizes), len(sizes)))
miind_balanced_inh_firing_rates = np.zeros((len(sizes), len(sizes)))

chdir("miind_results_sub_500/miind_files")
data_files = listdir("./")
data_files.sort()
for size in sizes:
    for file in data_files:
        if file[0:13] == "selfconnected" and int(file.split("_")[1]) == size:
            with open(file, "r") as rates:
                data = [float(i) for i in rates.readline().split(",")]
                data.pop()
                data = mean(data)
                miind_sf_firing_rates.append(data)

for exc_index, exc_size in enumerate(sizes):
    for inh_index, inh_size in enumerate(sizes):
        for file in data_files:
            if file[0:10] == "balancedEI" and int(file.split("_")[1]) == exc_size \
                    and int(file.split("_")[2]) == inh_size:
                with open(file, "r") as rates:
                    if file.split("_")[3] == "exc":
                        data = [float(i) for i in rates.readline().split(",")]
                        data.pop()
                        data = mean(data)
                        miind_balanced_exc_firing_rates[exc_index, inh_index] = data
                    elif file.split("_")[3] == "inh":
                        data = [float(i) for i in rates.readline().split(",")]
                        data.pop()
                        data = mean(data)
                        miind_balanced_inh_firing_rates[exc_index, inh_index] = data
chdir("../..")

chdir("nest_results_sub_500/nest_results")
data_files = listdir("./")
for size in sizes:
    for file in data_files:
        if file[0:13] == "selfconnected" and int(file.split("_")[1]) == size:
            with open(file, "r") as rates:
                data = [float(i) for i in rates.readline().split(",")]
                data.pop()
                data = mean(data)
                nest_sf_firing_rates.append(data)

for exc_index, exc_size in enumerate(sizes):
    for inh_index, inh_size in enumerate(sizes):
        for file in data_files:
            if file[0:10] == "balancedEI" and int(file.split("_")[1]) == exc_size \
                    and int(file.split("_")[2]) == inh_size:
                with open(file, "r") as rates:
                    if file.split("_")[3] == "exc":
                        data = [float(i) for i in rates.readline().split(",")]
                        data.pop()
                        data = mean(data)
                        nest_balanced_exc_firing_rates[exc_index, inh_index] = data
                    elif file.split("_")[3] == "inh":
                        data = [float(i) for i in rates.readline().split(",")]
                        data.pop()
                        data = mean(data)
                        nest_balanced_inh_firing_rates[exc_index, inh_index] = data
chdir("../..")

sf_fig, (miind_ax, nest_ax) = plt.subplots(1, 2)

sizes = [str(size) for size in sizes]

miind_ax.plot(sizes, miind_sf_firing_rates)
miind_ax.grid()

nest_ax.plot(sizes, nest_sf_firing_rates)
nest_ax.grid()

sf_fig.suptitle("Self-Connected Gain Curves")
sf_fig.supxlabel("Number of Connections")
sf_fig.supylabel("Firing Rate (Hz)")

test = np.random.rand(100, 100)

b_fig, ax = plt.subplots(2, 2, figsize=(8, 6))  # excitatory top row, inhibitory bottom row

ax[0][0].imshow(test, cmap="Greens")
ax[0][0].set_title("MIIND Excitatory Pop.")

ax[0][1].imshow(nest_balanced_exc_firing_rates, cmap="Greens")
ax[0][1].set_title("NEST Excitatory Pop.")

ax[1][0].imshow(test, cmap="Reds")
ax[1][0].set_title("MIIND Inhibitory Pop.")

ax[1][1].imshow(nest_balanced_inh_firing_rates, cmap="Reds")
ax[1][1].set_title("NEST Inhibitory Pop.")

b_fig.suptitle("Population Firing Rate Heatmaps")
b_fig.supxlabel("Number of Inhibitory Connections")
b_fig.supylabel("Number of Excitatory Connections")


# b_fig, ax = plt.subplots(2, 2)  # excitatory top row, inhibitory bottom row

# MIIND excitatory
# MIIND inhibitory

# NEST excitatory
# ax[0][1].plot(nest_balanced_exc_firing_rates)

# NEST inhibitory

plt.show()
