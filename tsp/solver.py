#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from itertools import combinations
import gurobipy as gp
from gurobipy import GRB

Point = namedtuple("Point", ["x", "y"])


def length(point1, point2):
    return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)


def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split("\n")

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount + 1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    # build a trivial solution
    # visit the nodes in the order they appear in the file
    # solution = range(0, nodeCount)

    # # calculate the length of the tour
    # obj = length(points[solution[-1]], points[solution[0]])
    # for index in range(0, nodeCount - 1):
    #     obj += length(points[solution[index]], points[solution[index + 1]])

    # # prepare the solution in the specified output format
    # output_data = "%.2f" % obj + " " + str(0) + "\n"
    # output_data += " ".join(map(str, solution))

    dist = {
        (c1, c2): length(points[c1], points[c2])
        for c1, c2 in combinations(range(nodeCount), 2)
    }

    mdl = gp.Model()

    # Variables: is city 'i' adjacent to city 'j' on the tour?
    vars_ = mdl.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name="x")

    # Symmetric direction: Copy the object
    for i, j in vars_.keys():
        vars_[j, i] = vars_[i, j]  # edge in opposite direction

    # Constraints: two edges incident to each city
    cons = mdl.addConstrs(vars_.sum(c, "*") == 2 for c in range(nodeCount))

    def subtourelim(model, where):
        if where == GRB.Callback.MIPSOL:
            # make a list of edges selected in the solution
            vals = model.cbGetSolution(model._vars)
            selected = gp.tuplelist(
                (i, j) for i, j in model._vars.keys() if vals[i, j] > 0.5
            )
            # find the shortest cycle in the selected edge list
            tour = subtour(selected)
            if len(tour) < len(range(nodeCount)):
                # add subtour elimination constr. for every pair of cities in subtour
                model.cbLazy(
                    gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                    <= len(tour) - 1
                )

    # Given a tuplelist of edges, find the shortest subtour

    def subtour(edges):
        unvisited = list(range(nodeCount)[:])
        cycle = list(range(nodeCount)[:])  # Dummy - guaranteed to be replaced
        while unvisited:  # true if list is non-empty
            thiscycle = []
            neighbors = unvisited
            while neighbors:
                current = neighbors[0]
                thiscycle.append(current)
                unvisited.remove(current)
                neighbors = [j for i, j in edges.select(current, "*") if j in unvisited]
            if len(thiscycle) <= len(cycle):
                cycle = thiscycle  # New shortest subtour
        return cycle

    mdl._vars = vars_
    mdl.Params.lazyConstraints = 1
    mdl.optimize(subtourelim)

    vals = mdl.getAttr("x", vars_)
    selected = gp.tuplelist((i, j) for i, j in vals.keys() if vals[i, j] > 0.5)

    tour = subtour(selected)
    assert len(tour) == nodeCount

    # prepare the solution in the specified output format
    output_data = "%.2f" % mdl.ObjVal + " " + str(0) + "\n"
    output_data += " ".join(map(str, tour))

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
            "This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)"
        )
