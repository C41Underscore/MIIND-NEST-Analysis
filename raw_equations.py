from random import randint
import matplotlib.pyplot as plt
import numpy as np


def poisson(k, rate):
    p = [0 for _ in k]
    for i, r in enumerate(k):
        p[i] = np.exp(-rate)*((rate**r)/np.math.factorial(r))
    return p


def generate_spike_train(fr, dt, steps):
    def f(n):
        if n < fr*dt:
            return 1
        else:
            return 0
    train = list(map(f, np.random.uniform(0., 1., steps)))
    return train


# v_prime = (-(v - E_r) - (h * v)) / tau_m
# h_prime = -h / tau_s
def conductance_lif(start, end, dt, e_r, e_t, tau, tau_e):
    steps = int((end - start)/dt)
    v = [e_r for _ in range(0, steps)]
    ge = [0. for _ in range(0, steps)]
    t = [0. for _ in range(0, steps)]
    spike_train = generate_spike_train(250, dt, steps)
    cur = [0.01 if spike_train[i] == 1 else 0. for i in range(0, steps)]
    for i in range(0, steps-1):
        v[i+1] = v[i] + dt*((-(v[i] - e_r) - (ge[i]*v[i]))/tau)
        if v[i+1] >= e_t:
            v[i+1] = e_r
        ge[i+1] = ge[i] + dt*((-ge[i] + cur[i])/tau_e)
        t[i+1] = t[i] + dt
    return v, ge, t, spike_train


def convert_train(spike_train):
    t = 0.
    spike_times = []
    for i in range(0, 200):
        if spike_train[i] == 1:
            spike_times.append(t)
        t += 0.001
    return spike_times


def main():
    vs, ge, ts, spike_train = conductance_lif(0., 0.2, 0.001, -0.070, -0.055, 0.020, 0.005)

#    plt.figure(1)
#    plt.title("Membrane Potential")
#    plt.plot(ts, vs)

 #   plt.figure(2)
 #   plt.title("Conductance Variable")
 #   plt.plot(ts, ge)
    print(vs)

    spike_times = convert_train(spike_train)
#    plt.figure(3)
#    plt.title("Spike Train Input")
#    plt.eventplot(spike_times, linelengths=0.01)
#
#    spikes = [convert_train(generate_spike_train(150, 0.001, 200)) for _ in range(0, 8)]
#    plt.figure(4)
#    plt.title("Spike Raster (Independent)")
#    plt.eventplot(spikes)

 #   plt.show()


if __name__ == "__main__":
    main()
