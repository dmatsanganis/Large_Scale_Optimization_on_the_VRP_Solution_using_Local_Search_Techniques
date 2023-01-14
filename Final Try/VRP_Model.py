import random
import math


class Model:

    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.matrix = []
        self.capacity = -1

    def BuildModel(self):
        random.seed(1)

        # Initialize depot at the middle of the map (x=y=50).
        depot = Node(0, 50, 50, 0)
        self.allNodes.append(depot)
        self.capacity = 50

        # Initialize total customers and through a for loop statement create
        # randomly (random seed 1) the 200 customers.
        totalCustomers = 200
        for i in range(0, totalCustomers):
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            dem = 100 * (1 + random.randint(1, 4))
            cust = Node(i + 1, x, y, dem)
            self.allNodes.append(cust)
            self.customers.append(cust)

        rows = len(self.allNodes)
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]

        # Calculate distance for all nodes through an inner forloop statement.
        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                self.matrix[i][j] = dist


class Node:
    def __init__(self, idd, xx, yy, dem):
        self.x = xx
        self.y = yy
        self.ID = idd
        self.demand = dem
        self.isRouted = False


class Route:
    def __init__(self, dp, cap):
        self.sequenceOfNodes = []
        self.sequenceOfNodes.append(dp)
        self.sequenceOfNodes.append(dp)
        self.cost = 0
        self.capacity = cap
        self.load = 0