#!/usr/bin/env python3
"""
Generate a professional 16:9 PowerPoint presentation (.pptx)
for the Cagayan de Oro Tourist TSP using Particle Swarm Optimization (Section 2.4).
"""

import os
import sys
from pathlib import Path

def create_presentation():
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
        from pptx.enum.shapes import MSO_SHAPE
    except ImportError:
        print("ERROR: python-pptx is not installed.")
        print("To install: pip install python-pptx")
        return False

    prs = Presentation()
    # 16:9 widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Color Palette
    BG_DARK = RGBColor(11, 19, 43)        # #0B132B Deep Navy
    CARD_BG = RGBColor(28, 37, 65)        # #1C2541 Slate Navy
    ACCENT_TEAL = RGBColor(91, 192, 190)  # #5BC0BE Mint / Cyan
    ACCENT_CYAN = RGBColor(111, 255, 233) # #6FFFE9 Bright Neon Mint
    ACCENT_AMBER = RGBColor(245, 158, 11) # #F59E0B Warm Amber
    TEXT_WHITE = RGBColor(248, 249, 250)  # #F8F9FA Near White
    TEXT_MUTED = RGBColor(156, 163, 175)  # #9CA3AF Cool Gray
    LINE_BORDER = RGBColor(58, 80, 107)   # #3A506B Subtle Border

    results_dir = Path("results").resolve()
    fig1_path = results_dir / "figure1_cdo_graph_network.png"
    fig2_path = results_dir / "figure2_pso_convergence.png"
    fig3_path = results_dir / "figure3_cdo_tour.png"

    def apply_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="GRAPH THEORY PIT | PARTICLE SWARM OPTIMIZATION"):
        # Category label
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        p_cat = tb_cat.text_frame.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_TEAL

        # Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(24)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

    def add_card(slide, left, top, width, height, title=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = LINE_BORDER
        card.line.width = Pt(1)

        if title:
            tb = slide.shapes.add_textbox(left + Inches(0.2), top + Inches(0.15), width - Inches(0.4), Inches(0.5))
            p = tb.text_frame.paragraphs[0]
            p.text = title
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = ACCENT_CYAN
        return card

    def set_speaker_notes(slide, notes_text):
        notes_slide = slide.notes_slide
        tf = notes_slide.notes_text_frame
        tf.text = notes_text

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    slide1 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide1)

    # Accent decorative pill
    pill = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(4.5), Inches(0.45))
    pill.fill.solid()
    pill.fill.fore_color.rgb = CARD_BG
    pill.line.color.rgb = ACCENT_TEAL
    p_pill = pill.text_frame.paragraphs[0]
    p_pill.text = "GRAPH THEORY PIT • PERFORMANCE INNOVATIVE TASK"
    p_pill.font.size = Pt(11)
    p_pill.font.bold = True
    p_pill.font.color.rgb = ACCENT_CYAN

    # Main Title
    tb = slide1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.7), Inches(2.0))
    tf = tb.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "Cagayan de Oro Tourist Driving Tour"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE

    p2 = tf.add_paragraph()
    p2.text = "Solving Real-Life Asymmetric TSP via Particle Swarm Optimization (Section 2.4)"
    p2.font.size = Pt(20)
    p2.font.color.rgb = ACCENT_TEAL

    # Meta Information Cards
    add_card(slide1, Inches(0.8), Inches(4.5), Inches(3.6), Inches(2.2), "Assigned Algorithm")
    tb = slide1.shapes.add_textbox(Inches(1.0), Inches(5.1), Inches(3.2), Inches(1.4))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Algorithm 2.4: Discrete PSO\n(Luna-Garcia et al., TMJM 2024)\nPosition: Permutation of vertices\nVelocity: Sequences of transposition swaps"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    add_card(slide1, Inches(4.8), Inches(4.5), Inches(3.6), Inches(2.2), "Problem Scope")
    tb = slide1.shapes.add_textbox(Inches(5.0), Inches(5.1), Inches(3.2), Inches(1.4))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "8 CDO Tourist Attractions\nDepot: Plaza Divisoria (V0)\n56 Directed Road Network Arcs\nSearch Space: 7! = 5,040 routes"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    add_card(slide1, Inches(8.8), Inches(4.5), Inches(3.7), Inches(2.2), "Key Result")
    tb = slide1.shapes.add_textbox(Inches(9.0), Inches(5.1), Inches(3.3), Inches(1.4))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Best Tour: 36.4739 km\nExact Optimum: 35.9537 km\nOptimality Gap: 1.45% (Approximate)\nRuntime: < 0.05 seconds"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_MUTED

    set_speaker_notes(slide1, 
        "Good day. Today, I am presenting our Graph Theory Performance Innovative Task: solving a real-life Traveling Salesperson Problem in Cagayan de Oro City using our assigned algorithm, Discrete Particle Swarm Optimization.\n"
        "Our scenario involves planning an efficient driving tour for a group of tourists visiting Cagayan de Oro. They hire a single vehicle, start at Plaza Divisoria, visit seven other prominent tourist destinations, and return to Plaza Divisoria.\n"
        "The mathematical challenge is to determine the optimal visiting order that minimizes the total driving distance while visiting each required location exactly once."
    )

    # ==========================================
    # SLIDE 2: TOURIST DESTINATIONS & VERIFICATION
    # ==========================================
    slide2 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide2)
    add_header(slide2, "Tourist Destinations & Google Maps Verification", "Component 1: Introduction & Data")

    add_card(slide2, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3), "Eight Verified Destinations (Cagayan de Oro City)")
    tb = slide2.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(7.1), Inches(4.5))
    tf = tb.text_frame
    destinations = [
        ("V0: Plaza Divisoria (Depot)", "RN Capistrano & Tirso Neri St, Poblacion", "Starting/ending civic center"),
        ("V1: Gaston Park", "Corner Gaerlan & Rizal St, Poblacion", "Historic heritage park & fountain"),
        ("V2: St. Augustine Cathedral", "Corner Gaston Circle, Poblacion", "Century-old metropolitan cathedral"),
        ("V3: Museo de Oro", "Corrales Ave entrance, XU Campus", "First folkloric museum in Mindanao"),
        ("V4: Vicente de Lara Park", "Antonio Luna St, Capitol Grounds", "Provincial Capitol park & monument"),
        ("V5: High Ridge", "Upper Macasandig scenic overlook", "Hilltop city panorama & dining"),
        ("V6: Amaya View", "Indahag highland resort", "Highest hilltop amusement resort"),
        ("V7: Gardens of Malasag", "Malasag Hill, Cugman", "Eco-tourism cultural village")
    ]
    for i, (name, loc, desc) in enumerate(destinations):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {name} — {loc} ({desc})"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_WHITE if i == 0 else TEXT_MUTED

    add_card(slide2, Inches(8.6), Inches(1.6), Inches(3.9), Inches(5.3), "Real-World Grounding")
    tb = slide2.shapes.add_textbox(Inches(8.8), Inches(2.2), Inches(3.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Curated Selection:\nBased on LakbayPinas Cagayan de Oro travel guide, strictly within CDO city limits.\n\n" \
             "Pedestrian vs Driving Nodes:\nLocations inside pedestrian campuses or parks (e.g. Museo de Oro, Cathedral) use street-level vehicular drop-off curb nodes on Corrales Ave and Gaston Circle.\n\n" \
             "Full Google Maps Verification:\nAll 8 coordinates are verified on Google Maps with street names, latitudes, and longitudes."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide2,
        "The destinations are selected from the LakbayPinas Cagayan de Oro travel guide. We chose eight key spots located strictly within Cagayan de Oro City:\n"
        "- V0: Plaza Divisoria (our start and finish depot)\n"
        "- V1: Gaston Park\n"
        "- V2: St. Augustine Metropolitan Cathedral\n"
        "- V3: Museo de Oro\n"
        "- V4: Vicente de Lara Park\n"
        "- V5: High Ridge in Macasandig\n"
        "- V6: Amaya View in Indahag\n"
        "- V7: Gardens of Malasag Eco-Tourism Village in Cugman\n"
        "Each location was verified on Google Maps. Because places like Museo de Oro and the Cathedral sit inside pedestrian campuses or plazas, we designated street-level vehicular drop-off nodes on Corrales Avenue and Gaston Circle to reflect realistic driving access."
    )

    # ==========================================
    # SLIDE 3: PROBLEM FORMULATION & CONSTRAINTS
    # ==========================================
    slide3 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide3)
    add_header(slide3, "Mathematical Formulation & Practical Assumptions", "Component 1: Problem Formulation")

    add_card(slide3, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Mathematical Formulation")
    tb = slide3.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Objective Function (Minimization):\n" \
             "Z(π) = Σ D[π[k], π[k+1 (mod 8)]]  for k = 0 to 7\n\n" \
             "Where:\n" \
             "• π is a cyclic permutation with π[0] = V0\n" \
             "• D[u, v] is the shortest driving distance from u to v\n\n" \
             "Constraints:\n" \
             "1. Closed Hamiltonian Cycle: Start and end at V0 (Plaza Divisoria).\n" \
             "2. All Intermediate Vertices Visited Exactly Once:\n" \
             "   {π[1], π[2], ..., π[7]} = {V1, V2, ..., V7}\n" \
             "3. Asymmetric Complete Directed Graph G = (V, A, D):\n" \
             "   |V| = 8, |A| = 56 directed arcs.\n" \
             "   Generally D[u, v] ≠ D[v, u] due to one-way traffic networks."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    add_card(slide3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Practical Assumptions")
    tb = slide3.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Pure Driving Distance Metric:\n" \
             "We optimize road driving distance in kilometres rather than duration or monetary fuel expenditure.\n\n" \
             "2. Static Traffic Network:\n" \
             "Road distances are fixed based on OpenStreetMap topologies via OSRM, abstracting live rush-hour bottlenecks.\n\n" \
             "3. Search Space Size:\n" \
             "With depot V0 fixed at position 0, the number of distinct candidate tours is (8 - 1)! = 7! = 5,040 tours.\n\n" \
             "4. Single Tourist Vehicle:\n" \
             "A single continuous itinerary without splitting passengers or visiting attractions concurrently."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide3,
        "Our objective is to minimize total driving distance in kilometres:\n"
        "Z(pi) = D[pi[0], pi[1]] + D[pi[1], pi[2]] + ... + D[pi[7], pi[0]]\n"
        "Key assumptions:\n"
        "1. Closed tour: Start and finish at V0, visiting V1 through V7 exactly once.\n"
        "2. The vehicle travels on real road networks. Because of one-way roads and traffic flow, travel between two stops is directed: distance from A to B does not necessarily equal B to A.\n"
        "3. We optimize distance; entrance fees, sightseeing durations, and live congestion are outside the distance objective."
    )

    # ==========================================
    # SLIDE 4: ASSIGNED ALGORITHM - DISCRETE PSO
    # ==========================================
    slide4 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide4)
    add_header(slide4, "Assigned Algorithm: Section 2.4 Discrete PSO", "Component 2: Algorithm Theory")

    add_card(slide4, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Mapping Continuous PSO to Permutations")
    tb = slide4.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Reference: Luna-Garcia et al., TMJM 2024 (Section 2.4)\n\n" \
             "• Particle Position X_i:\n" \
             "A valid permutation of [V1, ..., V7] with V0 fixed at index 0.\n\n" \
             "• Fitness Evaluation:\n" \
             "Tour cost Z(X_i) = Σ D[X_i[k], X_i[k+1 (mod 8)]]. Lower is better.\n\n" \
             "• Particle Velocity V_i:\n" \
             "A list of transposition/swap operators [(j1, k1), (j2, k2), ...].\n\n" \
             "• Cognitive Memory (pbest_i):\n" \
             "The lowest-cost permutation historically achieved by particle i.\n\n" \
             "• Social Swarm Memory (gbest):\n" \
             "The globally best permutation discovered across all particles."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    add_card(slide4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Update Equations & Hyperparameters")
    tb = slide4.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Velocity Update Mechanism:\n" \
             "V_i(t+1) = w ⊗ V_i(t) ⊕ c1 ⊗ (pbest_i ⊖ X_i(t)) ⊕ c2 ⊗ (gbest ⊖ X_i(t))\n\n" \
             "Position Update:\n" \
             "X_i(t+1) = X_i(t) ⊙ V_i(t+1)\n\n" \
             "Configured Hyperparameters:\n" \
             "• Swarm Size (N): 40 particles\n" \
             "• Max Iterations (T): 120 iterations (4,800 evaluations)\n" \
             "• Inertia Weight (w): 0.5 (probability of retaining old swaps)\n" \
             "• Cognitive Rate (c1): 0.8 (alignment to personal best)\n" \
             "• Social Rate (c2): 0.8 (alignment to global best)\n" \
             "• Random Mutation: 0.2 (exploratory swap to avoid local minima)"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide4,
        "Our assigned algorithm is Particle Swarm Optimization (PSO). In continuous PSO, particles move through space via position and velocity vectors. But TSP is a discrete permutation problem:\n"
        "- A particle represents a candidate visiting order, with depot V0 fixed at position 0.\n"
        "- Fitness is the total closed-tour distance Z.\n"
        "- Velocity is represented as a sequence of transpositions or swaps acting on non-depot cities.\n"
        "- Each particle remembers its personal best order (pbest), and the swarm shares the best order discovered so far (gbest).\n"
        "In our implementation, we use 40 particles and 120 iterations. Previous swaps are retained with inertia probability w = 0.5. Cognitive alignment toward pbest occurs with probability c1 = 0.8, social alignment toward gbest with probability c2 = 0.8, and an exploratory random swap occurs with probability 0.2."
    )

    # ==========================================
    # SLIDE 5: STEP-BY-STEP CALCULATION TRACE
    # ==========================================
    slide5 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide5)
    add_header(slide5, "Step-by-Step Calculation Trace & Swap Demonstration", "Component 2: Numerical Trace")

    add_card(slide5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Numerical Alignment Example")
    tb = slide5.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Initial Particle Position X:\n" \
             "[V0, V3, V1, V2, V4, V5, V6, V7]\n" \
             "Total Tour Cost = 38.50 km\n\n" \
             "Target Global Best (gbest):\n" \
             "[V0, V3, V4, V7, V6, V5, V2, V1]\n\n" \
             "Left-to-Right Position Alignment:\n" \
             "• Index 0: V0 == V0 (depot fixed)\n" \
             "• Index 1: V3 == V3 (match)\n" \
             "• Index 2: X[2] = V1, but target requires V4\n" \
             "  -> In X, V4 is currently at Index 4\n" \
             "  -> Generate Swap Operator: (2, 4)\n" \
             "  -> Execute Swap with probability c2 = 0.8\n\n" \
             "New Particle Position X':\n" \
             "[V0, V3, V4, V2, V1, V5, V6, V7]"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    add_card(slide5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Distance Delta & Cost Recalculation")
    tb = slide5.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Evaluating Affected Directed Legs:\n\n" \
             "Previous Legs (before swap):\n" \
             "• V3 -> V1 = 0.4496 km\n" \
             "• V1 -> V2 = 0.1585 km\n" \
             "• V2 -> V4 = 1.4880 km\n" \
             "• V4 -> V5 = 6.2238 km\n" \
             "Subtotal = 8.3199 km\n\n" \
             "Updated Legs (after swap):\n" \
             "• V3 -> V4 = 1.3014 km\n" \
             "• V4 -> V2 = 1.6845 km\n" \
             "• V2 -> V1 = 0.1585 km\n" \
             "• V1 -> V5 = 4.9691 km\n" \
             "Subtotal = 8.1135 km\n\n" \
             "Net Improvement: 8.1135 - 8.3199 = -0.2064 km\n" \
             "New Total Cost: 38.50 - 0.21 = 38.2936 km\n" \
             "Outcome: Improved! Particle updates its pbest."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide5,
        "Let’s look at a concrete step-by-step calculation:\n"
        "Suppose a particle currently has the route: X = [V0, V3, V1, V2, V4, V5, V6, V7]. Summing the 8 legs from our distance matrix gives a total cost of 38.50 km.\n"
        "Now, suppose the global best target gbest is [V0, V3, V4, V7, V6, V5, V2, V1].\n"
        "During social alignment, the algorithm scans from left to right:\n"
        "- Index 1 matches: both have V3.\n"
        "- At index 2, X[2] = V1, but the target requires V4.\n"
        "- In our particle X, V4 is located at index 4.\n"
        "- With probability c2 = 0.8, the algorithm executes swap (2, 4).\n"
        "- The new route becomes: [V0, V3, V4, V2, V1, V5, V6, V7].\n"
        "Recalculating the altered legs: V3 -> V4, V4 -> V2, V2 -> V1, and V1 -> V5, the new tour cost drops to 38.29 km. Because this cost is lower, the particle immediately updates its personal best!"
    )

    # ==========================================
    # SLIDE 6: GRAPH MODEL & DISTANCE MATRIX
    # ==========================================
    slide6 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide6)
    add_header(slide6, "Graph Model & Asymmetric Distance Matrix", "Component 3: Graph Model & Data")

    # Embed Figure 1
    if fig1_path.exists():
        slide6.shapes.add_picture(str(fig1_path), Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
    else:
        add_card(slide6, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3), "Figure 1: Labeled Graph & Weight Matrix")

    add_card(slide6, Inches(8.6), Inches(1.6), Inches(3.9), Inches(5.3), "Graph Properties")
    tb = slide6.shapes.add_textbox(Inches(8.8), Inches(2.2), Inches(3.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Graph Structure:\n" \
             "• Directed Graph G = (V, A, D)\n" \
             "• |V| = 8 nodes, |A| = 56 directed arcs\n" \
             "• Bold teal arrows show optimal Hamiltonian cycle\n\n" \
             "Weight Matrix Asymmetry:\n" \
             "• V0 -> V1 = 0.63 km\n" \
             "• V1 -> V0 = 0.36 km\n" \
             "Difference = 0.27 km (75% longer!)\n\n" \
             "Why Asymmetric?\n" \
             "Due to downtown CDO one-way streets (e.g. Capistrano & Burgos). Symmetrizing would create illegal or non-existent driving turns!"
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide6,
        "Here on Slide 6 is our complete Graph Model and Distance Matrix.\n"
        "On the left, we represent the problem as a complete directed weighted graph G = (V, A, D) with 8 vertices and 56 directed arcs. The bold teal arrows show the closed Hamiltonian cycle discovered by PSO, complete with leg distances.\n"
        "On the right is our 8-by-8 asymmetric weight matrix. Notice that travel costs are asymmetric. For example:\n"
        "- Driving from Plaza Divisoria (V0) to Gaston Park (V1) is 0.63 km.\n"
        "- But returning from Gaston Park (V1) to Plaza Divisoria (V0) is only 0.36 km.\n"
        "This asymmetry is caused by real-world one-way streets around downtown CDO. Symmetrizing the matrix would produce unrealistic routes, so we preserve the full directed structure."
    )

    # ==========================================
    # SLIDE 7: DATA ENGINEERING & REPRODUCIBILITY
    # ==========================================
    slide7 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide7)
    add_header(slide7, "Data Pipeline, OSRM Extraction & Verification", "Component 3: Methodology")

    add_card(slide7, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Pipeline Architecture")
    tb = slide7.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Geographic Node Acquisition:\n" \
             "• Latitudes & longitudes extracted from OpenStreetMap Overpass API and Google Maps.\n" \
             "• Street-level drop-off points ensured for pedestrian zones.\n\n" \
             "2. Road Network Routing via OSRM:\n" \
             "• Driving distance matrix generated via OSRM table service.\n" \
             "• Realistic turn-by-turn road geometries retrieved via OSRM route service.\n\n" \
             "3. Raw Artifact Archival:\n" \
             "• Raw JSON payloads saved in data/raw/.\n" \
             "• SHA-256 hash manifest guarantees immutability."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    add_card(slide7, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Software Quality & Testing")
    tb = slide7.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "15/15 Automated Unit Tests (pytest):\n" \
             "• Graph connectivity and node completeness\n" \
             "• Non-negative distance values & zero diagonal\n" \
             "• Permutation legality (each node visited exactly once)\n" \
             "• PSO convergence and repeatability under fixed seeds\n\n" \
             "Fully Offline Reproducible:\n" \
             "The entire workflow executes offline using preserved datasets without depending on external web APIs at runtime."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide7,
        "All road distances and geometries were generated using the Open Source Routing Machine (OSRM) driving API, referencing verified OpenStreetMap data.\n"
        "Every raw API response is preserved locally in data/raw/ with SHA-256 checksums in a manifest. Our entire dataset can be rebuilt and validated offline without internet access, ensuring full scientific reproducibility."
    )

    # ==========================================
    # SLIDE 8: LIVE CODE EXECUTION & VERIFICATION
    # ==========================================
    slide8 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide8)
    add_header(slide8, "Live Python Execution & Optimality Verification", "Component 4: Live Demonstration")

    add_card(slide8, Inches(0.8), Inches(1.6), Inches(6.0), Inches(5.3), "Solver Output & Tour Recalculation")
    tb = slide8.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.6), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Optimal Discovered Tour (Seed 123):\n" \
             "V0 -> V3 -> V4 -> V7 -> V6 -> V5 -> V2 -> V1 -> V0\n\n" \
             "Step-by-Step Edge Weight Recalculation:\n" \
             "• Leg 1: V0 -> V3 (Divisoria -> Museo de Oro) = 0.3565 km\n" \
             "• Leg 2: V3 -> V4 (Museo -> Vicente de Lara) = 1.3014 km\n" \
             "• Leg 3: V4 -> V7 (Vicente de Lara -> Malasag) = 8.7112 km\n" \
             "• Leg 4: V7 -> V6 (Malasag -> Amaya View) = 13.5305 km\n" \
             "• Leg 5: V6 -> V5 (Amaya View -> High Ridge) = 7.3656 km\n" \
             "• Leg 6: V5 -> V2 (High Ridge -> Cathedral) = 4.6876 km\n" \
             "• Leg 7: V2 -> V1 (Cathedral -> Gaston Park) = 0.1585 km\n" \
             "• Leg 8: V1 -> V0 (Gaston Park -> Divisoria) = 0.3626 km\n\n" \
             "Verified Total Distance = 36.4739 km"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE

    add_card(slide8, Inches(7.1), Inches(1.6), Inches(5.4), Inches(5.3), "Optimality Verification")
    tb = slide8.shapes.add_textbox(Inches(7.3), Inches(2.2), Inches(5.0), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Mathematical Benchmarking:\n\n" \
             "• Brute-Force Exact Minimum: 35.9537 km\n" \
             "  (Evaluated all 5,040 valid permutations)\n\n" \
             "• Best PSO Distance: 36.4739 km\n" \
             "• Optimality Gap: +1.4469% (+520.2 metres)\n\n" \
             "• Result Classification: APPROXIMATE SOLUTION\n" \
             "  (Honest reporting per PIT guidelines)\n\n" \
             "• 30-Seed Stability Analysis:\n" \
             "  - Exact optimum reached in 4/30 runs (13.3%)\n" \
             "  - Mean tour distance: 36.63 km\n" \
             "  - Worst tour distance: 37.89 km\n" \
             "  - Execution time: ~0.03 seconds per run"
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide8,
        "Now let us execute our Python implementation live.\n"
        "As you can see on screen, the solver loads the CSV dataset, validates the matrix, and executes our discrete PSO algorithm with seed 123.\n"
        "Let us examine the results:\n"
        "- PSO Tour Order: V0 -> V3 -> V4 -> V7 -> V6 -> V5 -> V2 -> V1 -> V0.\n"
        "- Total PSO Distance: 36.4739 kilometres.\n"
        "- Exact Matrix Optimum: Evaluated all 5,040 permutations by brute force. The absolute matrix minimum is 35.9537 kilometres.\n"
        "- Optimality Assessment: The optimality gap is 1.45% (520.2 metres). Therefore, we honestly report that our seed-123 PSO solution is an approximate solution, not the exact mathematical optimum.\n"
        "- Across 30 repeated random seeds, PSO matched the exact optimum 4 times, with a mean distance of 36.63 km."
    )

    # ==========================================
    # SLIDE 9: GEOGRAPHIC TOUR VISUALIZATION
    # ==========================================
    slide9 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide9)
    add_header(slide9, "Geographic Road Route & Spatial Clustering", "Component 5: Solution Analysis")

    # Embed Figure 3
    if fig3_path.exists():
        slide9.shapes.add_picture(str(fig3_path), Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3))
    else:
        add_card(slide9, Inches(0.8), Inches(1.6), Inches(7.5), Inches(5.3), "Figure 3: Geographic Tour Map")

    add_card(slide9, Inches(8.6), Inches(1.6), Inches(3.9), Inches(5.3), "Spatial Insights")
    tb = slide9.shapes.add_textbox(Inches(8.8), Inches(2.2), Inches(3.5), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Spatial Clustering:\n\n" \
             "1. Downtown Heritage Cluster:\n" \
             "Starts at Divisoria (V0), visits Museo de Oro (V3) and Capitol Park (V4).\n\n" \
             "2. Eastern Eco-Tourism Loop:\n" \
             "Sweeps east along Sayre Highway to Gardens of Malasag (V7).\n\n" \
             "3. Highland Ridge Overlook:\n" \
             "Climbs to Indahag at Amaya View (V6) and High Ridge (V5).\n\n" \
             "4. Return Descent:\n" \
             "Descends to historic Gaston Park (V1) & Cathedral (V2) before returning to V0."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide9,
        "On Slide 9, we project the optimal tour onto actual CDO road geometry.\n"
        "Notice how the tour smartly clusters stops:\n"
        "It leaves downtown Plaza Divisoria (V0), visits Museo de Oro (V3) and Capitol Park (V4), sweeps eastward to Gardens of Malasag (V7), circles to the Indahag hilltop at Amaya View (V6) and High Ridge (V5), and descends back to Gaston Park (V1) and the Cathedral (V2) before returning to Divisoria.\n"
        "The downtown inset separates the closely spaced heritage sites."
    )

    # ==========================================
    # SLIDE 10: LIMITATIONS, CONCLUSION & REFERENCES
    # ==========================================
    slide10 = prs.slides.add_slide(blank_layout)
    apply_slide_background(slide10)
    add_header(slide10, "Conclusions, Practical Limitations & References", "Component 5: Conclusion")

    add_card(slide10, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.3), "Conclusions & Limitations")
    tb = slide10.shapes.add_textbox(Inches(1.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Key Project Takeaways:\n" \
             "• Discrete PSO (Section 2.4) efficiently optimizes asymmetric road-network TSP problems.\n" \
             "• Found 36.47 km tour in <0.05 seconds, within 1.45% of the exact brute-force optimum.\n" \
             "• Asymmetry in real road graphs must be preserved for practical routing.\n\n" \
             "Practical Limitations:\n" \
             "1. Static Travel Metric: Does not capture live rush-hour delays on major corridors.\n" \
             "2. Opening Hours: Does not enforce time-window constraints for museum entry.\n" \
             "3. Parking Delay: Assumes curb drop-off without modeling parking search time."
    p.font.size = Pt(12)
    p.font.color.rgb = TEXT_WHITE

    add_card(slide10, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.3), "Academic References")
    tb = slide10.shapes.add_textbox(Inches(7.0), Inches(2.2), Inches(5.3), Inches(4.5))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Assigned Literature:\n" \
             "   Luna-Garcia, H., et al. (2024). The Traveling Salesperson Problem: An overview of algorithms, applications, and formulations. Trends in Mathematics and Journal of Mathematics, Section 2.4 (Particle Swarm Optimization).\n\n" \
             "2. Geographic & Routing Systems:\n" \
             "   • Open Source Routing Machine (OSRM). Car driving routing engine.\n" \
             "   • OpenStreetMap contributors. Open spatial database under ODbL.\n" \
             "   • LakbayPinas Travel Guide. Cagayan de Oro tourist destinations.\n\n" \
             "3. Graph Theory Foundation:\n" \
             "   Bondy, J. A., & Murty, U. S. R. Graph Theory with Applications."
    p.font.size = Pt(11)
    p.font.color.rgb = TEXT_WHITE

    set_speaker_notes(slide10,
        "In conclusion:\n"
        "- We successfully formulated an asymmetric 8-stop tourist TSP for Cagayan de Oro City.\n"
        "- Our discrete swap PSO algorithm rapidly discovered an approximate tour of 36.4739 km within 120 iterations, just 1.45% above the exact global optimum.\n"
        "- Limitations: The model assumes static driving routes without real-time congestion and does not account for attraction opening hours or parking search times.\n"
        "References: LakbayPinas for destination ideas, OpenStreetMap and OSRM for geographic data, and Luna-Garcia et al. (2024) for the discrete PSO adaptation.\n"
        "Thank you very much!"
    )

    out_path = results_dir / "CDO_TSP_PSO_Presentation.pptx"
    prs.save(str(out_path))
    print(f"SUCCESS: Presentation saved to {out_path}")
    return True

if __name__ == "__main__":
    create_presentation()
