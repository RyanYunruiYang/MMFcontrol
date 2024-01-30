import numpy as np
import math

def max_index(list1):
    max_value = max(list1)
    max_index = list1.index(max_value)
    return max_index

def waterfilling(users, RTTs, resources, incidence_matrix):
    """
    Perform water-filling for Max-Min fairness.

    :param users: Dictionary with weights for each user.
    :param resources: Dictionary with limits for each resource.
    :param incidence_matrix: NumPy array representing the incidence matrix.
    :return: Dictionary with throughput for each user.
    """
    print(f"MMF: users {users}")
    user_weights = [users[i]/RTTs[i] for i in range(len(users))]

    resource_caps = list(resources.values())
    allocation = [0 for i in range(len(users))]
    user_frozen = [False for i in range(len(users))]
    resource_frozen = [False for i in range(len(resources))]

    print(f"MMF: user_weights: {user_weights}")
    print(f"MMF: resource_caps: {resource_caps}")
    # print(f"allocation: {allocation}")
    # print(f"user_frozen: {user_frozen}")
    # print(f"resource_frozen: {resource_frozen}")


    while not all(user_frozen) and not all(resource_frozen):
        # print("newround")
        available_resources = [resource_caps[i] for i in range(len(resources))]
        resource_demand = [0 for i in range(len(resources))]
        
        for i in range(len(users)): 
            for j in range(len(resources)):
                if (incidence_matrix[i][j] == 1):
                    available_resources[j] -= allocation[i]
                    if (not user_frozen[i]):
                        resource_demand[j] += user_weights[i]

        # print(f"available_resources: {available_resources}")
        # print(f"resource_demand: {resource_demand}")


        next_resource_index = -1
        next_resource_step = np.infty
        for i in range(len(resources)):
            if (not resource_frozen[i]):
                ratio = available_resources[i]/resource_demand[i]
                if (ratio > 0 and ratio < next_resource_step):
                    next_resource_step = ratio
                    next_resource_index = i
        # print(f"next_resource_step: {next_resource_step}")
        # print(f"next_resource_index: {next_resource_index}")

        for i in range(len(users)):
            if (not user_frozen[i]):
                allocation[i] += user_weights[i] * next_resource_step


        resource_frozen[next_resource_index] = True 
        for i in range(len(users)):
            if (incidence_matrix[i][next_resource_index]):
                user_frozen[i ] = True

    return allocation


class WorldModel:
    def __init__(self, RTTs, resources, incidence_matrix):
        self.RTTs = RTTs
        self.resources = resources 
        self.incidence_matrix = incidence_matrix

    def tput(self, n):
        print(f"n: {n}")
        return waterfilling(n, self.RTTs, self.resources, self.incidence_matrix)


class Optimizer:
    def __init__(self, resources, incidence_matrix, ideal_weights):
        self.resources = resources 
        self.incidence_matrix = incidence_matrix
        self.ideal_weights = ideal_weights
        self.resource_caps = list(resources.values())        

    def update(self, throughput, n):
        delta_n = [0 for _ in n]

        resource_util = [0 for i in range(len(self.resources))]
        for i in range(len(throughput)):
            for j in range(len(self.resources)):
                if (self.incidence_matrix[i][j] == 1):
                    resource_util[j] += throughput[i]
        print(f"resource_util: {resource_util}")
        print(f"self.resource_caps: {self.resource_caps}")

        for j in range(len(self.resources)):
            if ( abs(resource_util[j]-self.resource_caps[j]) < 0.001):
                tputs = []
                for i in range(len(throughput)):
                    if (self.incidence_matrix[i][j] == 1):
                        tputs.append(throughput[i] / self.ideal_weights[i])
                print(f"tputs: {tputs}")

                delta_n[max_index(tputs)] = -1


        print(delta_n)
        for i in range(len(n)):
            n[i] += delta_n[i]


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

    ideal_weights = [9.01, 1, 1]
    goal = waterfilling(ideal_weights, [1,1,1], resources, incidence_matrix)
    print(f"GOAL: {goal}")


    world_model = WorldModel(RTTs, resources, incidence_matrix)  
    optimizer = Optimizer(resources, incidence_matrix, ideal_weights)

    n = [80,10,10] # Initial Connections
    sim_length = 100

    for i in range(sim_length):
        print(f"n: {n}")
        throughput = world_model.tput(n)
        n = optimizer.update(throughput, n)

        print("ROUND RESULTS")
        print(throughput)
        print(n)


if __name__ == "__main__":
    main()