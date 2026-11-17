"""Generate the source-controlled common B.Tech/BCA curriculum CSV.

These are authored curriculum outlines, not verbatim university syllabi.
Review source notes in CURRICULUM_SOURCES.md before extending this catalog.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Each subject is expressed as a small, teachable topic outline. Track-specific
# topics are intentionally explicit so recommendations never rely on synthetic
# placeholder topic names.
COMMON_BTECH = {
    "Engineering Mathematics I": ["Single-variable calculus", "Differential calculus and applications", "Integral calculus", "Matrices and linear systems", "Complex numbers"],
    "Engineering Physics": ["Wave optics and interference", "Electromagnetism", "Quantum physics foundations", "Semiconductor physics", "Lasers and fibre optics"],
    "Engineering Chemistry": ["Atomic structure and bonding", "Chemical thermodynamics", "Electrochemistry and corrosion", "Water chemistry and treatment", "Polymers and engineering materials"],
    "Programming for Problem Solving": ["Algorithms and flowcharts", "Data types and expressions", "Selection and iteration", "Arrays and strings", "Functions, pointers and structures"],
    "Basic Electrical Engineering": ["DC circuit laws and network theorems", "Single-phase AC circuits", "Magnetic circuits and transformers", "Electrical machines overview", "Electrical safety and measurements"],
    "Engineering Graphics": ["Engineering drawing standards", "Orthographic projections", "Isometric projections", "Sectional views", "Computer-aided drafting basics"],
    "Engineering Mechanics": ["Force systems and equilibrium", "Centroids and moments of inertia", "Friction", "Kinematics of particles", "Work, energy and impulse"],
    "Communication and Technical Writing": ["Technical reading and note-making", "Clear technical paragraphs", "Reports and proposals", "Oral presentations", "Professional and ethical communication"],
}

TRACK_SUBJECTS = {
    "BTECH_CSE": {},
    "BTECH_IT": {
        "Information Systems": ["Information system components", "Transaction and decision support systems", "Enterprise systems", "Systems analysis and design", "IT governance and service management"],
        "Data Communication": ["Signals and transmission media", "Data encoding and multiplexing", "Error detection and correction", "Switching and routing concepts", "Link protocols and performance"],
        "IT Infrastructure and Services": ["Server and storage architecture", "Virtualization and containers", "IT service lifecycle", "Availability and incident management", "Capacity and continuity planning"],
        "Web Application Engineering": ["HTTP and browser architecture", "Client-side application structure", "Server-side web patterns", "API design and integration", "Web security and deployment"],
    },
    "BTECH_ECE": {
        "Electronic Devices": ["PN junction and diode circuits", "Bipolar junction transistor", "Field-effect transistors", "Biasing and small-signal models", "Optoelectronic devices"],
        "Analog Circuits": ["Amplifier frequency response", "Feedback and stability", "Operational amplifier circuits", "Oscillators and waveform generators", "Power amplifier classes"],
        "Signals and Systems": ["Continuous and discrete signals", "Linear time-invariant systems", "Convolution and impulse response", "Fourier series and transforms", "Laplace and Z transforms"],
        "Digital Communication": ["Sampling and pulse modulation", "Baseband line coding", "Digital modulation schemes", "Detection and error probability", "Information theory and channel coding"],
        "Electromagnetic Fields": ["Vector calculus for fields", "Electrostatics and boundary conditions", "Magnetostatics", "Maxwell equations", "Uniform plane waves and transmission lines"],
    },
    "BTECH_EE": {
        "Electrical Circuit Analysis": ["Network laws and topology", "Network theorems", "Transient response of circuits", "Sinusoidal steady-state analysis", "Two-port networks"],
        "Electrical Machines": ["Transformers and equivalent circuits", "DC machine principles", "Three-phase induction machines", "Synchronous machines", "Machine testing and efficiency"],
        "Power Systems": ["Generation and load characteristics", "Transmission line parameters", "Power flow fundamentals", "Fault analysis and protection", "Economic operation and grid basics"],
        "Power Electronics": ["Power semiconductor devices", "Controlled rectifiers", "DC-DC converters", "Inverters and PWM", "Drives and applications"],
        "Control Systems": ["System modelling and block diagrams", "Time-domain response", "Stability criteria", "Root locus and frequency response", "PID control and compensation"],
    },
    "BTECH_ME": {
        "Engineering Thermodynamics": ["Properties of pure substances", "First law for closed and open systems", "Second law and entropy", "Power and refrigeration cycles", "Combustion and availability"],
        "Fluid Mechanics": ["Fluid properties and statics", "Continuity and momentum equations", "Bernoulli equation and applications", "Internal pipe flow and losses", "Boundary layers and dimensional analysis"],
        "Strength of Materials": ["Stress, strain and elastic constants", "Axial loading and thermal stress", "Shear force and bending moment", "Bending and shear stresses", "Torsion and column buckling"],
        "Manufacturing Processes": ["Casting processes and defects", "Forming and metalworking", "Machining mechanics and tools", "Joining processes", "Additive manufacturing fundamentals"],
        "Theory of Machines": ["Kinematic pairs and mechanisms", "Velocity and acceleration analysis", "Gears and gear trains", "Balancing of rotating masses", "Governors, flywheels and vibration"],
    },
    "BTECH_CE": {
        "Structural Analysis": ["Determinate beams and frames", "Deflection of beams", "Influence lines", "Indeterminate structures", "Matrix methods and structural idealization"],
        "Geotechnical Engineering": ["Soil formation and index properties", "Soil classification and compaction", "Permeability and seepage", "Effective stress and consolidation", "Shear strength and bearing capacity"],
        "Surveying": ["Chain and compass surveying", "Levelling and contouring", "Traversing and error adjustment", "Theodolite and total station", "GNSS, photogrammetry and GIS basics"],
        "Fluid Mechanics and Hydraulics": ["Fluid statics and pressure measurement", "Flow kinematics and dynamics", "Pipe networks and losses", "Open-channel flow", "Hydraulic machines and measurements"],
        "Transportation Engineering": ["Highway planning and alignment", "Geometric design", "Pavement materials and design", "Traffic flow and intersections", "Railway and airport engineering overview"],
    },
    "BTECH_CHE": {
        "Chemical Engineering Thermodynamics": ["First-law energy balances", "Second law and entropy", "Pure-fluid property relations", "Phase equilibrium", "Thermodynamic cycles and applications"],
        "Fluid Flow Operations": ["Fluid statics and dimensional analysis", "Continuity and momentum balances", "Flow in pipes and fittings", "Pumps and flow measurement", "Packed beds and fluidization"],
        "Heat Transfer": ["Steady-state conduction", "Convection correlations", "Thermal radiation", "Heat exchanger analysis", "Boiling, condensation and evaporation"],
        "Mass Transfer Operations": ["Diffusion and mass-transfer coefficients", "Equilibrium stages", "Distillation", "Gas absorption and stripping", "Liquid-liquid extraction and drying"],
        "Chemical Reaction Engineering": ["Rate laws and reaction kinetics", "Ideal batch and flow reactors", "Reactor design equations", "Non-isothermal reactors", "Catalysis and residence-time effects"],
    },
    "BTECH_MME": {
        "Physical Metallurgy": ["Crystal structures and defects", "Diffusion in solids", "Phase diagrams and lever rule", "Solidification and microstructure", "Mechanical behaviour of materials"],
        "Extractive Metallurgy": ["Ore preparation and concentration", "Pyrometallurgical principles", "Hydrometallurgical leaching", "Electrometallurgical extraction", "Metal refining and process selection"],
        "Heat Treatment of Materials": ["Iron-carbon equilibrium diagram", "Austenitizing and transformation products", "Annealing and normalizing", "Quenching and tempering", "Hardenability and surface treatment"],
        "Materials Characterization": ["Optical microscopy and specimen preparation", "X-ray diffraction principles", "Scanning electron microscopy", "Mechanical and hardness testing", "Failure analysis and fractography"],
    },
    "BTECH_BIOTECH": {
        "Cell Biology": ["Cell structure and organelles", "Membrane transport and signalling", "Cell cycle and division", "Cytoskeleton and motility", "Cell death and disease"],
        "Biochemistry": ["Biomolecules and molecular interactions", "Enzyme kinetics and inhibition", "Carbohydrate and lipid metabolism", "Bioenergetics and ATP", "Protein structure and function"],
        "Genetics and Molecular Biology": ["Mendelian inheritance", "DNA replication and repair", "Transcription and RNA processing", "Translation and gene regulation", "Mutation and genetic variation"],
        "Microbiology": ["Microbial cell structure", "Growth kinetics and culture methods", "Microbial genetics", "Pathogenesis and host response", "Sterilization and antimicrobial control"],
        "Bioprocess Engineering": ["Material and energy balances", "Bioreactor configurations", "Sterilization and aseptic operation", "Scale-up and mass transfer", "Downstream processing"],
    },
    "BTECH_AERO": {
        "Aerodynamics": ["Atmospheric properties and airfoils", "Incompressible potential flow", "Lift, drag and boundary layers", "Compressible flow and shock waves", "Finite-wing and aircraft performance"],
        "Aircraft Structures": ["Loads and structural idealization", "Stress analysis of beams and thin-walled members", "Airframe joints and fittings", "Buckling and stability", "Fatigue, fracture and damage tolerance"],
        "Flight Mechanics": ["Aircraft geometry and performance", "Static stability and control", "Equations of motion", "Longitudinal and lateral dynamics", "Flight envelope and manoeuvres"],
        "Propulsion Systems": ["Thrust and propulsion cycles", "Gas turbine components", "Compressor and turbine performance", "Combustion and nozzle flow", "Propeller and rocket propulsion overview"],
    },
    "BTECH_AGRI": {
        "Soil and Water Engineering": ["Soil-water relationships", "Infiltration and soil erosion", "Watershed hydrology", "Groundwater and wells", "Soil and water conservation structures"],
        "Irrigation and Drainage": ["Crop water requirement", "Canal and field irrigation", "Pumps and water conveyance", "Drainage design", "Irrigation scheduling and efficiency"],
        "Farm Power and Machinery": ["Farm power sources", "Tractor systems and performance", "Tillage and seedbed implements", "Planting and crop protection equipment", "Machinery selection and field capacity"],
        "Post-Harvest Engineering": ["Crop properties and quality", "Cleaning, grading and handling", "Drying and moisture relations", "Storage and preservation", "Processing systems and losses"],
    },
    "BTECH_BIOMED": {
        "Human Physiology for Engineers": ["Cell and tissue organization", "Cardiovascular system", "Respiratory system", "Nervous system and bioelectricity", "Homeostasis and physiological signals"],
        "Biomedical Instrumentation": ["Bio-potential electrodes", "ECG, EEG and EMG acquisition", "Signal conditioning and isolation", "Medical sensors and transducers", "Patient safety and instrument standards"],
        "Biomaterials": ["Material classes and host response", "Biocompatibility and testing", "Metallic and polymeric implants", "Ceramics and tissue engineering scaffolds", "Degradation, wear and implant failure"],
        "Medical Imaging Systems": ["X-ray generation and radiography", "Computed tomography principles", "Ultrasound imaging", "Magnetic resonance imaging", "Image quality and radiation safety"],
    },
    "BTECH_ENV": {
        "Environmental Chemistry": ["Water chemistry and equilibria", "Acid-base and redox systems", "Chemical oxygen demand and BOD", "Nutrient cycles and eutrophication", "Environmental sampling and analysis"],
        "Water and Wastewater Treatment": ["Water quality and treatment objectives", "Coagulation, flocculation and sedimentation", "Filtration and disinfection", "Biological wastewater treatment", "Sludge treatment and reuse"],
        "Air Pollution Control": ["Atmospheric structure and pollutant sources", "Dispersion and air quality metrics", "Particulate control devices", "Gas absorption and emission control", "Monitoring and regulatory concepts"],
        "Solid Waste Management": ["Waste characterization and hierarchy", "Collection and transport systems", "Composting and biological treatment", "Thermal treatment and energy recovery", "Landfill design and leachate control"],
    },
    "BTECH_AUTO": {
        "Automotive Powertrains": ["Internal-combustion engine cycles", "Fuel injection and combustion", "Engine performance and emissions", "Electric and hybrid powertrains", "Powertrain testing and calibration"],
        "Vehicle Dynamics": ["Tyre forces and vehicle models", "Longitudinal dynamics and braking", "Ride and suspension response", "Steering and handling", "Vehicle stability and control"],
        "Automotive Transmission Systems": ["Clutch and torque transfer", "Manual and automatic gearboxes", "Differentials and final drives", "Continuously variable transmissions", "Transmission efficiency and selection"],
        "Automotive Electrical and Electronics": ["Vehicle electrical architecture", "Sensors and actuators", "Engine and body control units", "Communication buses and diagnostics", "Functional safety and fault diagnosis"],
    },
    "BTECH_PROD": {
        "Production and Operations Research": ["Linear programming models", "Simplex and sensitivity analysis", "Transportation and assignment", "Inventory control", "Project scheduling with PERT and CPM"],
        "Manufacturing Systems": ["Process planning and routing", "Production system layouts", "Group technology and cellular manufacturing", "Flexible manufacturing systems", "Lean systems and bottleneck analysis"],
        "Quality Engineering": ["Quality principles and cost", "Statistical process control", "Process capability", "Acceptance sampling", "Reliability and continuous improvement"],
        "Metrology and Inspection": ["Measurement standards and errors", "Limits, fits and tolerances", "Gauges and comparators", "Coordinate measuring systems", "Inspection planning and uncertainty"],
    },
    "BTECH_MINING": {
        "Mining Geology": ["Minerals, rocks and structures", "Ore deposit formation", "Geological mapping and sampling", "Exploration methods", "Reserve estimation fundamentals"],
        "Surface Mining": ["Surface mine planning", "Drilling and blasting", "Excavation and haulage systems", "Slope stability and waste dumps", "Mine reclamation and environmental control"],
        "Underground Mining": ["Underground mine development", "Room-and-pillar methods", "Longwall mining", "Ground support and strata control", "Production planning and mechanization"],
        "Mine Ventilation and Safety": ["Mine air properties and flow", "Ventilation networks and fans", "Heat, humidity and contaminant control", "Gas detection and fire prevention", "Risk assessment and emergency response"],
    },
    "BTECH_PETRO": {
        "Petroleum Geoscience": ["Sedimentary basins and petroleum systems", "Source rocks and maturation", "Reservoir rocks and petrophysics", "Traps, seals and migration", "Well logs and subsurface correlation"],
        "Drilling Engineering": ["Rig systems and well planning", "Drilling fluids and hydraulics", "Drill-string mechanics", "Casing and cementing", "Well control and drilling hazards"],
        "Reservoir Engineering": ["Porosity, permeability and saturation", "Fluid properties and phase behaviour", "Material balance concepts", "Darcy flow and well productivity", "Waterflooding and enhanced recovery"],
        "Petroleum Production Engineering": ["Well completion design", "Reservoir inflow and tubing flow", "Artificial lift methods", "Production testing and allocation", "Flow assurance and surface facilities"],
    },
    "BTECH_TEXTILE": {
        "Textile Fibre Science": ["Natural and manufactured fibres", "Polymer structure and fibre properties", "Fibre identification and testing", "Spinning preparation and fibre blends", "Sustainable and technical fibres"],
        "Yarn Manufacturing": ["Opening, cleaning and carding", "Combing and drawing", "Ring spinning", "Rotor and air-jet spinning", "Yarn count, twist and quality"],
        "Fabric Structure and Weaving": ["Yarn and fabric geometry", "Weave notation and basic weaves", "Loom mechanisms", "Knitted and nonwoven structures", "Fabric defects and structural testing"],
        "Textile Chemical Processing": ["Preparation and pretreatment", "Dye-fibre interactions", "Dyeing methods and fastness", "Printing and finishing", "Effluent management and process safety"],
    },
    "BTECH_AI_DS": {
        "Applied Statistics for Data Science": ["Probability distributions", "Sampling and estimation", "Hypothesis testing", "Regression and correlation", "Experimental design and uncertainty"],
        "Data Engineering": ["Data formats and ingestion", "Relational and NoSQL storage", "ETL and data quality", "Batch and stream processing", "Data pipeline reliability"],
        "Machine Learning Foundations": ["Supervised learning and validation", "Linear and logistic models", "Tree-based methods", "Clustering and dimensionality reduction", "Bias, variance and evaluation metrics"],
        "Data Visualization": ["Data types and visual encoding", "Exploratory plots", "Uncertainty and statistical graphics", "Interactive dashboard design", "Responsible and accessible visualization"],
    },
    "BTECH_CSE_AIML": {
        "Artificial Intelligence": ["State-space search", "Uninformed and informed search", "Constraint satisfaction", "Knowledge representation", "Planning and decision making"],
        "Machine Learning": ["Learning objectives and data splits", "Linear models and regularization", "Classification and evaluation", "Tree ensembles", "Clustering and model selection"],
        "Deep Learning": ["Neural network foundations", "Backpropagation and optimization", "Convolutional networks", "Sequence models and attention", "Regularization and deployment"],
        "Natural Language Processing": ["Text normalization and tokenization", "Language modelling", "Word and sentence representations", "Sequence tagging and classification", "Attention and transformer basics"],
    },
    "BTECH_CSE_CYBER": {
        "Computer Security": ["Threat models and security goals", "Authentication and access control", "Operating-system security", "Web application vulnerabilities", "Secure development and testing"],
        "Cryptography and Network Security": ["Symmetric encryption and modes", "Public-key cryptography", "Hashing and digital signatures", "TLS and secure channels", "Key management and protocol pitfalls"],
        "Security Operations": ["Logging and monitoring", "Indicators of compromise", "Incident response lifecycle", "Vulnerability management", "Evidence handling and reporting"],
        "Cyber Risk and Governance": ["Asset and risk identification", "Threat and likelihood analysis", "Security policies and controls", "Business continuity planning", "Privacy, compliance and ethics"],
    },
    "BTECH_VLSI": {
        "CMOS Digital Design": ["MOS transistor switching", "CMOS inverter characteristics", "Combinational logic design", "Sequential logic and timing", "Power, performance and area trade-offs"],
        "Verilog Hardware Description": ["Modules and data types", "Combinational RTL", "Sequential RTL", "Testbenches and simulation", "Synthesis-aware coding"],
        "VLSI Design Flow": ["Specification and architecture", "RTL synthesis", "Static timing analysis", "Floorplanning and placement", "Routing, verification and sign-off"],
        "Semiconductor Devices for VLSI": ["MOS capacitor and threshold voltage", "Short-channel effects", "CMOS scaling", "Process variation and leakage", "Device reliability"],
    },
    "BTECH_MECHATRONICS": {
        "Embedded Systems": ["Microcontroller architecture", "Interrupts and timers", "Peripheral interfaces", "Real-time scheduling", "Embedded system debugging"],
        "Sensors and Actuators": ["Sensor characteristics and calibration", "Position and motion sensors", "Hydraulic and pneumatic actuators", "Electric drives and motors", "Signal conditioning and noise"],
        "Mechatronic System Design": ["System requirements and block models", "Mechanical-electrical integration", "Microcontroller-based control", "Safety and fault handling", "Prototyping and validation"],
        "Industrial Automation": ["PLC architecture and ladder logic", "Industrial sensors and actuators", "SCADA fundamentals", "Industrial communication networks", "Safety interlocks and commissioning"],
    },
    "BTECH_ROBOTICS": {
        "Robot Kinematics": ["Coordinate frames and transformations", "Forward kinematics", "Inverse kinematics", "Jacobian and velocity mapping", "Manipulator singularities"],
        "Robot Dynamics and Control": ["Rigid-body motion", "Manipulator dynamic models", "Trajectory generation", "Joint-space control", "Stability and force control"],
        "Robot Perception": ["Camera models and calibration", "Image features and geometry", "Range sensing and point clouds", "Localization and mapping", "Sensor fusion and uncertainty"],
        "Autonomous Mobile Robots": ["Mobile robot kinematics", "Mapping and localization", "Path planning", "Obstacle avoidance", "Navigation and system evaluation"],
    },
    "BTECH_INSTR": {
        "Industrial Instrumentation": ["Measurement system characteristics", "Pressure, flow and level measurement", "Temperature measurement", "Calibration and uncertainty", "Industrial signal standards"],
        "Process Control": ["Process models and dynamics", "Feedback control loops", "PID tuning", "Stability and performance", "Multivariable and cascade control"],
        "Sensors and Transducers": ["Resistive and capacitive sensors", "Inductive and magnetic sensors", "Optical and thermal sensors", "Signal conditioning", "Smart sensors and calibration"],
        "Control System Design": ["Transfer-function modelling", "Transient and steady-state response", "Root-locus methods", "Frequency-response methods", "Digital control implementation"],
    },
    "BTECH_INDUSTRIAL": {
        "Operations Research": ["Linear programming formulation", "Simplex and duality", "Transportation and assignment", "Inventory and queueing models", "Project scheduling and networks"],
        "Supply Chain Systems": ["Demand forecasting", "Procurement and supplier selection", "Inventory policies", "Distribution network design", "Resilience and sustainability"],
        "Industrial Quality and Reliability": ["Statistical process control", "Capability and measurement systems", "Reliability models", "Acceptance sampling", "Root-cause and improvement methods"],
        "Work Systems and Ergonomics": ["Work study and method design", "Time standards", "Human factors and ergonomics", "Facility layout", "Safety and productivity analysis"],
    },
    "BTECH_MARINE": {
        "Marine Propulsion": ["Marine diesel engine cycles", "Propeller characteristics", "Engine-propeller matching", "Fuel and lubrication systems", "Performance and emissions"],
        "Marine Auxiliary Systems": ["Pumps and piping aboard ships", "Boilers and heat exchangers", "Refrigeration and HVAC", "Steering and hydraulic systems", "Maintenance and fault diagnosis"],
        "Naval Architecture": ["Ship geometry and hydrostatics", "Buoyancy and stability", "Resistance and powering", "Ship structures and loads", "Seakeeping fundamentals"],
        "Marine Electrical Systems": ["Shipboard power generation", "Distribution and protection", "Electric propulsion", "Control and alarm systems", "Electrical safety at sea"],
    },
    "BTECH_FOODTECH": {
        "Food Process Engineering": ["Food properties and material balances", "Heat processing and pasteurization", "Evaporation and concentration", "Drying and dehydration", "Refrigeration and cold chain"],
        "Food Microbiology and Safety": ["Foodborne microorganisms", "Microbial growth and preservation", "Hygiene and sanitation", "Hazard analysis and critical control points", "Food safety verification"],
        "Food Chemistry": ["Water and food stability", "Carbohydrates and proteins", "Lipids and oxidation", "Pigments, flavours and additives", "Chemical changes during processing"],
        "Food Quality and Packaging": ["Sensory evaluation", "Food quality measurements", "Packaging materials and properties", "Modified-atmosphere packaging", "Shelf-life and traceability"],
    },
    "BTECH_DAIRY": {
        "Dairy Chemistry": ["Milk composition and properties", "Milk proteins and casein", "Milk fat and emulsion", "Lactose and minerals", "Chemical changes during processing"],
        "Dairy Processing": ["Milk reception and clarification", "Pasteurization and sterilization", "Homogenization and separation", "Fermented dairy products", "Cleaning-in-place systems"],
        "Dairy Microbiology": ["Raw milk microbiology", "Starter cultures", "Fermentation control", "Spoilage and pathogens", "Hygiene and dairy plant sanitation"],
        "Dairy Plant Engineering": ["Heat and mass balances", "Refrigeration systems", "Pumps and hygienic piping", "Process equipment selection", "Plant layout and utilities"],
    },
    "BTECH_CERAMIC": {
        "Ceramic Materials": ["Crystal structures and bonding", "Phase diagrams", "Powders and particle-size control", "Sintering and densification", "Mechanical and thermal properties"],
        "Ceramic Processing": ["Raw material preparation", "Powder forming methods", "Drying and firing", "Glazes and surface treatments", "Defects and process control"],
        "Refractories and Glass": ["Refractory classes and properties", "Slag and corrosion resistance", "Glass forming and annealing", "Thermal shock behaviour", "Applications in high-temperature processes"],
        "Advanced Ceramics": ["Structural ceramic applications", "Electrical and electronic ceramics", "Bioceramics", "Ceramic composites", "Characterization and failure analysis"],
    },
    "BTECH_POLYMER": {
        "Polymer Science": ["Polymer structure and molecular weight", "Polymerization mechanisms", "Crystallinity and thermal transitions", "Viscoelasticity and rheology", "Structure-property relationships"],
        "Polymer Processing": ["Extrusion and die flow", "Injection moulding", "Blow moulding and thermoforming", "Compression and transfer moulding", "Process defects and troubleshooting"],
        "Polymer Materials and Testing": ["Thermoplastics and thermosets", "Elastomers and blends", "Mechanical and thermal testing", "Degradation and stabilization", "Recycling and circular design"],
        "Composite Materials": ["Fibre and matrix selection", "Laminate mechanics", "Manufacturing processes", "Interface and failure modes", "Testing and applications"],
    },
    "BTECH_ENERGY": {
        "Energy Conversion Systems": ["Thermal power cycles", "Combustion and boiler systems", "Gas turbines and combined cycles", "Cogeneration and efficiency", "Energy auditing and balances"],
        "Renewable Energy Systems": ["Solar resource and photovoltaic systems", "Solar thermal conversion", "Wind energy conversion", "Bioenergy systems", "Grid integration and storage"],
        "Energy Storage and Power Systems": ["Battery chemistry and performance", "Fuel cells and hydrogen", "Thermal energy storage", "Power electronics for renewables", "Microgrids and dispatch"],
        "Energy Policy and Sustainability": ["Energy demand and supply", "Efficiency metrics and auditing", "Life-cycle assessment", "Emissions and decarbonization", "Energy economics and policy"],
    },
    "BTECH_GEO": {
        "Geospatial Data and GIS": ["Coordinate systems and projections", "Spatial data models", "GIS analysis and overlays", "Cartography and map design", "Accuracy and metadata"],
        "Remote Sensing": ["Electromagnetic spectrum and sensors", "Image acquisition and resolution", "Image enhancement and classification", "Change detection", "Applications and validation"],
        "Surveying and GNSS": ["Control networks and error adjustment", "GNSS positioning principles", "Total station and field workflows", "Photogrammetry fundamentals", "Survey data quality"],
        "Spatial Analysis": ["Raster and vector operations", "Terrain and hydrologic analysis", "Network analysis", "Spatial statistics", "Geospatial project design and ethics"],
    },
    "BCA": {
        "Discrete Mathematics for Computing": ["Logic and propositions", "Sets, relations and functions", "Counting and recurrence relations", "Graphs and trees", "Boolean algebra"],
        "Computer Organization": ["Number systems and data representation", "Boolean logic and combinational circuits", "Sequential circuits and registers", "CPU organization and instruction cycles", "Memory hierarchy and input-output"],
        "Web Programming": ["HTML document structure and accessibility", "CSS layout and responsive design", "JavaScript fundamentals and DOM", "Server-side requests and APIs", "Web forms, validation and security"],
        "Database Application Development": ["Relational modelling and keys", "SQL queries and constraints", "Normalization and transactions", "Application-to-database connectivity", "Access control and backup fundamentals"],
        "Software Project and Testing": ["Problem definition and requirements", "Use cases and design models", "Version control and collaboration", "Unit and integration testing", "Deployment, maintenance and documentation"],
    },
}

# The core Engineering Science foundation is shared across all engineering
# branches; course codes are stable so a student can change tracks safely.
TRACKS = [row["track_id"] for row in csv.DictReader((ROOT / "curriculum_tracks.csv").open(encoding="utf-8-sig"))]
ALL_BTECH = [track for track in TRACKS if track.startswith("BTECH_")]
TRACK_PARENTS = {}
for row in csv.DictReader((ROOT / "curriculum_track_parents.csv").open(encoding="utf-8-sig")):
    TRACK_PARENTS.setdefault(row["track_id"], []).append(row["parent_track_id"])

def main():
    rows = []
    for title, topics in COMMON_BTECH.items():
        code = {"Engineering Mathematics I":"ENGMATH1", "Engineering Physics":"ENGPHY1", "Engineering Chemistry":"ENGCHEM1", "Programming for Problem Solving":"ENGPROG", "Basic Electrical Engineering":"BASICEE", "Engineering Graphics":"ENGGRAPH", "Engineering Mechanics":"ENGMECH", "Communication and Technical Writing":"TECHCOMM"}[title]
        for track in ALL_BTECH:
            rows.append({"course_code": code, "course_name": title, "category": "Engineering Foundation", "track_id": track, "topics": "|".join(topics)})
    for track, subjects in TRACK_SUBJECTS.items():
        for index, (title, topics) in enumerate(subjects.items(), 1):
            prefix = track.removeprefix("BTECH_")
            code = f"{prefix}{index:02d}"
            rows.append({"course_code": code, "course_name": title, "category": track.replace("BTECH_", "").replace("_", " "), "track_id": track, "topics": "|".join(topics)})
    by_track = {}
    for row in rows:
        by_track.setdefault(row["track_id"], []).append(row)
    for child, parents in TRACK_PARENTS.items():
        existing = {row["course_code"] for row in by_track.get(child, [])}
        for parent in parents:
            for row in by_track.get(parent, []):
                if row["course_code"] in existing:
                    continue
                rows.append({**row, "track_id": child})
                existing.add(row["course_code"])
    path = ROOT / "branch_curriculum.csv"
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["course_code", "course_name", "category", "track_id", "topics"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} track-course rows to {path.name}")

if __name__ == "__main__":
    main()
