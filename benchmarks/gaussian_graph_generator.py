import matplotlib.pyplot as plt

sigmas = []
mus = []
miind_data = []
with open("gaussians_miind.dat", "r") as file:
    sigmas = [float(i) for i in file.readline().rstrip().split(",")]
    mus = [float(i) for i in file.readline().rstrip().split(",")]
    for line in file:
        miind_data.append([float(i) for i in line.rstrip().split(",")])

nest_data = []
with open("gaussians_nest.dat", "r") as file:
    file.readline()
    file.readline()
    for line in file:
        nest_data.append([float(i) for i in line.rstrip().split(",")])

fig, (miind_ax, nest_ax) = plt.subplots(1, 2)

miind_ax.grid()
for i in range(0, len(sigmas)):
    miind_ax.plot(mus, miind_data[i], label="\u03C3: " + str(sigmas[i]))
miind_ax.legend(loc="upper left")
miind_ax.set_title("Gaussian Profile (MIIND)")

nest_ax.grid()
for i in range(0, len(sigmas)):
    nest_ax.plot(mus, nest_data[i], label="\u03C3: " + str(sigmas[i]))
nest_ax.legend(loc="upper left")
nest_ax.set_title("Gaussian Profile (NEST)")

fig.supxlabel("\u00B5")
fig.supylabel("Firing Rate (Hz)")

plt.show()
