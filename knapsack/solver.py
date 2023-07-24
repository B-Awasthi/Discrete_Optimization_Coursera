#!/usr/bin/python
# -*- coding: utf-8 -*-

from collections import namedtuple
import gurobipy as gp
from gurobipy import GRB

Item = namedtuple("Item", ["index", "value", "weight"])


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split("\n")

    firstLine = lines[0].split()
    item_count = int(firstLine[0])
    capacity = int(firstLine[1])

    items = []

    for i in range(1, item_count + 1):
        line = lines[i]
        parts = line.split()
        items.append(Item(i - 1, int(parts[0]), int(parts[1])))

    # a trivial algorithm for filling the knapsack
    # it takes items in-order until the knapsack is full
    # value = 0
    # weight = 0
    # taken = [0] * len(items)

    # for item in items:
    #     if weight + item.weight <= capacity:
    #         taken[item.index] = 1
    #         value += item.value
    #         weight += item.weight
    model = gp.Model()
    dv_select = model.addVars(items, vtype="B")

    model.addConstr(gp.quicksum(dv_select[i] * i.weight for i in items) <= capacity)

    obj = gp.quicksum(dv_select[i] * i.value for i in items)

    model.setObjective(obj, sense=GRB.MAXIMIZE)

    model.params.OutputFlag = 0

    model.optimize()

    status = 0 if model.Status == 2 else 1

    taken = [int(dv_select[i].X) for i in items]

    # prepare the solution in the specified output format
    output_data = str(int(model.ObjVal)) + " " + str(status) + "\n"
    output_data += " ".join(map(str, taken))
    return output_data


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, "r") as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print(
            "This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)"
        )
