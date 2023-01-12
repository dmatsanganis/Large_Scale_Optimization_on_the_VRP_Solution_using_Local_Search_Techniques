from VRP_Model import *
from SolutionDrawer import *


class Solution:
    def __init__(self):
        self.cost = 0.0
        self.routes = []


class RelocationMove(object):
    def __init__(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = None
        self.moveCost_penalized = None

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9
        self.moveCost_penalized = 10 ** 9

class SwapMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = None
        self.moveCost_penalized = None

    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.costChangeFirstRt = None
        self.costChangeSecondRt = None
        self.moveCost = 10 ** 9
        self.moveCost_penalized = 10 ** 9

class TwoOptMove(object):
    def __init__(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = None
        self.moveCost_penalized = None

    def Initialize(self):
        self.positionOfFirstRoute = None
        self.positionOfSecondRoute = None
        self.positionOfFirstNode = None
        self.positionOfSecondNode = None
        self.moveCost = 10 ** 9
        self.moveCost_penalized = 10 ** 9


class CustomerInsertion(object):
    def __init__(self):
        self.customer = None
        self.route = None
        self.cost = 10 ** 9


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
        self.distance_matrix = m.matrix
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None
        self.searchTrajectory = []
        self.rtCounter = 0
        self.rtInd = -1
        self.iterations = None
        rows = len(self.allNodes)
        self.distance_matrix_penalized = [[self.distance_matrix[i][j] for j in range(rows)] for i in range(rows)]
        self.times_penalized = [[0 for j in range(rows)] for i in range(rows)]
        self.penalized_n1_ID = -1
        self.penalized_n2_ID = -1

    def solve(self):
        self.SetRoutedFlagToFalseForAllCustomers()
        self.MinimumInsertions()
        self.ReportSolution(self.sol)
        self.LocalSearch(2)
        self.ReportSolution(self.sol)

        return self.sol

    def SetRoutedFlagToFalseForAllCustomers(self):
        for i in range(0, len(self.customers)):
            self.customers[i].isRouted = False

    def Always_keep_an_empty_route(self):
        if len(self.sol.routes) == 0:
            rt = Route(self.depot, self.capacity)
            self.sol.routes.append(rt)
        else:
            rt = self.sol.routes[-1]
            if len(rt.sequenceOfNodes) > 2:
                rt = Route(self.depot, self.capacity)
                self.sol.routes.append(rt)

    def IdentifyMinimumCostInsertion(self, best_insertion):
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                for rt in self.sol.routes:
                    if rt.load + candidateCust.demand <= rt.capacity:
                        for j in range(0, len(rt.sequenceOfNodes) - 1):
                            A = rt.sequenceOfNodes[j]
                            B = rt.sequenceOfNodes[j + 1]
                            costAdded = self.distance_matrix[A.ID][candidateCust.ID] + \
                                        self.distance_matrix[candidateCust.ID][
                                            B.ID]
                            costRemoved = self.distance_matrix[A.ID][B.ID]
                            trialCost = costAdded - costRemoved
                            if trialCost < best_insertion.cost:
                                best_insertion.customer = candidateCust
                                best_insertion.route = rt
                                best_insertion.insertionPosition = j
                                best_insertion.cost = trialCost
                    else:
                        continue

    def MinimumInsertions(self):
        model_is_feasible = True
        self.sol = Solution()
        insertions = 0

        while insertions < len(self.customers):
            best_insertion = CustomerInsertionAllPositions()
            self.Always_keep_an_empty_route()
            self.IdentifyMinimumCostInsertion(best_insertion)

            if best_insertion.customer is not None:
                self.ApplyCustomerInsertionAllPositions(best_insertion)
                insertions += 1
            else:
                print('FeasibilityIssue')
                model_is_feasible = False
                break

        if model_is_feasible:
            self.TestSolution()
    # def MinimumInsertions(self):
    #     modelIsFeasible = True
    #     self.sol = Solution()
    #     insertions = 0
    #     distFrombase = self.distance_matrix[0]
    #
    #     closest26points = sorted(range(1, len(distFrombase)), key=lambda k: distFrombase[k])[:26]
    #     insPos = 0
    #
    #     for i in closest26points:
    #         rt = Route(self.depot, self.capacity)
    #         self.sol.routes.append(rt)
    #         randomInsertion = CustomerInsertionAllPositions()
    #         randomInsertion.customer = self.allNodes[i]
    #         randomInsertion.customer.demand = self.allNodes[i].demand
    #         randomInsertion.route = self.sol.routes[closest26points.index(i)]
    #         randomInsertion.cost = self.distance_matrix[0][i]
    #         randomInsertion.insertionPosition = insPos
    #         self.ApplyCustomerInsertionAllPositions(randomInsertion)
    #         insertions += 1
    #         self.rtCounter = 1
    #
    #     while insertions < len(self.points):
    #         bestInsertion = CustomerInsertionAllPositions()
    #         if self.rtInd == 25:
    #             self.rtInd = 0
    #         else:
    #             self.rtInd += 1
    #
    #         lastOpenRoute: Route = self.GetLastOpenRoute()
    #
    #         if lastOpenRoute is not None:
    #             self.IdentifyBestInsertionAllPositions(bestInsertion, lastOpenRoute)
    #
    #         if bestInsertion.customer is not None:
    #             self.ApplyCustomerInsertionAllPositions(bestInsertion)
    #             insertions += 1
    #
    #         else:
    #             # If there is an empty available route
    #             if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 2:
    #                 modelIsFeasible = False
    #                 break
    #             # If there is no empty available route and no feasible insertion was identified
    #             else:
    #                 self.rtCounter += 1
    #
    #     if modelIsFeasible == False:
    #         print('FeasibilityIssue')
    #
    #     self.TestSolution()

    def LocalSearch(self, operator):
        random.seed(1)
        localSearchIterator = 0
        self.bestSolution = self.cloneSolution(self.sol)

        terminationCondition = False

        rm = RelocationMove()
        sm = SwapMove()
        top = TwoOptMove()

        self.searchTrajectory.append(self.sol.cost)

        while terminationCondition is False:
            operator = random.randint(0, 2)
            self.InitializeOperators(rm, sm, top)

            SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost_penalized < 0:
                        self.ApplyRelocationMove(rm)
                        # print(localSearchIterator, self.sol.cost, operator)
                    else:
                        self.penalize_arcs()
                        localSearchIterator = localSearchIterator - 1
            # Swaps
            elif operator == 1:
                self.FindBestSwapMove(sm)
                if sm.positionOfFirstRoute is not None:
                    if sm.moveCost_penalized < 0:
                        self.ApplySwapMove(sm)
                        # print(localSearchIterator, self.sol.cost, operator)
                    else:
                        self.penalize_arcs()
                        localSearchIterator = localSearchIterator - 1

            elif operator == 2:
                self.FindBestTwoOptMove(top)
                if top.positionOfFirstRoute is not None:
                    if top.moveCost_penalized < 0:
                        self.ApplyTwoOptMove(top)
                        # print(localSearchIterator, self.sol.cost, operator)
                    else:
                        self.penalize_arcs()
                        localSearchIterator = localSearchIterator - 1

            self.TestSolution()

            if self.sol.cost < self.bestSolution.cost:
                self.bestSolution = self.cloneSolution(self.sol)
                print(localSearchIterator, self.bestSolution.cost)

            self.searchTrajectory.append(self.sol.cost)
            localSearchIterator = localSearchIterator + 1

        SolDrawer.drawTrajectory(self.searchTrajectory)
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
        cloned.cost = self.sol.cost
        return cloned

    def FindBestRelocationMove(self, rm):
        for originRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[originRouteIndex]
            for targetRouteIndex in range(0, len(self.sol.routes)):
                rt2: Route = self.sol.routes[targetRouteIndex]
                for originNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
                    for targetNodeIndex in range(0, len(rt2.sequenceOfNodes) - 1):

                        if originRouteIndex == targetRouteIndex and (targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue

                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        if rt1 != rt2:

                            if rt2.load + B.demand > rt2.capacity:
                                continue

                        costAdded = self.distance_matrix[A.ID][C.ID] + self.distance_matrix[F.ID][B.ID] + \
                                    self.distance_matrix[B.ID][G.ID]
                        costRemoved = self.distance_matrix[A.ID][B.ID] + self.distance_matrix[B.ID][C.ID] + \
                                      self.distance_matrix[F.ID][G.ID]

                        costAdded_penalized = self.distance_matrix_penalized[A.ID][C.ID] + \
                                              self.distance_matrix_penalized[F.ID][B.ID] + \
                                              self.distance_matrix_penalized[B.ID][G.ID]
                        costRemoved_penalized = self.distance_matrix_penalized[A.ID][B.ID] + \
                                                self.distance_matrix_penalized[B.ID][C.ID] + \
                                                self.distance_matrix_penalized[F.ID][G.ID]

                        originRtCostChange = self.distance_matrix[A.ID][C.ID] - self.distance_matrix[A.ID][B.ID] - \
                                             self.distance_matrix[B.ID][C.ID]
                        targetRtCostChange = self.distance_matrix[F.ID][B.ID] + self.distance_matrix[B.ID][G.ID] - \
                                             self.distance_matrix[F.ID][G.ID]

                        moveCost = costAdded - costRemoved
                        moveCost_penalized = costAdded_penalized - costRemoved_penalized


                        if (moveCost_penalized < rm.moveCost_penalized):
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                         targetNodeIndex, moveCost, moveCost_penalized, originRtCostChange,
                                                         targetRtCostChange, rm)

    def FindBestSwapMove(self, sm):
        for firstRouteIndex in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[firstRouteIndex]
            for secondRouteIndex in range(firstRouteIndex, len(self.sol.routes)):
                rt2: Route = self.sol.routes[secondRouteIndex]
                for firstNodeIndex in range(1, len(rt1.sequenceOfNodes) - 1):
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

                        moveCost = None
                        costChangeFirstRoute = None
                        costChangeSecondRoute = None

                        if rt1 == rt2:
                            if firstNodeIndex == secondNodeIndex - 1:
                                costRemoved = self.distance_matrix[a1.ID][b1.ID] + self.distance_matrix[b1.ID][b2.ID] + \
                                              self.distance_matrix[b2.ID][c2.ID]
                                costAdded = self.distance_matrix[a1.ID][b2.ID] + self.distance_matrix[b2.ID][b1.ID] + \
                                            self.distance_matrix[b1.ID][c2.ID]
                                moveCost = costAdded - costRemoved

                                costRemoved_penalized = self.distance_matrix_penalized[a1.ID][b1.ID] + \
                                                        self.distance_matrix_penalized[b1.ID][b2.ID] + \
                                                        self.distance_matrix_penalized[b2.ID][c2.ID]
                                costAdded_penalized = self.distance_matrix_penalized[a1.ID][b2.ID] + \
                                                      self.distance_matrix_penalized[b2.ID][b1.ID] + \
                                                      self.distance_matrix_penalized[b1.ID][c2.ID]
                                moveCost_penalized = costAdded_penalized - costRemoved_penalized

                            else:
                                costRemoved1 = self.distance_matrix[a1.ID][b1.ID] + self.distance_matrix[b1.ID][c1.ID]
                                costAdded1 = self.distance_matrix[a1.ID][b2.ID] + self.distance_matrix[b2.ID][c1.ID]
                                costRemoved2 = self.distance_matrix[a2.ID][b2.ID] + self.distance_matrix[b2.ID][c2.ID]
                                costAdded2 = self.distance_matrix[a2.ID][b1.ID] + self.distance_matrix[b1.ID][c2.ID]
                                moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                                costRemoved1_penalized = self.distance_matrix_penalized[a1.ID][b1.ID] + \
                                                         self.distance_matrix_penalized[b1.ID][c1.ID]
                                costAdded1_penalized = self.distance_matrix_penalized[a1.ID][b2.ID] + \
                                                       self.distance_matrix_penalized[b2.ID][c1.ID]
                                costRemoved2_penalized = self.distance_matrix_penalized[a2.ID][b2.ID] + \
                                                         self.distance_matrix_penalized[b2.ID][c2.ID]
                                costAdded2_penalized = self.distance_matrix_penalized[a2.ID][b1.ID] + \
                                                       self.distance_matrix_penalized[b1.ID][c2.ID]
                                moveCost_penalized = costAdded1_penalized + costAdded2_penalized - (
                                            costRemoved1_penalized + costRemoved2_penalized)
                        else:
                            if rt1.load - b1.demand + b2.demand > self.capacity:
                                continue
                            if rt2.load - b2.demand + b1.demand > self.capacity:
                                continue

                            costRemoved1 = self.distance_matrix[a1.ID][b1.ID] + self.distance_matrix[b1.ID][c1.ID]
                            costAdded1 = self.distance_matrix[a1.ID][b2.ID] + self.distance_matrix[b2.ID][c1.ID]
                            costRemoved2 = self.distance_matrix[a2.ID][b2.ID] + self.distance_matrix[b2.ID][c2.ID]
                            costAdded2 = self.distance_matrix[a2.ID][b1.ID] + self.distance_matrix[b1.ID][c2.ID]
                            costRemoved1_penalized = self.distance_matrix_penalized[a1.ID][b1.ID] + \
                                                     self.distance_matrix_penalized[b1.ID][c1.ID]
                            costAdded1_penalized = self.distance_matrix_penalized[a1.ID][b2.ID] + \
                                                   self.distance_matrix_penalized[b2.ID][c1.ID]
                            costRemoved2_penalized = self.distance_matrix_penalized[a2.ID][b2.ID] + \
                                                     self.distance_matrix_penalized[b2.ID][c2.ID]
                            costAdded2_penalized = self.distance_matrix_penalized[a2.ID][b1.ID] + \
                                                   self.distance_matrix_penalized[b1.ID][c2.ID]

                            costChangeFirstRoute = costAdded1 - costRemoved1
                            costChangeSecondRoute = costAdded2 - costRemoved2

                            moveCost = costAdded1 + costAdded2 - (costRemoved1 + costRemoved2)
                            moveCost_penalized = costAdded1_penalized + costAdded2_penalized - (
                                    costRemoved1_penalized + costRemoved2_penalized)

                        if moveCost_penalized < sm.moveCost_penalized:
                            self.StoreBestSwapMove(firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex,
                                                   moveCost, moveCost_penalized, costChangeFirstRoute,
                                                   costChangeSecondRoute, sm)

    def ApplyRelocationMove(self, rm: RelocationMove):

        oldCost = self.CalculateTotalCost(self.sol)

        originRt = self.sol.routes[rm.originRoutePosition]
        targetRt = self.sol.routes[rm.targetRoutePosition]

        B = originRt.sequenceOfNodes[rm.originNodePosition]

        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            if (rm.originNodePosition < rm.targetNodePosition):
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition, B)
            else:
                targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)

            originRt.cost += rm.moveCost
        else:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            targetRt.sequenceOfNodes.insert(rm.targetNodePosition + 1, B)
            originRt.cost += rm.costChangeOriginRt
            targetRt.cost += rm.costChangeTargetRt
            originRt.load -= B.demand
            targetRt.load += B.demand

        self.sol.cost += rm.moveCost

        # newCost = self.CalculateTotalCost(self.sol)
        # # debuggingOnly
        # if abs((newCost - oldCost) - rm.moveCost) > 0.0001:
        #     print('Cost Issue')

    def ApplySwapMove(self, sm):
        oldCost = self.CalculateTotalCost(self.sol)
        rt1 = self.sol.routes[sm.positionOfFirstRoute]
        rt2 = self.sol.routes[sm.positionOfSecondRoute]
        b1 = rt1.sequenceOfNodes[sm.positionOfFirstNode]
        b2 = rt2.sequenceOfNodes[sm.positionOfSecondNode]
        rt1.sequenceOfNodes[sm.positionOfFirstNode] = b2
        rt2.sequenceOfNodes[sm.positionOfSecondNode] = b1

        if (rt1 == rt2):
            rt1.cost += sm.moveCost
        else:
            rt1.cost += sm.costChangeFirstRt
            rt2.cost += sm.costChangeSecondRt
            rt1.load = rt1.load - b1.demand + b2.demand
            rt2.load = rt2.load + b1.demand - b2.demand

        self.sol.cost += sm.moveCost

        newCost = self.CalculateTotalCost(self.sol)
        # debuggingOnly
        if abs((newCost - oldCost) - sm.moveCost) > 0.0001:
            print('Cost Issue')


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

    def GetLastOpenRoute(self):
        if len(self.sol.routes) == 0:
            return None
        else:
            return self.sol.routes[-1]

    def IdentifyBestInsertion(self, bestInsertion, rt):
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                if rt.load + candidateCust.demand <= rt.capacity:
                    lastNodePresentInTheRoute = rt.sequenceOfNodes[-2]
                    trialCost = self.distance_matrix[lastNodePresentInTheRoute.ID][candidateCust.ID]
                    if trialCost < bestInsertion.cost:
                        bestInsertion.customer = candidateCust
                        bestInsertion.route = rt
                        bestInsertion.cost = trialCost

    def ApplyCustomerInsertion(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        # before the second depot occurrence
        insIndex = len(rt.sequenceOfNodes) - 1
        rt.sequenceOfNodes.insert(insIndex, insCustomer)

        beforeInserted = rt.sequenceOfNodes[-3]

        costAdded = self.distance_matrix[beforeInserted.ID][insCustomer.ID] + self.distance_matrix[insCustomer.ID][
            self.depot.ID]
        costRemoved = self.distance_matrix[beforeInserted.ID][self.depot.ID]

        rt.cost += costAdded - costRemoved
        self.sol.cost += costAdded - costRemoved

        rt.load += insCustomer.demand

        insCustomer.isRouted = True

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex, targetNodeIndex, moveCost,
                                moveCost_penalized, originRtCostChange, targetRtCostChange, rm: RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost
        rm.moveCost_penalized = moveCost_penalized

    def StoreBestSwapMove(self, firstRouteIndex, secondRouteIndex, firstNodeIndex, secondNodeIndex, moveCost,
                          moveCost_penalized, costChangeFirstRoute, costChangeSecondRoute, sm):
        sm.positionOfFirstRoute = firstRouteIndex
        sm.positionOfSecondRoute = secondRouteIndex
        sm.positionOfFirstNode = firstNodeIndex
        sm.positionOfSecondNode = secondNodeIndex
        sm.costChangeFirstRt = costChangeFirstRoute
        sm.costChangeSecondRt = costChangeSecondRoute
        sm.moveCost = moveCost
        sm.moveCost_penalized = moveCost_penalized

    def CalculateTotalCost(self, sol):
        c = []
        for i in range(0, len(sol.routes)):
            rt = sol.routes[i]
            r = []
            for j in range(0, len(rt.sequenceOfNodes) - 1):
                a = rt.sequenceOfNodes[j]
                b = rt.sequenceOfNodes[j + 1]
                r.append(self.distance_matrix[a.ID][b.ID])
            c.append(sum(r))
        cst = max(c)
        return cst

    def InitializeOperators(self, rm, sm, top):
        rm.Initialize()
        sm.Initialize()
        top.Initialize()

    def FindBestTwoOptMove(self, top):
        for rtInd1 in range(0, len(self.sol.routes)):
            rt1: Route = self.sol.routes[rtInd1]
            for rtInd2 in range(rtInd1, len(self.sol.routes)):
                rt2: Route = self.sol.routes[rtInd2]
                for nodeInd1 in range(0, len(rt1.sequenceOfNodes) - 1):
                    start2 = 0
                    if (rt1 == rt2):
                        start2 = nodeInd1 + 2

                    for nodeInd2 in range(start2, len(rt2.sequenceOfNodes) - 1):
                        moveCost = 10 ** 9
                        moveCost_penalized = 10 ** 9

                        A = rt1.sequenceOfNodes[nodeInd1]
                        B = rt1.sequenceOfNodes[nodeInd1 + 1]
                        K = rt2.sequenceOfNodes[nodeInd2]
                        L = rt2.sequenceOfNodes[nodeInd2 + 1]

                        if rt1 == rt2:
                            if nodeInd1 == 0 and nodeInd2 == len(rt1.sequenceOfNodes) - 2:
                                continue
                            costAdded = self.distance_matrix[A.ID][K.ID] + self.distance_matrix[B.ID][L.ID]
                            costRemoved = self.distance_matrix[A.ID][B.ID] + self.distance_matrix[K.ID][L.ID]
                            costAdded_penalized = self.distance_matrix_penalized[A.ID][K.ID] + \
                                                  self.distance_matrix_penalized[B.ID][L.ID]
                            costRemoved_penalized = self.distance_matrix_penalized[A.ID][B.ID] + \
                                                    self.distance_matrix_penalized[K.ID][L.ID]
                            moveCost = costAdded - costRemoved
                            moveCost_penalized = costAdded_penalized - costRemoved_penalized
                        else:
                            if nodeInd1 == 0 and nodeInd2 == 0:
                                continue
                            if nodeInd1 == len(rt1.sequenceOfNodes) - 2 and nodeInd2 == len(rt2.sequenceOfNodes) - 2:
                                continue

                            if self.CapacityIsViolated(rt1, nodeInd1, rt2, nodeInd2):
                                continue
                            costAdded = self.distance_matrix[A.ID][L.ID] + self.distance_matrix[B.ID][K.ID]
                            costRemoved = self.distance_matrix[A.ID][B.ID] + self.distance_matrix[K.ID][L.ID]
                            costAdded_penalized = self.distance_matrix_penalized[A.ID][L.ID] + \
                                                  self.distance_matrix_penalized[B.ID][K.ID]
                            costRemoved_penalized = self.distance_matrix_penalized[A.ID][B.ID] + \
                                                    self.distance_matrix_penalized[K.ID][L.ID]
                            moveCost = costAdded - costRemoved
                            moveCost_penalized = costAdded_penalized - costRemoved_penalized
                        if moveCost_penalized < top.moveCost_penalized:
                            self.StoreBestTwoOptMove(rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, moveCost_penalized,
                                                     top)

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

    def StoreBestTwoOptMove(self, rtInd1, rtInd2, nodeInd1, nodeInd2, moveCost, moveCost_penalized, top):
        top.positionOfFirstRoute = rtInd1
        top.positionOfSecondRoute = rtInd2
        top.positionOfFirstNode = nodeInd1
        top.positionOfSecondNode = nodeInd2
        top.moveCost = moveCost
        top.moveCost_penalized = moveCost_penalized

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

    def UpdateRouteCostAndLoad(self, rt: Route):
        tc = 0
        tl = 0
        for i in range(0, len(rt.sequenceOfNodes) - 1):
            A = rt.sequenceOfNodes[i]
            B = rt.sequenceOfNodes[i + 1]
            tc += self.distance_matrix[A.ID][B.ID]
            tl += A.demand
        rt.load = tl
        rt.cost = tc

    def TestSolution(self):
        totalSolCost = 0
        for r in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtCost = 0
            rtLoad = 0
            for n in range(0, len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtCost += self.distance_matrix[A.ID][B.ID]
                rtLoad += A.demand
            if abs(rtCost - rt.cost) > 0.0001:
                print('Route Cost problem: ' + str(abs(rtCost - rt.cost)))
            if rtLoad != rt.load:
                print('Route Load problem')

            totalSolCost = max(totalSolCost, rt.cost)

        if abs(totalSolCost - self.sol.cost) > 0.0001:
            print('Solution Cost problem')


    def IdentifyBestInsertionAllPositions(self, bestInsertion, rt):
        for i in range(0, len(self.customers)):
            candidateCust: Node = self.customers[i]
            if candidateCust.isRouted is False:
                if rt.load + candidateCust.demand <= rt.capacity:
                    lastNodePresentInTheRoute = rt.sequenceOfNodes[-2]
                    for j in range(0, len(rt.sequenceOfNodes) - 1):
                        A = rt.sequenceOfNodes[j]
                        B = rt.sequenceOfNodes[j + 1]
                        costAdded = self.distance_matrix[A.ID][candidateCust.ID] + \
                                    self.distance_matrix[candidateCust.ID][
                                        B.ID]
                        costRemoved = self.distance_matrix[A.ID][B.ID]
                        trialCost = costAdded - costRemoved

                        if trialCost < bestInsertion.cost:
                            bestInsertion.customer = candidateCust
                            bestInsertion.route = rt
                            bestInsertion.cost = trialCost
                            bestInsertion.insertionPosition = j

    def ApplyCustomerInsertionAllPositions(self, insertion):
        insCustomer = insertion.customer
        rt = insertion.route
        # before the second depot occurrence
        insIndex = insertion.insertionPosition
        rt.sequenceOfNodes.insert(insIndex + 1, insCustomer)
        rt.cost += insertion.cost
        self.sol.cost += insertion.cost
        rt.load += insCustomer.demand
        insCustomer.isRouted = True

    def penalize_arcs(self):
        # if self.penalized_n1_ID != -1 and self.penalized_n2_ID != -1:
        #     self.distance_matrix_penalized[self.penalized_n1_ID][self.penalized_n2_ID] = self.distance_matrix[self.penalized_n1_ID][self.penalized_n2_ID]
        #     self.distance_matrix_penalized[self.penalized_n2_ID][self.penalized_n1_ID] = self.distance_matrix[self.penalized_n2_ID][self.penalized_n1_ID]
        max_criterion = 0
        pen_1 = -1
        pen_2 = -1
        for i in range(len(self.sol.routes)):
            rt = self.sol.routes[i]
            for j in range(len(rt.sequenceOfNodes) - 1):
                id1 = rt.sequenceOfNodes[j].ID
                id2 = rt.sequenceOfNodes[j + 1].ID
                criterion = self.distance_matrix[id1][id2] / (1 + self.times_penalized[id1][id2])
                if criterion > max_criterion:
                    max_criterion = criterion
                    pen_1 = id1
                    pen_2 = id2
        self.times_penalized[pen_1][pen_2] += 1
        self.times_penalized[pen_2][pen_1] += 1

        pen_weight = 0.15

        self.distance_matrix_penalized[pen_1][pen_2] = (1 + pen_weight * self.times_penalized[pen_1][pen_2]) * \
                                                       self.distance_matrix[pen_1][pen_2]
        self.distance_matrix_penalized[pen_2][pen_1] = (1 + pen_weight * self.times_penalized[pen_2][pen_1]) * \
                                                       self.distance_matrix[pen_2][pen_1]
        self.penalized_n1_ID = pen_1
        self.penalized_n2_ID = pen_2
