import miind.miindsimv as miind
from miind.grid_generate import generate
from os import chdir, mkdir, listdir, getcwd, remove, system
from os.path import isdir
from shutil import rmtree
from time import perf_counter
from string import Template
import numpy as np
from statistics import mean


MIIND_DATA_LOCATION = "miind_files/"
BALANCED_IE_TEMPLATE = "balancedIE_template.xml"
GENERATE_FILES = True
PERFORM_EXPERIMENTS = True
ANALYSIS_TIME_STEP = 0.01


NUMBER_OF_REPEATS = 2
SIMULATION_TIME = 1.
SIMULATION_TIME_STEP = 1e-03
SIMULATION_THRESHOLD = -55.0e-3
SIMULATION_RESET = -70.0e-3
SIMULATION_MIN = -75.0e-3
SIMULATION_TAU = 50e-3

MAX_CONNECTIONS = 2


def generate_selfconnected_average_firing_rates():
    files = listdir("./")
    average_rates = [0. for _ in range(0, int(SIMULATION_TIME/SIMULATION_TIME_STEP))]
    for file in files:
        with open(file, "r") as data:
            rates = [float(i) for i in data.readline().split(",")]
            for i in range(0, len(rates)):
                average_rates[i] += (1/NUMBER_OF_REPEATS)*rates[i]
    system("rm *.dat")
    with open("firing_rates.dat", "w") as file:
        data = ",".join([str(round(i, 3)) for i in average_rates])
        file.write(data)


def generate_balancedei_average_firing_rates():
    files = listdir("./")
    exc_average_rates = [0. for _ in range(0, int(SIMULATION_TIME/SIMULATION_TIME_STEP))]
    inh_average_rates = [0. for _ in range(0, int(SIMULATION_TIME/SIMULATION_TIME_STEP))]
    for file in files:
        with open(file, "r") as data:
            rates = [float(i) for i in data.readline().split(",")]
            for i in range(0, len(rates)):
                if file[0:3] == "exc":
                    exc_average_rates[i] += (1/NUMBER_OF_REPEATS)*rates[i]
                else:
                    inh_average_rates[i] += (1/NUMBER_OF_REPEATS)*rates[i]
    system("rm *.dat")
    with open("exc_firing_rates.dat", "w") as file:
        data = ",".join([str(round(i, 3)) for i in exc_average_rates])
        file.write(data)
    with open("inh_firing_rates.dat", "w") as file:
        data = ",".join([str(round(i, 3)) for i in inh_average_rates])
        file.write(data)


def compress_rates(firing_rates):
    rates_per_step = int(ANALYSIS_TIME_STEP/SIMULATION_TIME_STEP)
    new_rates = []
    for i in range(0, len(firing_rates), rates_per_step):
        new_rates.append(mean(firing_rates[i:i+rates_per_step]))
    return new_rates


def generate_files(basename, efficacy):
    miind_filegen_cmds = ["generate-lif-mesh %s %f %f %f %f 0.001 750" %
                          (basename, SIMULATION_TAU, SIMULATION_THRESHOLD, SIMULATION_RESET, SIMULATION_MIN),
                          "generate-model %s %f %f" % (basename, SIMULATION_RESET, SIMULATION_THRESHOLD),
                          "generate-empty-fid %s" % basename,
                          "generate-matrix %s %f 100 0.0 0.0 true" % (basename, efficacy)
                          ]
    for cmd in miind_filegen_cmds:
        system("python3 -m miind.miindio " + cmd)


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


def generate_and_perform_self_connected(sim_name, connections, trial_number):
    h = round(np.random.uniform(0, 1.), 3)
    generate_files(sim_name, h)
    generate_files(sim_name + "noise", 1.)
    entire_file = ""
    with open("../selfconnected_template.xml", "r") as file:
        for line in file:
            entire_file += line
    t = Template(entire_file)
    simulation_xml = t.substitute({
        "sim_name": sim_name,
        "time_step": str(SIMULATION_TIME_STEP),
        "simulation_time": str(SIMULATION_TIME),
        "matrix_fileNoise": sim_name + "noise_1_0_0_0_.mat",
        "matrix_file": sim_name + "_" + str(h) + "_0_0_0_.mat",
        "connections": connections,
        "h": str(h)
    })
    with open(sim_name + ".xml", "w") as file:
        file.write(simulation_xml)

    if PERFORM_EXPERIMENTS:
        results = run_experiment(sim_name)

        spikes = str([rate[0] for rate in results])
        spikes = spikes[1:len(spikes) - 1]
        file = open("test" + str(trial_number) + ".dat", "w")
        file.write(spikes)
        file.close()


def generate_and_perform_balanced_ie(sim_name, exc_connections, inh_connections, trial_number):
    ee_h = round(np.random.uniform(0., 1.), 3)
    ii_h = round(np.random.uniform(-1., 0.), 3)
    ei_h = round(np.random.uniform(0., 1.), 3)
    ie_h = round(np.random.uniform(-1., 0), 3)
    efficacies = [("ee", ee_h), ("ii", ii_h), ("ei", ei_h), ("ie", ie_h), ("noise", 1.)]
    for efficacy in efficacies:
        generate_files(sim_name + efficacy[0], efficacy[1])
    entire_file = ""
    with open("../balanced_ie_template.xml", "r") as file:
        for line in file:
            entire_file += line
    t = Template(entire_file)
    simulation_xml = t.substitute({
        "sim_name": sim_name,
        "time_step": str(SIMULATION_TIME_STEP),
        "simulation_time": str(SIMULATION_TIME),
        "matrix_fileNoise": sim_name + "noise_1_0_0_0_.mat",
        "matrix_fileEE": sim_name + "ee_" + str(ee_h) + "_0_0_0_.mat",
        "matrix_fileII": sim_name + "ii_" + str(ii_h) + "_0_0_0_.mat",
        "matrix_fileEI": sim_name + "ei_" + str(ei_h) + "_0_0_0_.mat",
        "matrix_fileIE": sim_name + "ie_" + str(ie_h) + "_0_0_0_.mat",
        "exc_connections": str(exc_connections),
        "inh_connections": str(inh_connections),
        "randomEE": str(ee_h),
        "randomII": str(ii_h),
        "randomEI": str(ei_h),
        "randomIE": str(ie_h)
    })

    with open(sim_name + ".xml", "w") as file:
        file.write(simulation_xml)

    if PERFORM_EXPERIMENTS:
        results = run_experiment(sim_name)

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
            if file == "exc_firing_rates.dat" or file == "inh_firing_rates.dat" or file == "firing_rates.dat":
                remove(file)
    chdir("..")


def main():
    np.random.seed()
    chdir(MIIND_DATA_LOCATION)
    files = listdir("./")
    for file in files:
        if isdir(file):
            rmtree(file)
    count = 0
    start = perf_counter()
    for exc_connections in range(1, MAX_CONNECTIONS + 1):
        for inh_connections in range(1, MAX_CONNECTIONS + 1):
            sim_dir = "balancedEI_{0}_{1}".format(exc_connections, inh_connections)
            create_and_reset_sim_dir(sim_dir)
            for trial_number in range(1, NUMBER_OF_REPEATS + 1):
                count += 1
                refresh_sim_dir(sim_dir)
                chdir(sim_dir)
                generate_and_perform_balanced_ie(sim_dir, exc_connections, inh_connections, trial_number)
                chdir("..")
                if trial_number == NUMBER_OF_REPEATS:
                    refresh_sim_dir(sim_dir)
                    chdir(sim_dir)
                    generate_balancedei_average_firing_rates()
                    chdir("..")
            chdir(sim_dir)
            system("cp exc_firing_rates.dat ../{0}_exc_firing_rates.dat; "
                   "cp inh_firing_rates.dat ../{0}_inh_firing_rates.dat".format(sim_dir))
            chdir("..")
            rmtree(sim_dir)

    for connections in range(1, MAX_CONNECTIONS + 1):
        sim_dir = "selfconnected_{0}".format(connections)
        create_and_reset_sim_dir(sim_dir)
        for trial_number in range(1, NUMBER_OF_REPEATS + 1):
            count += 1
            refresh_sim_dir(sim_dir)
            chdir(sim_dir)
            generate_and_perform_self_connected(sim_dir, connections, trial_number)
            chdir("..")
            if trial_number == NUMBER_OF_REPEATS:
                refresh_sim_dir(sim_dir)
                chdir(sim_dir)
                generate_selfconnected_average_firing_rates()
                chdir("..")
        chdir(sim_dir)
        system("cp firing_rates.dat ../{0}_firing_rates.dat".format(sim_dir))
        chdir("..")
        rmtree(sim_dir)

    end = perf_counter() - start
    print(str(count) + " MIIND experiments performed in " + str(end) + " seconds.")


def run_miind_experiment():
    main()


if __name__ == "__main__":
    main()
