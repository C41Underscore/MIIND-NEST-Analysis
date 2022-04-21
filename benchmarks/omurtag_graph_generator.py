import matplotlib.pyplot as plt

miind_data = []

with open("rate_0", "r") as file:
    data = file.readline()
    data = [float(i) for i in data.split(",")]
    miind_data = data[::10]

nest_data = []

with open("omurtag.dat", "r") as file:
    data = file.readline()
    nest_data = [float(i) for i in data.split(",")]


plt.figure(1)
plt.plot(miind_data, label="MIIND")
plt.plot(nest_data, label="NEST")
plt.xlabel("Time (ms)")
plt.ylabel("Firing Rate (Hz)")
plt.grid()
plt.legend(loc="lower right")

plt.show()
