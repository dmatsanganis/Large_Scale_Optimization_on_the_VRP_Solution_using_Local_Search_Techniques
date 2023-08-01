from VRP_Model import *
from SolutionDrawer import *

############ Team members: ################
### Hegla Ruci, f2822219,               ###
### Foteini Nefeli Nouskali, f2822213,  ###
### Julia Anna Baardse, f2822201,       ###
### Dimitrios Matsanganis, f2822212,    ###
### Team ID: 1.                         ###
###########################################

##################### Classes #######################

# Solution's Class.
class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []

# Saving's Class (For Clarke and Wright algorithm).
class Saving:
    def __init__(self, n1, n2, sav):
        self.n1 = n1
        self.n2 = n2
        self.score = sav

# Relocation Move's Class.
class RelocationMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = None

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9

# Swap Move's Class.
class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = None

    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9

# TwoOpt Move's Class.
class TwoOptMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = None

    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = 10 ** 9

# Solver's Class.
class Solver:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None
        self.iterations = None

    def solve(self):

        print("Clarke and Wright Algorithm for the initial solution \n")
        # We firstly build the initial solution through Clarke and Wright algorithm
        # (initially as closed routes, and then we modify them, in order to become open routes).
        # We have tried both NN and MI, but CW outputs the best results, which we output afterwards.
        self.Clarke_n_Wright()
        self.ReportSolution(self.sol)

        # DEBUG ONLY - Since using VNDs.
        # self.LocalSearch(2)

        print("\n===================================================================\n")
        print("DefaultVND implementation \n")
        print("\n===================================================================\n")


        # Then, we implement the DefaultVND, which searches all the routes to implement the move types
        # and not only the - each iteration's - most delayed (worst) route, which defines our solution cost.
        self.DefaultVND()

        # DEBUG ONLY - Outputs the DefaultVND's findings.
        # self.ReportSolution(self.sol)

        print("\n===================================================================\n")
        print("AdvancedVND implementation \n")
        print("\n===================================================================\n")

        # Afterward, we move on to the AdvancedVND, a VND that is focused on reducing our worst route's cost
        # (solution cost) though the Local Search Operators and more particular the FindBest*** functions.
        # We have found out that the implementation of this VND leads to better results when is applied on the solution
        # of the DefaultVND, throughout both the graphs and the solution's cost (better results than a
        # signal AdvancedVND implementation).
        self.AdvancedVND()
        self.ReportSolution(self.sol)

        # Return the final solution.
        return self.sol

############################### Clarke and Wright - Initial Solution ###########################################

    # Apply the Clarke and Wright algorithm, initially to create closed routes - as the algorithm does,
    # and then removing the return to the depot and updating the routes costs.
    def Clarke_n_Wright(self):

        # Create the initial routes, through create_initial_routes function.
        self.sol = self.create_initial_routes()

        # Create the savings matrix through the calculate_savings function (Creates 200 routes of the
        # following format: 0 - customer - 0, where 0 is the depot).
        savings: list = self.calculate_savings()

        # Sort the list by lambda expression and the 200-initially routes costs.
        savings.sort(key=lambda s: s.score, reverse=True)

        # Initialize an iterator - CW merge counter, that will prevent the CW algorithm from fitting the customer to 24
        # vehicles (it is possible in our problem), since we do not care about the number of trucks used, which is
        # static to 26.
        k = 0

        # A for-loop statement, in order to implement the CW algorithm.
        for i in range(0, len(savings)):
            sav = savings[i]
            n1 = sav.n1
            n2 = sav.n2
            rt1 = n1.route
            rt2 = n2.route

            # Check if the four necessary constraints of CW are fulfilled.
            if n1.route == n2.route:
                continue
            if self.not_first_or_last(rt1, n1) or self.not_first_or_last(rt2, n2):
                continue
            if rt1.load + rt2.load > self.capacity:
                continue

            # DEBUG Only.
            # cst = self.CalculateTotalCost(self.sol)

            # Calculate cost, before merge routes - while rt2 still exists.
            costcalc = rt1.cost + rt2.cost - sav.score

            # If the merge indicator is less that 174 continue to merge, otherwise stop in order to have 26 routes.
            if k < 174:
                # Continue to merge routes.
                self.merge_routes(n1, n2)
                # Calculate rt1's cost.
                rt1.cost = costcalc

                # Calculate the sol.cost, through the Calculate Total Cost function.
                self.sol.cost = self.CalculateTotalCost(self.sol)

                # Update the iteration counter.
                k = k + 1

                # DEBUG ONLY
                # print(cst, self.sol.cost, k)

        # We should remove the depot from all routes of the solution and then print the initials' solution final cost.
        for i in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[i]
            rt.sequenceOfNodes.pop()
            self.UpdateRouteCostAndLoad(rt)

        # Calculate the initials' solution total cost.
        self.sol.cost = self.CalculateTotalCost(self.sol)
        # Print the results.
        print("After removing the depot from all of solution's routes the solutions actual cost is", self.sol.cost, "\n")

    # A function to calculate the savings scores for all 200 nodes.
    def calculate_savings(self):

        # Creates savings as an empty list.
        savings = []

        # A for-loop statement for the 200 customers.
        for i in range(0, len(self.customers)):
            n1 = self.customers[i]
            for j in range(i + 1, len(self.customers)):
                n2 = self.customers[j]

                # Follow the CW theory, regarding the saving score.
                score = self.distanceMatrix[n1.ID][self.depot.ID] + self.distanceMatrix[self.depot.ID][n2.ID]
                score -= self.distanceMatrix[n1.ID][n2.ID]

                # Create and append into the above created list, a Saving class object.
                sav = Saving(n1, n2, score)
                savings.append(sav)

        # Return the savings list.
        return savings

    # A function that creates the initial routes for the CW algorithm.
    def create_initial_routes(self):

        # Creates a Solution object.
        s = Solution()

        # Creates initial_routes_costs as an empty list.
        initial_routes_costs = []

        # A for-loop statement
        for i in range(0, len(self.customers)):
            n = self.customers[i]
            rt = Route(self.depot, self.capacity)
            n.route = rt
            n.position_in_route = 1
            rt.sequenceOfNodes.insert(1, n)
            rt.load = n.demand
            rt.cost = self.distanceMatrix[self.depot.ID][n.ID] + self.distanceMatrix[n.ID][self.depot.ID]
            s.routes.append(rt)
            initial_routes_costs.append(rt.cost)

        # Solution cost will be the maximum of the initial routes costs.
        s.cost = max(initial_routes_costs)

        # Return the solution object.
        return s

    # A function that checks if the node is first or last at its route (excluding depot), used for the CW algorithm.
    def not_first_or_last(self, rt, n):

        # Check if the node is first or last in it's route - without taking into accounting the depot.
        if n.position_in_route != 1 and n.position_in_route != len(rt.sequenceOfNodes) - 2:
            return True

        return False

    # A function that is used to merge routes, used in the CW implementation.
    def merge_routes(self, n1, n2):

        # Get the two routes.
        rt1 = n1.route
        rt2 = n2.route

        # Decide how to merge the two routes, depending on the two nodes positions.
        if n1.position_in_route == 1 and n2.position_in_route == len(rt2.sequenceOfNodes) - 2:
            for i in range(len(rt2.sequenceOfNodes) - 2, 0, -1):
                n = rt2.sequenceOfNodes[i]
                rt1.sequenceOfNodes.insert(1, n)

        elif n1.position_in_route == 1 and n2.position_in_route == 1:
            for i in range(1, len(rt2.sequenceOfNodes) - 1, 1):
                n = rt2.sequenceOfNodes[i]
                rt1.sequenceOfNodes.insert(1, n)

        elif n1.position_in_route == len(rt1.sequenceOfNodes) - 2 and n2.position_in_route == 1:
            for i in range(1, len(rt2.sequenceOfNodes) - 1, 1):
                n = rt2.sequenceOfNodes[i]
                rt1.sequenceOfNodes.insert(len(rt1.sequenceOfNodes) - 1, n)

        elif n1.position_in_route == len(rt1.sequenceOfNodes) - 2 and n2.position_in_route == len(
                rt2.sequenceOfNodes) - 2:
            for i in range(len(rt2.sequenceOfNodes) - 2, 0, -1):
                n = rt2.sequenceOfNodes[i]
                rt1.sequenceOfNodes.insert(len(rt1.sequenceOfNodes) - 1, n)

        # Add the rt2 load to the merged one, rt1.
        rt1.load += rt2.load

        # Remove the rt2, since is now merged and part of rt1.
        self.sol.routes.remove(rt2)
        # Update route's customers.
        self.UpdateRouteCustomers(rt1)

    # A function that updates the route's customers, through a for-loop statement.
    def UpdateRouteCustomers(self, rt):

        for i in range(1, len(rt.sequenceOfNodes) - 1):
            n = rt.sequenceOfNodes[i]
            n.route = rt
            n.position_in_route = i

################################### Calculation and Reporting Functions ################################################

    # A function that updates the routes costs, mainly using a for loop.
    def UpdateRouteCostAndLoad(self, rt: Route):

        tc = 0
        tl = 0

        for i in range(0, len(rt.sequenceOfNodes) - 1):
            A = rt.sequenceOfNodes[i]
            B = rt.sequenceOfNodes[i + 1]
            tc += self.distanceMatrix[A.ID][B.ID]
            tl += A.demand

        rt.load = tl
        rt.cost = tc

    # Calculate the total cost function, using it to calculate the solution cost with respect to
    # the problem's objective function (the max - worst route's cost).
    # We change the cost calculation method as it should return the max time needed to serve the last customer
    # in every route and then find the global maximum of all routes.
    def CalculateTotalCost(self, sol):

        # Create an initially empty list, c.
        c = []

        # A for-loop statement to calculate the cost.
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            r = []

            for j in range(0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                r.append(self.distanceMatrix[a.ID][b.ID])
            c.append(sum(r))

        # cst will be the max of the 26 routes (the worst one, time-wise).
        cst = max(c)

        # Return cst.
        return cst

    # The reporting function, used to prints out all the routes and the solution's cost.
    def ReportSolution(self, sol):
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            for j in range(0, len(rt.sequenceOfNodes)):
                print(rt.sequenceOfNodes[j].ID, end=' ')
            print(rt.cost)
        print(self.sol.cost)

        if self.iterations is not None:
            iterationStr = "The objective function was trapped in the optimal cost of {} hours after {} iterations." \
                .format(str(self.CalculateTotalCost(self.sol)), str(self.iterations))
            print(iterationStr)

#################################### LocalSearch Operators #############################################################

    # A function that implements the three Local Search Operators.
    def LocalSearch(self, operator):

        # Create a copy of the initial solution to always store the solution of the last iteration that gives one
        # solution of the neighborhood w.r.t. a local search operator.
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        # Create one new empty object of each class of each operator to store the information for the implementation
        # of each move type.
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()

        # Start the while loop until the local minimum w.r.t. a particular move type occurs.
        while terminationCondition is False:

            # Set the default values on the class objects for each local search operator.
            self.InitializeOperators(rm, sm, top)
            SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

            # Relocations
            if operator == 0:
                # Call the function that tests all the possible relocation moves and find the move that leads to the
                # most a next solution with lower objective function.
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    # Apply the best move and change the solution's routes with respect to the selected move.
                    self.ApplyRelocationMove(rm)

            # Swaps
            elif operator == 1:
                # Call the function that tests all the possible relocation moves and find the move that leads to the
                # most a next solution with lower objective function.
                self.FindBestSwapMove(sm)
                # Apply the best move and change the solution's routes with respect to the selected move.
                if sm.positionOfFirstRoute is not None:
                    self.ApplySwapMove(sm)

            # Two Opt Move.
            elif operator == 2:
                # Call the function that tests all the possible relocation moves and find the move that leads to the
                # most a next solution with lower objective function.
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None:
                    # Apply the best move and change the solution's routes with respect to the selected move.
                    self.ApplyTwoOptMove(top)

            # Check if the new solution has a lower cost than the previous best solution and then store the solution
            # as the new best.
            if self.sol.cost < self.bestSolution.cost:
                self.bestSolution = self.cloneSolution(self.sol)

            else:
                # If the new solution has not lower cost the application of the move type is terminated.
                terminationCondition = True

            localSearchIterator = localSearchIterator + 1
            print(localSearchIterator, "For this iteration the solution cost is", self.sol.cost)

        # Update and keep the actual best solution of Local Search Operator Applied
        self.sol = self.bestSolution

    # A function that clones the routes.
    def cloneRoute(self, rt: Route):
        cloned = Route(self.depot, self.capacity)
        cloned.cost = rt.cost
        cloned.load = rt.load
        cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
        return cloned

    # A function that clones the solutions.
    def cloneSolution(self, sol: Solution):
        cloned = Solution()

        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            clonedRoute = self.cloneRoute(rt)
            cloned.routes.append(clonedRoute)

        # The sol.cost for us is calculated inside the report function in order to update the solution cost
        cloned.cost = self.sol.cost
        return cloned

    # A functions that initializes the three operators.
    def InitializeOperators(self, rm, sm, top):
        rm.Initialize()
        sm.Initialize()
        top.Initialize()

##################################### Relocation Move Functions ########################################################

    # A function that stores the best relocation move, used for comparisons purposes between the candidate moves.
    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex,
                                moveCost, originRtCostChange, targetRtCostChange, rm: RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    # Apply the best relocation move.
    def ApplyRelocationMove(self, rm: RelocationMove):

        # Calculate the solution cost before the application of the relocation move.
        oldCost = self.CalculateTotalCost(self.sol)

        # Define the two routes.
        originRt = self.sol.routes[rm.originRoutePosition]
        targetRt = self.sol.routes[rm.targetRoutePosition]

        # The node to be relocated.
        B = originRt.sequenceOfNodes[rm.originNodePosition]

        # The case that the relocation move is being applied inside the same route.
        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]

            if rm.originNodePosition < rm.targetNodePosition:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)

            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.cost += rm.costChangeOriginRt + rm.costChangeTargetRt

        # The case that the node is relocated in another route.
        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.cost += rm.costChangeOriginRt
            targetRt.cost += rm.costChangeTargetRt
            originRt.load -= B.demand
            targetRt.load += B.demand

        # Calculate the solution.
        self.sol.cost = self.CalculateTotalCost(self.sol)
        self.ReportSolution(self.sol)

        # DEBUG
        # We add this print for monitoring reasons we should exclude it later
        newCost = self.CalculateTotalCost(self.sol)

        print("\nThe relocation move cost for the applied relocation is", rm.moveCost)
        print("Old-New:", oldCost, newCost)
        print("The estimated cost from the apply function of the latest solution is", self.sol.cost, "\n")
        print("===================================================================\n")


    # Find the best relocation move function.
    def FindBestRelocationMove(self, rm):

        # Find the index of the max cost routes index in the routes solution list
        # Create the worst_routes_lst.
        worst_routes_lst = []

        for i in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[i]
            worst_routes_lst.append(rt)

        worst_routes_lst.sort(key=lambda x: x.cost, reverse=True)

        # Trace originRouteIndex.
        for i in range(0, len(self.sol.routes)):
            if worst_routes_lst[0] != self.sol.routes[i]:
                continue
            else:
                originRouteIndex = i

        # Worst route index.
        print("The index of the max cost route is", originRouteIndex)

        # Set the route with the higher cost as an origin route.
        rt1: Route = self.sol.routes[originRouteIndex]

        # Iterate over all origin route's nodes.
        for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
            A = rt1.sequenceOfNodes[originNodeIndex - 1]
            B = rt1.sequenceOfNodes[originNodeIndex]
            C = rt1.sequenceOfNodes[originNodeIndex + 1]

            # Iterate over all other available routes in the solution to be the target route of the relocated node.
            for targetRouteIndex in range(0, originRouteIndex):
                rt2: Route = self.sol.routes[targetRouteIndex]
                # Iterate over all nodes of a target route.
                for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                    F = rt2.sequenceOfNodes[targetNodeIndex]
                    G = rt2.sequenceOfNodes[targetNodeIndex + 1]
                    # Check the capacity constraint of the target route before the actual applycation of the
                    # relocation of the node.
                    if rt2.load + B.demand > rt2.capacity:
                        continue

                    # Calculate the cost change in both routes affected by the relocation move.
                    originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - \
                                         self.distanceMatrix[B.ID][C.ID]
                    targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - \
                                         self.distanceMatrix[F.ID][G.ID]

                    # Calculate the cost change of the solution after the relocation move.
                    moveCost = originRtCostChange

                    # Check if the relocation move leads to a lower solution cost of the origin route that represents
                    # the route with the higher cost and that the relocation cost do not lead the target route to
                    # have higher cost than the initial cost of the origin route before the relocation.
                    if moveCost < rm.moveCost and rt2.cost + targetRtCostChange < rt1.cost + moveCost:

                        # Update the relocation move characteristics with the respect to the last move that leads to
                        # a lower cost.
                        self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                     targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange,
                                                     rm)

        # Continue the examination of other relocation moves for the remained routes to be set as target routes.
        # Iterate over all origin route's nodes.
        for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
            A = rt1.sequenceOfNodes[originNodeIndex - 1]
            B = rt1.sequenceOfNodes[originNodeIndex]
            C = rt1.sequenceOfNodes[originNodeIndex + 1]

            # Iterate over all other available routes in the solution to be the target route of the relocated node.
            for targetRouteIndex in range(originRouteIndex + 1, len(self.sol.routes)):
                rt2: Route = self.sol.routes[targetRouteIndex]

                # Iterate over all nodes of a target route.
                for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                    F = rt2.sequenceOfNodes[targetNodeIndex]
                    G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                    # Check the capacity constraint of the target route before the actual applycation of the
                    # relocation of the node.
                    if rt2.load + B.demand > rt2.capacity:
                        continue

                    # Calculate the cost change in both routes affected by the relocation move.
                    originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - \
                                         self.distanceMatrix[B.ID][C.ID]
                    targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - \
                                         self.distanceMatrix[F.ID][G.ID]

                    # Calculate the cost change of the solution after the relocation move.
                    moveCost = originRtCostChange

                    # Check if the relocation move leads to a lower solution cost of the origin route that represents
                    # the route with the higher cost and that the relocation cost do not lead the target route to
                    # have higher cost than the initial cost of the origin route before the relocation.
                    if moveCost < rm.moveCost and rt2.cost + targetRtCostChange < rt1.cost + moveCost:

                        # Update the relocation move characteristics with the respect to the last move that leads to
                        # a lower cost.
                        self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                     targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange,
                                                     rm)

        # Second case the origin route is the max cost route and the target route is also the max cost target route
        # Set the target route to be the same as the origin one.
        targetRouteIndex = originRouteIndex
        rt2: Route = self.sol.routes[targetRouteIndex]

        # Iterate over all origin route's nodes.
        for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
            A = rt1.sequenceOfNodes[originNodeIndex - 1]
            B = rt1.sequenceOfNodes[originNodeIndex]
            C = rt1.sequenceOfNodes[originNodeIndex + 1]

            # Iterate over all target's route's nodes.
            for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                # Check and surpass the case that node is relocated in the same position or on the exact adjacent.
                if targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1:
                    continue

                F = rt2.sequenceOfNodes[targetNodeIndex]
                G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                # Calculate the cost change in both routes affected by the relocation move.
                originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - \
                                     self.distanceMatrix[B.ID][C.ID]
                targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - \
                                     self.distanceMatrix[F.ID][G.ID]

                # Calculate the cost change of the solution after the relocation move.
                moveCost = originRtCostChange + targetRtCostChange

                # Check if the relocation move leads to a lower solution cost of the origin route that represents
                # the route with the higher cost and that the relocation cost do not lead the target route to
                # have higher cost than the initial cost of the origin route before the relocation.
                if (moveCost < rm.moveCost) and ((originRtCostChange + rt1.cost + targetRtCostChange) < rt1.cost):

                    # Update the relocation move characteristics with the respect to the last move that leads to
                    # a lower cost.
                    self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex,
                                                 moveCost, originRtCostChange, targetRtCostChange, rm)

    # Find the best relocation move function for the default VND implementation.
    def FindBestRelocationMove2(self, rm):
        # Iterate over all routes of the solution object.
        for originRouteIndex in range(0, len(self.sol.routes)):
            # Set each route of the solution as the origin route of the relocation move.
            rt1: Route = self.sol.routes[originRouteIndex]
            # Iterate over all nodes in the origin route
            for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                # Note the node to be relocated (B) and nodes affected by this relocation.
                A = rt1.sequenceOfNodes[originNodeIndex - 1]
                B = rt1.sequenceOfNodes[originNodeIndex]
                C = rt1.sequenceOfNodes[originNodeIndex + 1]
                # Iterate over all routes that represent the possible target routes that can host the relocated node.
                for targetRouteIndex in range(0, len(self.sol.routes)):
                    # Set the target route.
                    rt2: Route = self.sol.routes[targetRouteIndex]
                    # Iterate over the nodes/positions of the target route for the relocated node to be settled.
                    for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):
                        # Here we check the only case that the relocation move does not belong to the
                        # two cases that the relocation
                        if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex
                                                                     or targetNodeIndex == originNodeIndex - 1):
                            continue
                        # Note the nodes to the target route that will host the relocated node in the middle position.
                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        # In case the relocation move is between different routes you need to check the violation of
                        # capacity of the distinct route
                        if rt1 != rt2:
                            if rt2.load + B.demand > rt2.capacity:
                                continue

                        originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - \
                                             self.distanceMatrix[B.ID][C.ID]
                        targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - \
                                             self.distanceMatrix[F.ID][G.ID]
                        # In case the relocation move takes place in the same route.
                        if rt1 == rt2:
                            # The move cost of the total solution is the sum of the cost changes of the orignin and
                            # the target route.
                            moveCost = originRtCostChange + targetRtCostChange

                            # Check if the relocation move leads to a lower solution cost of the origin route that represents
                            # the route with the higher cost and that the relocation cost do not lead the target route to
                            # have higher cost than the initial cost of the origin route before the relocation.
                            if moveCost < 0 and (moveCost < rm.moveCost) and ((originRtCostChange + rt1.cost +
                                                                               targetRtCostChange) < rt1.cost):

                                # Update the relocation move characteristics with the respect to the last move that leads to
                                # a lower cost.
                                self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                             targetNodeIndex, moveCost, originRtCostChange,
                                                             targetRtCostChange, rm)
                        # In case the relocation move takes place in different routes.
                        if rt1 != rt2:
                            # Calculate the total solution cost change.
                            moveCost = originRtCostChange + targetRtCostChange

                            # Check if the relocation move leads to a lower solution cost of the origin route
                            # that represents the route with the higher cost and that the relocation cost do not
                            # lead the target route to have higher cost than the initial cost of the origin route
                            # before the relocation.
                            if moveCost < 0 and moveCost < rm.moveCost \
                                    and rt1.cost + originRtCostChange < self.sol.cost \
                                    and rt2.cost + targetRtCostChange < self.sol.cost:

                                # Update the relocation move characteristics with the respect to the last move
                                # that leads to a lower cost.
                                self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                             targetNodeIndex, moveCost, originRtCostChange,
                                                             targetRtCostChange, rm)

####################################### Swap Move Functions ############################################################

    # Find the best possible swap move.
    def FindBestSwapMove(self, sm):

        # Find the index of the max cost routes index in the routes solution list
        # Create the worst_routes_lst.
        worst_routes_lst = []

        for i in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[i]
            worst_routes_lst.append(rt)
        # Sort all the solution's routes in terms of their total cost in descending order.
        worst_routes_lst.sort(key=lambda x: x.cost, reverse=True)

        # Trace originRouteIndex.
        for i in range(0, len(self.sol.routes)):
            if worst_routes_lst[0] != self.sol.routes[i]:
                continue
            else:
                firstRouteIndex = i

        # Worst route index.
        print("The index of the max cost route is", firstRouteIndex)

        # Set the most costly route as the first route
        rt1: Route = self.sol.routes[firstRouteIndex]

        # Iterate over the first route's nodes
        for firstNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):

            a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
            b1 = rt1.sequenceOfNodes[firstNodeIndex]
            c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

            # Iterate over all routes except the one that has been set as the first route.
            for secondRouteIndex in range(firstRouteIndex, len(self.sol.routes)):
                # Set the second route.
                rt2: Route = self.sol.routes[secondRouteIndex]
                startOfSecondNodeIndex = 1

                if rt1 == rt2:
                    startOfSecondNodeIndex = firstNodeIndex + 1
                # Iterate over all nodes of the second route of the swap move.
                for secondNodeIndex in range(startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                    a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                    b2 = rt2.sequenceOfNodes[secondNodeIndex]
                    c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                    # Initialize the cost change variables of the routes' cost change to none.
                    costChangeFirstRoute = None
                    costChangeSecondRoute = None

                    # The case the swap move of two nodes is being made inside the same route.
                    if rt1 == rt2:

                        # Case of consecutive nodes swap.
                        if firstNodeIndex == secondNodeIndex - 1:

                            costRemoved = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][b2.ID] + \
                                          self.distanceMatrix[b2.ID][c2.ID]

                            costAdded = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][b1.ID] + \
                                        self.distanceMatrix[b1.ID][c2.ID]
                            # The total cost change of the solution after this relocation move.
                            moveCost = costAdded - costRemoved

                        # Same route no consecutive nodes swap.
                        else:

                            costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                            costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]

                            costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                            costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                            # The total cost change of the solution after this relocation move.
                            moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                        # Check if the swap move leads to a lower solution cost of the origin route that
                        # represents the route with the higher cost and that the swap cost do not lead the
                        # origin route to have higher cost than the initial cost of the origin route before the
                        # swap move.
                        if moveCost < 0 and moveCost < sm.moveCost and rt1.cost + moveCost < rt1.cost:

                            # Update the swap move characteristics with the respect to the last move that leads to
                            # a lower cost.
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                   moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

                    # rt1 != rt2
                    else:

                        # Capacity constraints.
                        if rt1.load - b1.demand + b2.demand > self.capacity:
                            continue
                        if rt2.load - b2.demand + b1.demand > self.capacity:
                            continue

                        costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                        costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                        costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                        costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]

                        costChangeFirstRoute = costAdded1 - costRemoved1
                        costChangeSecondRoute = costAdded2 - costRemoved2

                        moveCost = costChangeFirstRoute

                        # Check if the swap move leads to a lower solution cost of the origin route that
                        # represents the route with the higher cost and that the swap cost do not lead the
                        # target route to have higher cost than the initial cost of the origin route plus the moveCost
                        # swap move.
                        if moveCost < 0 and moveCost < sm.moveCost \
                                and rt2.cost + costChangeSecondRoute < rt1.cost + moveCost:

                            # Update the swap move characteristics with the respect to the last move that leads to
                            # a lower cost.
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                   moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

    # A function that stores the best swap move, used for comparisons purposes between the candidate moves.
    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost,
                          costChangeFirstRoute, costChangeSecondRoute, sm):

        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost

    # A function that apply the best swap move.
    def ApplySwapMove(self, sm):

        # Calculate the total cost of the solution before the relocation
        oldCost = self.CalculateTotalCost(self.sol)

        # Set the two routes that participate in the swap move.
        originRt = self.sol.routes[sm.positionOfFirstRoute]
        targetRt = self.sol.routes[sm.positionOfSecondRoute]

        # Set the nodes that will swap places.
        b1 = originRt.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = targetRt.sequenceOfNodes[sm.positionOfSecondNode]

        # Swap the places of two nodes.
        originRt.sequenceOfNodes[sm.positionOfFirstNode] = b2
        targetRt.sequenceOfNodes[sm.positionOfSecondNode] = b1

        # The case that the two nodes belong to the same route.
        if originRt == targetRt:
            # The route's cost change is the same with the change in the total cost of the solution.
            originRt.cost += sm.moveCost

        # The case the swap nodes belong to different routes.
        else:
            # Update of the routes' cost after the nodes' swap.
            originRt.cost += sm.costChangeFirstRt
            targetRt.cost += sm.costChangeSecondRt

            # Update of the routes' load after the nodes' swap.
            originRt.load = originRt.load - b1.demand + b2.demand
            targetRt.load = targetRt.load + b1.demand - b2.demand

        # The total cost of the solution after the swap move was applied.
        self.sol.cost = self.CalculateTotalCost(self.sol)
        self.ReportSolution(self.sol)

        # DEBUG
        newCost = self.CalculateTotalCost(self.sol)

        print("\nThe swap move cost for the applied relocation is", sm.moveCost)
        print("old new", oldCost, newCost)
        print("The estimated cost from the apply function of the latest solution is", self.sol.cost, "\n")
        print("===================================================================\n")

    # FindBestSwapMove2 for DefaultVND.
    def FindBestSwapMove2(self, sm):
        # Iterate over the routes of the solution.
        for firstRouteIndex in range(0, len(self.sol.routes)):
            # Set the origin route.
            rt1: Route = self.sol.routes[firstRouteIndex]

            # Iterate over the nodes of the origin route.
            for firstNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):

                # first swapped node is determined
                # Iterate over the routes of the solution to set the second route of the swap move.
                for secondRouteIndex in range(firstRouteIndex, len(self.sol.routes)):
                    # Set the second route.
                    rt2: Route = self.sol.routes[secondRouteIndex]
                    # Initialize the first possible node of the second route to swap places.
                    startOfSecondNodeIndex = 1

                    # Incase the swap move is being held in the same route.
                    if rt1 == rt2:
                        # Initialize the first possible node of the second route to swap places.
                        startOfSecondNodeIndex = firstNodeIndex + 1

                    # Iterate over all nodes in the second selected route.
                    for secondNodeIndex in range(startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                        # Set the nodes that will be affected in both routes from the swap move.
                        a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]
                        c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                        a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]
                        c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                        # Initialize the cost change values of routes' cost changes to none.
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        # In case the swap move is being held inside the same route.
                        if rt1 == rt2:

                            # Case of consecutive nodes swap.
                            if firstNodeIndex == secondNodeIndex - 1:

                                costRemoved = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][b2.ID] + \
                                              self.distanceMatrix[b2.ID][c2.ID]

                                costAdded = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][b1.ID] + \
                                            self.distanceMatrix[b1.ID][c2.ID]
                                # The total cost change of the solution after this relocation move.
                                moveCost = costAdded - costRemoved

                            # Same route no consecutive nodes swap.
                            else:

                                costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]

                                costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]

                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                            # Check if the move cost lead to a solution with lower total cost.
                            if moveCost < 0 and moveCost < sm.moveCost and rt1.cost + moveCost < self.sol.cost:
                                # Update the swap move characteristics with the respect to the last move that leads to
                                # a lower cost.
                                self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex,
                                                       secondNodeIndex, moveCost, costChangeFirstRoute,
                                                       costChangeSecondRoute, sm)

                        # The case the swap nodes belong to different routes.
                        # rt1 != rt2
                        else:

                            # Capacity constraints.
                            if rt1.load - b1.demand + b2.demand > self.capacity:
                                continue
                            if rt2.load - b2.demand + b1.demand > self.capacity:
                                continue

                            # Estimate the total cost removed and added to the solution because of the swap move.
                            costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                            costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                            costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                            costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]

                            # Estimate the cost change in the first and the second route of the swap nodes.
                            costChangeFirstRoute = costAdded1 - costRemoved1
                            costChangeSecondRoute = costAdded2 - costRemoved2

                            # Estimate the total cost change of the total Solution.
                            moveCost = costChangeFirstRoute + costChangeSecondRoute

                            # Check if the swap move leads to a lower solution cost.
                            if moveCost < 0 and moveCost < sm.moveCost \
                                    and rt1.cost + costChangeFirstRoute < self.sol.cost \
                                    and rt2.cost + costChangeSecondRoute < self.sol.cost:

                                # Update the swap move characteristics with the respect to the last move that leads to
                                # a lower cost.
                                self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex,
                                                       secondNodeIndex, moveCost, costChangeFirstRoute,
                                                       costChangeSecondRoute, sm)

#################################### Two Opt Move Functions ############################################################

    # FindBestTwoOptMove for AdvancedVND, focuses only on the worst route as the origin route.
    def FindBestTwoOptMove(self, top):

        # Find the index of the max cost routes index in the routes solution list
        # Create the worst_routes_lst.
        worst_routes_lst = []

        for i in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[i]
            worst_routes_lst.append(rt)

        # Sort all the solution's routes in terms of their total cost in descending order.
        worst_routes_lst.sort(key=lambda x: x.cost, reverse=True)

        # Trace originRouteIndex.
        for i in range(0, len(self.sol.routes)):
            if worst_routes_lst[0] != self.sol.routes[i]:
                continue
            else:
                firstRouteIndex = i

        # Prints the worst route index.
        print("The index of the max cost route is", firstRouteIndex)

        # Case: worst route = rt1.
        # Set the route with the higher cost as an origin route.
        rt1: Route = self.sol.routes[firstRouteIndex]

        # Iterate over all origin route's nodes.
        for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):

            # The first node is determined.
            A = rt1.sequenceOfNodes[nodeInd1]
            B = rt1.sequenceOfNodes[nodeInd1 + 1]

            # Iterate over all other available routes in the solution to be the target route of the two opt node.
            for rtInd2 in range(firstRouteIndex, len(self.sol.routes)):
                rt2: Route = self.sol.routes[rtInd2]

                # Inter-route move.
                start2 = 0

                # Intra-route move.
                if rt1 == rt2:
                    start2 = nodeInd1 + 2

                # Iterate over all nodes of a target route.
                for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):

                    K = rt2.sequenceOfNodes[nodeInd2]
                    L = rt2.sequenceOfNodes[nodeInd2 + 1]

                    # Same route.
                    if rt1 == rt2:

                        # Check the constraints.
                        if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                            continue

                        # Calculate the cost change in both routes affected by the two opt move.
                        costAdded = self.distanceMatrix[A.ID][K.ID] + self.distanceMatrix[B.ID][L.ID]
                        costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]

                        # Calculate the cost change of the solution after the two opt move.
                        moveCost = costAdded - costRemoved

                        # Check if the two opt move leads to a lower solution cost of the origin route that
                        # represents the route with the higher cost and that the two opt cost do not lead the
                        # rt1 route to have higher cost than the initial
                        # cost of the origin route before the two opt move.
                        if moveCost < 0 and moveCost < top.moveCost and rt1.cost + moveCost < rt1.cost:

                            # Update the two opt move characteristics with the respect to the last move that leads to
                            # a lower cost.
                            self.StoreBestTwoOptMove(firstRouteIndex, rtInd2, nodeInd1, nodeInd2, moveCost, top)

                    # Different routes, rt1 != rt2.
                    else:

                        if nodeInd1 == 0 and nodeInd2 == 0:
                            continue

                        if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                            continue

                        # Check the capacity constrain.
                        if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                            continue

                        # Calculate the costs change of the solution after the two opt move.
                        rt2movecost = self.distanceMatrix[B.ID][K.ID] - self.distanceMatrix[K.ID][L.ID]
                        moveCost = self.distanceMatrix[A.ID][L.ID] - self.distanceMatrix[A.ID][B.ID]

                        # Check if the two opt move leads to a lower solution cost of the origin route that
                        # represents the route with the higher cost and that the two opt cost do not lead the
                        # rt2 cost after add to it the adjustments cost is less than the rt1 route and
                        # its own adjustments.
                        if moveCost < 0 and moveCost < top.moveCost and rt2.cost + rt2movecost < rt1.cost + moveCost:

                            # Update the two opt move characteristics with the respect to the last move that leads to
                            # a lower cost.
                            self.StoreBestTwoOptMove(firstRouteIndex, rtInd2, nodeInd1, nodeInd2, moveCost, top)

    # Capacity is violated function, checks if the capacity constraint is violated, before applying the two opt move.
    def CapacityIsViolated(self, rt1, nodeInd1, rt2, nodeInd2):

        # Checks the first route, through a for-loop statement.
        rt1FirstSegmentLoad = 0
        for i in range(0, nodeInd1 + 1):
            n = rt1.sequenceOfNodes[i]
            rt1FirstSegmentLoad += n.demand
        rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad

        # Checks the second route, through a for-loop statement.
        rt2FirstSegmentLoad = 0
        for i in range(0, nodeInd2 + 1):
            n = rt2.sequenceOfNodes[i]
            rt2FirstSegmentLoad += n.demand
        rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

        # Checks through if-statements and returns true if the capacity constrain is violated.
        if rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity:
            return True
        if rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity:
            return True

        # Otherwise, false will be returned.
        return False

    # A function that stores the best two opt move, used for comparisons purposes between the candidate moves.
    def StoreBestTwoOptMove(self, rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top):
        top.positionOfFirstRoute = rtInd1
        top.positionOfSecondRoute = rtInd2
        top.positionOfFirstNode = nodeInd1
        top.positionOfSecondNode = nodeInd2
        top.moveCost = moveCost

    # Apply the two opt move function.
    def ApplyTwoOptMove(self, top):
        # Calculate the solution cost before the application of the two opt move.
        oldCost = self.CalculateTotalCost(self.sol)

        # Define the two routes.
        rt1: Route = self.sol.routes[top.positionOfFirstRoute]
        rt2: Route = self.sol.routes[top.positionOfSecondRoute]

        # If the two opt move occurs in one route.
        if rt1 == rt2:

            # Reverses the nodes in the segment [positionOfFirstNode + 1,  top.positionOfSecondNode].
            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])

            rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegment

            # Updates the rt1 cost and load.
            self.UpdateRouteCostAndLoad(rt1)

        # Between two routes.
        else:
            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]

            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            del rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]
            del rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2)
            rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1)

            # Updates the rt1 and rt2 cost and load.
            self.UpdateRouteCostAndLoad(rt1)
            self.UpdateRouteCostAndLoad(rt2)

        # Calculate again the solution.
        self.sol.cost = self.CalculateTotalCost(self.sol)
        self.ReportSolution(self.sol)

        # DEBUG
        # We add this print for monitoring reasons we should exclude it later
        newCost = self.CalculateTotalCost(self.sol)

        # Output messages.
        # In many cases the top.moveCost represent the decreasment on the worst route, but since another
        # worst route pops up the difference between the old and new cost does not match the moveCost (like
        # the examples given).
        print("\nThe two opt move cost for the applied relocation is", top.moveCost)
        print("old new", oldCost, newCost)
        print("The estimated cost from the apply function of the latest solution is", self.sol.cost, "\n")
        print("===================================================================\n")

    # FindBestTwoOptMove for DefaultVND (check all routes with all routes).
    def FindBestTwoOptMove2(self, top):

        # Find the index of the first route index.
        for rtInd1 in range(0, len(self.sol.routes)):
            # Defines first route.
            rt1: Route = self.sol.routes[rtInd1]

            # Iterate over all origin route's nodes.
            for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):

                # The first node is determined.
                A = rt1.sequenceOfNodes[nodeInd1]
                B = rt1.sequenceOfNodes[nodeInd1 + 1]

                # Iterate over all other available routes in the solution to be the target route of the two opt node.
                for rtInd2 in range(rtInd1, len(self.sol.routes)):
                    rt2: Route = self.sol.routes[rtInd2]

                    # Inter-route move.
                    start2 = 0

                    # Intra-route move.
                    if rt1 == rt2:
                        start2 = nodeInd1 + 2

                    # Iterate over all nodes of a target route.
                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):

                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]

                        # Same route.
                        if rt1 == rt2:

                            # Check the constraints.
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue

                            # Calculate the cost change in both routes affected by the two opt move.
                            costAdded = self.distanceMatrix[A.ID][K.ID] + self.distanceMatrix[B.ID][L.ID]
                            costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]

                            # Calculate the cost change of the solution after the two opt move.
                            moveCost = costAdded - costRemoved

                            # Check if the two opt move leads to a lower solution cost of the origin route that
                            # represents the route with the higher cost and that the two opt cost do not lead the
                            # rt1 route to have higher cost than the initial
                            # cost of the origin route before the two opt.
                            if moveCost < 0 and moveCost < top.moveCost and rt1.cost + moveCost < self.sol.cost:

                                # Update the two opt move characteristics with the respect to the last move that
                                # leads to a lower cost.
                                self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top)

                        # Different routes, rt1 != rt2.
                        else:

                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue

                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and nodeInd2 == len(
                                    rt2.sequenceOfNodes) - 2:
                                continue

                            # Check the capacity constrain.
                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue

                            # Calculate the costs change of the solution after the two opt move.
                            costAdded = self.distanceMatrix[A.ID][L.ID] + self.distanceMatrix[B.ID][K.ID]
                            costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]

                            moveCost = costAdded - costRemoved

                            rt2movecost = self.distanceMatrix[B.ID][K.ID] - self.distanceMatrix[K.ID][L.ID]
                            rt1movecost = self.distanceMatrix[A.ID][L.ID] - self.distanceMatrix[A.ID][B.ID]

                            # Check if the two opt move leads to a lower solution cost of the origin route that
                            # represents the route with the higher cost and that the two opt cost do not lead the
                            # rt1 amd rt2 to not the worst solutions than the solution's cost.
                            if moveCost < 0 and moveCost < top.moveCost and rt2.cost + rt2movecost < self.sol.cost\
                                    and rt1.cost + rt1movecost < self.sol.cost:

                                # Update the two opt move characteristics with the respect to the last move that
                                # leads to a lower cost.
                                self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top)


############################################### AdvancedVND ############################################################

    # AdvancedVND is the VND that is applied in the second phase, after the implementation of the DefaultVND, and it has
    # as its main focuses on decreasing our objective function, the worst route time-wise throughout move types.
    def AdvancedVND(self):
        # Get the best solution.
        self.bestSolution = self.cloneSolution(self.sol)

        # Initialize components.
        VNDIterator = 0
        kmax = 2
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        k = 0

        # While-loop statement that iterates while the solution keeps improving.
        while k <= kmax:

            # Draw the solution, through the Solution Drawer Class.
            SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
            # Initialize components.
            self.InitializeOperators(rm, sm, top)

            # Relocation Move.
            if k == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                    VNDIterator = VNDIterator + 1
                    print('Relocation Move  -  ', 'Iteration number:', VNDIterator,
                          'Solution Cost:', self.sol.cost)
                    k = 0
                else:
                    k += 1

            # Swap Move.
            elif k == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None and sm.moveCost < 0:
                    self.ApplySwapMove(sm)
                    VNDIterator = VNDIterator + 1
                    print('Swap Move  -  ', 'Iteration number:', VNDIterator,
                          'Solution Cost:', self.sol.cost)
                    k = 0
                else:
                    k += 1

            # Two Opt Move.
            elif k == 2:
                self.FindBestTwoOptMove(top)
                if top.positionOfSecondRoute is not None and top.moveCost < 0:
                    self.ApplyTwoOptMove(top)
                    VNDIterator = VNDIterator + 1
                    print('TwoOpt Move  -  ', 'Iteration number:', VNDIterator,
                          'Solution Cost:', self.sol.cost)
                    k = 0

                else:
                    k += 1

            # Store the best solution.
            if self.sol.cost < self.bestSolution.cost:
                self.bestSolution = self.cloneSolution(self.sol)


############################################### DefaultVND #############################################################

    # DefaultVND is the VND that is implemented first of the two VND, and focuses on all routes to all routes, until
    # they do not make our solution worst. It is found out that the AdvancedVND outputs way better results - since the
    # advanced one focuses on reducing the worst route's cost. However, lots of crisscrosses to routes will relative
    # small cost were observed. Then, we thought that it will help if we implement a more general approach in between
    # the initial and the final solution. This idea lead us to implement the DefaultVND, and lead us to better results.
    # Throughout its architecture, the default VND may not lead us to better results but will eventually help the
    # Advanced one to output even better results than before.
    def DefaultVND(self):
        # Get the best solution.
        self.bestSolution = self.cloneSolution(self.sol)

        # Initialize components.
        VNDIterator = 0
        kmax = 2
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        k = 0

        # While-loop statement that iterates while the solution keeps improving.
        while k <= kmax:

            # Draw the solution, through the Solution Drawer Class (different drawer than the AdvancedVND).
            SolDrawer.draw2(VNDIterator, self.sol, self.allNodes)
            # Initialize components.
            self.InitializeOperators(rm, sm, top)

            # Relocation Move.
            if k == 2:
                self.FindBestRelocationMove2(rm)
                if rm.originRoutePosition is not None and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                    VNDIterator = VNDIterator + 1
                    print('Relocation Move  -  ', 'Iteration number:', VNDIterator,
                          'Solution Cost:', self.sol.cost)
                    k = 0
                else:
                    k += 1

            # Swap Move.
            elif k == 1:
                self.FindBestSwapMove2(sm)
                if sm.positionOfFirstRoute is not None and sm.moveCost < 0:
                    self.ApplySwapMove(sm)
                    VNDIterator = VNDIterator + 1
                    print('Swap Move  -  ', 'Iteration number:', VNDIterator,
                          'Solution Cost:', self.sol.cost)
                    k = 0
                else:
                    k += 1

            # Two Opt Move.
            elif k == 0:
                self.FindBestTwoOptMove2(top)
                if top.positionOfSecondRoute is not None and (top.moveCost < 0):
                    self.ApplyTwoOptMove(top)
                    VNDIterator = VNDIterator + 1
                    print('TwoOpt Move  -  ', 'Iteration number:', VNDIterator,
                          'Solution Cost:', self.sol.cost)
                    k = 0
                else:
                    k += 1

            # Store the best solution.
            if self.sol.cost < self.bestSolution.cost:
                self.bestSolution = self.cloneSolution(self.sol)