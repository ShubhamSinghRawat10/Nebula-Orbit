"""Add original, topic-balanced practice for shared B.Tech foundations and BCA.

The questions are original Nebula drafts. PrepInsta and GeeksforGeeks are used
as topic/difficulty references only; their question wording is not copied.
All additions remain pending until a subject expert reviews them.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BANK = ROOT / "practice_question_bank.csv"

# Each course has two additional questions for each of its five outline topics.
# Fields: prompt, correct option, three distractors, explanation, difficulty.
PACKS = {
    "ENGMATH1": [
        [
            ("For f(x)=x^3, what is f′(2)?", "12", ["6", "8", "16"], "The derivative is 3x², which evaluates to 12 at x=2.", "easy"),
            ("If a function is increasing on an interval, what is true of its derivative wherever it is differentiable there?", "The derivative is nonnegative", ["The derivative must be constant", "The function must be linear", "The second derivative must be zero"], "An increasing differentiable function has a nonnegative derivative at interior points where the derivative exists.", "intermediate"),
        ],
        [
            ("A differentiable function has f′(a)=0. What does this condition identify?", "A stationary point that may be a local extremum or neither", ["A guaranteed global maximum", "A point where f(a)=0", "A discontinuity"], "A zero first derivative is a candidate condition; additional analysis is needed to classify the point.", "easy"),
            ("For small Δx, which expression gives the first-order approximation to f(x+Δx)?", "f(x)+f′(x)Δx", ["f(x)Δx", "f′(x)+Δx", "f(x)+f″(x)"], "The linearization uses the function value and its first derivative at x.", "intermediate"),
        ],
        [
            ("What is the value of ∫₀² 3x² dx?", "8", ["4", "6", "12"], "An antiderivative is x³; evaluating from 0 to 2 gives 8.", "easy"),
            ("If f(x) is a rate of flow, what does ∫ₐᵇ f(x)dx represent?", "The accumulated quantity over the interval", ["The rate at the midpoint only", "The derivative at b", "The maximum value of f"], "Integration accumulates a rate over time or another independent variable.", "intermediate"),
        ],
        [
            ("For a square matrix A, what does det(A)=0 imply?", "A is singular and has no inverse", ["A is the identity matrix", "A is diagonal", "A has only positive eigenvalues"], "A square matrix is invertible exactly when its determinant is nonzero.", "easy"),
            ("For a consistent system of linear equations, what does a unique solution correspond to geometrically?", "The constraint hyperplanes intersect at one point", ["They have no common point", "They coincide along a line", "Every point satisfies every equation"], "A unique solution is the single vector satisfying all equations simultaneously.", "intermediate"),
        ],
        [
            ("What is the complex conjugate of 2−5i?", "2+5i", ["−2−5i", "−2+5i", "5+2i"], "Complex conjugation changes the sign of the imaginary component.", "easy"),
            ("What is (1+i)(1−i)?", "2", ["2i", "1", "−2"], "Using (a+b)(a−b)=a²−b² gives 1−i²=2.", "intermediate"),
        ],
    ],
    "ENGPHY1": [
        [
            ("In a double-slit pattern, what happens to fringe spacing if the screen distance is doubled while wavelength and slit separation stay fixed?", "It doubles", ["It halves", "It stays unchanged", "It becomes zero"], "Fringe spacing is proportional to screen distance for fixed wavelength and slit separation.", "easy"),
            ("A stable interference pattern requires the two waves to have what relationship?", "A constant phase difference", ["Different frequencies", "Perpendicular polarizations in every case", "Random phase at every instant"], "Coherence keeps the phase difference sufficiently stable for a persistent pattern.", "intermediate"),
        ],
        [
            ("A charge moves parallel to a uniform magnetic field. What magnetic force acts on it?", "Zero", ["qvB", "qB/v", "Infinite"], "The magnetic-force magnitude is qvB sin θ; for parallel motion θ=0.", "easy"),
            ("Which quantity is the SI unit of magnetic flux?", "Weber", ["Tesla per metre", "Coulomb", "Ampere-turn"], "Magnetic flux is measured in webers; one weber is one tesla-square metre.", "intermediate"),
        ],
        [
            ("For a particle in a one-dimensional box, what happens to the spacing between allowed energy levels as the box becomes narrower?", "The spacing increases", ["The spacing decreases to zero", "The levels become continuous", "The spacing is unchanged for every width"], "Quantized energy scales inversely with the square of the box width.", "intermediate"),
            ("Which observation is a central motivation for quantized photon energy?", "The photoelectric effect has a threshold frequency", ["All metals have identical work functions", "Light always travels at different vacuum speeds", "Electrons have no charge"], "The threshold behaviour is explained when light energy is exchanged in photons with energy proportional to frequency.", "intermediate"),
        ],
        [
            ("In a semiconductor at thermal equilibrium, what is the product of electron and hole concentrations?", "It equals the square of the intrinsic carrier concentration", ["It is always zero", "It equals the band gap", "It depends only on sample length"], "The mass-action relation gives np=nᵢ² at thermal equilibrium for a non-degenerate semiconductor.", "intermediate"),
            ("What happens to the conductivity of a typical intrinsic semiconductor as temperature rises over a moderate range?", "It generally increases", ["It must become zero", "It is independent of carrier concentration", "It changes sign"], "Thermal excitation creates more electron-hole pairs, increasing carrier concentration and usually conductivity.", "intermediate"),
        ],
        [
            ("For total internal reflection at a dielectric interface, light must travel from which medium toward which?", "A higher-index medium toward a lower-index medium", ["A lower-index medium toward a higher-index medium", "Vacuum toward a perfect conductor only", "Two media with identical refractive index"], "Total internal reflection requires incidence from the optically denser medium and an angle above the critical angle.", "easy"),
            ("Why is a laser beam often more directional than light from a lamp?", "Its stimulated emission produces a narrow, coherent optical mode", ["Its photons have zero energy", "It contains every wavelength equally", "It is emitted only by heated metal"], "Laser operation amplifies selected optical modes, producing coherent, directional output.", "intermediate"),
        ],
    ],
    "ENGCHEM1": [
        [
            ("Which subatomic particle determines an element's atomic number?", "Proton", ["Neutron", "Valence shell", "Molecule"], "Atomic number is the number of protons in the nucleus.", "easy"),
            ("A polar covalent bond forms when bonded atoms do what?", "Share electrons unequally", ["Transfer all nuclei", "Share electrons equally in every case", "Exchange neutrons"], "Different electronegativities cause unequal sharing and a bond dipole.", "intermediate"),
        ],
        [
            ("At constant pressure, what does enthalpy change equal for a process with only pressure-volume work?", "Heat transferred to the system", ["Work divided by temperature", "Change in entropy only", "The system's volume"], "For a constant-pressure process with only pressure-volume work, qₚ=ΔH.", "intermediate"),
            ("Which quantity is a state function?", "Enthalpy", ["Heat", "Work", "Path length"], "Enthalpy depends on the thermodynamic state, not on the path taken between states.", "easy"),
        ],
        [
            ("During electrolysis, where does reduction occur?", "At the cathode", ["At the anode", "At both electrodes by definition", "In the salt bridge only"], "Reduction is gain of electrons and occurs at the cathode in both galvanic and electrolytic cells.", "easy"),
            ("What is the role of a salt bridge in a galvanic cell?", "Maintain electrical neutrality by allowing ion migration", ["Supply electrons through the external wire", "Stop all ion movement", "Act as the cathode catalyst in every cell"], "Ion migration in the bridge prevents charge buildup while completing the internal ionic path.", "intermediate"),
        ],
        [
            ("Which treatment is commonly used to remove suspended particles by allowing them to settle under gravity?", "Sedimentation", ["Reverse osmosis", "Ion exchange", "Chlorination"], "Sedimentation separates settleable suspended solids from water by gravity.", "easy"),
            ("Why is activated carbon used in some water-treatment stages?", "Its porous surface adsorbs many dissolved organic compounds", ["It adds hardness ions", "It sterilizes by raising pressure", "It converts all salts into oxygen"], "Activated carbon provides high surface area for adsorption of many organic contaminants and taste/odour compounds.", "intermediate"),
        ],
        [
            ("What generally happens to the average molecular mass of a polymer when its degree of polymerization increases?", "It increases", ["It decreases to zero", "It stays equal to the monomer mass", "It becomes independent of repeat units"], "More repeat units in a chain generally produce greater molecular mass.", "easy"),
            ("Which property is a common advantage of thermosetting polymers after curing?", "They retain a cross-linked shape at elevated temperatures better than remeltable thermoplastics", ["They can be remelted repeatedly without change", "They contain no covalent bonds", "They are always electrically conductive"], "Covalent cross-linking limits flow on reheating, though it also makes remoulding difficult.", "intermediate"),
        ],
    ],
    "ENGPROG": [
        [
            ("A deterministic algorithm receives the same input twice. What should it produce under the same execution conditions?", "The same output", ["A random output every time", "No output", "An output that depends on source-file name"], "Determinism means the same input and conditions lead to the same sequence of decisions and result.", "easy"),
            ("Why should an algorithm specify how it terminates?", "So every valid execution reaches a defined result in finite steps", ["So it can use global variables", "So it avoids all branching", "So the input has no size"], "A well-defined algorithm must make progress and finish for inputs in its stated domain.", "intermediate"),
        ],
        [
            ("In C, what is the value of `5 / 2` when both operands have type int?", "2", ["2.5", "3", "Undefined in every C implementation"], "Integer division discards the fractional part when both operands are integers.", "easy"),
            ("Which conversion can lose information when assigning a floating-point value to an integer type?", "The fractional part can be discarded", ["The sign is always inverted", "The value becomes a pointer", "The variable becomes immutable"], "Converting floating point to integer truncates toward zero when the value is representable.", "intermediate"),
        ],
        [
            ("A menu should be shown at least once before the user is asked whether to continue. Which loop structure expresses that directly?", "do-while", ["while", "if-else", "switch"], "A do-while loop tests its continuation condition after its body, so the body runs at least once.", "easy"),
            ("What does a `break` statement do inside the nearest enclosing loop?", "Exits that loop immediately", ["Skips only the current iteration", "Restarts the program", "Returns from every caller"], "break transfers control to the statement after the nearest enclosing loop or switch.", "easy"),
        ],
        [
            ("In C, what does `strlen(s)` count for a valid null-terminated string?", "Characters before the terminating null character", ["Bytes including the terminator", "Array capacity in every case", "The number of words separated by spaces"], "strlen returns the number of characters before the first null terminator.", "easy"),
            ("Why must an array index be checked against its valid range before access?", "An out-of-range access has undefined behaviour in C", ["C automatically wraps every index", "The compiler turns it into a string", "It changes the array's element type"], "C does not perform automatic bounds checking for ordinary array indexing.", "intermediate"),
        ],
        [
            ("Which declaration creates a pointer to an int in C?", "int *p;", ["int p*;", "pointer int p;", "int &p;"], "The declarator `*p` declares p as a pointer to int.", "easy"),
            ("Why is `sizeof(array) / sizeof(array[0])` not a reliable array-length expression inside a function parameter declared as `int array[]`?", "The parameter is adjusted to a pointer", ["The array becomes a linked list", "sizeof always returns zero for integers", "The function parameter is immutable"], "An array parameter declaration is adjusted to a pointer parameter, so sizeof measures the pointer, not the caller's array.", "intermediate"),
        ],
    ],
    "BASICEE": [
        [
            ("For two resistors in series, what is the equivalent resistance?", "The sum of their resistances", ["Their product divided by their sum", "The smaller resistance only", "Zero"], "Series elements carry the same current and their voltage drops add, so resistances sum.", "easy"),
            ("Thevenin's theorem represents a linear two-terminal network by what equivalent?", "A voltage source in series with a resistance", ["A current source in series with an ideal open circuit", "A transformer with unity turns ratio", "A capacitor in parallel with an inductor only"], "The Thevenin equivalent is an ideal voltage source and a series equivalent resistance seen at the terminals.", "intermediate"),
        ],
        [
            ("For a sinusoidal voltage across a pure inductor, how does current phase compare with voltage?", "Current lags voltage by 90 degrees", ["Current leads by 90 degrees", "Current is always in phase", "Current is opposite in phase by 180 degrees"], "In an ideal inductor, voltage leads current by a quarter cycle.", "easy"),
            ("What is the RMS value of a sinusoid with peak value Vₘ?", "Vₘ/√2", ["2Vₘ", "Vₘ/2", "√2Vₘ"], "The RMS value of a pure sinusoid is its peak divided by the square root of two.", "easy"),
        ],
        [
            ("An ideal transformer has 200 primary turns and 50 secondary turns. If the primary voltage is 120 V, what is the secondary voltage magnitude?", "30 V", ["60 V", "120 V", "480 V"], "The ideal voltage ratio equals the turns ratio: 120×50/200=30 V.", "intermediate"),
            ("Why is a transformer core laminated?", "To reduce eddy-current losses", ["To increase winding resistance", "To eliminate magnetic flux", "To make the supply frequency zero"], "Thin insulated laminations interrupt circulating paths and reduce eddy currents in the core.", "intermediate"),
        ],
        [
            ("In a DC motor, what is the principal purpose of the commutator?", "Reverse armature current at suitable intervals to keep torque direction consistent", ["Convert DC into three-phase supply", "Measure shaft speed without sensors", "Remove the magnetic field"], "The commutator switches armature connections so the developed torque continues in one direction.", "intermediate"),
            ("What is the synchronous speed of an AC machine with supply frequency f and P poles?", "120f/P revolutions per minute", ["60P/f revolutions per minute", "fP/120 revolutions per minute", "120P/f revolutions per minute"], "The rotating magnetic field speed is Ns=120f/P rpm.", "intermediate"),
        ],
        [
            ("Why is an earth conductor provided in equipment supplied from the mains?", "Provide a low-impedance fault path that helps protective devices disconnect supply", ["Increase normal operating voltage", "Carry normal load current continuously", "Replace insulation"], "Protective earthing limits exposed conductive-part voltage and supports fault-current operation of protection.", "easy"),
            ("What should be done before measuring resistance with a handheld ohmmeter?", "De-energize the circuit and isolate the component as needed", ["Measure while the circuit is at full mains voltage", "Short the meter leads to the circuit supply", "Remove the meter's internal battery"], "An ohmmeter applies its own test current; an energized circuit can damage the meter and produce unsafe readings.", "easy"),
        ],
    ],
    "ENGGRAPH": [
        [
            ("In a standard engineering drawing, what does a thick continuous line commonly represent?", "Visible outlines and edges", ["Hidden edges", "A centre line", "A cutting-plane path in every case"], "Line conventions distinguish visible outlines from hidden, centre, and annotation lines.", "easy"),
            ("Why should dimensions be placed clearly and consistently on a drawing?", "So the part can be interpreted and manufactured without guessing", ["To make the drawing scale irrelevant", "To remove the need for units", "To hide the projection method"], "Unambiguous dimensioning communicates size and location requirements for construction and inspection.", "easy"),
        ],
        [
            ("In first-angle orthographic projection, where is the top view conventionally placed relative to the front view?", "Below it", ["Above it", "Inside the front view", "At an arbitrary angle"], "In first-angle projection, the object lies between observer and projection plane, placing the top view below the front view.", "intermediate"),
            ("What does an orthographic view preserve for an object face parallel to the projection plane?", "True shape and size", ["Perspective convergence", "Only colour", "A photographic shading pattern"], "A face parallel to the plane projects without foreshortening in that view.", "intermediate"),
        ],
        [
            ("In an isometric projection, how are the projected lengths along the three principal axes treated?", "They use the same foreshortening scale", ["One axis is always twice the others", "Only the vertical axis is measurable", "They are shown in perspective with vanishing points"], "Isometric projection applies equal foreshortening along the three principal directions.", "intermediate"),
            ("Which set of projected axis directions is typical in an isometric drawing?", "One vertical axis and two axes about 30° to the horizontal", ["Three parallel horizontal axes", "Two vertical axes and one horizontal axis", "Axes that converge at a vanishing point"], "The standard isometric orientation shows the two receding axes symmetrically at about 30° to horizontal.", "easy"),
        ],
        [
            ("What does hatch lining in a sectional view usually indicate?", "Material cut by the section plane", ["A hidden edge behind the object", "A dimension extension line", "The centre of gravity"], "Hatching conventionally identifies solid material intersected by the cutting plane.", "easy"),
            ("Why are hidden lines often omitted from a sectional view when they would clutter it?", "To make the cut surfaces and internal geometry easier to read", ["Because sections cannot show internal geometry", "To indicate that the part is transparent", "Because dimensions are not allowed"], "Section views expose internal features; removing unnecessary hidden lines can improve legibility.", "intermediate"),
        ],
        [
            ("What does a CAD object snap help a drafter do?", "Select precise geometric points such as endpoints or centres", ["Change the drawing's material strength", "Render a physical prototype automatically", "Encrypt the drawing file"], "Object snaps align cursor input to exact geometric locations rather than approximate screen positions.", "easy"),
            ("Why are reusable CAD blocks useful for repeated symbols?", "They keep repeated geometry consistent and easier to update", ["They force every component to have the same dimensions", "They convert 2D drawings into finite-element results", "They remove all object properties"], "A block reuses a defined group of geometry and can be edited consistently across placements.", "intermediate"),
        ],
    ],
    "ENGMECH": [
        [
            ("For a planar rigid body in static equilibrium, what must the sum of moments about any point be?", "Zero", ["Equal to the mass", "Equal to the largest force", "Nonzero and constant"], "Rotational equilibrium requires zero net moment about any point.", "easy"),
            ("A force system has zero resultant force but a nonzero resultant couple. Is the body in complete static equilibrium?", "No, because the net moment is nonzero", ["Yes, zero force alone is sufficient", "Yes, if the body is rigid", "Only if its mass is zero"], "Static equilibrium requires both zero resultant force and zero resultant moment.", "intermediate"),
        ],
        [
            ("Where is the centroid of a uniform rectangular lamina located?", "At the intersection of its diagonals", ["At one corner", "At the midpoint of one edge", "Outside the rectangle"], "By symmetry and uniform density, the centroid is at the rectangle's geometric centre.", "easy"),
            ("What does the second moment of area measure in beam bending?", "How area is distributed relative to a chosen axis", ["The total mass of the beam", "The beam's thermal conductivity", "The applied force direction only"], "The area moment of inertia depends on the squared distance of area elements from the axis and influences bending stiffness.", "intermediate"),
        ],
        [
            ("For a block on a horizontal surface, what is the maximum static friction before sliding in the Coulomb model?", "μₛN", ["μₖ/N", "N/μₛ", "mg/μₛ"], "The limiting static friction magnitude is μₛ times the normal reaction.", "easy"),
            ("If the applied horizontal force is below the limiting static friction, what happens to the block?", "It can remain at rest and static friction balances the applied force", ["It must accelerate at μₖg", "Friction becomes zero", "It moves at constant terminal speed"], "Static friction adjusts up to its limit to prevent relative motion.", "intermediate"),
        ],
        [
            ("A particle's position is x(t)=4t². What is its velocity at t=3 s?", "24 m/s", ["12 m/s", "36 m/s", "4 m/s"], "Velocity is dx/dt=8t, giving 24 m/s at t=3 s.", "easy"),
            ("In curvilinear motion, can a particle have constant speed but nonzero acceleration?", "Yes, if its direction of motion changes", ["No, acceleration is always zero at constant speed", "Only if its mass changes", "Only in one-dimensional motion"], "A change in velocity direction produces normal acceleration even when speed remains constant.", "intermediate"),
        ],
        [
            ("What is the kinetic energy of a particle of mass m moving at speed v?", "½mv²", ["mv", "m/v²", "2mv²"], "Translational kinetic energy is one half the mass times speed squared.", "easy"),
            ("For a constant force F acting for time Δt, what is the impulse magnitude when force and motion direction align?", "FΔt", ["F/Δt", "FΔt²", "Δt/F"], "Impulse is the time integral of force; for a constant aligned force it is FΔt and equals momentum change.", "intermediate"),
        ],
    ],
    "TECHCOMM": [
        [
            ("When reading a technical standard, which note is most useful for later verification?", "The exact clause or page plus a concise paraphrase", ["A copied fragment with no citation", "Only the document's cover colour", "A guess about the author's intent"], "A locator and a clear paraphrase make notes traceable to the source.", "easy"),
            ("What should a reader do when a technical source uses an unfamiliar term?", "Check its definition in context and record the source", ["Assume it means the most familiar everyday sense", "Skip every paragraph containing it", "Replace it with a synonym without checking"], "Context and authoritative definitions reduce misinterpretation of domain-specific terms.", "intermediate"),
        ],
        [
            ("What is a useful purpose for a topic sentence in a technical paragraph?", "State the paragraph's main point", ["Introduce an unrelated example", "List every citation without context", "Repeat the title verbatim"], "A topic sentence helps readers understand the paragraph's focus before supporting details.", "easy"),
            ("Which revision most improves a paragraph containing several unrelated claims?", "Split it into focused paragraphs with clear transitions", ["Add more unrelated claims", "Remove all topic sentences", "Replace precise terms with vague words"], "Grouping related ideas improves coherence and helps readers follow the argument.", "intermediate"),
        ],
        [
            ("What should the methods section of a technical report enable a reader to understand?", "How the work was carried out and how results were obtained", ["Only the author's job title", "The conclusion before any evidence", "The full history of the organization"], "Methods describe procedures, measurements, and analysis sufficiently for readers to interpret the results.", "easy"),
            ("A proposal recommends a new process. What should its justification connect?", "The identified need, proposed approach, evidence, and expected outcomes", ["The cover design and the author's preferences", "Only the purchase price", "A list of unrelated technologies"], "A persuasive proposal links the problem to a feasible solution and measurable outcomes.", "intermediate"),
        ],
        [
            ("For a slide shown in a large room, which choice usually improves readability?", "Use concise text with sufficiently large type and strong contrast", ["Put the full report on one slide", "Use several low-contrast font colours", "Make every label very small"], "Concise text, readable type, and contrast help audiences follow projected material.", "easy"),
            ("What should a presenter do when showing a data chart?", "Explain the key pattern and identify units and relevant context", ["Read every axis tick aloud", "Hide the data source", "Remove labels to save space"], "A short interpretation and clear units help the audience understand what the chart supports.", "intermediate"),
        ],
        [
            ("How should an engineer report a result that does not support the original hypothesis?", "Report it accurately and discuss limitations without changing the data", ["Omit it to protect the hypothesis", "Alter the measurements to fit expectations", "Present it as a proven result without uncertainty"], "Responsible reporting preserves the evidence and explains uncertainty or limitations transparently.", "easy"),
            ("When using another author's figure in a report, what should the writer do?", "Follow permission and licence terms and provide attribution", ["Remove the author's name", "Claim the figure as original", "Assume online availability means public domain"], "Attribution and licence compliance respect the creator's rights and let readers trace the source.", "intermediate"),
        ],
    ],
    "BCA01": [
        [
            ("What is the negation of the proposition “p and q”?", "not p or not q", ["not p and not q", "p or q", "p and not q"], "De Morgan's law gives ¬(p∧q)=¬p∨¬q.", "easy"),
            ("A proposition p implies q. In which case is p→q false?", "p is true and q is false", ["Both are true", "p is false and q is true", "Both are false"], "Material implication is false only when its antecedent is true and consequent is false.", "easy"),
        ],
        [
            ("A relation R on a set is symmetric if which condition holds?", "Whenever aRb, then bRa", ["Whenever aRb and bRc, then aRc", "Every element relates only to itself", "Every pair of elements is related"], "Symmetry requires each ordered pair in the relation to have its reverse pair.", "easy"),
            ("A function f:A→B is injective when what is true?", "Different inputs in A map to different outputs in B", ["Every element of B is an output", "Every input maps to two outputs", "A and B must be identical sets"], "Injectivity means f(a₁)=f(a₂) implies a₁=a₂.", "intermediate"),
        ],
        [
            ("How many subsets does a set with four distinct elements have?", "16", ["4", "8", "24"], "A set with n elements has 2ⁿ subsets; 2⁴=16.", "easy"),
            ("For a recurrence T(n)=T(n−1)+1 with T(1)=1, what is T(n)?", "n", ["log₂n", "n²", "2ⁿ"], "Each step adds one, so expanding the recurrence yields T(n)=n.", "intermediate"),
        ],
        [
            ("In an undirected graph, what does the degree of a vertex count?", "The number of incident edges", ["The number of connected components", "The number of vertices at distance two only", "The number of graph labels"], "Degree is the count of edges incident to the vertex, with special handling for loops depending on convention.", "easy"),
            ("What is a tree with n vertices guaranteed to have?", "n−1 edges and a path between every pair of vertices", ["n edges and exactly one cycle", "No leaves", "At least two cycles"], "A finite tree is connected and acyclic, which implies it has n−1 edges.", "intermediate"),
        ],
        [
            ("Which Boolean identity is the complement of A OR B?", "NOT A AND NOT B", ["NOT A OR NOT B", "A AND B", "A OR NOT B"], "De Morgan's law states ¬(A∨B)=¬A∧¬B.", "easy"),
            ("What is the output of an XOR gate when its two inputs are equal?", "0", ["1", "The input voltage doubled", "Undefined for binary inputs"], "XOR is 1 when inputs differ and 0 when they are equal.", "easy"),
        ],
    ],
    "BCA02": [
        [
            ("What is the unsigned decimal value of the 8-bit binary number 00001101?", "13", ["11", "12", "14"], "The set bits represent 8+4+1=13.", "easy"),
            ("In 8-bit two's-complement representation, what decimal value does 11111111 represent?", "−1", ["255", "−127", "−2"], "In two's complement, all ones is the representation of negative one.", "intermediate"),
        ],
        [
            ("Which logic gate produces 1 only when both inputs are 1?", "AND", ["OR", "XOR", "NOR"], "The AND operation is true only when both binary inputs are true.", "easy"),
            ("A half adder's sum output is produced by which gate?", "XOR", ["AND", "OR", "NOT"], "The sum bit of a half adder is A XOR B; the carry is A AND B.", "easy"),
        ],
        [
            ("What is the key difference between a latch and an edge-triggered flip-flop?", "A latch is level-sensitive; a flip-flop responds to a clock edge", ["A latch stores no state", "A flip-flop is always combinational", "A latch can store only analogue values"], "A latch is transparent over an enable level, while an edge-triggered flip-flop samples at a clock transition.", "intermediate"),
            ("What does a D flip-flop normally do at its active clock edge?", "Copies D to Q", ["Sets Q to D's complement in every case", "Adds D to Q", "Clears the clock"], "At the active edge, the D input is sampled and appears at Q after propagation delay.", "easy"),
        ],
        [
            ("Which register holds the address of the next instruction to be fetched in a basic CPU model?", "Program counter", ["Instruction register", "Status register only", "Memory data register"], "The program counter identifies the next instruction address in the fetch sequence.", "easy"),
            ("What is the role of an instruction decoder?", "Interpret the instruction's opcode and generate control signals", ["Store all program files permanently", "Translate an IP address to a MAC address", "Increase clock frequency"], "The decoder identifies the operation and helps control the datapath components needed to execute it.", "intermediate"),
        ],
        [
            ("Which memory is typically volatile and directly used for a running program's working data?", "Main memory (RAM)", ["Optical disc", "Read-only firmware only", "Magnetic tape archive"], "RAM is volatile primary memory used to hold active instructions and data.", "easy"),
            ("Why does a cache use locality to improve average access time?", "Recently used or nearby data is likely to be requested again", ["All memory requests are random", "Cache capacity exceeds disk capacity", "Caches eliminate address translation"], "Temporal and spatial locality make recently accessed or adjacent data useful to keep near the processor.", "intermediate"),
        ],
    ],
    "BCA03": [
        [
            ("Which HTML element is appropriate for the primary heading of a page?", "<h1>", ["<div>", "<span>", "<meta>"], "A top-level heading should use the semantic h1 element.", "easy"),
            ("Why should a form control have an associated label?", "It gives the control an accessible name and a larger clickable target", ["It encrypts the submitted value", "It automatically validates every possible rule", "It replaces the need for a form"], "A programmatically associated label improves screen-reader identification and usability.", "easy"),
        ],
        [
            ("Which CSS layout system is designed to align items along one dimension at a time?", "Flexbox", ["SQL", "DNS", "HTML canvas only"], "Flexbox is primarily a one-dimensional layout model for arranging items in a row or column.", "easy"),
            ("In the CSS box model, what does `box-sizing: border-box` include in the declared width?", "Content, padding, and border", ["Content only", "Margin only", "Padding but not border"], "With border-box, the specified width includes content, padding, and border.", "intermediate"),
        ],
        [
            ("What does `querySelector()` return when a matching element exists?", "The first matching element", ["A list of every match", "The document's HTML string", "The element's computed CSS only"], "querySelector returns the first element matching the CSS selector, or null if none matches.", "easy"),
            ("Why should an event listener often be registered instead of assigning inline JavaScript in HTML?", "It separates behaviour from markup and supports structured event handling", ["It disables the browser event loop", "It makes the page immune to all attacks", "It converts JavaScript to CSS"], "Listeners keep code organization clearer and let scripts manage event propagation and multiple handlers.", "intermediate"),
        ],
        [
            ("What does an HTTP 404 response indicate?", "The server did not find a current representation for the target resource", ["The request succeeded with a new resource", "The client must retry authentication", "The server has permanently shut down"], "404 Not Found means the origin did not find a current representation or is unwilling to disclose one.", "easy"),
            ("What is a common benefit of using JSON in a web API?", "It provides a text-based structured format that many languages can parse", ["It guarantees data is encrypted", "It replaces HTTP status codes", "It can represent only numbers"], "JSON is a language-independent structured data format commonly used in HTTP APIs.", "easy"),
        ],
        [
            ("Where should a web application perform authoritative permission checks for a protected action?", "On the server for each request", ["Only by hiding the button in CSS", "Only in browser-side JavaScript", "Only after sending the database password to the client"], "Client code can be bypassed, so the server must enforce authorization on every protected request.", "easy"),
            ("Why should a server validate input even when the browser form already validates it?", "Clients can bypass or modify browser-side checks", ["HTML validation is encrypted", "Server validation makes HTTPS unnecessary", "Browsers cannot send strings"], "Client-side validation improves usability but is not a security boundary.", "intermediate"),
        ],
    ],
    "BCA04": [
        [
            ("Why is a foreign key useful in an orders table that references customers?", "It can enforce that each customer reference points to a valid customer row", ["It sorts orders automatically", "It encrypts customer data", "It ensures every order has a different product name"], "A foreign-key constraint enforces referential integrity between related rows.", "easy"),
            ("What is a composite key?", "A key formed from more than one attribute", ["A key shared by different databases only", "A non-unique descriptive note", "A key that cannot identify rows"], "A composite key uses multiple columns together to identify a tuple.", "easy"),
        ],
        [
            ("Which SQL clause orders result rows by a column?", "ORDER BY", ["GROUP BY", "WHERE", "FROM"], "ORDER BY specifies the sort order of rows returned by a query.", "easy"),
            ("What does `COUNT(*)` count in a SQL group?", "Rows in the group", ["Only non-null values in the first column", "Distinct tables", "The number of indexes"], "COUNT(*) counts rows, including rows containing NULL values in individual columns.", "easy"),
        ],
        [
            ("What does atomicity require for a transaction?", "Its operations succeed together or are rolled back together", ["Every query uses an index", "Every table has one column", "The database is stored only in memory"], "Atomicity provides all-or-nothing transaction behaviour.", "easy"),
            ("What is a common purpose of a database transaction isolation level?", "Control how concurrent transactions can observe each other's effects", ["Choose the user-interface theme", "Compress every value", "Set the database's network address"], "Isolation levels define guarantees around visibility of concurrent transaction activity.", "intermediate"),
        ],
        [
            ("Why should an application use a connection pool for repeated database requests?", "Reuse a limited set of connections and avoid setup overhead for every request", ["Make each request open unlimited sockets", "Disable authentication", "Store SQL queries in browser cookies"], "A pool manages reusable connections, reducing repeated connection setup and resource pressure.", "intermediate"),
            ("Why should an application close or return a borrowed connection after use?", "So the pool can safely reuse the resource", ["To delete the database", "To disable transactions permanently", "To change every primary key"], "Returning connections prevents leaks and allows other requests to use the pool.", "easy"),
        ],
        [
            ("What is the purpose of a database backup restore drill?", "Confirm that data can actually be recovered within expected limits", ["Increase query latency", "Prove that backups are unnecessary", "Remove the need for access controls"], "A restore test validates recoverability; an untested backup may be unusable or incomplete.", "intermediate"),
            ("Which practice best limits exposure if an application account is compromised?", "Grant only the database permissions the application needs", ["Use the database owner account everywhere", "Share one password across all services", "Disable all audit logs"], "Least-privilege access reduces the actions available to a compromised account.", "easy"),
        ],
    ],
    "BCA05": [
        [
            ("What should a well-scoped functional requirement describe?", "A behaviour or service the system must provide", ["A particular paint colour only", "The developer's preferred editor", "A guess about next year's team structure"], "Functional requirements state what the product or system must do.", "easy"),
            ("Why include an acceptance criterion with a requirement?", "It makes completion observable and checkable", ["It guarantees zero defects", "It replaces stakeholder review", "It hides edge cases"], "Acceptance criteria define evidence by which stakeholders can determine whether a requirement is met.", "intermediate"),
        ],
        [
            ("What does a sequence diagram primarily show?", "Interactions and message order among participants over time", ["A database's disk layout", "Only a class's inheritance tree", "A source-code formatting standard"], "Sequence diagrams model participants exchanging messages in temporal order.", "easy"),
            ("Why is low coupling generally desirable in a modular design?", "Changes in one module are less likely to require changes in unrelated modules", ["It forces all modules into one file", "It prevents testing", "It makes interfaces unnecessary"], "Lower coupling reduces dependency spread and makes components easier to change independently.", "intermediate"),
        ],
        [
            ("What does a version-control commit represent?", "A recorded snapshot of staged changes in repository history", ["A production server restart", "A database backup by definition", "A pull request review"], "A commit records a set of changes with metadata in the version history.", "easy"),
            ("Why create a branch for a feature change?", "Work can be developed and reviewed separately before integration", ["It duplicates the production database", "It removes the need for tests", "It guarantees there will be no conflicts"], "Branches isolate work and provide a collaboration path; they do not guarantee conflict-free merges.", "easy"),
        ],
        [
            ("What is the main focus of a unit test?", "A small function or component's behaviour", ["A full production deployment", "Every possible behaviour of the entire system", "The organisation's annual budget"], "Unit tests focus on small pieces of behaviour, typically with controlled dependencies.", "easy"),
            ("What does an integration test primarily check?", "Whether multiple components work together through their interfaces", ["Whether one line follows a style guide", "Whether a user likes the logo", "Whether the source repository is encrypted"], "Integration tests exercise interactions and contracts between components.", "easy"),
            ("A test passes alone but fails when run with another component. Which test level is most relevant for investigating the interaction?", "An integration test", ["A spelling check", "A code-format check", "A deployment smoke test only"], "An integration test examines a boundary or interaction between components and can reveal contract or configuration mismatches.", "intermediate"),
        ],
        [
            ("Why should a deployment have a rollback or recovery plan?", "A faulty release can be reversed or mitigated quickly", ["It guarantees the release has no bugs", "It removes the need for backups", "It prevents users from reporting problems"], "A rollback plan reduces recovery time when a change causes production problems.", "intermediate"),
            ("What should maintenance documentation record after a significant system change?", "The actual changed behaviour, configuration, and operational steps", ["Only the original project slogan", "A prediction that nothing will change", "Private passwords in a public file"], "Current documentation helps operators and maintainers understand how the system really works.", "easy"),
        ],
    ],
}


def main() -> None:
    with BANK.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    fields = list(rows[0])
    topics = {}
    title = {}
    # Take canonical topic order from the curriculum, not from the current CSV
    # row order (which can differ for imported legacy questions).
    curriculum = list(csv.DictReader((ROOT / "branch_curriculum.csv").open("r", encoding="utf-8-sig", newline="")))
    legacy = list(csv.DictReader((ROOT / "topics.csv").open("r", encoding="utf-8-sig", newline="")))
    legacy_by_course = {}
    for row in legacy:
        legacy_by_course.setdefault(row["course_code"], []).append(row["topic_name"])
    branch_by_course = {}
    for row in curriculum:
        branch_by_course.setdefault(row["course_code"], [topic.strip() for topic in row["topics"].split("|") if topic.strip()])
    for row in rows:
        title.setdefault(row["course_id"], row["quiz_title"])
    for code in title:
        names = legacy_by_course.get(code) or branch_by_course.get(code)
        if not names or len(names) != 5:
            raise ValueError(f"Expected five canonical curriculum topics for {code}.")
        topics[code] = names

    additions = []
    generated_prompts = set()
    for course_id, topic_sets in PACKS.items():
        if course_id not in topics or len(topics[course_id]) != 5:
            raise ValueError(f"Expected five existing course topics for {course_id}.")
        if len(topic_sets) != len(topics[course_id]):
            raise ValueError(f"Question pack topic count does not match the outline for {course_id}.")
        option_position = 0
        for topic_index, questions in enumerate(topic_sets):
            for prompt, correct, distractors, explanation, difficulty in questions:
                prompt_key = (course_id, prompt)
                if prompt_key in generated_prompts:
                    raise ValueError(f"Duplicate generated prompt: {prompt}")
                generated_prompts.add(prompt_key)
                options = [correct, *distractors]
                target = option_position % len(options)
                options[0], options[target] = options[target], options[0]
                option_position += 1
                additions.append({
                    "course_id": course_id,
                    "quiz_title": title[course_id],
                    "quiz_topic": "Course-wide practice",
                    "question_topic": topics[course_id][topic_index],
                    "prompt": prompt,
                    "options_json": json.dumps(options, ensure_ascii=False),
                    "answer_index": str(target),
                    "explanation": explanation,
                    "difficulty": difficulty,
                    "review_status": "pending",
                    "reviewer_name": "",
                    "reviewer_role": "",
                    "source_url": "",
                    "review_notes": "Original Nebula draft; instructor review required.",
                    "review_date": "",
                })

    rows = [row for row in rows if (row["course_id"], row["prompt"]) not in generated_prompts]
    rows.extend(additions)
    with BANK.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Added {len(additions)} original questions across {len(PACKS)} courses; all are pending instructor review.")


if __name__ == "__main__":
    main()
