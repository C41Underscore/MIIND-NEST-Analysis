import miind.miindsim as miind
from miind.grid_generate import generate
from os import chdir, mkdir, listdir
from os.path import isdir
from shutil import rmtree
import matplotlib.pyplot as plt
from time import perf_counter
from string import Template
from joblib import Parallel, delayed


MIIND_DATA_LOCATION = "miind_files/"
BALANCED_IE_TEMPLATE = "balancedIE_template.xml"
GENERATE_FILES = True

POPULATION_SIZES_MAX = 1

SIMULATION_TIME_STEP = 1e-03
SIMULATION_THRESHOLD = -55.0e-3
SIMULATION_RESET_V = -70.0e-3

RESULTS = []


# pre-defined MIIND conductance-based LIF neuron equation
def cond(y, t):
    E_r = -65e-3
    tau_m = 20e-3
    tau_s = 5e-3

    v = y[0]
    h = y[1]

    v_prime = (-(v - E_r) - (h * v)) / tau_m
    h_prime = -h / tau_s

    return [v_prime, h_prime]


def generate_files(sim_name):
    generate(
        func=cond,
        timestep=SIMULATION_TIME_STEP,
        timescale=1,
        tolerance=1e-6,
        basename=sim_name,
        threshold_v=SIMULATION_THRESHOLD,
        reset_v=SIMULATION_RESET_V,
        reset_shift_h=0.0,
        grid_v_min=-72.0e-3,
        grid_v_max=-54.0e-3,
        grid_h_min=-1.0,
        grid_h_max=2.0,
        grid_v_res=200,
        grid_h_res=200,
        efficacy_orientation='h'
    )


def run_experiment(sim_file):
    miind.init(1, sim_file + ".xml")

    timestep = miind.getTimeStep()
    simulation_length = miind.getSimulationLength()
    # print("Timestep from XML : {}".format(timestep))
    # print("Sim time from XML: {}".format(simulation_length))

    miind.startSimulation()
    constant_input = []
    exc_activities = []
    inh_activities = []
    for i in range(int(simulation_length / timestep)):
        exc_activities.append(miind.evolveSingleStep(constant_input)[0])
        inh_activities.append(miind.evolveSingleStep(constant_input)[1])

    miind.endSimulation()

    return sim_file, (exc_activities, inh_activities)


def generate_and_perform_balanced_ie(size, exc_connections, inh_connections, input_type):
    sim_dir = "balancedIE_{0}_{1}_{2}_{3}".format(size, exc_connections, inh_connections, input_type)
    if GENERATE_FILES:
        create_and_reset_sim_dir(sim_dir)
        # generate_balanced_ie_files(sim_dir, size, exc_connections, inh_connections, input_type)
        entire_file = ""
        with open("balanced_ie_template.xml", "r") as file:
            for line in file:
                entire_file += line
        t = Template(entire_file)
        poisson_exc_input = "<Node algorithm=\"ExcitatoryInput\" name=\"INPUT_E\" type=\"EXCITATORY_DIRECT\" />"
        poisson_inh_input = "<Node algorithm=\"InhibitoryInput\" name=\"INPUT_I\" type=\"INHIBITORY_DIRECT\" />"
        exc_input_conn = "<Connection In=\"INPUT_E\" Out=\"E\" num_connections=\"" + str(size) + \
                         "\" efficacy=\"1.0\" delay=\"0.001\"/>\n\t\t  <Connection In=\"INPUT_E\" Out=\"I\" " \
                         "num_connections=\"" + str(size) + \
                         "\" efficacy=\"1.0\" delay=\"0.001\"/>"
        inh_input_conn = "<Connection In=\"INPUT_I\" Out=\"I\" num_connections=\"" + str(size) + \
                         "\" efficacy=\"-1.0\" delay=\"0.001\"/>\n\t\t  <Connection In=\"INPUT_I\" Out=\"E\" " \
                         "num_connections=\"" + str(size) + \
                         "\" efficacy=\"-1.0\" delay=\"0.001\"/>"
        simulation_xml = t.substitute({
            "sim_dir": sim_dir,
            "timestep": str(SIMULATION_TIME_STEP),
            "size": size,
            "exc_connections": exc_connections,
            "inh_connections": inh_connections,
            "exc_input": poisson_exc_input if input_type == "poisson" else "",
            "inh_input": poisson_inh_input if input_type == "poisson" else "",
            "exc_input_conn": exc_input_conn if input_type == "poisson" else "",
            "inh_input_conn": inh_input_conn if input_type == "poisson" else ""
        })
        chdir(sim_dir)
        with open(sim_dir + ".xml", "w") as file:
            file.write(simulation_xml)
        generate_files(sim_dir)
    else:
        chdir(sim_dir)

    experiment_results = run_experiment(sim_dir)

    # print(experiment_results)
    chdir("..")
    #
    # plt.figure(1)
    # plt.plot(exc_activities)
    # plt.title("Excitatory Firing Rate.")
    #
    # plt.figure(2)
    # plt.plot(inh_activities)
    # plt.title("Inhibitory Firing Rate.")
    #
    # plt.show()


def create_and_reset_sim_dir(name):
    if isdir(name):
        rmtree(name)
    mkdir(name)


# Rate 2 is Excitatory, Rate 3 is Inhibitory
def main():
    chdir(MIIND_DATA_LOCATION)
    sim_files = []
    count = 0
    start = perf_counter()
    # Iterate over sizes
    jobs = Parallel(n_jobs=4)(delayed(generate_and_perform_balanced_ie)(size, exc_connections, inh_connections,
                                                                        input_type)
                              for size in range(1, POPULATION_SIZES_MAX+1)
                              for exc_connections in range(1, size+1)
                              for inh_connections in range(1, size+1)
                              for input_type in ["poisson"])

    # for size in range(1, POPULATION_SIZES_MAX+1):
    #     for connections in range(1, size+1):
    #         for input_type in ["poisson", "cortical"]:
    #             sim_dir = "selfconnected_{0}_{1}_{2}".format(size, connections, input_type)

    # chdir(MIIND_DATA_LOCATION)
    # for sim_dir in sim_files:
    #     if isdir(sim_dir):
    #         rmtree(sim_dir)
    #     mkdir(sim_dir)
    #     chdir(sim_dir)

    end = perf_counter() - start
    number_of_experiments = len(listdir("./")) - 2
    print(str(number_of_experiments) + " MIIND experiments performed in " + str(end) + " seconds.")


if __name__ == "__main__":
    main()
