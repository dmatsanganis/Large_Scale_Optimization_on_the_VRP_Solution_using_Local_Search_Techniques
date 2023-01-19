from VRP_Model import *
from SolutionDrawer import *


class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []


class Saving:
    def __init__(self, n1, n2, sav):
        self.n1 = n1
        self.n2 = n2
        self.score = sav


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


class CustomerInsertionAllPositions(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.insertionPosition = None
        self.cost = 10 ** 9


class Solver:
    def __init__(self, m):
        self.allNodes = m.allNodes
        self.customers = m.customers
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None
        self.rtCounter = 0
        self.rtInd = -1
        self.iterations = None
        self.reloMove = False

    def solve(self):
        # self.MinimumInsertions()
        self.Clarke_n_Wright()

        self.ReportSolution(self.sol)
        self.LocalSearch(0)
        # self.VND()
        self.ReportSolution(self.sol)

        return self.sol

    ###################
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

    def Clarke_n_Wright(self):
        self.sol = self.create_initial_routes()
        savings: list = self.calculate_savings()
        savings.sort(key=lambda s: s.score, reverse=True)
        k = 0

        for i in range(0, len(savings)):
            sav = savings[i]
            n1 = sav.n1
            n2 = sav.n2
            rt1 = n1.route
            rt2 = n2.route

            if n1.route == n2.route:
                continue
            if self.not_first_or_last(rt1, n1) or self.not_first_or_last(rt2, n2):
                continue
            if rt1.load + rt2.load > self.capacity:
                continue

            cst = self.CalculateTotalCost(self.sol)
            costcalc = rt1.cost + rt2.cost - sav.score

            if k < 174:
                self.merge_routes(n1, n2)
                rt1.cost = costcalc

                # #self.sol.cost -= sav.score
                self.sol.cost = self.CalculateTotalCost(self.sol)
                k = k + 1
                print(cst, self.sol.cost, k)

    def calculate_savings(self):
        savings = []
        for i in range(0, len(self.customers)):
            n1 = self.customers[i]
            for j in range(i + 1, len(self.customers)):
                n2 = self.customers[j]

                score = self.distanceMatrix[n1.ID][self.depot.ID] + self.distanceMatrix[self.depot.ID][n2.ID]
                score -= self.distanceMatrix[n1.ID][n2.ID]

                sav = Saving(n1, n2, score)
                savings.append(sav)

        return savings

    def create_initial_routes(self):
        s = Solution()
        initial_routes_costs = []
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
        s.cost = max(initial_routes_costs)
        return s

    def not_first_or_last(self, rt, n):
        if n.position_in_route != 1 and n.position_in_route != len(rt.sequenceOfNodes) - 2:
            return True
        return False

    def merge_routes(self, n1, n2):
        rt1 = n1.route
        rt2 = n2.route

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
        rt1.load += rt2.load
        self.sol.routes.remove(rt2)
        self.update_route_customers(rt1)

    def update_route_customers(self, rt):
        for i in range(1, len(rt.sequenceOfNodes) - 1):
            n = rt.sequenceOfNodes[i]
            n.route = rt
            n.position_in_route = i

    def CalculateTotalCost(self, sol):
        # We change the cost calculation method as it should return the max time needed to serve the last customer
        # in every route and then find the global maximum of all routes.
        c = []
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            r = []
            for j in range(0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                r.append(self.distanceMatrix[a.ID][b.ID])
            c.append(sum(r))
        cst = max(c)
        return cst

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

    def LocalSearch(self, operator):
        self.bestSolution = self.cloneSolution(self.sol)
        terminationCondition = False
        localSearchIterator = 0

        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()

        while terminationCondition is False:

            self.InitializeOperators(rm, sm, top)
            # SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost < 0:
                        self.ApplyRelocationMove(rm)
                    else:
                        terminationCondition = True

            # Swaps
            elif operator == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:
                    if sm.moveCost < 0:
                        self.ApplySwapMove(sm)
                    else:
                        terminationCondition = True

            # Two Opt Move.
            elif operator == 2:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None:
                    if top.moveCost < 0:
                        self.ApplyTwoOptMove(top)
                    else:
                        terminationCondition = True

            # self.TestSolution()

            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

            localSearchIterator = localSearchIterator + 1
            print(localSearchIterator, self.sol.cost)

        self.sol = self.bestSolution

    def cloneRoute(self, rt: Route):
        cloned = Route(self.depot, self.capacity)
        cloned.cost = rt.cost
        cloned.load = rt.load
        cloned.sequenceOfNodes = rt.sequenceOfNodes.copy()
        return cloned

    def cloneSolution(self, sol: Solution):
        cloned = Solution()
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            clonedRoute = self.cloneRoute(rt)
            cloned.routes.append(clonedRoute)
            # The sol.cost for us is calculated inside the report function in order to update the solution cost
        cloned.cost = self.sol.cost
        return cloned

    def InitializeOperators(self, rm, sm, top):
        rm.Initialize()
        sm.Initialize()
        top.Initialize()

    def FindBestRelocationMove(self, rm):

        # Create the worst_routes_lst.
        worst_routes_lst = []

        for i in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[i]
            worst_routes_lst.append(rt)

        worst_routes_lst.sort(key=lambda x: x.cost, reverse=True)

        # # DEBUG ONLY.
        # for i in range(0, len(worst_routes_lst)):
        #     rt = worst_routes_lst[i]
        #     for j in range(0, len(rt.sequenceOfNodes)):
        #         print(rt.sequenceOfNodes[j].ID, end=' ')
        #     print(rt.cost)
        #
        # print(worst_routes_lst)

        # The worst route is the original index, initially.
        # rt1: Route = worst_routes_lst[0]

        # Trace originRouteIndex.
        for originRouteIndex in range(0, len(self.sol.routes)):
            if worst_routes_lst[0] != self.sol.routes[originRouteIndex]:
                continue
            else:
                rt1: Route = self.sol.routes[originRouteIndex]

            for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):

                A = rt1.sequenceOfNodes[originNodeIndex - 1]
                B = rt1.sequenceOfNodes[originNodeIndex]
                C = rt1.sequenceOfNodes[originNodeIndex + 1]

                # A for-loop statement for all the routes of the solution.
                for targetRouteIndex in range(0, len(self.sol.routes)):
                    rt2: Route = self.sol.routes[targetRouteIndex]

                    for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                        if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - \
                                             self.distanceMatrix[B.ID][C.ID]

                        targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - \
                                             self.distanceMatrix[F.ID][G.ID]


                        # Relocation move is performed on one route.
                        if rt1 == rt2:
                            moveCost = originRtCostChange + targetRtCostChange

                            if (moveCost < rm.moveCost) and ((originRtCostChange + rt1.cost + targetRtCostChange) < self.sol.cost):
                                self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                             targetNodeIndex, moveCost, originRtCostChange,
                                                             targetRtCostChange, rm)

                                print("1dddddddddddddddddddddd1111111111")

                            else:
                                self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                             targetNodeIndex, 10000, originRtCostChange,
                                                             targetRtCostChange, rm)
                                print("ddddddddddd5555555555")
                                continue

                        # Relocation move is performed between two routes (the worst and another one).
                        elif rt1 != rt2 and rt2.load + B.demand <= rt2.capacity:
                            moveCost = originRtCostChange

                            if (moveCost < rm.moveCost) and ((originRtCostChange + rt1.cost) < self.sol.cost) and ((targetRtCostChange + rt2.cost) < self.sol.cost):
                                self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                             targetNodeIndex, moveCost, originRtCostChange,
                                                             targetRtCostChange, rm)
                                print("11111111111")

                            else:
                                self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                             targetNodeIndex, 10000, originRtCostChange,
                                                             targetRtCostChange, rm)
                                print("5555555555")
                                continue

                        else:
                            continue

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost, originRtCostChange, targetRtCostChange, rm: RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    def ApplyRelocationMove(self, rm: RelocationMove):
        originRt = self.sol.routes[rm.originRoutePosition]
        targetRt = self.sol.routes[rm.targetRoutePosition]

        # The node to be relocated
        B = originRt.sequenceOfNodes[rm.originNodePosition]

        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]

            if rm.originNodePosition < rm.targetNodePosition:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)

            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.cost += rm.costChangeOriginRt + rm.costChangeTargetRt

        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.cost += rm.costChangeOriginRt
            targetRt.cost += rm.costChangeTargetRt
            originRt.load -= B.demand
            targetRt.load += B.demand

        self.sol.cost = self.CalculateTotalCost(self.sol)

        # self.TestSolution()

        # # We add this print for monitoring reasons we should exclude it later
        # print(rm.moveCost)
        # newCost = self.CalculateTotalCost(self.sol)
        # #debuggingOnly
        # if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
        #     print('Cost Issue')

    def FindBestSwapMove(self, sm):
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[firstRouteIndex]
            for firstNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                # first swapped node is cdetermined
                for secondRouteIndex in range(firstRouteIndex, len(self.sol.routes)):
                    rt2: Route = self.sol.routes[secondRouteIndex]
                    startOfSecondNodeIndex = 1
                    if rt1 == rt2:
                        startOfSecondNodeIndex = firstNodeIndex + 1
                    for secondNodeIndex in range(startOfSecondNodeIndex, len(rt2.sequenceOfNodes) - 1):

                        a1 = rt1.sequenceOfNodes[firstNodeIndex - 1]
                        b1 = rt1.sequenceOfNodes[firstNodeIndex]
                        c1 = rt1.sequenceOfNodes[firstNodeIndex + 1]

                        a2 = rt2.sequenceOfNodes[secondNodeIndex - 1]
                        b2 = rt2.sequenceOfNodes[secondNodeIndex]
                        c2 = rt2.sequenceOfNodes[secondNodeIndex + 1]

                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                # case of consecutive nodes swap
                                costRemoved = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][b2.ID] + \
                                              self.distanceMatrix[b2.ID][c2.ID]
                                costAdded = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][b1.ID] + \
                                            self.distanceMatrix[b1.ID][c2.ID]
                                moveCost = costAdded - costRemoved
                            else:

                                costRemoved1 = self.distanceMatrix[a1.ID][b1.ID] + self.distanceMatrix[b1.ID][c1.ID]
                                costAdded1 = self.distanceMatrix[a1.ID][b2.ID] + self.distanceMatrix[b2.ID][c1.ID]
                                costRemoved2 = self.distanceMatrix[a2.ID][b2.ID] + self.distanceMatrix[b2.ID][c2.ID]
                                costAdded2 = self.distanceMatrix[a2.ID][b1.ID] + self.distanceMatrix[b1.ID][c2.ID]
                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                        else:
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

                            moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)

                        if moveCost < sm.moveCost:
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                   moveCost, costChangeFirstRoute, costChangeSecondRoute, sm)

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost,
                          costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost

    def ApplySwapMove(self, sm):
        oldCost = self.CalculateTotalCost(self.sol)
        rt1 = self.sol.routes[sm.positionOfFirstRoute]
        rt2 = self.sol.routes[sm.positionOfSecondRoute]
        b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
        rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
        rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

        if rt1 == rt2:
            rt1.cost += sm.moveCost
        else:
            rt1.cost += sm.costChangeFirstRt
            rt2.cost += sm.costChangeSecondRt
            rt1.load = rt1.load - b1.demand + b2.demand
            rt2.load = rt2.load + b1.demand - b2.demand

        self.sol.cost += sm.moveCost
        self.TestSolution()

        # newCost = self.CalculateTotalCost(self.sol)
        # # debuggingOnly
        # if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
        #     print('Cost Issue')

    def FindBestTwoOptMove(self, top):
        for rtInd1 in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[rtInd1]
            for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                # first node is determined
                A = rt1.sequenceOfNodes[nodeInd1]
                B = rt1.sequenceOfNodes[nodeInd1 + 1]

                for rtInd2 in range(rtInd1, len(self.sol.routes)):

                    rt2: Route = self.sol.routes[rtInd2]
                    start2 = 0  # inter-route move
                    if rt1 == rt2:
                        start2 = nodeInd1 + 2  # intra-route move

                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):

                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue
                            costAdded = self.distanceMatrix[A.ID][K.ID] + self.distanceMatrix[B.ID][L.ID]
                            costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]
                            moveCost = costAdded - costRemoved
                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue

                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue
                            costAdded = self.distanceMatrix[A.ID][L.ID] + self.distanceMatrix[B.ID][K.ID]
                            costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[K.ID][L.ID]
                            moveCost = costAdded - costRemoved
                        if moveCost < top.moveCost:
                            self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top)

    def CapacityIsViolated(self, rt1, nodeInd1, rt2, nodeInd2):
        rt1FirstSegmentLoad = 0
        for i in range(0, nodeInd1 + 1):
            n = rt1.sequenceOfNodes[i]
            rt1FirstSegmentLoad += n.demand
        rt1SecondSegmentLoad = rt1.load - rt1FirstSegmentLoad

        rt2FirstSegmentLoad = 0
        for i in range(0, nodeInd2 + 1):
            n = rt2.sequenceOfNodes[i]
            rt2FirstSegmentLoad += n.demand
        rt2SecondSegmentLoad = rt2.load - rt2FirstSegmentLoad

        if (rt1FirstSegmentLoad + rt2SecondSegmentLoad > rt1.capacity):
            return True
        if (rt2FirstSegmentLoad + rt1SecondSegmentLoad > rt2.capacity):
            return True

        return False

    def StoreBestTwoOptMove(self, rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, top):
        top.positionOfFirstRoute = rtInd1
        top.positionOfSecondRoute = rtInd2
        top.positionOfFirstNode = nodeInd1
        top.positionOfSecondNode = nodeInd2
        top.moveCost = moveCost

    def ApplyTwoOptMove(self, top):
        rt1: Route = self.sol.routes[top.positionOfFirstRoute]
        rt2: Route = self.sol.routes[top.positionOfSecondRoute]

        if rt1 == rt2:
            # reverses the nodes in the segment [positionOfFirstNode + 1,  top.positionOfSecondNode]
            reversedSegment = reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1])
            # lst = list(reversedSegment)
            # lst2 = list(reversedSegment)
            rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegment

            # reversedSegmentList = list(reversed(rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1]))
            # rt1.sequenceOfNodes[top.positionOfFirstNode + 1: top.positionOfSecondNode + 1] = reversedSegmentList

            rt1.cost += top.moveCost


        else:
            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt1 = rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]

            # slice with the nodes from position top.positionOfFirstNode + 1 onwards
            relocatedSegmentOfRt2 = rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            del rt1.sequenceOfNodes[top.positionOfFirstNode + 1:]
            del rt2.sequenceOfNodes[top.positionOfSecondNode + 1:]

            rt1.sequenceOfNodes.extend(relocatedSegmentOfRt2)
            rt2.sequenceOfNodes.extend(relocatedSegmentOfRt1)

            self.UpdateRouteCostAndLoad(rt1)
            self.UpdateRouteCostAndLoad(rt2)

        self.sol.cost += top.moveCost
        self.TestSolution()

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

    def VND(self):
        self.bestSolution = self.cloneSolution(self.sol)

        VNDIterator = 0
        kmax = 2
        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()
        k = 0

        while k <= kmax:
            # SolDrawer.draw(VNDIterator, self.sol, self.allNodes)
            self.InitializeOperators(rm, sm, top)

            if k == 2:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None and rm.moveCost < 0:
                    self.ApplyRelocationMove(rm)
                    VNDIterator = VNDIterator + 1
                    print('Relocation Move  -  ', 'Iteration number:', VNDIterator,
                          'Solution Cost:', self.sol.cost)
                    k = 0
                else:
                    k += 1

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

            elif k == 0:
                self.FindBestTwoOptMove(top)
                if top.positionOfSecondRoute is not None and (top.moveCost < 0):
                    self.ApplyTwoOptMove(top)
                    VNDIterator = VNDIterator + 1
                    print('TwoOpt Move  -  ', 'Iteration number:', VNDIterator,
                          'Solution Cost:', self.sol.cost)
                    k = 0
                else:
                    k += 1

            if (self.sol.cost < self.bestSolution.cost):
                self.bestSolution = self.cloneSolution(self.sol)

        # allrt_costs = []
        #
        # for i in range(0, len(self.bestSolution.routes)):
        #     rt = self.bestSolution.routes[i]
        #
        #     for j in range(0, len(rt.sequenceOfNodes)):
        #         print(rt.sequenceOfNodes[j].ID, end=' ')
        #
        #     print(rt.cost)
        #     allrt_costs.append(rt.cost)
        #
        # print(self.bestSolution.cost)
        # #self.ReportSolution(self.bestSolution)
