#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import math
import itertools
import gurobipy as gp
from gurobipy import GRB

Point = namedtuple("Point", ["x", "y"])
Facility = namedtuple("Facility", ["index", "setup_cost", "capacity", "location"])
Customer = namedtuple("Customer", ["index", "demand", "location"])


def length(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split("\n")

    parts = lines[0].split()
    facility_count = int(parts[0])
    customer_count = int(parts[1])

    facilities = []
    for i in range(1, facility_count + 1):
        parts = lines[i].split()
        facilities.append(
            Facility(
                i - 1,
                float(parts[0]),
                int(parts[1]),
                Point(float(parts[2]), float(parts[3])),
            )
        )

    customers = []
    for i in range(facility_count + 1, facility_count + 1 + customer_count):
        parts = lines[i].split()
        customers.append(
            Customer(
                i - 1 - facility_count,
                int(parts[0]),
                Point(float(parts[1]), float(parts[2])),
            )
        )

    model = gp.Model("")
    dv_cust_fac = model.addVars(
        itertools.product(range(customer_count), range(facility_count)), vtype="B"
    )

    # every customers demand should be met
    model.addConstrs(dv_cust_fac.sum(i, "*") == 1 for i in range(customer_count))

    # is facility open
    is_facility_open = model.addVars(range(facility_count), vtype="B")
    for i in range(facility_count):
        model.addGenConstrMax(is_facility_open[i], dv_cust_fac.select("*", i))

    dist_cust_fac = {}
    for i in range(customer_count):
        for j in range(facility_count):
            dist_cust_fac[(i, j)] = length(customers[i].location, facilities[j].location)

    model.addConstrs(
        gp.quicksum(
            m * n
            for m, n in zip(dv_cust_fac.select("*", i), [j.demand for j in customers])
        )
        <= facilities[i].capacity
        for i in range(facility_count)
    )

    obj = gp.quicksum(
        is_facility_open[i] * facilities[i].setup_cost for i in range(facility_count)
    ) + dv_cust_fac.prod(dist_cust_fac)

    model.setObjective(obj, sense=GRB.MINIMIZE)
    model.optimize()

    solution = []
    for i in range(customer_count):
        solution.append([j for j in range(facility_count) if dv_cust_fac[i, j].X > 0][0])

    # build a trivial solution
    # pack the facilities one by one until all the customers are served
    # solution = [-1] * len(customers)
    # capacity_remaining = [f.capacity for f in facilities]

    # facility_index = 0
    # for customer in customers:
    #     if capacity_remaining[facility_index] >= customer.demand:
    #         solution[customer.index] = facility_index
    #         capacity_remaining[facility_index] -= customer.demand
    #     else:
    #         facility_index += 1
    #         assert capacity_remaining[facility_index] >= customer.demand
    #         solution[customer.index] = facility_index
    #         capacity_remaining[facility_index] -= customer.demand

    # used = [0] * len(facilities)
    # for facility_index in solution:
    #     used[facility_index] = 1

    # # calculate the cost of the solution
    # obj = sum([f.setup_cost * used[f.index] for f in facilities])
    # for customer in customers:
    #     obj += length(customer.location, facilities[solution[customer.index]].location)

    # prepare the solution in the specified output format
    output_data = "%.2f" % model.ObjVal + " " + str(0) + "\n"
    output_data += " ".join(map(str, solution))

    return output_data


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
            "This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/fl_16_2)"
        )
