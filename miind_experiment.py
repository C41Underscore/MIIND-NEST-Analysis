import miind.miindsim as miind
from miind_files.cond.generateCondFiles import generate_files
from os import chdir, mkdir
from os.path import isdir
from shutil import rmtree
import matplotlib.pyplot as plt
from time import perf_counter


MIIND_DATA_LOCATION = "miind_files/"
BALANCED_IE_TEMPLATE = "balancedIE_template.xml"

POPULATION_SIZES_MAX = 10


def generate_balanced_ie_xml(sim_dir, size, exc_connections, inh_connections, input_type):
    with open(sim_dir + ".xml", "w") as sim_file:
        lines = ["<Simulation>",
                 "<WeightType>CustomConnectionParameters</WeightType>",
                 "<Algorithms>",
                 "<Algorithm type=\"GridAlgorithm\" name=\"{0}\" modelfile=\"{0}.model\" tau_refractive=\"0.0\" \
                 transformfile=\"{0}.tmat\" start_v=\"-0.070\" start_w=\"0.0\" >".format(sim_dir),
                 "<TimeStep>1e-03</TimeStep>", "</Algorithm>",
                 "<Algorithm type=\"RateAlgorithm\" name=\"ExcitatoryInput\">", "<rate>100.0</rate>", "</Algorithm>"]

        #  FIX THIS - USE TEMPLATE STRINGS INSTEAD


def create_and_reset_sim_dir(name):
    if isdir(name):
        rmtree(name)
    mkdir(name)


def main():
    sim_files = []
    count = 0
    start = perf_counter()
    # Iterate over sizes
    for size in range(1, POPULATION_SIZES_MAX+1):
        for exc_connections in range(1, size+1):
            for inh_connections in range(1, size+1):
                for input_type in ["poisson", "cortical"]:
                    sim_dir = "balancedIE_{0}_{1}_{2}_{3}".format(size, exc_connections, inh_connections, input_type)
                    create_and_reset_sim_dir(sim_dir)
                    chdir(sim_dir)
                    generate_balanced_ie_xml(sim_dir, size, exc_connections, inh_connections, input_type)

    for size in range(1, POPULATION_SIZES_MAX+1):
        for connections in range(1, size+1):
            for input_type in ["poisson", "cortical"]:
                sim_dir = "selfconnected_{0}_{1}_{2}".format(size, connections, input_type)

    chdir(MIIND_DATA_LOCATION)
    for sim_dir in sim_files:
        if isdir(sim_dir):
            rmtree(sim_dir)
        mkdir(sim_dir)
        chdir(sim_dir)

    exit(0)
    chdir("cond")

    generate_files()

    miind.init(1, "cond.xml")

    timestep = miind.getTimeStep()
    simulation_length = miind.getSimulationLength()
    # print("Timestep from XML : {}".format(timestep))
    # print("Sim time from XML: {}".format(simulation_length))

    miind.startSimulation()
    constant_input = [2500]
    exc_activities = []
    inh_activities = []
    for i in range(int(simulation_length / timestep)):
        exc_activities.append(miind.evolveSingleStep(constant_input)[0])
        inh_activities.append(miind.evolveSingleStep(constant_input)[1])

    miind.endSimulation()

    plt.figure(1)
    plt.plot(exc_activities)
    plt.title("Excitatory Firing Rate.")

    plt.figure(2)
    plt.plot(inh_activities)
    plt.title("Inhibitory Firing Rate.")

    plt.show()


if __name__ == "__main__":
    main()
