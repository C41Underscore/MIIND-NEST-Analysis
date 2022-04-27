import matplotlib.cm
import matplotlib.pyplot as plt
from os import listdir, chdir
from statistics import mean
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

exc_sizes = [i for i in range(0, 260, 10)]
inh_sizes = [i for i in range(0, 260, 10)]

miind_sf_firing_rates = []
nest_sf_firing_rates = []

nest_balanced_exc_firing_rates = np.zeros((len(exc_sizes), len(inh_sizes)))
nest_balanced_inh_firing_rates = np.zeros((len(exc_sizes), len(inh_sizes)))

miind_balanced_exc_firing_rates = np.zeros((len(exc_sizes), len(inh_sizes)))
miind_balanced_inh_firing_rates = np.zeros((len(exc_sizes), len(inh_sizes)))

chdir("miind_results")
data_files = listdir("./")
data_files.sort()
for size in exc_sizes:
    for file in data_files:
        if file[len(file)-4:len(file)] != ".xml":
            if file[0:13] == "selfconnected" and int(file.split("_")[1]) == size:
                with open(file, "r") as rates:
                    data = [float(i) for i in rates.readline().split(",")]
                    data.pop()
                    data = mean(data)
                    miind_sf_firing_rates.append(data)

for exc_index, exc_size in enumerate(exc_sizes):
    exc_index = len(exc_sizes)-1-exc_index
    for inh_index, inh_size in enumerate(inh_sizes):
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
chdir("..")

chdir("nest_results")
data_files = listdir("./")
for size in exc_sizes:
    for file in data_files:
        if file[0:13] == "selfconnected" and int(file.split("_")[1]) == size:
            with open(file, "r") as rates:
                data = [float(i) for i in rates.readline().split(",")]
                data.pop()
                data = mean(data)
                nest_sf_firing_rates.append(data)

for exc_index, exc_size in enumerate(exc_sizes):
    exc_index = len(exc_sizes)-1-exc_index
    for inh_index, inh_size in enumerate(inh_sizes):
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

sizes = [str(size) for size in exc_sizes]

y_smoothed = gaussian_filter1d(miind_sf_firing_rates, sigma=0.45)

miind_ax.plot(sizes, miind_sf_firing_rates, label="Raw Data")
miind_ax.plot(sizes, y_smoothed, label="Smoothed Trend Line")
miind_ax.grid(axis="y")
miind_ax.legend(loc="lower right")
miind_ax.set_title("MIIND")

n = 5
for i, label in enumerate(miind_ax.xaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)

y_smoothed = gaussian_filter1d(nest_sf_firing_rates, sigma=0.9)

nest_ax.plot(sizes, nest_sf_firing_rates, label="Raw Data")
nest_ax.plot(sizes, y_smoothed, label="Smoothed Trend Line")
nest_ax.grid(axis="y")
nest_ax.legend(loc="lower right")
nest_ax.set_title("NEST")

for i, label in enumerate(nest_ax.xaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)

sf_fig.suptitle("Self-Connected Gain Curves")
sf_fig.supxlabel("Number of Connections")
sf_fig.supylabel("Firing Rate (Hz)")

# test = np.random.rand(25, 25)

b_fig, ax = plt.subplots(2, 2, figsize=(8, 6))  # excitatory top row, inhibitory bottom row

ticks = [i[0] for i in enumerate(sizes)]
x_labels = [str(i[0] * 10) for i in enumerate(sizes)]
y_labels = list(reversed(x_labels))

im = ax[0][0].imshow(miind_balanced_exc_firing_rates, cmap="Greens")
ax[0][0].set_title("MIIND Excitatory Pop.")
plt.sca(ax[0][0])
plt.colorbar(im, ax=ax[0][0])
plt.xticks(ticks, x_labels)
for i, label in enumerate(ax[0][0].xaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)
plt.yticks(ticks, y_labels)
for i, label in enumerate(ax[0][0].yaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)

im = ax[0][1].imshow(nest_balanced_exc_firing_rates, cmap="Greens")
ax[0][1].set_title("NEST Excitatory Pop.")
plt.sca(ax[0][1])
plt.colorbar(im, ax=ax[0][1])
plt.xticks(ticks, x_labels)
for i, label in enumerate(ax[0][1].xaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)
plt.yticks(ticks, y_labels)
for i, label in enumerate(ax[0][1].yaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)

im = ax[1][0].imshow(miind_balanced_inh_firing_rates, cmap="Reds")
ax[1][0].set_title("MIIND Inhibitory Pop.")
plt.sca(ax[1][0])
plt.colorbar(im, ax=ax[1][0])
plt.xticks(ticks, x_labels)
for i, label in enumerate(ax[1][0].xaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)
plt.yticks(ticks, y_labels)
for i, label in enumerate(ax[1][0].yaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)

im = ax[1][1].imshow(nest_balanced_inh_firing_rates, cmap="Reds")
ax[1][1].set_title("NEST Inhibitory Pop.")
plt.sca(ax[1][1])
plt.colorbar(im, ax=ax[1][1])
plt.xticks(ticks, x_labels)
for i, label in enumerate(ax[1][1].xaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)
plt.yticks(ticks, y_labels)
for i, label in enumerate(ax[1][1].yaxis.get_ticklabels()):
    if i % n != 0:
        label.set_visible(False)

b_fig.suptitle("Population Firing Rate Heatmaps")
b_fig.supxlabel("Number of Inhibitory Connections")
b_fig.supylabel("Number of Excitatory Connections")

plt.show()
