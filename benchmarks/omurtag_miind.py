# MIIND

import matplotlib.pyplot as plt
import miind.miindsim as miind

miind.init(1, "lifomurtag.xml")

timestep = miind.getTimeStep()
simulation_length = miind.getSimulationLength()
print("Timestep from XML : {}".format(timestep))
print("Sim time from XML : {}".format(simulation_length))

miind.startSimulation()
constant_input = []
activities = []
for i in range(int(simulation_length/timestep)):
    activities.append(miind.evolveSingleStep(constant_input)[0])

miind.endSimulation()

lines = []
with open("rate_0", "r") as file:
    while True:
        line = file.readline()
        if line == "":
            break
        else:
            line = line.split("\t")
            lines.append(float(line[1][0:len(line[1])-1]))

miind_results = lines[0:998]
print(activities)

plt.figure(1)
plt.plot(activities)
plt.show()