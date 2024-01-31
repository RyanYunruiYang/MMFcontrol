from waterfilling import waterfilling
import numpy as np
import random

def debug(s):
    if(False):
        print(s)

# Stochastic Rounding of any number into floor(x) and ceil(x) 
def stochastic_round(x):
    floor_x = int(x)
    ceil_x = floor_x + 1
    if (random.random() < (x - floor_x)):
        return ceil_x
    else:
        return floor_x

class WorldModel:
    def __init__(self, RTTs, resources, incidence_matrix):
        self.RTTs = RTTs
        self.resources = resources 
        self.incidence_matrix = incidence_matrix

    def tput(self, n):
        debug(f"n: {n}")
        weights = [n[i]/self.RTTs[i] for i in range(len(n))]
        return waterfilling(weights, self.resources, self.incidence_matrix)


class Optimizer:
    def __init__(self, resources, incidence_matrix, ideal_weights):
        self.resources = resources 
        self.incidence_matrix = incidence_matrix
        self.ideal_weights = ideal_weights
        self.resource_caps = list(resources.values())        

    def update(self, throughput, n):
        delta_n = [{'value': 0, 'priority': 0} for _ in n]

        resource_util = [0 for i in range(len(self.resources))]
        for i in range(len(throughput)):
            for j in range(len(self.resources)):
                if (self.incidence_matrix[i][j] == 1):
                    resource_util[j] += throughput[i]
        debug(f"resource_util: {resource_util}")
        # debug(f"self.resource_caps: {self.resource_caps}")

        for j in range(len(self.resources)):
            # With probability 80% we remove a connection from the largest flow,
            # with probability 20% we scale up all connections by 10%

            # If the sum of n on the resource is greater than 50, we scale down
            # Compute the sum of n on the resource
            sum_n = 0
            for i in range(len(n)):
                if (self.incidence_matrix[i][j] == 1):
                    sum_n += n[i]

            action = 0
            if (sum_n < 10):
                action = 1
            if (sum_n > 100):
                action = 3
            if (sum_n >= 10 and sum_n <= 50):
                if (random.random() < 0.95):
                    action = 2
                else:
                    action = 1
            if (action == 1):
                for i in range(len(n)):
                    if (action > delta_n[i]['priority']):
                        delta_n[i]['value'] = stochastic_round(n[i] * 0.1)
                        delta_n[i]['priority'] = action
            
            if (action == 2):
                tputs = {}
                for i in range(len(throughput)):
                    if (self.incidence_matrix[i][j] == 1):
                        tputs[i] = throughput[i] / self.ideal_weights[i]
                print(f"tputs: {tputs}")

                index = max(tputs, key=tputs.get)
                if (action > delta_n[index]['priority']):
                    delta_n[index]['value'] = -1    
                    delta_n[index]['priority'] = action
            
            if (action == 3):
                for i in range(len(n)):
                    delta_n[i]['value'] = -stochastic_round(n[i] * 0.1)
                    delta_n[i]['priority'] = action


        print(delta_n)
        for i in range(len(n)):
            n[i] += delta_n[i]['value']
            if (n[i] <= 2):
                n[i] = 3

        return n


def main():
    # # Example 1
    # users = {'A': 1, 'B': 2, 'C': 1}
    # resources = {'R1': 100, 'R2': 150}
    # incidence_matrix = np.array([
    #     [1, 1],  # User A uses R1 and R2
    #     [1, 0],  # User B uses R1
    #     [0, 1]   # User C uses R2
    # ])

    # Example 2
    RTTs = [3, 1, 0.1] # Physical Situation, RTT scale down
    resources = {'R1': 10, 'R2': 4, 'R3': 1}
    incidence_matrix = np.array([
        [1, 0, 0],  # User A uses R1
        [1, 1, 0],  # User B uses R1, R2
        [0, 1, 1]   # User C uses R2, R3
    ])

    ideal_weights = [10, 1, 1]
    goal = waterfilling(ideal_weights, resources, incidence_matrix)
    print(f"GOAL: {goal}")


    world_model = WorldModel(RTTs, resources, incidence_matrix)  
    optimizer = Optimizer(resources, incidence_matrix, ideal_weights)

    n = [80,10,10] # Initial Connections
    sim_length = 2000

    throughputs = []
    for i in range(sim_length):
        print(f"n: {n}")
        throughput = world_model.tput(n)
        throughputs.append(throughput)
        print(throughput)
        n = optimizer.update(throughput, n)

    # Display the throughputs as three separate lines on a curve
    # As well as the GOAL throughputs as horizontal lines
    import matplotlib.pyplot as plt
    plt.plot(throughputs)
    
    # Plot horizontal line at y=9 
    print(goal)
    plt.axhline(y=goal[0], color='r', linestyle='-', label='A Goal')
    plt.axhline(y=goal[1], color='r', linestyle='-', label='B Goal')
    # plt.axhline(y=goal[2], color='r', linestyle='-', label='C Goal')

    plt.show()

if __name__ == "__main__":
    main()