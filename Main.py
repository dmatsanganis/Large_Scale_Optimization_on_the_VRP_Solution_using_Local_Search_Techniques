from Solver import *

m = Model()
m.BuildModel()
s = Solver(m)
sol = s.solve()

# Creates the demanded txt file.
file1 = open("results.txt", "w")

# Write the team credentials - members on the txt file.
file1.write("Team members: \n\n"
            "Hegla Ruci, f2822219, \n"
            "Foteini Nefeli Nouskali, f2822213, \n"
            "Julia Anna Baardse, f2822201, \n"
            "Dimitrios Matsanganis, f2822212, \n"
            "Team ID: 1.\n\n")

# Output the best - final solution.
file1.write("Objective: \n")
file1.write(str(sol.cost))
file1.write(" hr \n\n")
file1.write("Routes: \n")
file1.write(str(len(sol.routes)))
file1.write("\n\nRoutes Summary: \n")

# A for-loop statement to write to the txt the best solution's
# routes summary, along with each route's cost.
for i in range(0, len(sol.routes)):
    rt = sol.routes[i]
    file1.write("Route ")
    file1.write(str(i+1))
    file1.write(": ")
    for j in range(0, len(rt.sequenceOfNodes)):
        file1.write(str(rt.sequenceOfNodes[j].ID))
        file1.write(", ")

    file1.write("Route's Cost: ")
    file1.write(str(rt.cost))
    file1.write("\n\n")

file1.write("The service time completion of the customer to be served last is ")
file1.write(str(sol.cost))

file1.close()