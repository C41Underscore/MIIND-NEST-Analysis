import miind.miindsim as miind
from miind.grid_generate import generate
from os import chdir, mkdir, listdir, getcwd, remove
from os.path import isdir
from shutil import rmtree
from time import perf_counter
from string import Template
from joblib import Parallel, delayed
from numpy.random import uniform
from statistics import mean


MIIND_DATA_LOCATION = "miind_files/"
BALANCED_IE_TEMPLATE = "balancedIE_template.xml"
GENERATE_FILES = True
PERFORM_EXPERIMENTS = False
ANALYSIS_TIME_STEP = 0.01

POPULATION_SIZES_MAX = 1

I = float(0)

NUMBER_OF_REPEATS = 2
SIMULATION_TIME = 0.2
SIMULATION_TIME_STEP = 1e-03
SIMULATION_THRESHOLD = -55.0e-3
SIMULATION_RESET_V = -70.0e-3

RESULTS = []


# pre-defined MIIND conductance-based LIF neuron equation
def cond(y, t):
    E_r = -70e-3
    tau_m = 20e-3
    tau_s = 5e-3

    v = y[0]
    h = y[1]

    v_prime = (-(v - E_r) - (h * v)) / tau_m
    h_prime = (-h / tau_s) + 65.

    return [v_prime, h_prime]

# def cond(y, t):
#     E_r = -70e-3
#     r = 0.15
#     c = 0.92
#     tau = r*c
#     # tau_s = 5e-3
#
#     v = y[0]
#     # h = y[1]
#
#     v_prime = (-(1/r)*(v - E_r))/tau
#     # h_prime = -h / tau_s
#
#     return [v_prime]


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
        grid_h_max=1.0,
        grid_v_res=200,
        grid_h_res=200,
        efficacy_orientation='h'
    )


def compress_rates(firing_rates):
    rates_per_step = int(ANALYSIS_TIME_STEP/SIMULATION_TIME_STEP)
    new_rates = []
    for i in range(0, len(firing_rates), rates_per_step):
        new_rates.append(mean(firing_rates[i:i+rates_per_step]))
    return new_rates


def run_experiment(sim_file):
    miind.init(1, sim_file + ".xml")

    time_step = miind.getTimeStep()
    simulation_length = miind.getSimulationLength()

    activities = []
    miind.startSimulation()
    for i in range(int(simulation_length / time_step)):
        activities.append(miind.evolveSingleStep([]))

    miind.endSimulation()

    return activities


def generate_and_perform_self_connected(connections, input_type):
    sim_dir = "selfconnected_{0}_{1}".format(connections, input_type)
    for trial_number in range(1, NUMBER_OF_REPEATS + 1):
        if trial_number == 1:
            create_and_reset_sim_dir(sim_dir)
        if GENERATE_FILES:
            refresh_sim_dir(sim_dir)
            entire_file = ""
            with open("selfconnected_template.xml", "r") as file:
                for line in file:
                    entire_file += line
            t = Template(entire_file)
            poisson_exc_input = "<Node algorithm=\"ExcitatoryInput\" name=\"INPUT_E\" type=\"EXCITATORY_DIRECT\" />"
            poisson_inh_input = "<Node algorithm=\"InhibitoryInput\" name=\"INPUT_I\" type=\"INHIBITORY_DIRECT\" />"
            exc_input_conn = "<Connection In=\"INPUT_E\" Out=\"E\" num_connections=\"" + str(connections) + \
                             "\" efficacy=\"1.0\" delay=\"0.001\"/>"
            inh_input_conn = "<Connection In=\"INPUT_I\" Out=\"E\" num_connections=\"" + str(connections) + \
                             "\" efficacy=\"-1.0\" delay=\"0.001\"/>"
            simulation_xml = t.substitute({
                "sim_dir": sim_dir,
                "simulation_time": SIMULATION_TIME,
                "timestep": str(SIMULATION_TIME_STEP),
                "size": POPULATION_SIZES_MAX,
                "connections": connections,
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

        results = None
        if PERFORM_EXPERIMENTS:
            results = run_experiment(sim_dir)

            spikes = str([rate[0] for rate in results])
            spikes = spikes[1:len(spikes) - 1]
            file = open("test" + str(trial_number) + ".dat", "w")
            file.write(spikes)
            file.close()

        chdir("..")


def generate_and_perform_balanced_ie(size, exc_connections, inh_connections, input_type):
    global I
    sim_dir = "balancedIE_{0}_{1}_{2}".format(exc_connections, inh_connections, input_type)
    for trial_number in range(1, NUMBER_OF_REPEATS + 1):
        if trial_number == 1:
            create_and_reset_sim_dir(sim_dir)
        if GENERATE_FILES:
            refresh_sim_dir(sim_dir)
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
                             "num_connections=\"" + str(size) + "\" efficacy=\"1.0\" delay=\"0.001\"/>"
            inh_input_conn = "<Connection In=\"INPUT_I\" Out=\"I\" num_connections=\"" + str(size) + "\" " \
                             "efficacy=\"-1.0\" delay=\"0.001\"/>\n\t\t  <Connection In=\"INPUT_I\" Out=\"E\" " \
                             "num_connections=\"" + str(size) + "\" efficacy=\"-1.0\" delay=\"0.001\"/>"
            cortical_input = "<Node algorithm=\"CorticalBackground\" name=\"Background\" type=\"EXCITATORY_DIRECT\" />"
            cortical_exc_input_conn = "<Connection In=\"Background\" Out=\"E\" num_connections=\"" \
                                      + str(size) + "\" efficacy=\"1.0\" delay=\"0.001\"/>"
            cortical_inh_input_conn = "<Connection In=\"Background\" Out=\"I\" num_connections=\"" \
                                      + str(size) + "\" efficacy=\"1.0\" delay=\"0.001\"/>"
            simulation_xml = t.substitute({
                "sim_dir": sim_dir,
                "simulation_time": SIMULATION_TIME,
                "timestep": str(SIMULATION_TIME_STEP),
                "size": size,
                "exc_connections": exc_connections,
                "inh_connections": inh_connections,
                "exc_input": poisson_exc_input if input_type == "poisson" else "",
                "inh_input": poisson_inh_input if input_type == "poisson" else "",
                "exc_input_conn": exc_input_conn if input_type == "poisson" else "",
                "inh_input_conn": inh_input_conn if input_type == "poisson" else "",
                "randomEE": uniform(0., 2., None),
                "randomII": -uniform(0., 2., None),
                "randomEI": uniform(0., 2., None),
                "randomIE": -uniform(0., 2., None)
            })
            chdir(sim_dir)
            with open(sim_dir + ".xml", "w") as file:
                file.write(simulation_xml)
            if input_type == "cortical":
                I = 80000.*size*1.
            else:
                I = 0.
            generate_files(sim_dir)
        else:
            chdir(sim_dir)

        results = None
        if PERFORM_EXPERIMENTS:
            results = run_experiment(sim_dir)

            exc_spikes = str([rate[0] for rate in results])
            exc_spikes = exc_spikes[1:len(exc_spikes) - 1]
            file = open("exc_test" + str(trial_number) + ".dat", "w")
            file.write(exc_spikes)
            file.close()

            inh_spikes = str([rate[1] for rate in results])
            inh_spikes = inh_spikes[1:len(inh_spikes) - 1]
            file = open("inh_test" + str(trial_number) + ".dat", "w")
            file.write(inh_spikes)
            file.close()

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


def refresh_sim_dir(name):
    if isdir(name):
        chdir(name)
        files = listdir("./")
        for file in files:
            if file[len(file)-4:len(file)] != ".dat":
                remove(file)
    chdir("..")


# Rate 2 is Excitatory, Rate 3 is Inhibitory
def main():
    chdir(MIIND_DATA_LOCATION)
    sim_files = []
    count = 0
    start = perf_counter()
    # Iterate over sizes
    # jobs = Parallel(n_jobs=4)(delayed(generate_and_perform_balanced_ie)(POPULATION_SIZES_MAX, exc_connections,
    #                                                                     inh_connections, input_type)
    #                           for exc_connections in range(1, POPULATION_SIZES_MAX+1)
    #                           for inh_connections in range(1, POPULATION_SIZES_MAX+1)
    #                           for input_type in ["poisson"])
    for exc_connections in range(1, POPULATION_SIZES_MAX + 1):
        for inh_connections in range(1, POPULATION_SIZES_MAX + 1):
            for input_type in ["cortical"]:
                generate_and_perform_balanced_ie(POPULATION_SIZES_MAX, exc_connections, inh_connections, input_type)

    # jobs = Parallel(n_jobs=4)(delayed(generate_and_perform_self_connected)(connections, input_type)
    #                           for connections in range(1, POPULATION_SIZES_MAX+1)
    #                           for input_type in ["poisson"])
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
    number_of_experiments = len(listdir("./")) - 4
    print(str(number_of_experiments) + " MIIND experiments performed in " + str(end) + " seconds.")


def run_miind_experiment():
    main()


if __name__ == "__main__":
    main()
