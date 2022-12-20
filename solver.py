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

    def Initialize(self):
        self.originRoutePosition = None
        self.targetRoutePosition = None
        self.originNodePosition = None
        self.targetNodePosition = None
        self.costChangeOriginRt = None
        self.costChangeTargetRt = None
        self.moveCost = 10 ** 9


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
        self.points = m.points
        self.depot = m.allNodes[0]
        self.distanceMatrix = m.matrix
        self.capacity = m.capacity
        self.sol = None
        self.bestSolution = None
        self.searchTrajectory = []
        self.rtCounter = 0
        self.rtInd = -1
        self.iterations = None

    def solve(self):
        self.SetRoutedFlagToFalseForAllpoints()
        self.MinimumInsertions()
        self.ReportSolution(self.sol)
        self.LocalSearch(0)
        self.ReportSolution(self.sol)

        return self.sol

    def SetRoutedFlagToFalseForAllpoints(self):
        for i in range(0, len(self.points)):
            self.points[i].isRouted = False

    def MinimumInsertions(self):
        modelIsFeasible = True
        self.sol = Solution()
        insertions = 0
        distFrombase = self.distanceMatrix[0]
        closest26points = sorted(range(1, len(distFrombase)), key=lambda k: distFrombase[k])[:26]
        j = 1
        insPos = 0
        for i in closest26points:
            rt = Route(self.depot, self.capacity)
            self.sol.routes.append(rt)
            randomInsertion = CustomerInsertionAllPositions()
            randomInsertion.customer = self.allNodes[i]
            randomInsertion.customer.demand = self.allNodes[i].demand
            randomInsertion.route = self.sol.routes[closest26points.index(i)]
            randomInsertion.cost = self.distanceMatrix[0][i]
            randomInsertion.insertionPosition = insPos
            self.ApplyCustomerInsertionAllPositions(randomInsertion)
            insertions += 1
            self.rtCounter = 1

        while insertions < len(self.points):
            bestInsertion = CustomerInsertionAllPositions()
            if self.rtInd == 25:
                self.rtInd = 0
            else:
                self.rtInd += 1

            lastOpenRoute: Route = self.GetLastOpenRoute()

            if lastOpenRoute is not None:
                self.IdentifyBestInsertionAllPositions(bestInsertion, lastOpenRoute)

            if bestInsertion.customer is not None:
                self.ApplyCustomerInsertionAllPositions(bestInsertion)
                insertions += 1

            else:
                # If there is an empty available route
                if lastOpenRoute is not None and len(lastOpenRoute.sequenceOfNodes) == 2:
                    modelIsFeasible = False
                    break
                # If there is no empty available route and no feasible insertion was identified
                else:
                    self.rtCounter += 1

        if modelIsFeasible == False:
            print('FeasibilityIssue')

        self.TestSolution()

    def LocalSearch(self, operator):
        localSearchIterator = 0
        self.bestSolution = self.cloneSolution(self.sol)

        terminationCondition = False

        rm = RelocationMove()

        self.searchTrajectory.append(self.sol.cost)

        while terminationCondition is False:

            self.InitializeOperators(rm, )
            SolDrawer.draw(localSearchIterator, self.sol, self.allNodes)

            # Relocations
            if operator == 0:
                self.FindBestRelocationMove(rm)
                if rm.originRoutePosition is not None:
                    if rm.moveCost < 0:
                        self.ApplyRelocationMove(rm)
                    else:
                        self.iterations = localSearchIterator
                        terminationCondition = True
            else:
                print("wrong operator, try again with 0")

            self.TestSolution()

            if self.sol.cost < self.bestSolution.cost:
                self.bestSolution = self.cloneSolution(self.sol)
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

                        if originRouteIndex == targetRouteIndex and (
                                targetNodeIndex == originNodeIndex or targetNodeIndex == originNodeIndex - 1):
                            continue

                        A = rt1.sequenceOfNodes[originNodeIndex - 1]
                        B = rt1.sequenceOfNodes[originNodeIndex]
                        C = rt1.sequenceOfNodes[originNodeIndex + 1]

                        F = rt2.sequenceOfNodes[targetNodeIndex]
                        G = rt2.sequenceOfNodes[targetNodeIndex + 1]

                        if rt1 != rt2:

                            if rt2.load + B.demand > rt2.capacity:
                                continue

                        costAdded = self.distanceMatrix[A.ID][C.ID] + self.distanceMatrix[F.ID][B.ID] + \
                                    self.distanceMatrix[B.ID][G.ID]
                        costRemoved = self.distanceMatrix[A.ID][B.ID] + self.distanceMatrix[B.ID][C.ID] + \
                                      self.distanceMatrix[F.ID][G.ID]

                        originRtCostChange = self.distanceMatrix[A.ID][C.ID] - self.distanceMatrix[A.ID][B.ID] - \
                                             self.distanceMatrix[B.ID][C.ID]
                        targetRtCostChange = self.distanceMatrix[F.ID][B.ID] + self.distanceMatrix[B.ID][G.ID] - \
                                             self.distanceMatrix[F.ID][G.ID]

                        moveCost = costAdded - costRemoved

                        if (moveCost < rm.moveCost) and abs(moveCost) \
                                and originRtCostChange + rt1.cost < self.sol.cost and targetRtCostChange + rt2.cost < \
                                self.sol.cost:
                            self.StoreBestRelocationMove(originRouteIndex, targetRouteIndex, originNodeIndex,
                                                         targetNodeIndex, moveCost, originRtCostChange,
                                                         targetRtCostChange, rm)

    def ApplyRelocationMove(self, rm: RelocationMove):

        originRt = self.sol.routes[rm.originRoutePosition]
        targetRt = self.sol.routes[rm.targetRoutePosition]

        B = originRt.sequenceOfNodes[rm.originNodePosition]

        if originRt == targetRt:
            del originRt.sequenceOfNodes[rm.originNodePosition]
            if rm.originNodePosition < rm.targetNodePosition:
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

        self.sol.cost = self.CalculateTotalCost(self.sol)

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
        if self.rtCounter == 0:
            return None
        else:
            return self.sol.routes[self.rtInd]

    def InitializeOperators(self, rm):
        rm.Initialize()

    def StoreBestRelocationMove(self, originRouteIndex, targetRouteIndex, originNodeIndex,
                                targetNodeIndex, moveCost,
                                originRtCostChange, targetRtCostChange, rm: RelocationMove):
        rm.originRoutePosition = originRouteIndex
        rm.originNodePosition = originNodeIndex
        rm.targetRoutePosition = targetRouteIndex
        rm.targetNodePosition = targetNodeIndex
        rm.costChangeOriginRt = originRtCostChange
        rm.costChangeTargetRt = targetRtCostChange
        rm.moveCost = moveCost

    def CalculateTotalCost(self, sol):
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

    def TestSolution(self):
        totalSolCost = 0
        for r in range(0, len(self.sol.routes)):
            rt: Route = self.sol.routes[r]
            rtCost = 0
            rtLoad = 0
            for n in range(0, len(rt.sequenceOfNodes) - 1):
                A = rt.sequenceOfNodes[n]
                B = rt.sequenceOfNodes[n + 1]
                rtCost += self.distanceMatrix[A.ID][B.ID]
                rtLoad += A.demand
            if abs(rtCost - rt.cost) > 0.0001:
                print('Route Cost problem: ' + str(abs(rtCost - rt.cost)))
            if rtLoad != rt.load:
                print('Route Load problem')

            totalSolCost = max(totalSolCost, rt.cost)

        if abs(totalSolCost - self.sol.cost) > 0.0001:
            print('Solution Cost problem')

    def IdentifyBestInsertionAllPositions(self, bestInsertion, rt):
        for i in range(0, len(self.points)):
            candidateCust: Node = self.points[i]
            if candidateCust.isRouted is False:
                if rt.load + candidateCust.demand <= rt.capacity:
                    for j in range(0, len(rt.sequenceOfNodes) - 1):
                        A = rt.sequenceOfNodes[j]
                        B = rt.sequenceOfNodes[j + 1]
                        costAdded = self.distanceMatrix[A.ID][candidateCust.ID] + self.distanceMatrix[candidateCust.ID][
                            B.ID]
                        costRemoved = self.distanceMatrix[A.ID][B.ID]
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
        self.sol.cost = max(self.sol.cost, rt.cost)
        rt.load += insCustomer.demand
        insCustomer.isRouted = True
