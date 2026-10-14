# AUDIO-VIDEO PRESENTATION SCRIPT & SLIDE DECK GUIDE
## Traveling Salesperson Problem (TSP) in Cagayan de Oro City
### Optimization of Commercial Courier Delivery Routes Using Particle Swarm Optimization (PSO)

**Course:** Graph Theory  
**Target Duration:** 11–13 Minutes (Requirement: 10–15 minutes)  
**Primary Paper Citation:** Luna-Garcia, R., Candano, T. M. C., & Caga-anan, R. L. (2024). *Performance Analysis of Classical Algorithms for the Traveling Salesman Problem*. The Mindanawan Journal of Mathematics (TMJM), MSU-Iligan Institute of Technology, 6(2), 79–111.  

---

## Presentation Timing Overview

| Slide # | Section Title | Target Timestamp | Suggested Duration | Rubric Component |
|:---:|:---|:---:|:---:|:---|
| **Slide 1** | Title & Introduction | 0:00 – 1:15 | 1m 15s | Introduction & Overview |
| **Slide 2** | Real-World CDO Problem & Objective | 1:15 – 3:00 | 1m 45s | Problem & Objective (Rubric: 10 pts) |
| **Slide 3** | Assigned Algorithm: PSO Fundamentals | 3:00 – 4:30 | 1m 30s | Assigned Algorithm (Rubric: 20 pts) |
| **Slide 4** | PSO Operators: Velocity as Swaps & $O(n^3)$ | 4:30 – 6:00 | 1m 30s | Algorithm Mechanics & Complexity |
| **Slide 5** | Graph Theory Model $G = (V, E, W)$ & Google Maps | 6:00 – 7:30 | 1m 30s | Graph Model & Data (Rubric: 15 pts) |
| **Slide 6** | Google Maps Distance Matrix & Verification | 7:30 – 8:30 | 1m 00s | Matrix Formulation |
| **Slide 7** | Live Python Demonstration & Code Walkthrough | 8:30 – 10:45 | 2m 15s | Implementation (Rubric: 25 pts) |
| **Slide 8** | Solution Interpretation & Closed Tour Audit | 10:45 – 12:00 | 1m 15s | Solution Verification (Rubric: 20 pts) |
| **Slide 9** | Optimality Analysis, Limitations & Future Work | 12:00 – 13:00 | 1m 00s | Conclusion & Proof |
| **Slide 10** | References & Acknowledgments | 13:00 – 13:30 | 0m 30s | Submission & References (5 pts) |

---

## Slide-by-Slide Visuals & Spoken Narration

```
========================================================================================
SLIDE 1: TITLE SLIDE (0:00 – 1:15)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Graph Theory Performance Innovative Task
* **Title:** Solving the Traveling Salesperson Problem (TSP) in Cagayan de Oro City Using Particle Swarm Optimization (PSO)
* **Subtitle:** An Empirical Study Based on the 2024 TMJM Published Paper by MSU-IIT
* **Visuals:** Map outline of Cagayan de Oro City; swarm particles icon; university logo
* **Presenter Information:** [Your Name / Group Members], 3rd Year BS Computer Science / Mathematics

### Spoken Narration (Word-for-Word):
> "Good day, everyone! Welcome to our presentation for our Graph Theory Performance Innovative Task.
>
> Today, we are presenting our work on solving the classical Traveling Salesperson Problem—commonly known as the TSP—applied directly to a real-world logistics challenge in our local community here in Cagayan de Oro City.
>
> In this study, we implement and evaluate **Particle Swarm Optimization (PSO)**, specifically following Section 2.4 and Appendix 4.4 of the research paper published in *The Mindanawan Journal of Mathematics* by Rene Luna-Garcia, Thricia Mae Candano, and Randy Caga-anan from MSU-Iligan Institute of Technology.
>
> Over the next 12 minutes, we will walk you through our real-life CDO delivery scenario, explain how PSO mathematically navigates discrete permutation spaces, present our weighted graph model built from actual Google Maps road network data, demonstrate a live run of our Python implementation, and verify the resulting optimal tour. Let's begin!"

---

```
========================================================================================
SLIDE 2: PROBLEM AND OBJECTIVE (1:15 – 3:00)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Real-Life Application: Cagayan de Oro Last-Mile Commercial Delivery
* **Problem Statement:** Dispatching parcels to 8 key retail, maritime, and transit hubs across CDO
* **Key Locations:** Plaza Divisoria (Central Depot), Centrio Mall, SM Downtown, Limketkai, Carmen Market, Bulua Terminal, Macabalan Port, SM Uptown
* **Objective:** Minimize total road travel distance in kilometers (km)
* **Visual:** Map graphic showing geographical division of CDO (Downtown vs Carmen/Westbank vs Uptown Pueblo)

### Spoken Narration (Word-for-Word):
> "Let's first define our real-life problem and objective.
>
> Cagayan de Oro City is the primary commercial and logistics capital of Northern Mindanao. However, its geography presents unique challenges for delivery fleets. The city is bisected by the Cagayan River, separating the eastern downtown core from Carmen and the western transit corridors, while Masterson Avenue ascends into the southern plateau of Uptown Pueblo de Oro.
>
> Consider a prominent courier company—such as J&T Express or Flash Express—operating a central dispatch depot located at Plaza Divisoria in Downtown CDO. Every morning, a single delivery van must fulfill commercial deliveries to seven major commercial and logistics hubs across the city:
> - Ayala Malls Centrio,
> - SM CDO Downtown Premier,
> - Limketkai Center,
> - Carmen Commercial Center,
> - Bulua Westbound Integrated Terminal,
> - The Port of Cagayan de Oro in Macabalan, and
> - SM City CDO Uptown.
>
> Our operational constraints follow the classical TSP:
> 1. The vehicle starts and ends at the Plaza Divisoria depot.
> 2. Every client destination must be visited exactly once.
> 3. The objective function is strictly to **minimize the total road travel distance in kilometers**, measured from actual Google Maps driving routes.
>
> Without algorithmic optimization, couriers frequently make redundant trips across bridges and through congested corridors, wasting fuel and driving over 45 kilometers. Our objective is to find the mathematical minimum."

---

```
========================================================================================
SLIDE 3: ASSIGNED ALGORITHM — PARTICLE SWARM OPTIMIZATION (3:00 – 4:30)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Section 2.4 — Particle Swarm Optimization (PSO) for TSP
* **Origin:** Kennedy & Eberhart (1995); Discrete TSP adaptation by Lian et al. (2004) and TMJM Paper (2024)
* **Core Concept:** Nature-inspired metaheuristic based on bird flocking and fish schooling
* **Three Swarm Influences:**
  1. *Inertia Weight ($w$)*: Momentum and exploratory random search
  2. *Cognitive Weight ($c_1$)*: Attraction toward individual personal best ($pbest$)
  3. *Social Weight ($c_2$)*: Attraction toward swarm-wide global best ($gbest$)
* **Optimality Status:** Heuristic / Metaheuristic — Approximate solution with polynomial scalability

### Spoken Narration (Word-for-Word):
> "Now, let us examine our assigned algorithm: Particle Swarm Optimization, or PSO.
>
> PSO was originally developed in 1995 by Kennedy and Eberhart to solve continuous optimization problems by simulating the collective intelligence of bird flocks. In continuous space, particles fly by adding continuous velocity vectors to position coordinates.
>
> However, as emphasized in our reference paper from *The Mindanawan Journal of Mathematics*, the Traveling Salesperson Problem is a discrete combinatorial optimization problem. A tour is a permutation of discrete vertices, meaning continuous vector arithmetic cannot be used directly.
>
> In the discrete TSP formulation:
> - A particle's position is a permutation vector representing a complete closed tour.
> - A particle's fitness is the total round-trip distance of that tour, which we aim to minimize.
> - Each particle remembers its personal best tour discovered so far, termed **$pbest$**.
> - The entire swarm shares knowledge of the single best tour found by any particle, termed **$gbest$**.
>
> It is important to emphasize that PSO is a **metaheuristic algorithm**. It does not guarantee finding the theoretical global optimum on every run like exhaustive exact algorithms do, but it provides near-optimal or optimal solutions in polynomial time without combinatorial explosion."

---

```
========================================================================================
SLIDE 4: PSO MECHANICS & TIME COMPLEXITY (4:30 – 6:00)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Discrete Velocity: Swap Operators & Complexity Proof
* **Swap Operator:** $SO(i, j)$ exchanges city at index $i$ with city at index $j$
* **Velocity Equation:** $V_i = \text{Inertia Swaps}(w) \cup \text{Cognitive Swaps}(c_1) \cup \text{Social Swaps}(c_2)$
* **Position Update:** $X_i \leftarrow X_i \oplus V_i$
* **Theorem 2.4 (Luna-Garcia et al., 2024):** Time Complexity is $\mathcal{O}(n^3)$
* **Proof Summary:** $P = \mathcal{O}(n)$ particles, $T = \mathcal{O}(n)$ iterations $\implies T \times P \times n = \mathcal{O}(n^3)$

### Spoken Narration (Word-for-Word):
> "How does a particle move across discrete tours?
>
> In Section 2.4 and Appendix 4.4 of our reference paper, velocity is defined as a sequence of **swap operators**, or elementary transpositions. A swap operator $(i, j)$ exchanges the city at position $i$ with the city at position $j$.
>
> In each generation, a particle constructs its velocity from three distinct components:
> 1. **The Inertia Component:** With probability $w$, random swaps are generated, allowing the particle to explore new permutations and escape local optima.
> 2. **The Cognitive Component:** With probability $c_1$, the particle compares its current tour to its personal best ($pbest$). Wherever a city mismatches, a swap is appended to steer the particle toward its own previous success.
> 3. **The Social Component:** With probability $c_2$, the particle compares its current tour to the swarm's global best ($gbest$), appending swaps to steer it toward the swarm's collective discovery.
>
> Applying these swaps updates the particle's tour.
>
> Regarding time complexity, Theorem 2.4 of the TMJM paper formally proves that Discrete PSO for TSP has a time complexity of **$\mathcal{O}(n^3)$**. In each iteration, evaluating fitness takes $\mathcal{O}(P \times n)$ operations, and swap updates take $\mathcal{O}(P \times n)$ operations. Across $T$ iterations, total time is $\mathcal{O}(T \cdot P \cdot n)$. Since swarm size $P$ and iterations $T$ scale linearly with $n$, the overall time complexity is $\mathcal{O}(n^3)$. This cubic polynomial complexity allows PSO to scale easily, whereas exact algorithms like Brute Force scale factorially at $\mathcal{O}(n!)$."

---

```
========================================================================================
SLIDE 5: METHODOLOGY & GRAPH MODEL (6:00 – 7:30)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Graph Theoretic Formulation: $G = (V, E, W)$
* **Vertices ($V$):** 8 labeled nodes with geographic coordinates (Latitude, Longitude)
  - $V_0$: Plaza Divisoria (Central Hub)
  - $V_1$: Ayala Malls Centrio | $V_2$: SM CDO Downtown Premier | $V_3$: Limketkai Center
  - $V_4$: Carmen Commercial Center | $V_5$: Bulua Westbound Terminal
  - $V_6$: Port of CDO (Macabalan) | $V_7$: SM City CDO Uptown
* **Edges ($E$):** Complete graph with 28 undirected road edges
* **Weights ($W$):** Google Maps driving road distances in kilometers
* **Visual:** Embed `figure1_cdo_graph_network.png` showing the 8 nodes and coordinate grid

### Spoken Narration (Word-for-Word):
> "Let us now examine our graph model.
>
> As shown on the slide in Figure 1, we represent our Cagayan de Oro problem as a complete, weighted graph $G = (V, E, W)$:
> - The vertex set $V$ consists of 8 vertices, where each vertex represents a physical location in CDO defined by its exact geographic coordinates.
>   - $V_0$ is Plaza Divisoria at 8.47775° North, 124.64378° East, serving as our central delivery depot.
>   - $V_1$ is Ayala Malls Centrio along Recto Avenue.
>   - $V_2$ is SM CDO Downtown Premier.
>   - $V_3$ is Limketkai Center in Lapasan.
>   - $V_4$ is Carmen Commercial Center across the Cagayan River.
>   - $V_5$ is Bulua Westbound Terminal in the west.
>   - $V_6$ is the Port of Cagayan de Oro in Macabalan.
>   - And $V_7$ is SM City CDO Uptown on the Pueblo de Oro plateau.
> - The edge set $E$ contains 28 complete pairwise travel connections.
> - Edge weights represent actual road driving distances in kilometers, obtained directly from Google Maps directions between the real physical addresses. This ensures our graph reflects genuine road distances rather than hypothetical straight-line Euclidean approximations."

---

```
========================================================================================
SLIDE 6: DISTANCE MATRIX & APPLICATION DATA (7:30 – 8:30)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Google Maps Pairwise Road Distance Matrix ($D \in \mathbb{R}^{8 \times 8}$)
* **Matrix Table:** Display the full $8 \times 8$ distance matrix in kilometers
* **Data Transparency:** Actual Google Maps driving routes vs modeling assumptions
* **Key Observations:**
  - Downtown cluster ($V_1, V_2, V_3$) is very tight (0.4 km to 1.1 km)
  - Longest legs are to peripheral hubs: Uptown ($V_7$) and Bulua ($V_5$) at 6.5 to 9.8 km

### Spoken Narration (Word-for-Word):
> "Here on Slide 6 is our complete $8 \times 8$ distance matrix.
>
> Notice the significant variance in edge weights across Cagayan de Oro:
> - Between Ayala Malls Centrio ($V_1$) and SM Downtown ($V_2$), the road distance is just 0.4 kilometers along Claro M. Recto.
> - Between SM Downtown ($V_2$) and Limketkai Center ($V_3$), it is only 0.8 kilometers.
> - In contrast, traveling from the Port of Macabalan ($V_6$) up to SM Uptown ($V_7$) spans 9.8 kilometers.
>
> This matrix serves as the exact numerical input for our Python solver. To maintain complete transparency, the dataset is stored in an independent CSV file titled `cdo_tsp_dataset.csv`, containing all vertex coordinates, descriptions, and pairwise distances."

---

```
========================================================================================
SLIDE 7: PYTHON IMPLEMENTATION & LIVE RUN DEMONSTRATION (8:30 – 10:45)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Python Implementation & Execution Demonstration
* **Screen Recording Area:** Terminal window running `python cdo_tsp_pso_solver.py`
* **Parameters Shown:** Swarm Size = 40, Iterations = 120, $w = 0.5$, $c_1 = 1.5$, $c_2 = 1.5$
* **Output Display:** Iteration logs, convergence progress, and execution results
* **Visual:** Embed `figure2_pso_convergence.png` showing the drop from 31.00 km to 28.80 km

### Spoken Narration (Word-for-Word):
> *(At this point, switch your video recording to show the terminal and run the code)*
>
> "Now, let us demonstrate the actual execution of our Python implementation.
>
> We have implemented our solver in `cdo_tsp_pso_solver.py`, following the exact object-oriented structure from Appendix 4.4 of the TMJM paper. We set a swarm size of 40 particles and run for 120 iterations, with an inertia weight of 0.5 and cognitive and social coefficients of 1.5.
>
> Let's run the script now:
> `python cdo_tsp_pso_solver.py`
>
> Look at the terminal output:
> - First, the script prints our location coordinates and the full distance matrix.
> - Next, it executes an exact Brute Force benchmark across all 5,040 permutations, establishing the true theoretical minimum of **28.80 kilometers**.
> - Then, our PSO swarm launches. In iteration 1, the initial random swarm best was 31.00 km.
> - By iteration 21, social and cognitive learning pull the swarm down to 29.10 km.
> - And by iteration 41, the swarm discovers the optimal route of **28.80 kilometers**!
>
> Over the remaining iterations, the swarm converges steadily at 28.80 km, as shown in the convergence curve in Figure 2. The algorithm executed in less than 0.2 seconds!"

---

```
========================================================================================
SLIDE 8: SOLUTION INTERPRETATION & CLOSED TOUR AUDIT (10:45 – 12:00)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Resulting Closed Delivery Route & Geographic Logic
* **Visual:** Embed `figure3_optimal_cdo_tour.png` showing the directional route overlaid on CDO coordinates
* **Route Sequence:** $V_0 \to V_4 \to V_7 \to V_5 \to V_6 \to V_3 \to V_2 \to V_1 \to V_0$
* **Audit Table:** Step-by-step breakdown of each leg's distance in km
  - $1.30 + 5.80 + 9.20 + 6.80 + 3.30 + 0.80 + 0.40 + 1.20 = 28.80\text{ km}$
* **Hamiltonian Tour Verification:** Starts at $V_0$, visits all 7 hubs once, returns to $V_0$

### Spoken Narration (Word-for-Word):
> "Slide 8 displays our final optimized delivery route, shown in Figure 3.
>
> Let us verify the tour:
> 1. The van departs from the Central Depot at Plaza Divisoria ($V_0$) and crosses Ysalina Bridge to Carmen Commercial Center ($V_4$) for 1.3 km.
> 2. It ascends Masterson Avenue to deliver to SM City CDO Uptown ($V_7$) for 5.8 km.
> 3. It descends from Uptown toward the western transit corridor at Bulua Terminal ($V_5$) for 9.2 km.
> 4. It takes the Coastal Bypass Road eastward directly to the Port of Macabalan ($V_6$) for 6.8 km.
> 5. It heads south into the downtown retail district to Limketkai Center ($V_3$) for 3.3 km.
> 6. It visits SM CDO Downtown Premier ($V_2$) for 0.8 km.
> 7. It crosses Claro M. Recto to Ayala Malls Centrio ($V_1$) for just 0.4 km.
> 8. Finally, it drives down Don Apolinar Velez Street back to the Central Depot at Divisoria ($V_0$) for 1.2 km.
>
> Recalculating the leg distances independently:
> $1.3 + 5.8 + 9.2 + 6.8 + 3.3 + 0.8 + 0.4 + 1.2 = \mathbf{28.80\text{ km}}$.
>
> Every required location is visited exactly once before returning to the depot, confirming a valid Hamiltonian cycle."

---

```
========================================================================================
SLIDE 9: OPTIMALITY ANALYSIS, LIMITATIONS & FUTURE EXTENSIONS (12:00 – 13:00)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Optimality Evaluation, Limitations & Enhancements
* **Optimality Status:**
  - *Theoretical Nature:* Metaheuristic / Approximate Algorithm
  - *Empirical Proof:* 100% matched exact Brute Force minimum (28.80 km vs 28.80 km, 0.00% gap)
* **Real-World Limitations:**
  - Static road distances vs peak-hour bridge congestion (Ysalina & Kagay-an bridges)
  - Symmetric assumption vs downtown one-way streets
* **Future Work:**
  - Hybrid PSO with 2-Opt local search
  - Time-dependent edge weights based on live traffic data

### Spoken Narration (Word-for-Word):
> "Let us evaluate our solution and discuss limitations.
>
> Regarding optimality: in the general theoretical case, Particle Swarm Optimization is an **approximate metaheuristic**. It does not guarantee finding the global optimum for arbitrary graphs. However, on our specific 8-location Cagayan de Oro problem instance, benchmarking against exhaustive Brute Force proves that our PSO route achieved the **exact mathematical global optimum** of 28.80 kilometers.
>
> Logistically, the tour makes intuitive sense: it groups the dense downtown malls together and circles the city's perimeter, avoiding wasteful zig-zagging across the Cagayan River.
>
> For future improvements:
> 1. Incorporating time-dependent traffic models would capture peak-hour congestion on Carmen and Ysalina Bridges.
> 2. Integrating a 2-Opt local search operator with PSO could further enhance convergence speed on larger problem instances with 50 or more delivery stops."

---

```
========================================================================================
SLIDE 10: REFERENCES & CONCLUSION (13:00 – 13:30)
========================================================================================
```

### Visual Slide Elements:
* **Header:** Academic References & Acknowledgments
* **Primary Source:** Luna-Garcia, Candano, & Caga-anan (2024), *The Mindanawan Journal of Mathematics*, MSU-IIT, Vol. 6, No. 2, pp. 79–111.
* **Algorithm Foundations:** Kennedy & Eberhart (1995); Lian et al. (2004); Shi et al. (2010).
* **Data Sources:** Google Maps Platform (2024).
* **Closing:** Thank you! Q&A.

### Spoken Narration (Word-for-Word):
> "In conclusion, we have modeled a real-world last-mile delivery challenge in Cagayan de Oro City using Graph Theory and solved it using Particle Swarm Optimization as presented in the 2024 *Mindanawan Journal of Mathematics* research paper.
>
> Our implementation successfully identified the globally optimal 28.80 km closed tour, visited all 8 commercial hubs exactly once, and verified the calculations with precision.
>
> All submitted materials—including our runnable Python solver, dataset CSV, and comprehensive academic report—are available in our project repository.
>
> Thank you very much for your time and attention! We are now open for questions."

---

```
========================================================================================
END OF PRESENTATION SCRIPT (Total Word Count: ~1,580 words | ~12.5 minutes at 125 wpm)
========================================================================================
```
