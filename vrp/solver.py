#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from itertools import permutations
import gurobipy as gp
from gurobipy import GRB

Customer = namedtuple("Customer", ["index", "demand", "x", "y"])


def length(customer1, customer2):
    return math.sqrt((customer1.x - customer2.x) ** 2 + (customer1.y - customer2.y) ** 2)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split("\n")

    parts = lines[0].split()
    customer_count = int(parts[0])
    num_vehicles = int(parts[1])
    vehicle_capacity = int(parts[2])

    distance_matrix = {}
    locations = range(customer_count)
    demands = []
    customers = []
    for i in range(1, customer_count + 1):
        line = lines[i]
        parts = line.split()
        demands.append(int(parts[0]))
        customers.append(
            Customer(i - 1, int(parts[0]), float(parts[1]), float(parts[2]))
        )

    distance_matrix = {}
    for i in range(customer_count):
        for j in range(customer_count):
            distance_matrix[(i, j)] = length(customers[i], customers[j])

    # the depot is always the first customer in the input
    # depot = 0  # customers[0]

    mdl = gp.Model()

    # Build decision variables :
    varbs = mdl.addVars(
        distance_matrix.keys(), range(num_vehicles), vtype=GRB.BINARY, name="x"
    )

    # Objective function
    total_distance_route = gp.quicksum(
        varbs[i, j, k] * distance_matrix[i, j]
        for i in locations
        for j in locations
        for k in range(num_vehicles)
    )

    mdl.setObjective(total_distance_route, GRB.MINIMIZE)

    # 1. Vehicle leaves node that it enters
    # Ensure that the number of times a vehicle enters a node is equal to the number of
    # times it leaves that node:

    for j in locations:
        for k in range(num_vehicles):
            mdl.addConstr(
                gp.quicksum(varbs[i, j, k] for i in locations)
                == gp.quicksum(varbs[j, i, k] for i in locations)
            )

    # 2. Ensure that every node is entered once
    # Together with the first constraint, it ensures that the every node is entered only once,
    # and it is left by the same vehicle.

    for j in locations[1:]:
        mdl.addConstr(
            gp.quicksum(varbs[i, j, k] for k in range(num_vehicles) for i in locations)
            == 1
        )

    # 3. Every vehicle leaves the depot
    # Together with constraint 1, we know that every vehicle arrives again at the depot.

    for k in range(num_vehicles):
        mdl.addConstr(gp.quicksum(varbs[0, j, k] for j in locations[1:]) <= 1)

    # 4. Capacity constraint
    # Respect the capacity of the vehicles. Note that all vehicles have the same capacity.

    for k in range(num_vehicles):
        mdl.addConstr(
            gp.quicksum(
                varbs[i, j, k] * demands[j] for i in locations for j in locations[1:]
            )
            <= vehicle_capacity
        )

    # 5. no travel from a node to itself
    for k in range(num_vehicles):
        for i in locations:
            mdl.addConstr(varbs[i, i, k] == 0)

    u_nodes = mdl.addVars(list(locations), vtype=GRB.INTEGER)

    for vehc in range(num_vehicles):
        for i in locations[1:]:
            for j in locations[1:]:
                mdl.addConstr(
                    u_nodes[j] - u_nodes[i]
                    >= demands[j] - (vehicle_capacity * (1 - varbs[(i, j, vehc)]))
                )

    for i in locations[1:]:
        mdl.addConstr(u_nodes[i] >= demands[i])
        mdl.addConstr(vehicle_capacity >= u_nodes[i])

    mdl.optimize()

    solution = [(i, j, k) for i, j, k in varbs.keys() if varbs[i, j, k].X > 0.5]
    solution.sort(key=lambda x: x[2])

    # prepare the solution in the specified output format
    status = 1 if mdl.Status == 2 else 0
    outputData = "%.2f" % mdl.ObjVal + " " + str(status) + "\n"
    for v in range(0, num_vehicles):
        sol = [i for i in solution if i[2] == v]
        if not sol:
            outputData += str(0) + " " + str(0) + "\n"
        else:
            lst = []
            chain = [i[:-1] for i in sol]
            lst.append([j for i, j in chain if i == 0][0])
            next_node = lst[0]
            while next_node != 0:
                next_node = [j for i, j in chain if i == next_node][0]
                if next_node > 0:
                    lst.append(next_node)

            outputData += (
                str(0) + " " + " ".join([str(i) for i in lst]) + " " + str(0) + "\n"
            )

    return outputData


import sys

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, "r") as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print(
            "This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/vrp_5_4_1)"
        )
