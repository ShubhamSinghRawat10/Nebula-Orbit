"""Original short diagnostic quizzes for Nebula's demo curriculum.

These are baseline checks, not a replacement for a complete course question bank.
Question wording and distractors are authored for Nebula.
"""
from datetime import datetime, timezone


TOPIC_AREAS = [
    "Fundamentals & Core Concepts",
    "Architecture & Principles",
    "Primary Protocols & Operations",
    "Data Structures & Types",
    "Algorithms & Control Logic",
    "Implementation & Syntax",
    "Optimization & Performance",
    "Error Handling & Debugging",
]


def _question(prompt, options, answer, explanation, topic_index):
    return {
        "prompt": prompt,
        "options": options,
        "answer_index": answer,
        "explanation": explanation,
        "topic_index": topic_index,
    }


def _quiz(course_id, course_name, questions):
    built_questions = []
    for item in questions:
        question = {key: value for key, value in item.items() if key != "topic_index"}
        question["topic"] = f"{course_name} - {TOPIC_AREAS[item['topic_index']]}"
        built_questions.append(question)
    return {
        "title": f"{course_name} baseline diagnostic",
        "course_id": course_id,
        "source": "nebula_starter",
        "topic": f"{course_name} - Fundamentals & Core Concepts",
        "difficulty": "mixed",
        "published": True,
        "created_at": datetime.now(timezone.utc),
        "questions": built_questions,
    }


def starter_quizzes():
    """Return starter quizzes for courses without an existing seed diagnostic."""
    q = _question
    quizzes = [
        _quiz("CN", "Computer Networks", [
            q("Which layer is responsible for routing packets between networks?", ["Application", "Network", "Session", "Presentation"], 1, "The network layer handles logical addressing and routing.", 0),
            q("What is a key difference between TCP and UDP?", ["TCP is connection-oriented; UDP is connectionless", "UDP guarantees delivery; TCP does not", "TCP is only for local networks", "UDP always encrypts traffic"], 0, "TCP establishes a connection and provides ordered, reliable delivery; UDP does not guarantee those properties.", 1),
            q("What does DNS primarily do?", ["Assigns MAC addresses", "Maps domain names to IP addresses", "Encrypts every web page", "Chooses Wi-Fi channels"], 1, "DNS resolves human-readable host names to network records such as IP addresses.", 2),
            q("Which device commonly forwards frames using MAC addresses?", ["Ethernet switch", "Web server", "DNS resolver", "Load balancer only"], 0, "A layer-2 switch learns MAC addresses and forwards Ethernet frames within a LAN.", 3),
            q("If a packet's TTL reaches zero, what should a router do?", ["Forward it forever", "Discard it", "Convert it to TCP", "Store it in DNS"], 1, "Routers decrement TTL; when it reaches zero, the packet is discarded to prevent routing loops.", 4),
        ]),
        _quiz("OOPS", "Object-Oriented Programming", [
            q("What is encapsulation in object-oriented programming?", ["Bundling state with methods and controlling access", "Copying a class into a database", "Running many programs at once", "Sorting object fields alphabetically"], 0, "Encapsulation groups data and behavior while exposing a controlled interface.", 0),
            q("What does inheritance allow a class to do?", ["Reuse or extend behavior from another class", "Encrypt all of its fields", "Run without an object or function", "Prevent every method from changing state"], 0, "A derived class can reuse and specialize behavior from a base class.", 1),
            q("What is polymorphism commonly used for?", ["One interface supporting different implementations", "Making every variable global", "Removing all method calls", "Converting source code to machine code"], 0, "Polymorphism lets callers use a shared interface while runtime objects provide different behavior.", 2),
            q("Which access design best protects an object's internal state?", ["Expose fields publicly and allow unchecked writes", "Keep fields private and provide validated methods", "Store fields in comments", "Duplicate the fields in every subclass"], 1, "Controlled methods can validate changes and preserve object invariants.", 3),
            q("When is composition often preferable to deep inheritance?", ["When behavior should be assembled from replaceable collaborators", "When a program has no objects", "When every class must share one constructor", "When method names must be unique globally"], 0, "Composition connects objects through contained collaborators and often keeps designs more flexible.", 4),
        ]),
        _quiz("DBMS", "Database Management Systems", [
            q("What does a primary key identify?", ["A row uniquely within a table", "A database server's password", "A query plan only", "Every column with the same value"], 0, "A primary key uniquely identifies each row in its table.", 0),
            q("What is the purpose of a foreign key?", ["To link a row to a referenced key in another or the same table", "To encrypt a table", "To order query results", "To create a backup automatically"], 0, "A foreign key represents a relationship and can enforce referential integrity.", 1),
            q("Which SQL clause filters grouped results after aggregation?", ["WHERE", "HAVING", "ORDER BY", "VALUES"], 1, "HAVING filters groups after GROUP BY; WHERE filters rows before aggregation.", 2),
            q("Which ACID property means a transaction is all-or-nothing?", ["Atomicity", "Consistency", "Isolation", "Durability"], 0, "Atomicity prevents a transaction from being only partially applied.", 3),
            q("Why normalize a relational schema?", ["To reduce avoidable duplication and update anomalies", "To make all columns contain the same value", "To remove every relationship", "To prevent SELECT queries"], 0, "Normalization organizes dependencies to reduce duplication and common anomalies.", 4),
        ]),
        _quiz("OS", "Operating Systems", [
            q("What is a process?", ["A program in execution with its own execution state", "A folder of source files", "A CPU instruction only", "A network cable"], 0, "A process is a running program together with its resources and state.", 0),
            q("How do threads in the same process typically differ from separate processes?", ["Threads usually share the process address space", "Threads always have separate physical computers", "Processes cannot run concurrently", "Threads do not need a stack"], 0, "Threads share process resources such as address space, while each has its own execution context.", 1),
            q("What is a context switch?", ["Saving one execution state and restoring another", "Formatting a disk", "Changing a source file extension", "Translating a URL to an IP address"], 0, "The OS switches the CPU from one process or thread to another by saving and restoring state.", 2),
            q("What does virtual memory provide to a process?", ["An address space abstraction backed by memory and storage", "A guarantee that RAM is unlimited", "A replacement for the CPU cache", "A method for naming files"], 0, "Virtual memory gives processes an address-space abstraction and maps pages to physical memory or backing storage.", 3),
            q("Which condition is necessary for deadlock?", ["Circular wait", "Infinite disk capacity", "A single user account", "Every resource being shareable"], 0, "Circular wait is one of the classic necessary Coffman conditions for deadlock.", 4),
        ]),
        _quiz("AI", "Artificial Intelligence & ML", [
            q("In supervised learning, training examples usually include what?", ["Inputs paired with target labels or values", "Only unlabeled images", "Only a list of model names", "No observations"], 0, "Supervised models learn from examples paired with expected outputs.", 0),
            q("What is overfitting?", ["A model fits training details but generalizes poorly", "A model has no parameters", "A dataset has no missing values", "A prediction is always correct"], 0, "An overfit model captures noise or training-specific patterns and performs worse on unseen data.", 1),
            q("Why keep a test set separate from model training?", ["To estimate performance on data not used to fit the model", "To increase the number of training labels", "To make every model score 100%", "To remove the need for validation"], 0, "A held-out test set offers a less biased estimate of generalization than training data.", 2),
            q("For a binary classifier, what does a confusion matrix summarize?", ["Counts of correct and incorrect predictions by class", "The source-code line count", "The dataset's storage format", "The order of gradient updates"], 0, "It compares predicted and actual classes, including true and false positives and negatives.", 3),
            q("What is gradient descent used for in many models?", ["Adjusting parameters to reduce a loss function", "Sorting the test set", "Encrypting training labels", "Selecting a file path"], 0, "Gradient descent updates parameters in a direction that reduces the objective or loss.", 4),
        ]),
        _quiz("SE", "Software Engineering", [
            q("What is the main purpose of a software requirements specification?", ["Describe expected behavior and constraints", "Replace all source code", "Store compiled binaries only", "Measure CPU temperature"], 0, "Requirements capture what a system should do and the constraints it must satisfy.", 0),
            q("What does a unit test usually check?", ["A small unit of code in isolation", "The entire organization chart", "Network cabling quality", "A production database backup only"], 0, "Unit tests focus on small code units such as functions or methods.", 1),
            q("What is continuous integration intended to encourage?", ["Frequent integration with automated build and checks", "One large merge at the end of a year", "Manual copying of binaries", "Avoiding version control"], 0, "CI integrates changes frequently and runs automated validation to catch issues early.", 2),
            q("In a version-control system, what is a commit?", ["A recorded change set in repository history", "A database index", "A network handshake", "A user-interface animation"], 0, "A commit records a snapshot of changes and metadata in version history.", 3),
            q("What is the purpose of code review?", ["Find issues and improve maintainability before or after integration", "Guarantee that software has no bugs", "Replace all automated testing", "Prevent developers from discussing design"], 0, "Review can catch defects and improve clarity, though it cannot guarantee bug-free software.", 4),
        ]),
        _quiz("WT", "Web Technologies", [
            q("What does HTML primarily describe?", ["The structure and meaning of web content", "The database transaction log", "The router's forwarding table", "A machine-learning loss function"], 0, "HTML marks up document structure and semantics.", 0),
            q("What is CSS primarily used for?", ["Styling and layout", "Server-side authentication by itself", "DNS resolution", "Persisting passwords"], 0, "CSS controls presentation, layout, and responsive visual behavior.", 1),
            q("Which HTTP method is commonly used to retrieve a resource?", ["GET", "PATCH", "DELETE", "CONNECT"], 0, "GET requests a representation of a resource and is intended to be safe.", 2),
            q("Which JavaScript value represents an explicitly absent object property result?", ["undefined", "NaN only", "Infinity", "document"], 0, "Reading a missing object property typically evaluates to undefined.", 3),
            q("What does responsive web design aim to do?", ["Adapt layouts to different screens and input contexts", "Force every page to have one fixed width", "Disable CSS on phones", "Replace HTML with images"], 0, "Responsive layouts adapt to viewport size and device capabilities.", 4),
        ]),
        _quiz("CD", "Compiler Design", [
            q("What is the usual role of a lexical analyzer?", ["Convert character sequences into tokens", "Schedule operating-system processes", "Allocate IP addresses", "Execute database joins"], 0, "Lexical analysis groups characters into tokens such as identifiers and operators.", 0),
            q("What does a parser check?", ["Whether tokens fit a grammar and form a syntax structure", "Whether a network cable is connected", "Whether a disk is full", "Whether a model is overfit"], 0, "A parser checks grammatical structure and commonly builds a parse tree or AST.", 1),
            q("What does semantic analysis commonly verify?", ["Meaning-related rules such as types and declarations", "Pixel color on a monitor", "Packet transmission delay", "File compression ratio"], 0, "Semantic analysis checks rules beyond grammar, including types and symbol use.", 2),
            q("What is a symbol table used for in a compiler?", ["Tracking identifiers and associated information", "Storing network packets", "Drawing the user interface", "Sorting machine instructions by color"], 0, "A symbol table tracks names and information such as scope, type, or storage.", 3),
            q("What is a common goal of compiler optimization?", ["Improve execution or resource use while preserving program behavior", "Change the program's intended result", "Remove all error checks", "Make source code longer"], 0, "Valid optimizations improve performance or resource use without changing observable semantics.", 4),
        ]),
        _quiz("COA", "Computer Organization & Architecture", [
            q("Which CPU component performs arithmetic and logical operations?", ["ALU", "Control bus", "Hard drive", "Network interface"], 0, "The arithmetic logic unit performs arithmetic and Boolean operations.", 0),
            q("Why is cache memory placed close to the CPU?", ["To reduce average access time for frequently used data", "To permanently store every file", "To replace all registers", "To increase network bandwidth"], 0, "Caches exploit locality to serve frequently or recently used data faster than main memory.", 1),
            q("What is the program counter used for?", ["Holding the address of the next instruction", "Counting user accounts", "Storing a database password", "Measuring cache temperature"], 0, "The program counter identifies the next instruction to fetch or execute.", 2),
            q("What does an instruction set architecture define?", ["The machine-visible instructions and programmer-visible behavior", "Only the computer case dimensions", "The office network policy", "A programming language's indentation style"], 0, "An ISA specifies the instructions, registers, and behavior visible to software.", 3),
            q("What is a pipeline hazard?", ["A condition that can prevent an instruction from executing in its planned cycle", "A type of database key", "A secure password format", "A file-system directory"], 0, "Data, control, or structural hazards can disrupt ideal pipelined execution.", 4),
        ]),
        _quiz("CC", "Cloud Computing", [
            q("Which cloud service model provides virtual machines and storage primitives?", ["IaaS", "SaaS", "On-premises only", "DNSaaS"], 0, "Infrastructure as a Service offers configurable compute, storage, and networking resources.", 0),
            q("What is a key feature of a managed PaaS offering?", ["The provider manages much of the runtime and platform infrastructure", "The customer must manufacture servers", "It can only deliver spreadsheets", "It removes the need for application code"], 0, "PaaS provides a managed platform so teams can focus more on application code.", 1),
            q("What does horizontal scaling generally mean?", ["Adding more instances or nodes", "Increasing only one CPU's clock speed", "Deleting replicas", "Compressing source code"], 0, "Horizontal scaling adds machines or instances to share load.", 2),
            q("Why deploy across multiple availability zones?", ["To improve resilience to a zone-level failure", "To guarantee zero software bugs", "To avoid using networks", "To make passwords public"], 0, "Separate zones can reduce the impact of a localized infrastructure failure.", 3),
            q("What is a cloud object store best suited for?", ["Durable storage of blobs addressed by keys", "Executing CPU instructions", "Replacing all relational queries", "Allocating thread stacks"], 0, "Object storage keeps data objects with metadata and key-based access.", 4),
        ]),
        _quiz("TOC", "Theory of Computation", [
            q("What does a finite automaton do?", ["Recognizes patterns in strings using a finite set of states", "Stores unlimited external memory", "Compiles a database schema", "Encrypts network packets"], 0, "Finite automata process input strings through a finite state machine.", 0),
            q("What language class is recognized by deterministic finite automata?", ["Regular languages", "Only context-sensitive languages", "All undecidable languages", "Only natural-language sentences"], 0, "DFAs recognize exactly the regular languages.", 1),
            q("What is a context-free grammar commonly used to describe?", ["Nested syntactic structures", "IP routing tables", "CPU cache replacement only", "Pixel formats"], 0, "Context-free grammars can describe nested structures such as many programming-language constructs.", 2),
            q("What is the key theoretical resource of a standard Turing machine?", ["An unbounded tape with a finite control", "Infinite parallel CPUs", "A network connection", "A relational table"], 0, "A Turing machine has finite control and an unbounded tape used as memory.", 3),
            q("What does it mean for a language to be decidable?", ["Some algorithm halts on every input and answers membership correctly", "Every input is accepted", "No program can recognize it", "It contains only finite strings"], 0, "A decider always halts and correctly determines whether an input belongs to the language.", 4),
        ]),
        _quiz("C", "C Programming & Problem Solving", [
            q("What does a pointer store in C?", ["A memory address", "A guaranteed string", "A loop condition only", "A floating-point format"], 0, "A pointer value refers to an object's memory location or is null.", 0),
            q("What is the relationship between an array name and its elements in most C expressions?", ["It often converts to a pointer to its first element", "It is always a complete copy of every element", "It is a function call", "It can only hold characters"], 0, "In many expressions an array converts to a pointer to its first element, with important exceptions such as sizeof.", 1),
            q("Which format specifier is commonly used with printf for an int?", ["%d", "%s", "%p", "%f"], 0, "%d is commonly used for an int in printf.", 2),
            q("What does a function prototype provide?", ["A declaration of a function's name, return type, and parameter types", "A copy of the function's runtime output", "A memory allocator", "A file permission"], 0, "A prototype lets the compiler check calls against the function signature.", 3),
            q("What must a loop condition eventually do to avoid an unintended infinite loop?", ["Become false or otherwise exit the loop", "Remain true forever", "Allocate memory on every iteration", "Change the function return type"], 0, "A terminating loop needs a path to its exit condition or an explicit break.", 4),
        ]),
        _quiz("CPP", "Advanced C++ Programming", [
            q("When is a C++ constructor called?", ["When an object is initialized", "Only when a program exits", "Whenever a header is included", "Only after a network request"], 0, "Constructors initialize objects as their lifetime begins.", 0),
            q("What is RAII intended to connect?", ["Resource lifetime with object lifetime", "Network addresses with class names", "Comments with compiler warnings", "Inheritance with database tables"], 0, "RAII acquires resources during object construction and releases them during destruction.", 1),
            q("Why declare a base-class destructor virtual when deleting derived objects through a base pointer?", ["So the derived destructor is called correctly", "So the object becomes immutable", "So constructors are skipped", "So the pointer becomes a reference"], 0, "A virtual destructor ensures destruction dispatches through the dynamic type.", 2),
            q("What does std::unique_ptr express?", ["Exclusive ownership of a dynamically managed object", "Shared ownership by every thread", "A raw integer address only", "A database transaction"], 0, "unique_ptr provides single-owner semantics and releases the managed object automatically.", 3),
            q("What is the typical purpose of move semantics?", ["Transfer resources from an object instead of copying them", "Sort objects by memory address", "Make every function virtual", "Prevent objects from being destroyed"], 0, "Move operations can transfer owned resources efficiently when the source can be left valid but unspecified.", 4),
        ]),
        _quiz("JAVA", "Java Application Development", [
            q("What does the Java Virtual Machine execute?", ["Java bytecode", "HTML markup only", "SQL tables directly", "Python indentation"], 0, "The JVM executes bytecode and provides runtime services.", 0),
            q("What does an interface primarily define?", ["A contract of operations that implementing types provide", "A physical network adapter", "A database backup schedule", "An operating-system process"], 0, "An interface describes behavior that implementing classes agree to provide.", 1),
            q("What is the purpose of a try-catch block?", ["Handle exceptions that may be thrown during execution", "Create an object without a constructor", "Compile source without a JVM", "Sort a collection automatically"], 0, "try-catch lets code respond to exceptions rather than allowing them to propagate unchecked.", 2),
            q("Which Java collection interface represents an ordered sequence that may contain duplicates?", ["List", "Set", "Map", "Queue only"], 0, "List represents an ordered collection and generally permits duplicates.", 3),
            q("Why should equals and hashCode be consistent for hash-based collections?", ["Equal objects must produce the same hash code", "Hash codes must be unique for every object", "equals must always return false", "Collections ignore both methods"], 0, "Hash-based collections use hashCode to find buckets and equals to compare keys; equal objects need equal hash codes.", 4),
        ]),
        _quiz("CS", "Cyber Security & Cryptography", [
            q("Which CIA property concerns preventing unauthorized changes?", ["Integrity", "Availability", "Confidentiality", "Latency"], 0, "Integrity protects information from unauthorized or improper modification.", 0),
            q("How does hashing differ from encryption?", ["Hashing is generally one-way; encryption is designed to be reversible with a key", "Hashing always needs two keys", "Encryption cannot protect data", "They are identical operations"], 0, "Cryptographic hashes are one-way digests; encryption supports decryption with the appropriate key.", 1),
            q("What does multi-factor authentication require?", ["More than one distinct factor category", "Two passwords from the same password manager", "A public username only", "A longer email address"], 0, "MFA combines categories such as something known, possessed, or inherent.", 2),
            q("What is SQL injection?", ["Untrusted input changes the structure of a database query", "A database backup process", "A safe way to store passwords", "A network cable fault"], 0, "SQL injection occurs when untrusted input is interpreted as part of SQL syntax.", 3),
            q("What is the principle of least privilege?", ["Grant only the access needed for a task", "Give every user administrator access", "Disable all authentication", "Share one account across a team"], 0, "Least privilege limits permissions to what a role or task needs.", 4),
        ]),
        _quiz("BD", "Big Data Analytics", [
            q("Which characteristic is commonly associated with big data's 'volume'?", ["The amount of data", "The number of user passwords", "The shape of a chart", "The programming language used"], 0, "Volume describes the scale or amount of data.", 0),
            q("Why partition data across a distributed system?", ["To divide storage and work across nodes", "To guarantee all nodes never fail", "To remove the need for schemas", "To encrypt data automatically"], 0, "Partitioning distributes data so storage and processing can scale across machines.", 1),
            q("In MapReduce, what does the reduce phase commonly do?", ["Aggregate or combine values grouped by key", "Draw a user interface", "Assign MAC addresses", "Compile source code"], 0, "Reducers combine values associated with the same intermediate key.", 2),
            q("What does a data lake commonly store?", ["Large collections of raw and processed data in varied formats", "Only compiled applications", "Only relational indexes", "Only network packets"], 0, "Data lakes retain data in multiple formats for later processing and analysis.", 3),
            q("Why use a distributed processing framework?", ["To process large workloads in parallel across machines", "To avoid all data movement", "To force every task onto one core", "To replace data validation"], 0, "Distributed frameworks divide work and coordinate parallel computation across nodes.", 4),
        ]),
        _quiz("DE", "Digital Electronics & Logic Design", [
            q("What is the output of an AND gate when one input is 0?", ["0", "1", "It toggles", "Undefined in all cases"], 0, "An AND gate outputs 1 only when all inputs are 1.", 0),
            q("What is a combinational circuit's output based on?", ["Current inputs", "Inputs from exactly one day ago", "A hidden operating system", "Network latency"], 0, "A combinational circuit has no stored state; its outputs depend on current inputs.", 1),
            q("What does a multiplexer do?", ["Selects one of several inputs to pass to an output", "Stores a bit permanently without power", "Adds decimal numbers only", "Converts source code to tokens"], 0, "A multiplexer uses select lines to route one chosen input to its output.", 2),
            q("What is the main difference between a latch and an edge-triggered flip-flop?", ["A latch is level-sensitive; a flip-flop responds to a clock edge", "A latch stores no state", "A flip-flop has no inputs", "They are both combinational gates"], 0, "Latches respond during an enable level, whereas edge-triggered flip-flops sample on a clock edge.", 3),
            q("What does a Karnaugh map help simplify?", ["Boolean expressions", "Network routing tables", "Database joins", "Machine-learning feature names"], 0, "Karnaugh maps group adjacent minterms to reduce Boolean logic.", 4),
        ]),
        _quiz("MP", "Microprocessors & Interfacing", [
            q("What is an interrupt used for?", ["Notify the processor that an event needs attention", "Increase a register's physical size", "Store a web page", "Replace the instruction set"], 0, "An interrupt requests processor attention for an event or service.", 0),
            q("What is memory-mapped I/O?", ["Treating device registers as locations in the memory address space", "Copying all memory into a printer", "Using a keyboard as RAM", "Storing code only in cache"], 0, "Memory-mapped I/O assigns device registers addresses accessible through memory operations.", 1),
            q("What is the role of a program counter in a microprocessor?", ["Identify the next instruction address", "Store every I/O device's data", "Count the number of users", "Encrypt the instruction stream"], 0, "The program counter holds the address used for the next instruction fetch.", 2),
            q("What does a stack pointer typically track?", ["The current top of a stack in memory", "The current network route", "The CPU's clock frequency", "The number of source files"], 0, "The stack pointer refers to the active stack position used for calls, returns, and temporary data.", 3),
            q("Why can interrupt priority be useful?", ["It helps decide which event is serviced first", "It makes all events simultaneous", "It removes the need for an interrupt handler", "It converts interrupts into memory"], 0, "Priority lets a processor distinguish urgent events from less urgent ones.", 4),
        ]),
        _quiz("DL", "Deep Learning & Neural Networks", [
            q("What is an activation function used for in a neural network?", ["Introduce nonlinearity between learned transformations", "Sort the training examples", "Store the labels outside the model", "Replace all weights with zeros"], 0, "Nonlinear activations allow networks to represent more than a single linear transformation.", 0),
            q("What does backpropagation compute?", ["Gradients of a loss with respect to model parameters", "A sorted list of labels", "An encryption key", "A database index"], 0, "Backpropagation applies the chain rule to compute parameter gradients.", 1),
            q("What is a common role of convolutional layers?", ["Learn local spatial patterns using shared filters", "Translate every word into a token", "Guarantee a model cannot overfit", "Store files across a cluster"], 0, "Convolutions apply shared filters to capture local structure in data such as images.", 2),
            q("What does dropout do during training?", ["Randomly disable some activations to regularize the model", "Delete the training dataset", "Add labels to unlabeled examples", "Sort each layer by weight"], 0, "Dropout randomly masks activations during training to reduce reliance on particular units.", 3),
            q("Why normalize inputs for neural-network training?", ["It can improve numerical conditioning and make optimization easier", "It guarantees perfect accuracy", "It removes the need for labels", "It prevents gradient computation"], 0, "Well-scaled inputs often help optimization behave more consistently, though normalization does not guarantee accuracy.", 4),
        ]),
        _quiz("NLP", "Natural Language Processing", [
            q("What is tokenization?", ["Splitting text into units such as words or subwords", "Encrypting a document", "Sorting sentences by length", "Translating a model into hardware"], 0, "Tokenization converts text into units a model or pipeline can process.", 0),
            q("What does stemming attempt to do?", ["Reduce related word forms to a common stem", "Find a sentence's author", "Translate text into binary", "Measure network throughput"], 0, "Stemming heuristically strips affixes to group related word forms.", 1),
            q("What does TF-IDF help represent?", ["How important a term is in a document relative to a collection", "The order of CPU instructions", "The encryption strength of a key", "The size of a neural layer"], 0, "TF-IDF weights terms by local frequency and how uncommon they are across documents.", 2),
            q("What is a word embedding?", ["A learned vector representation of a token", "A database backup", "A grammar rule only", "A network address"], 0, "Embeddings map tokens to vectors that can encode useful similarity patterns.", 3),
            q("What does attention let a sequence model do?", ["Weight different context positions when forming a representation", "Ignore all input tokens", "Sort words alphabetically", "Replace training with encryption"], 0, "Attention computes context-dependent weights over other positions or elements.", 4),
        ]),
        _quiz("DEVOPS", "DevOps & CI/CD Pipelines", [
            q("What is continuous delivery intended to make routine?", ["Keeping changes in a releasable state through automated checks", "Releasing every untested change", "Avoiding version control", "Manually copying code between servers"], 0, "Continuous delivery automates the path to a releasable artifact; production release may remain a human decision.", 0),
            q("What is a container image?", ["A packaged filesystem and metadata used to create containers", "A screenshot of a server", "A live CPU thread", "A database query"], 0, "An image packages application files and metadata from which containers can be created.", 1),
            q("What does infrastructure as code provide?", ["Versioned, repeatable definitions of infrastructure", "A guarantee that servers never fail", "A replacement for application tests", "A way to store passwords in source code"], 0, "IaC describes infrastructure declaratively or procedurally so it can be reviewed and reproduced.", 2),
            q("Why use automated deployment checks?", ["Catch configuration or release problems consistently", "Make rollback impossible", "Remove the need for monitoring", "Increase code duplication"], 0, "Automated checks make common deployment validations repeatable and fast.", 3),
            q("What is a blue-green deployment?", ["Switching traffic between two production-like environments", "Compiling code in two languages", "A database color scheme", "Running without a rollback option"], 0, "Blue-green deployments use parallel environments and switch traffic between them.", 4),
        ]),
        _quiz("BC", "Blockchain & Distributed Ledgers", [
            q("What does a cryptographic hash contribute to a linked block structure?", ["A compact digest that helps detect changes", "A guarantee that all transactions are true", "A private key shared with every user", "A replacement for consensus"], 0, "Block hashes link history and make modifications detectable; they do not prove every claim is true.", 0),
            q("What is consensus used for in a distributed ledger?", ["Agreeing on an accepted ordering or state among participants", "Choosing a website's font", "Compressing every transaction", "Creating unlimited storage"], 0, "Consensus mechanisms help distributed participants agree on ledger state or ordering.", 1),
            q("What does a private key allow its holder to do in a digital-signature system?", ["Create signatures that can be verified with the corresponding public key", "Reveal every other user's private key", "Reverse a cryptographic hash", "Guarantee a transaction is legal"], 0, "A private key signs data; a corresponding public key can verify the signature.", 2),
            q("What is a smart contract?", ["Code executed under the rules of a blockchain platform", "A legally complete paper contract by itself", "A secure password vault", "A physical network switch"], 0, "A smart contract is program code deployed to and executed by a blockchain environment.", 3),
            q("Why are blockchains often described as append-oriented ledgers?", ["New records extend history instead of silently rewriting prior entries", "Old records can never be challenged", "Every participant has administrator access", "They do not use data structures"], 0, "Many ledgers append new entries and use cryptographic links to make past changes detectable.", 4),
        ]),
        _quiz("DGA", "Design & Analysis of Algorithms", [
            q("What does Big-O notation commonly describe?", ["An asymptotic upper bound on growth", "The exact runtime in milliseconds on every computer", "The memory address of a function", "The number of comments in code"], 0, "Big-O describes an asymptotic upper bound, abstracting away constant factors.", 0),
            q("What precondition does binary search require for a conventional sorted-array search?", ["The data is ordered by the searched key", "The array has no integers", "Every item is unique", "The array length is prime"], 0, "Binary search discards half the range based on order, so the collection must be sorted consistently.", 1),
            q("What is the time complexity of merge sort in its standard form?", ["O(n log n)", "O(1)", "O(log n) for all inputs", "O(n³)"], 0, "Merge sort divides the input recursively and merges in linear work per level, giving O(n log n).", 2),
            q("When is dynamic programming especially useful?", ["When subproblems overlap and have useful optimal substructure", "When every input is already sorted", "When no state can be stored", "When an algorithm must use no recursion or iteration"], 0, "Dynamic programming reuses solutions to overlapping subproblems when the problem has suitable structure.", 3),
            q("What is the greedy-choice property?", ["A locally optimal choice can be part of a globally optimal solution", "Every local choice is always wrong", "The algorithm must randomly choose", "The algorithm cannot compare options"], 0, "Greedy algorithms are valid for problems where a locally optimal choice leads to a global optimum.", 4),
    ])
    ]

    additional_questions = {
        "CN": [
            ("Which protocol securely provides web communication over TLS?", ["HTTPS", "ARP", "ICMP", "DHCP"], 0, "HTTPS is HTTP carried over a TLS-protected connection.", 5),
            ("What is the main purpose of DHCP on a typical local network?", ["Assign network configuration such as IP addresses", "Resolve source code symbols", "Encrypt files on disk", "Route between every autonomous system"], 0, "DHCP can automatically provide clients with address and network configuration.", 6),
            ("What does packet loss usually mean?", ["One or more packets failed to reach the destination", "A domain name changed spelling", "A switch learned a MAC address", "A host gained a second CPU"], 0, "Packet loss is the failure of transmitted packets to arrive at their destination.", 7),
        ],
        "OOPS": [
            ("What is method overriding?", ["A subclass provides its own implementation of an inherited method", "A method changes the source file name", "A field becomes a constructor", "An object deletes its class"], 0, "Overriding specializes an inherited method using a compatible signature.", 5),
            ("What is an object's state usually represented by?", ["The values of its fields at a point in time", "The number of comments in its class", "The order of files on disk", "Its display color only"], 0, "An object's fields capture data that can change over its lifetime.", 6),
            ("Why should a class validate input in methods that change its state?", ["To preserve its invariants", "To make every field global", "To disable polymorphism", "To force all objects to share memory"], 0, "Validation helps prevent objects from entering invalid states.", 7),
        ],
        "DBMS": [
            ("What does an INNER JOIN return?", ["Rows with matching join keys in both inputs", "Every possible row pair", "Only rows with NULL keys", "The database schema definition"], 0, "An inner join keeps rows satisfying the join condition in both relations.", 5),
            ("What is an index generally used for?", ["Speeding up selected data lookups", "Replacing every table constraint", "Encrypting database backups", "Guaranteeing a query never uses memory"], 0, "Indexes can accelerate reads for selected access patterns, with storage and write costs.", 6),
            ("Why use a transaction for several related updates?", ["To commit them together or roll them back on failure", "To sort table names", "To avoid all locking", "To permanently disable constraints"], 0, "Transactions provide a controlled unit of work with commit and rollback behavior.", 7),
        ],
        "OS": [
            ("What does a counting semaphore represent?", ["A counter used to coordinate access to a limited number of resources", "A file extension", "A CPU instruction address", "A network name server"], 0, "A counting semaphore tracks available permits for a resource pool.", 5),
            ("What is a page fault?", ["A reference to a virtual-memory page that is not currently mapped in RAM", "A syntax error in a program", "A damaged monitor pixel", "A missed network packet"], 0, "A page fault occurs when memory access requires OS handling because the page is not currently resident or valid.", 6),
            ("What is one way to reduce race conditions?", ["Protect shared state with suitable synchronization", "Increase variable name length", "Remove all tests", "Run the same thread twice"], 0, "Locks or other synchronization primitives can serialize unsafe shared-state access.", 7),
        ],
        "AI": [
            ("What does a validation set help with during model development?", ["Choosing settings and comparing candidate models", "Replacing all training data", "Guaranteeing future outcomes", "Encrypting model weights"], 0, "Validation data supports model selection without using the final test set repeatedly.", 5),
            ("What does precision measure for a binary classifier?", ["The fraction of predicted positives that are true positives", "The fraction of all negatives correctly rejected", "The average training time", "The number of model parameters"], 0, "Precision is TP divided by TP plus FP.", 6),
            ("What is data leakage?", ["Information unavailable at prediction time influences model training or evaluation", "A CSV file has a blank row", "A model has too few features", "A classifier predicts both classes"], 0, "Leakage gives the model information it would not have in real use, making evaluation misleading.", 7),
        ],
        "SE": [
            ("What is a user story commonly used to describe?", ["A user need and the value they expect", "A database's physical disk layout", "A compiler's token stream", "A CPU cache line"], 0, "A user story summarizes a capability from a user's perspective and its value.", 5),
            ("Why refactor code?", ["Improve its internal structure while keeping behavior the same", "Add features without understanding requirements", "Remove every test", "Change all public APIs randomly"], 0, "Refactoring improves design or maintainability without intentionally changing behavior.", 6),
            ("What does regression testing check?", ["That recent changes did not break existing behavior", "That every feature is new", "That source code has no comments", "That the server has a particular color"], 0, "Regression tests protect previously working behavior as changes are made.", 7),
        ],
        "WT": [
            ("What does a semantic HTML element provide?", ["Meaning about the role of its content", "Automatic server authentication", "A database connection", "A cryptographic signature"], 0, "Semantic elements communicate the purpose of page regions to browsers and assistive technology.", 5),
            ("What does event bubbling describe in the DOM?", ["An event can propagate from a target toward ancestor elements", "Images loading in random order", "CSS variables inheriting from children", "A request being encrypted"], 0, "In event bubbling, an event propagates up the DOM ancestor chain.", 6),
            ("Why validate data on the server even if the browser validates it?", ["Client-side checks can be bypassed", "Browsers cannot display errors", "Server code cannot receive strings", "HTML validation encrypts requests"], 0, "Client-side validation improves usability but is not a security boundary.", 7),
        ],
        "CD": [
            ("What is an abstract syntax tree?", ["A tree representation of meaningful program structure", "A network topology map", "A database index", "A compressed executable image"], 0, "An AST represents language constructs while omitting some surface syntax details.", 5),
            ("What is intermediate representation used for?", ["A compiler-friendly form between source and target code", "Storing user passwords", "Routing IP packets", "Drawing pixels"], 0, "IR separates language front ends from optimization and target-code generation.", 6),
            ("What does a type error indicate?", ["An operation is incompatible with the values' types under the language rules", "A network packet expired", "A file has no extension", "A CPU has no cache"], 0, "Type checking detects operations that do not satisfy the language's type rules.", 7),
        ],
        "COA": [
            ("What is the purpose of a control unit?", ["Coordinate instruction execution and control signals", "Store long-term user documents", "Resolve domain names", "Run database normalization"], 0, "The control unit sequences operations and generates signals for instruction execution.", 5),
            ("What is the effect of cache locality?", ["Recently or nearby used data is more likely to be accessed again", "Every memory access has identical latency", "The disk becomes a CPU register", "Instructions no longer need addresses"], 0, "Temporal and spatial locality make caching effective for many workloads.", 6),
            ("What is an overflow in fixed-width signed arithmetic?", ["A result falls outside the representable range", "A cache line is loaded", "A program counter increments", "A bus transmits data"], 0, "Overflow occurs when the mathematical result cannot be represented in the chosen width and type.", 7),
        ],
        "CC": [
            ("What is autoscaling designed to do?", ["Adjust resource capacity in response to demand or policy", "Change source-code syntax", "Guarantee every request has zero latency", "Disable monitoring"], 0, "Autoscaling changes the number or size of resources according to configured signals.", 5),
            ("Why use identity and access management roles?", ["Grant scoped permissions to users or workloads", "Store application source code", "Compress backups", "Replace network protocols"], 0, "IAM roles attach defined permissions to identities and workloads.", 6),
            ("What should an application do when a cloud dependency is temporarily unavailable?", ["Use bounded retries and graceful error handling where appropriate", "Retry forever without delay", "Expose secret keys to users", "Delete all local state immediately"], 0, "Bounded retries with backoff and clear failure handling can improve resilience without retry storms.", 7),
        ],
        "TOC": [
            ("What is a nondeterministic finite automaton allowed to do at a state?", ["Have multiple possible transitions for an input symbol", "Use an infinite number of states", "Store an unbounded stack", "Decide every undecidable problem"], 0, "An NFA may have multiple possible next states and can also include epsilon transitions.", 5),
            ("What does a pushdown automaton add to finite-state control?", ["A stack", "A relational database", "A network card", "An infinite number of control states"], 0, "A pushdown automaton has a stack, enabling recognition of context-free languages.", 6),
            ("What is an undecidable problem?", ["No algorithm can correctly decide all instances while always halting", "A problem with a slow but terminating algorithm", "A problem with a finite input", "A syntax error"], 0, "Undecidability means no total algorithm decides membership for every input.", 7),
        ],
        "C": [
            ("What does malloc return on success?", ["A pointer to allocated memory", "An integer count of source lines", "A file handle", "A function prototype"], 0, "malloc returns a pointer to allocated storage, or NULL if allocation fails.", 5),
            ("What should a program do after it no longer needs memory allocated with malloc?", ["Release it with free", "Call printf on it", "Change its type to int", "Leave it allocated forever"], 0, "Calling free releases dynamically allocated storage when it is no longer needed.", 6),
            ("What is undefined behavior in C?", ["Behavior for which the C standard imposes no requirements", "A guaranteed runtime exception", "A compiler warning with a fixed result", "A comment without punctuation"], 0, "Undefined behavior means the language standard does not define what happens.", 7),
        ],
        "CPP": [
            ("What does const on a member function generally promise?", ["The function will not modify the object's non-mutable state", "The function cannot return a value", "The function is always static", "The object is deleted after the call"], 0, "A const member function cannot modify ordinary data members through this.", 5),
            ("What is a reference in C++?", ["An alias bound to an existing object", "A heap allocator", "A thread scheduler", "A kind of exception only"], 0, "A reference names an existing object and must be initialized when declared.", 6),
            ("When can std::optional be useful?", ["When a value may be present or absent", "When a function must run on a GPU", "When a pointer must own shared state", "When a class has no fields"], 0, "optional represents a value that may be absent without using a sentinel value.", 7),
        ],
        "JAVA": [
            ("What does garbage collection do in Java?", ["Reclaims memory for objects that are no longer reachable", "Deletes every object after one method call", "Encrypts all heap objects", "Compiles interfaces into SQL"], 0, "The JVM garbage collector reclaims memory occupied by unreachable objects.", 5),
            ("What does the final keyword mean on a local variable?", ["It can be assigned once", "It is shared across all processes", "It becomes public", "It is always null"], 0, "A final local variable can be assigned once and cannot then be reassigned.", 6),
            ("What can cause a NullPointerException?", ["Using a null reference where an object is required", "Calling a static method", "Creating an empty list", "Importing a package"], 0, "The exception commonly occurs when code dereferences a null reference.", 7),
        ],
        "CS": [
            ("Why should passwords be stored using a salted password hash?", ["To make offline guessing harder and avoid storing plaintext", "To make the password reversible", "To share one password among users", "To remove the need for authentication"], 0, "A unique salt and slow password-hashing function make precomputed attacks less useful.", 5),
            ("What does TLS primarily protect in transit?", ["Confidentiality and integrity of a connection, with peer authentication depending on configuration", "Data after it is printed", "Every server from software bugs", "A user's device from all malware"], 0, "TLS protects transport connections; it does not secure every endpoint or application behavior.", 6),
            ("What is a good first response to a suspected credential leak?", ["Revoke or rotate the exposed credential and investigate its use", "Post it in a public issue", "Keep using it unchanged", "Disable all audit logs"], 0, "Revocation or rotation limits further use while investigation determines the impact.", 7),
        ],
        "BD": [
            ("What is a data pipeline?", ["A sequence of steps that moves and transforms data", "A CPU instruction set", "A type of encryption key", "A web page layout"], 0, "Data pipelines ingest, transform, and deliver data to downstream systems.", 5),
            ("Why choose a partition key carefully?", ["It affects data distribution and query efficiency", "It determines the programming language", "It prevents node failures", "It changes the meaning of a row"], 0, "A partition key influences workload placement and can create skew if values are uneven.", 6),
            ("What is a common risk when ingesting messy source data?", ["Incorrect or inconsistent records can distort downstream analysis", "It increases CPU register count", "It automatically fixes missing values", "It guarantees unbiased conclusions"], 0, "Poor quality inputs can propagate errors and bias into derived results.", 7),
        ],
        "DE": [
            ("What does a half adder produce?", ["A sum bit and a carry bit for two input bits", "A stored byte and an address", "A clock and a reset signal", "A network frame and checksum"], 0, "A half adder adds two bits and produces sum and carry outputs.", 5),
            ("What is the purpose of a flip-flop in a sequential circuit?", ["Store a bit of state", "Perform DNS lookup", "Convert analog audio to text", "Sort Boolean expressions"], 0, "A flip-flop stores one bit and updates state according to its clock and inputs.", 6),
            ("What is a floating input on a logic gate likely to cause?", ["Unpredictable logic behavior", "A guaranteed logic zero", "A new clock cycle", "Automatic error correction"], 0, "Unconnected inputs can pick up noise and should be tied to valid logic levels.", 7),
        ],
        "MP": [
            ("What is the role of an instruction register?", ["Hold the instruction currently being decoded or executed", "Store the network's DNS records", "Count all files on disk", "Replace the program counter"], 0, "The instruction register holds the fetched instruction for processing.", 5),
            ("What is polling in device communication?", ["The processor repeatedly checks whether a device needs service", "A device sends an interrupt only once", "A memory page is swapped out", "A compiler checks source grammar"], 0, "Polling checks device status in software, which can be simple but may waste CPU time.", 6),
            ("Why debounce a mechanical switch input?", ["To avoid treating contact bounce as many separate presses", "To increase processor clock speed", "To allocate extra memory", "To change an interrupt into a register"], 0, "Mechanical contacts can rapidly fluctuate, so debouncing filters spurious transitions.", 7),
        ],
        "DL": [
            ("What does an epoch mean during model training?", ["One pass through the training dataset", "One individual neuron", "A type of loss function", "A GPU memory address"], 0, "An epoch is a complete pass over the training examples.", 5),
            ("What is the vanishing-gradient problem?", ["Gradients become very small in earlier layers, slowing learning", "A dataset loses its labels", "A model has too many output classes", "A GPU deletes model weights"], 0, "Very small gradients can make it difficult to update parameters in earlier layers.", 6),
            ("Why monitor validation loss during training?", ["It can reveal poor generalization or overfitting", "It proves the model is fair", "It replaces the test set permanently", "It guarantees the best deployment"], 0, "A widening gap between training and validation performance can signal overfitting.", 7),
        ],
        "NLP": [
            ("What is named-entity recognition?", ["Finding spans such as person, organization, or location names", "Ranking web servers by speed", "Encrypting every token", "Counting GPU cores"], 0, "NER identifies entity mentions and often assigns them categories.", 5),
            ("What is a stop word in some text pipelines?", ["A very common term sometimes filtered for a particular task", "A word that ends every sentence", "A token that always carries the label positive", "A command to stop model training"], 0, "Stop-word lists contain common terms that may be removed when appropriate to the task.", 6),
            ("Why can text preprocessing change model results?", ["It changes the representation and information the model receives", "It always increases accuracy", "It removes the need for evaluation", "It guarantees the same vocabulary"], 0, "Tokenization and normalization choices affect features, vocabulary, and downstream behavior.", 7),
        ],
        "DEVOPS": [
            ("What is a health check endpoint commonly used for?", ["Report whether a service is ready or alive", "Store user passwords", "Compile the source code", "Choose a database schema"], 0, "Health checks let orchestrators or monitors determine whether a service can run or receive traffic.", 5),
            ("Why pin dependency versions in a build?", ["Improve reproducibility and control unexpected upgrades", "Make every dependency secure forever", "Avoid reading release notes", "Remove all transitive packages"], 0, "Pinned versions make builds more repeatable, though updates still need maintenance.", 6),
            ("What should a deployment rollback plan include?", ["A way to restore a known-good release and verify service health", "A public copy of secrets", "A guarantee no data migration occurs", "A disabled monitoring system"], 0, "Rollback planning covers restoring code and checking compatibility and service health.", 7),
        ],
        "BC": [
            ("What is a Merkle tree used for?", ["Efficiently summarize and verify data through hashes", "Store private keys in plaintext", "Replace all network consensus", "Execute a user interface"], 0, "Merkle trees combine hashes so subsets of data can be verified efficiently.", 5),
            ("What is a wallet in many blockchain systems primarily responsible for?", ["Managing keys used to authorize transactions", "Holding physical coins", "Reversing hashes", "Guaranteeing asset prices"], 0, "A wallet manages key material and transaction signing; assets are represented on the ledger.", 6),
            ("Why is exposing a private key dangerous?", ["Others may be able to authorize actions as its owner", "It makes hashes longer", "It slows block production safely", "It prevents signature verification"], 0, "Anyone with the private key may be able to create valid signatures for the associated account.", 7),
        ],
        "DGA": [
            ("What is a stable sorting algorithm?", ["It preserves the relative order of equal-key items", "It always uses constant memory", "It sorts only integers", "It has the same runtime on every input"], 0, "Stability preserves original relative ordering for elements whose keys compare equal.", 5),
            ("What is a recurrence relation used to express in algorithm analysis?", ["The running time or work in terms of smaller input sizes", "A database foreign key", "A program's user interface", "A network address"], 0, "Recurrences describe recursive algorithm cost using costs on smaller subproblems.", 6),
            ("Why analyze worst-case complexity?", ["It bounds resource use for the most demanding inputs of a given size", "It gives exact timing on every machine", "It guarantees the input will be worst-case", "It measures only code style"], 0, "Worst-case analysis provides an upper bound across inputs of a specified size.", 7),
        ],
    }

    for quiz in quizzes:
        additions = additional_questions.get(quiz["course_id"], [])
        quiz["questions"].extend(
            {
                "prompt": prompt,
                "options": options,
                "answer_index": answer,
                "explanation": explanation,
                "topic": f"{quiz['title'].removesuffix(' baseline diagnostic')} - {TOPIC_AREAS[topic_index]}",
            }
            for prompt, options, answer, explanation, topic_index in additions
        )
    return quizzes
