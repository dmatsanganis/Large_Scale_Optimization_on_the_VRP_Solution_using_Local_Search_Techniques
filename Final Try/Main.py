#from TSP_Model import Model
from Solver import *

m = Model()
m.BuildModel()
s = Solver(m)
sol = s.solve()





