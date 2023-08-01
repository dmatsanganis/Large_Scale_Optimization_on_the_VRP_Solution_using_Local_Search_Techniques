# Vehicle Routing Problem Solver

This repository contains a Python implementation of a solution to the Vehicle Routing Problem (VRP) using the Variable Neighborhood Descent (VND) methodology.

## Project Description

The Vehicle Routing Problem (VRP) is a complex combinatorial optimization problem that focuses on the optimal route selection for a fleet of vehicles delivering goods or services to various locations. This project provides an efficient and effective solution for the VRP by implementing the Variable Neighborhood Descent (VND) algorithm.

The `Solver.py` script uses a two-phase VND approach to tackle the VRP:

### Initialization

The script begins by initializing certain parameters, such as the distance matrix and the solution object. The solution object encapsulates the routes for all vehicles in the problem.

### Advanced VND

The advanced VND focuses on the most costly (or "worst") route. It applies three types of operations (moves) to improve the solution:

- **Relocation Move**: A customer/node is relocated from its current position to a different position within the same route or to a different route.
- **Swap Move**: Two customers/nodes from the same or different routes are swapped.
- **2-opt Move**: A pair of edges in a route are removed and then reconnected in another way without creating a cycle.

The algorithm iterates through these three types of moves, always applying the best move that decreases the total cost of the solution, until no further improvements can be made.

### Default VND

After applying the Advanced VND, the script applies a default version of the VND algorithm. This version is more general and applies the three types of moves (relocation, swap, and 2-opt) to all routes, without focusing on the worst one. This algorithm may not necessarily lead to better results but can help to find a better starting point for the next iteration of the advanced VND.

### Output

The best solution found is stored and outputted at the end of the script. The cost of the solution and other key metrics are also reported.

## Requirements

To run this script, you need Python 3.10+ and the following Python libraries installed:

- [NumPy](https://numpy.org/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)

## Usage

To run the VRP solver on a problem instance, use the following command:

```bash
python Solver.py
```

## Contributors

- [X] [Julia Baardse](https://github.com/juliaxab) 
- [X] [Dimitris Matsanganis](https://github.com/dmatsanganis) 
- [X] [Foteini Nefeli](https://github.com/FoteiniNefeli)
- [X] [Eva Routsi](https://github.com/EvaRoutsi)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
