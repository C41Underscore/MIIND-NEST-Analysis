from nest_experiment import run_nest_experiment
from miind_experiment import run_miind_experiment

# TODO: Simulation of cortical background activity in MIIND
# TODO: Run experiments with small samples, examine the data to see if the experiments are producing reasonable results
# TODO: Increase the number of parameters that the experiment will run
# TODO: Construct appropriate functions for analysis


def main():
    run_nest_experiment()
    run_miind_experiment()


if __name__ == "__main__":
    main()
