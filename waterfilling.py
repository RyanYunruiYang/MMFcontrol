import numpy as np 

def debug(s):
    if(False):
        print(s)

def waterfilling(weights, resources, incidence_matrix):
    """
    Perform water-filling for Max-Min fairness.

    :param users: Dictionary with weights for each user.
    :param resources: Dictionary with limits for each resource.
    :param incidence_matrix: NumPy array representing the incidence matrix.
    :return: Dictionary with throughput for each user.
    """
    user_weights = weights
    resource_caps = list(resources.values())

    allocation = [0 for i in range(len(weights))]
    available_resources = [resource_caps[i] for i in range(len(resources))]

    user_frozen = [False for i in range(len(weights))]
    resource_frozen = [False for i in range(len(resources))]

    debug(f"MMF: user_weights: {user_weights}")
    debug(f"MMF: resource_caps: {resource_caps}")

    while not all(user_frozen) and not all(resource_frozen):
        debug("newround")
        debug(f"allocation: {allocation}")
        debug(available_resources)
        debug(f"user_frozen: {user_frozen}")
        debug(f"resource_frozen: {resource_frozen}")

        resource_demand = [0 for i in range(len(resources))]
        for i in range(len(weights)): 
            for j in range(len(resources)):
                if (incidence_matrix[i][j] == 1):
                    if (not user_frozen[i]):
                        resource_demand[j] += user_weights[i]

        debug(f"resource_demand: {resource_demand}")

        next_resource_step = 0
        for i in range(len(resources)):
            if (available_resources[i] > 0 and resource_demand[i] > 0):
                ratio = available_resources[i]/resource_demand[i]
                if (ratio < next_resource_step or next_resource_step == 0):
                    next_resource_step = ratio

        debug(f"next_resource_step: {next_resource_step}")

        for i in range(len(weights)):
            if (not user_frozen[i]):
                allocation[i] += user_weights[i] * next_resource_step

                # For all resources that the user uses, subtract the demand
                for j in range(len(resources)):
                    if (incidence_matrix[i][j] == 1):
                        available_resources[j] -= user_weights[i] * next_resource_step

        for i in range(len(resources)):
            if (abs(available_resources[i]) < 0.001):
                resource_frozen[i] = True
        # Freeze all the users which use frozen resources
        for i in range(len(weights)):
            for j in range(len(resources)):
                if (incidence_matrix[i][j] == 1 and resource_frozen[j]):
                    user_frozen[i] = True

    assert all(user_frozen)

    # Calculate resource usage on each resource, and assert it is less than capacity
    resource_util = [0 for i in range(len(resources))]
    for i in range(len(weights)):
        for j in range(len(resources)):
            if (incidence_matrix[i][j] == 1):
                resource_util[j] += allocation[i]
    assert all(resource_util[i] <= resource_caps[i]+0.000001 for i in range(len(resources)))     

    return allocation
