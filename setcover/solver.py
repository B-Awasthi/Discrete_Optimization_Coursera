#!/usr/bin/python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2014 Carleton Coffrin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


from collections import namedtuple
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

Set = namedtuple("Set", ["index", "cost", "items"])


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split("\n")

    parts = lines[0].split()
    item_count = int(parts[0])
    set_count = int(parts[1])

    set_item = {}
    set_cost = {}
    for i in range(1, set_count + 1):
        parts = lines[i].split()
        set_item[i - 1] = list(map(int, parts[1:]))
        set_cost[i - 1] = float(parts[0])

    set_item_df = pd.DataFrame(
        [(k, i) for k, v in set_item.items() for i in v], columns=["set_id", "item_id"]
    )

    item_in_sets = {}
    unique_items = set_item_df["item_id"].unique()
    for itm in unique_items:
        item_in_sets[itm] = set_item_df[set_item_df["item_id"] == itm][
            "set_id"
        ].to_list()

    model = gp.Model("")
    dv_items = model.addVars(range(item_count), vtype="B")
    dv_sets = model.addVars(range(set_count), vtype="B")

    for i in dv_sets:
        itms = set_item[i]
        sum_items = gp.quicksum([dv_items[k] for k in itms])
        model.addGenConstrIndicator(dv_sets[i], 1, sum_items >= len(itms))

    model.addConstrs(
        gp.quicksum(dv_sets[k] for k in item_in_sets[i]) >= 1 for i in item_in_sets
    )

    obj_fn = gp.quicksum(dv_sets[i] * set_cost[i] for i in range(set_count))

    model.setObjective(obj_fn, sense=GRB.MINIMIZE)

    model.optimize()

    solution = [int(dv_sets[i].X) for i in range(set_count)]

    # calculate the cost of the solution
    # obj = sum([s.cost * solution[s.index] for s in sets])

    # prepare the solution in the specified output format
    output_data = str(int(model.ObjVal)) + " " + str(0) + "\n"
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
            "This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/sc_6_1)"
        )
