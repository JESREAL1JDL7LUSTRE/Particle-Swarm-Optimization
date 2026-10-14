# Particle-Swarm-Optimization

Implementation and performance analysis of **Particle Swarm Optimization (PSO)** applied to the **Traveling Salesperson Problem (TSP)** for last-mile commercial delivery routing in **Cagayan de Oro City, Philippines**.

---

## 📌 Project Overview
This project benchmarks and solves the Traveling Salesperson Problem (TSP) across 8 major commercial, seaport, and transit hubs in Cagayan de Oro City using:
- **Central Depot**: Plaza Divisoria ($V_0$)
- **Hollow / Target Nodes**: Centrio Mall ($V_1$), SM CDO Downtown Premier ($V_2$), Limketkai Center ($V_3$), Carmen Commercial Center ($V_4$), Bulua Westbound Terminal ($V_5$), Port of CDO Macabalan ($V_6$), SM City CDO Uptown ($V_7$).
- **Distance Metric**: Real-world driving distances matrix ($D_{ij}$ in km) obtained via road network mapping.

---

## 🧠 Algorithms Implemented & Compared
1. **Particle Swarm Optimization (PSO)**: Discrete permutation-based PSO utilizing swap sequences and velocity operators ($c_1, c_2, w$).
2. **Brute Force (Exhaustive Search)**: Exact optimal ground truth via permutation factorial evaluation ($O((n-1)!)$).
3. **Nearest Neighbor Heuristic (Greedy)**: Greedy construction baseline ($O(n^2)$).
4. **Genetic Algorithm (GA)**: Order crossover (OX) and swap mutation baseline.

---

## 📁 Repository Structure
```text
.
├── cdo_tsp_pso_solver.py           # Core Python implementation and evaluation script
├── cdo_tsp_dataset.csv             # Pairwise distance matrix and node coordinates
├── cdo_tsp_pso_notebook.ipynb      # Interactive Jupyter notebook demonstration
├── CDO_TSP_PSO_Report.md           # Comprehensive technical report & analysis
├── CDO_TSP_Presentation_Script.md  # Presentation script and slide-by-slide notes
├── figure1_cdo_graph_network.png   # Topological road network graph
├── figure2_pso_convergence.png     # PSO cost convergence curve across iterations
├── figure3_optimal_cdo_tour.png    # Optimal route overlay on CDO map coordinates
└── README.md                       # Project documentation
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Required libraries:
```bash
pip install numpy matplotlib networkx
```

### Running the Solver
```bash
python cdo_tsp_pso_solver.py
```
Outputs console evaluation statistics, convergence rates, and saves the three high-resolution figures.
