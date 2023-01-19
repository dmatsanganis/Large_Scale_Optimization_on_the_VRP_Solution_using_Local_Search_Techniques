import random
import math


class Model:

    def __init__(self):
        self.allNodes = []
        self.customers = []
        self.matrix = []
        self.distmatrix = []
        self.capacity = -1

    def BuildModel(self):
        # Keep the same random seed - results.
        random.seed(1)

        # Initialize depot at the middle of the map (x=y=50).
        depot = Node(0, 50, 50, 0, 0)
        self.allNodes.append(depot)
        self.capacity = 3000

        # Initialize total customers and through a for loop statement create
        # randomly (random seed 1) the 200 customers.
        cust_num = 200
        for i in range(cust_num):
            x = random.randint(0, 100)
            y = random.randint(0, 100)
            dem = 100 * (1 + random.randint(1, 4))
            # 1/4 of hour.
            unloading_time = 0.25
            customers = Node(i + 1, x, y, dem, unloading_time)
            self.allNodes.append(customers)
            self.customers.append(customers)

        rows = len(self.allNodes)
        self.matrix = [[0.0 for x in range(rows)] for y in range(rows)]
        self.distmatrix = [[0.0 for x in range(rows)] for y in range(rows)]

        # Calculate distance & time for all nodes through an inner for loop statement.
        for i in range(0, len(self.allNodes)):
            for j in range(0, len(self.allNodes)):
                a = self.allNodes[i]
                b = self.allNodes[j]
                dist = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2))
                time = math.sqrt(math.pow(a.x - b.x, 2) + math.pow(a.y - b.y, 2)) / 40 + unloading_time
                # j!=i calculate the matrix cells except diagonal else for the diagonal we should put zero values
                if j != i:
                    self.distmatrix[i][j] = dist
                    self.matrix[i][j] = time
                else:
                    self.distmatrix[i][j] = 0
                    self.matrix[i][j] = 0

class Node:
    def __init__(self, idd, xx, yy, dem, unloading_time):
        self.unloading_time = unloading_time
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