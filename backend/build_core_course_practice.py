"""Replace legacy generic computing topics with authored, topic-linked outlines.

The source bank remains pending instructor review. This deterministic builder
keeps the first five legacy topic IDs (so pilot lesson links remain valid),
removes placeholder topics, and writes one starter question per new topic.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CORE = {
    "CN": ("Computer Networks", [
        ("Layered network architecture", "A network stack separates communication functions into layers. What is a key benefit?", ["Each layer can provide a defined service to the layer above", "Every layer must use the same protocol", "Applications no longer need addresses", "All packets arrive in order automatically"], 0, "Layering defines interfaces and separates concerns, making protocols easier to develop and interoperate."),
        ("Ethernet and local networks", "Which address is normally used by an Ethernet switch to forward a frame on a local link?", ["Destination MAC address", "DNS name", "TCP port", "URL path"], 0, "A layer-2 switch learns and forwards frames using MAC addresses."),
        ("Internet routing and IP", "Which IP-layer device function chooses a next hop between different networks?", ["Router", "Repeater only", "Keyboard controller", "CSS engine"], 0, "Routers forward packets between IP networks using routing information."),
        ("Transport protocols and reliability", "Which transport protocol provides ordered delivery and retransmission as part of its core service?", ["TCP", "UDP", "ARP", "DNS"], 0, "TCP provides a reliable, ordered byte stream using acknowledgements and retransmission."),
        ("Name resolution and application protocols", "What does DNS commonly resolve for a client starting a connection to a website?", ["A domain name to records such as an IP address", "A MAC address to a password", "A URL path to a TCP sequence number", "An Ethernet frame to HTML"], 0, "DNS resolves names to records such as IP addresses that clients use to locate services."),
    ]),
    "DBMS": ("Database Management Systems", [
        ("Relational models, keys, and constraints", "What property should a primary key have for each row?", ["It uniquely identifies the row", "It must contain the full row as text", "It must be the last column", "It can repeat freely"], 0, "A primary key uniquely identifies each row in a relation."),
        ("Normalization and relational design", "Why split repeated customer details into a Customers table and reference it from Orders?", ["To reduce duplicated data and update anomalies", "To make every query slower by design", "To remove all relationships", "To store passwords in the order number"], 0, "Normalization reduces repeated facts and helps avoid inconsistent updates."),
        ("SQL querying and aggregation", "Which SQL clause filters individual rows before grouping?", ["WHERE", "HAVING", "ORDER BY", "LIMIT"], 0, "WHERE filters rows before GROUP BY forms groups; HAVING filters groups after aggregation."),
        ("Transactions and concurrency", "What does a transaction provide when two related updates must succeed together or not at all?", ["Atomicity", "A larger cache", "A new primary key", "A network route"], 0, "Atomicity means a transaction's operations are treated as one all-or-nothing unit."),
        ("Indexes, security, and recovery", "An application builds SQL by concatenating untrusted input into a query. What is the safer common approach?", ["Use parameterized queries", "Hide the query in the browser", "Give the input database administrator access", "Disable all constraints"], 0, "Parameterized queries keep untrusted values separate from SQL syntax and help prevent injection."),
    ]),
    "DSA": ("Data Structures & Algorithms", [
        ("Linear data structures and operations", "A service must undo the most recent operation first. Which structure matches that order?", ["Stack", "Queue", "Sorted array", "Graph"], 0, "A stack is last-in, first-out, so the newest operation is removed first."),
        ("Arrays, linked structures, and access costs", "You need frequent reads by numeric index and few insertions near the front. Which choice is usually simplest?", ["Singly linked list", "Array", "Queue", "Binary tree"], 1, "Arrays support constant-time indexed access; inserting at the front can be costly, but that is rare here."),
        ("Hashing and associative lookup", "A dictionary-like lookup is needed for student IDs, with no requirement to keep keys sorted. Which structure is a natural fit?", ["Stack", "Linked list", "Hash table", "Queue"], 2, "A hash table gives expected fast lookup by key; ordering is not its primary guarantee."),
        ("Trees and graph traversal", "A breadth-first graph traversal needs to visit the earliest discovered frontier node next. Which structure should hold that frontier?", ["Stack", "Heap", "Queue", "Hash map"], 2, "FIFO queue order processes vertices by discovery distance, which is the basis of BFS."),
        ("Algorithm analysis and search", "Binary search is applied to an array of n sorted values. What is its worst-case comparison growth?", ["O(log n)", "O(1)", "O(n)", "O(n²)"], 0, "Each comparison discards about half the remaining range, giving logarithmic growth."),
    ]),
    "OS": ("Operating Systems", [
        ("Processes, threads, and execution state", "What is a process?", ["A program in execution with state and resources", "A source file that has never run", "A CPU cache line", "A network protocol"], 0, "A process is a running program instance with execution state and allocated resources."),
        ("CPU scheduling and concurrency", "In round-robin scheduling, what happens when a runnable task's time slice expires?", ["It is preempted and typically returns to the ready queue", "It is always terminated", "It permanently owns the CPU", "It is moved to disk"], 0, "Round robin gives each ready task a bounded slice, then schedules another runnable task."),
        ("Memory management and virtual memory", "What does virtual memory primarily provide to each process?", ["An address-space abstraction mapped to physical memory and backing storage", "Unlimited physical RAM", "A replacement for every CPU register", "Guaranteed constant-time disk access"], 0, "Virtual memory gives a process a logical address space mapped to physical pages and, when needed, backing storage."),
        ("Synchronization and deadlocks", "Two threads increment the same shared counter without synchronization. What risk exists?", ["A race condition can cause a lost update", "The counter becomes immutable", "The process automatically forks", "The OS guarantees both increments are atomic"], 0, "Interleaved read-modify-write operations can overwrite each other unless protected or made atomic."),
        ("File systems, protection, and reliability", "What is the purpose of file-system permissions?", ["Control which users or processes may perform operations on files", "Guarantee that a disk never fails", "Compress every file automatically", "Choose a CPU scheduling policy"], 0, "Permissions enforce access-control rules for operations such as reading, writing, or executing files."),
    ]),
    "PY": ("Python for Data Science", [
        ("Python values, types, and control flow", "A loop visits each of n records once and performs constant work per record. What is its time growth?", ["O(n)", "O(1)", "O(log n)", "O(n²)"], 0, "The work grows linearly with the number of records when each record receives constant work."),
        ("Lists, dictionaries, and collection operations", "What does `items = [2, 4]; items.append(6)` leave in `items`?", ["[2, 4, 6]", "[6, 2, 4]", "[2, 4]", "An error because lists cannot change"], 0, "append adds the supplied item to the end of the mutable list."),
        ("Functions, modules, and interfaces", "A function should return a new list while leaving its input unchanged. Which approach best expresses that intent?", ["Build and return a separate list", "Call clear() on the input and return it", "Assign the input to a global variable", "Mutate the input and rename it"], 0, "Constructing a separate result avoids modifying the caller's list."),
        ("Data handling and iteration", "What does `enumerate(names)` provide in a loop?", ["Pairs of an index and corresponding item", "Only the list length", "A sorted copy of the names", "A dictionary of unique values"], 0, "enumerate yields an index-item pair for each value in the iterable."),
        ("Errors, testing, and performance", "What does `scores.get('midterm', 0)` return when `midterm` is absent?", ["0", "None always", "False", "A KeyError"], 0, "dict.get returns the supplied default when the key is missing."),
    ]),
    "AI": ("Artificial Intelligence & ML", [
        ("Search strategies and state spaces", "A shortest-path search needs the fewest-cost route and all step costs are non-negative. Which algorithm is appropriate?", ["Breadth-first search in all cases", "Uniform-cost search", "Depth-first search", "Random walk"], 1, "Uniform-cost search expands the frontier item with the least accumulated path cost and is optimal under non-negative costs."),
        ("Knowledge representation and inference", "In a rule-based system, what does forward chaining do?", ["Starts with known facts and fires applicable rules", "Starts with a goal and works backward only", "Sorts facts alphabetically", "Trains weights using gradient descent"], 0, "Forward chaining is data-driven: known facts trigger rules that can derive additional facts."),
        ("Supervised learning and generalization", "A classifier is trained on labelled examples of email marked spam or not spam. This is an example of what?", ["Unsupervised clustering", "Supervised classification", "Reinforcement learning", "Dimensionality reduction only"], 1, "The training examples include labels, and the model predicts a discrete class, so this is supervised classification."),
        ("Model evaluation and overfitting", "Training accuracy is high but validation accuracy is much lower. What is the most likely issue?", ["The model is overfitting the training data", "The labels are necessarily perfect", "The model has no parameters", "The validation set trained the model"], 0, "A large train-validation gap is a common sign that the model learned patterns that do not generalize."),
        ("Responsible AI and data limitations", "A training dataset under-represents a group of users. What is a key risk?", ["The model may perform less reliably for that group", "The model becomes deterministic", "The labels are encrypted automatically", "The dataset gains more examples"], 0, "Under-representation can make measured performance and model behaviour less reliable for that population."),
    ]),
    "BC": ("Blockchain & Distributed Ledgers", [
        ("Blocks, hashes, and chain integrity", "What does a block's reference to the previous block's hash primarily provide?", ["A link that makes later tampering detectable", "A guarantee of transaction confidentiality", "A replacement for digital signatures", "Automatic legal finality"], 0, "Changing earlier block data changes its hash and breaks the hash-linked chain unless later blocks are recomputed."),
        ("Consensus and distributed agreement", "Why do distributed ledgers use a consensus protocol?", ["To coordinate which proposed state update the network accepts", "To make every node's clock identical", "To remove the need for cryptography", "To guarantee zero network delay"], 0, "Consensus helps participants agree on an accepted ledger state despite distributed communication and failures."),
        ("Smart contracts and state transitions", "A smart contract transfer checks that the sender has enough balance before updating balances. The check is best understood as what?", ["A state-transition precondition", "A public-key derivation", "A block header", "A network route"], 0, "The precondition guards the state transition so an invalid transfer does not alter contract state."),
        ("Wallet keys and digital signatures", "What does a digital signature created with a private key let others verify?", ["That the matching key signed the message and it was not altered", "That the message is secret from everyone", "That the signer cannot lose the key", "That the transaction is automatically reversible"], 0, "Verification with the corresponding public key supports authenticity and integrity, not confidentiality."),
        ("Ledger limits and threat models", "A blockchain consensus mechanism is secure only under assumptions about participants and resources. What should a threat model identify?", ["The adversary's capabilities and the protocol's trust assumptions", "Only the user-interface colours", "The average block size alone", "A guarantee that attacks are impossible"], 0, "Security claims depend on explicit assumptions about attackers, resources, network conditions, and protocol rules."),
    ]),
    "BD": ("Big Data Analytics", [
        ("Distributed storage and partitioning", "A large dataset is split across machines so workers can process separate portions. What is this strategy called?", ["Partitioning", "Normalization", "Serialization only", "Deadlock prevention"], 0, "Partitioning divides data into manageable pieces that can be stored and processed across nodes."),
        ("Batch processing and MapReduce", "In MapReduce, what does the reduce stage usually do?", ["Combines intermediate values grouped by key", "Reads keyboard input from each worker", "Encrypts every source file", "Chooses the cluster leader"], 0, "Reducers aggregate or combine intermediate records sharing a key, such as summing counts."),
        ("Stream processing and event time", "A stream processor must handle events that arrive late but carry an earlier event timestamp. Which concept helps define when to close an event-time window?", ["Watermarks", "Foreign keys", "CPU registers", "Static linking"], 0, "Watermarks estimate event-time progress and help systems decide when a window is sufficiently complete."),
        ("Data quality and governance", "Two sources use different units for the same measurement. What is the first data-quality step before combining them?", ["Validate and standardize the units", "Drop the source timestamps", "Average the raw numbers directly", "Duplicate every row"], 0, "Values must use compatible units and documented transformations before they can be meaningfully combined."),
        ("Analytics architectures and trade-offs", "A dashboard needs fresh updates within seconds, while a nightly report can wait for a complete dataset. Which pairing is most suitable?", ["Streaming for the dashboard and batch for the report", "Batch for both regardless of latency", "Streaming only because it is always cheaper", "Manual copying for both"], 0, "Streaming fits low-latency updates; batch processing is often appropriate for scheduled complete workloads."),
    ]),
    "C": ("C Programming & Problem Solving", [
        ("C types, expressions, and conversions", "In C, what is the value category of the expression `5 / 2` when both operands are int?", ["2", "2.5", "2.0", "A compile-time error"], 0, "Integer division discards the fractional part when both operands have integer type."),
        ("Selection, iteration, and control flow", "A loop must execute its body at least once before checking a condition. Which construct directly expresses that?", ["do-while", "while", "for with zero iterations", "switch"], 0, "A do-while loop evaluates its condition after the body, so the body runs at least once."),
        ("Arrays, strings, and bounds", "For `int a[5]`, which is the last valid array index?", ["4", "5", "-1", "6"], 0, "C array indices start at zero, so a five-element array has valid indices 0 through 4."),
        ("Functions, pointers, and parameter passing", "To let a C function modify the caller's integer variable, what should the caller pass?", ["The variable's address using `&`", "A second copy of the value", "The variable's type name", "The address of an unrelated constant"], 0, "Passing a pointer to the variable lets the function write through that pointer to the caller's object."),
        ("Structures, memory, and lifetime", "After `malloc` succeeds, which operation releases that allocated block when it is no longer needed?", ["free(pointer)", "close(pointer)", "delete(pointer)", "return(pointer)"], 0, "C uses `free` to release storage obtained from `malloc`, `calloc`, or `realloc`."),
    ]),
    "CC": ("Cloud Computing", [
        ("Cloud service models", "A team deploys its own application code while the provider manages the runtime and operating system. Which model is closest?", ["Platform as a Service", "Infrastructure as a Service", "On-premises only", "Bare-metal ownership"], 0, "PaaS provides a managed application platform while customers deploy and manage their applications and data."),
        ("Deployment models and tenancy", "A cloud environment is dedicated to one organization, though a provider may operate it. Which model does this describe?", ["Private cloud", "Public cloud shared by all tenants", "Peer-to-peer network", "Edge cache only"], 0, "A private cloud is dedicated to one organization; ownership and operation can vary."),
        ("Virtual machines and containers", "Compared with a virtual machine, a container commonly shares which component with other containers on the host?", ["The host operating-system kernel", "Its process namespace in every configuration", "A separate physical CPU", "A dedicated hypervisor per container"], 0, "Containers isolate processes while generally sharing the host kernel; virtual machines run guest operating systems."),
        ("Elasticity, availability, and recovery", "A service automatically adds instances when demand rises and removes them when demand falls. What is this property?", ["Elasticity", "Normalization", "Encryption", "Compilation"], 0, "Elasticity adjusts resources with changing workload demand."),
        ("Cloud security and shared responsibility", "In a managed cloud service, who is still responsible for configuring access permissions to the customer's data?", ["The customer, according to the shared-responsibility model", "Only the network carrier", "Nobody once the service is managed", "Every other tenant"], 0, "Providers secure parts of the service, but customers remain responsible for their data, identities, and configuration choices."),
    ]),
    "CD": ("Compiler Design", [
        ("Lexical analysis and tokens", "A compiler's lexer typically converts a character stream into what?", ["Tokens", "Machine interrupts", "Database rows", "CPU cache lines"], 0, "Lexical analysis groups characters into tokens such as identifiers, keywords, and operators."),
        ("Parsing and grammar", "A parser primarily checks whether a token sequence conforms to what?", ["A grammar's syntax rules", "The program's runtime output", "The operating system's file permissions", "A network routing table"], 0, "Parsing determines whether tokens form valid grammatical structures, often building a syntax tree."),
        ("Semantic analysis and symbol tables", "A program uses a variable name that was never declared in the visible scope. Which compiler phase commonly reports this?", ["Semantic analysis", "Lexical tokenization only", "Instruction scheduling", "Link-time compression"], 0, "Semantic analysis checks declarations, types, scopes, and other meaning-related constraints."),
        ("Intermediate representations and control flow", "Why do compilers often translate source code into an intermediate representation?", ["To separate front-end language parsing from later optimizations and target code generation", "To guarantee that source code has no bugs", "To execute the program without a processor", "To remove the need for parsing"], 0, "An IR gives compiler stages a common form and makes optimization and target-specific back ends easier to organize."),
        ("Optimization and code generation", "Which compiler optimization can remove a computation whose result is never used and has no side effects?", ["Dead-code elimination", "Lexical analysis", "Parsing", "Register reset"], 0, "Dead-code elimination removes instructions that cannot affect program behaviour or observable output."),
    ]),
    "COA": ("Computer Organization & Architecture", [
        ("Data representation and Boolean logic", "In unsigned binary, how many distinct values can an n-bit field represent?", ["2^n", "n^2", "2n", "n!"], 0, "Each bit has two possible values, giving 2 multiplied by itself n times, or 2^n patterns."),
        ("Instruction sets and datapaths", "What does an instruction set architecture specify for software and processor implementations?", ["The visible machine instructions, registers, and architectural behaviour", "The exact source code of every operating system", "Only the processor's package dimensions", "The database schema used by an application"], 0, "An ISA defines the software-visible machine interface; implementations may realize it with different microarchitectures."),
        ("Pipelining and hazards", "A data hazard occurs when an instruction needs a value that an earlier instruction has not produced yet. What is the issue?", ["A dependency between overlapping pipeline stages", "A disk-sector failure", "An invalid source-language keyword", "A missing DNS record"], 0, "Overlapped instructions can have read-after-write dependencies that require forwarding, scheduling, or a stall."),
        ("Memory hierarchy and cache", "Why does a cache improve average memory-access time?", ["It keeps recently or nearby used data in faster storage", "It makes main memory infinitely large", "It removes all address translation", "It guarantees every access is a hit"], 0, "Locality lets caches serve many accesses from faster storage, though misses still occur."),
        ("Input-output and interrupts", "What is a typical purpose of an I/O interrupt?", ["Notify the processor that an I/O event needs attention", "Increase the clock frequency automatically", "Translate every source-language expression", "Replace all device drivers"], 0, "An interrupt lets a device signal the processor without requiring continuous polling."),
    ]),
    "CPP": ("Advanced C++ Programming", [
        ("Classes, constructors, and object lifetime", "What is RAII intended to do in C++?", ["Tie resource acquisition and release to object lifetime", "Disable constructors", "Allocate every object globally", "Replace type checking with comments"], 0, "RAII uses constructors and destructors so resources are released when their owning objects leave scope."),
        ("Templates and generic programming", "A function template is useful when the same algorithm should operate on several types. What does the template provide?", ["A type-parameterized definition instantiated for compatible types", "A runtime database connection", "Automatic proof that every type is safe", "A replacement for function calls"], 0, "Templates allow code to be parameterized by types or values and instantiated by the compiler."),
        ("Standard library containers and algorithms", "Which standard container is designed for fast average key lookup without maintaining sorted key order?", ["`std::unordered_map`", "`std::vector`", "`std::stack`", "`std::array`"], 0, "`std::unordered_map` is hash-based and provides average constant-time lookup, subject to hashing and collisions."),
        ("Polymorphism and virtual dispatch", "When a base-class pointer calls an overridden virtual function, which implementation is selected?", ["The derived object's override at runtime", "Always the base implementation at compile time", "The first function alphabetically", "No function can be called"], 0, "Virtual dispatch selects the final overrider for the object's dynamic type."),
        ("Exceptions and move semantics", "What is the main purpose of a move constructor?", ["Transfer resources from a temporary or expiring object instead of copying them", "Convert every exception into success", "Make an object immutable", "Sort an object's fields"], 0, "Move operations can transfer ownership of resources when the source object is no longer needed."),
    ]),
    "CS": ("Cyber Security & Cryptography", [
        ("Threat models and security goals", "A threat model is most useful when it documents what?", ["Assets, adversaries, assumptions, attack surfaces, and trust boundaries", "Only the product logo", "Only successful attacks from the past", "The guarantee that no vulnerability exists"], 0, "Threat modelling makes security assumptions and important attack paths explicit for design and review."),
        ("Authentication and access control", "Authentication and authorization answer which two questions, respectively?", ["Who are you? and what are you allowed to do?", "Where is the server? and how fast is it?", "What is encrypted? and what is compressed?", "When was the file created? and who compiled it?"], 0, "Authentication verifies identity; authorization checks whether that identity may perform an action."),
        ("Cryptographic hashes and signatures", "Which property is a cryptographic hash designed to provide when used correctly?", ["A fixed-length digest useful for integrity checking", "Reversible encryption with the same output size", "Guaranteed secrecy of the original message", "Proof that a user is authorized"], 0, "A cryptographic hash maps data to a digest; it is not encryption and does not itself grant access."),
        ("Web application vulnerabilities", "A web app inserts raw user input into SQL text. What is a standard defense against SQL injection?", ["Parameterized queries", "Hiding the submit button", "Encoding the database password in JavaScript", "Allowing more input characters"], 0, "Bound parameters keep data separate from SQL syntax and prevent user input from changing query structure."),
        ("Incident response and evidence", "During incident response, why preserve logs and document handling steps?", ["To support investigation while maintaining evidence integrity and context", "To guarantee that the incident cannot recur", "To replace access control", "To make every log publicly searchable"], 0, "Preserving provenance and context helps investigators understand events and assess whether evidence was altered."),
    ]),
    "DE": ("Digital Electronics & Logic Design", [
        ("Number systems and Boolean algebra", "By De Morgan's law, what is the complement of `A AND B`?", ["NOT A OR NOT B", "NOT A AND NOT B", "A OR B", "A AND NOT B"], 0, "De Morgan's law states that the complement of a product is the sum of the complemented variables."),
        ("Combinational logic and minimization", "What distinguishes a combinational circuit from a sequential circuit?", ["Its outputs depend on current inputs, not stored past state", "It must contain a clock", "It always has a memory array", "It can only implement addition"], 0, "Combinational logic has no state; its output is a function of the current input values."),
        ("Sequential circuits and flip-flops", "What does a D flip-flop normally do at its active clock edge?", ["Stores the D input as its output state", "Adds the input to an address", "Inverts every clock cycle without an input", "Selects a memory bank by software"], 0, "A D flip-flop captures its D input at the triggering clock edge and holds that state until updated."),
        ("Timing, propagation delay, and hazards", "Why must a synchronous circuit's input meet setup time before the clock edge?", ["The data must be stable long enough for reliable capture", "The clock frequency must become zero", "The input must be encrypted", "The output must already be tri-stated"], 0, "Violating setup time can cause incorrect capture or metastability in the receiving flip-flop."),
        ("Counters and data conversion", "A modulo-8 binary counter needs how many state bits?", ["3", "4", "8", "2"], 0, "Three bits encode 2^3 = 8 distinct states, sufficient for a modulo-8 sequence."),
    ]),
    "DGA": ("Design & Analysis of Algorithms", [
        ("Asymptotic analysis and complexity", "An algorithm performs 4n + 20 operations. What is its asymptotic time complexity?", ["O(n)", "O(n^2)", "O(log n)", "O(1)"], 0, "The linear term dominates growth as n increases; constant factors and lower-order terms are omitted."),
        ("Recurrences and divide-and-conquer", "A divide-and-conquer algorithm splits a problem into two halves and does linear extra work. Which recurrence models it?", ["T(n)=2T(n/2)+O(n)", "T(n)=T(n-1)+O(1)", "T(n)=T(n/2)+O(1)", "T(n)=nT(n)+1"], 0, "Two half-size subproblems plus linear combine work give the recurrence shown."),
        ("Graph traversal and shortest paths", "For an unweighted graph, which algorithm finds shortest paths by number of edges from a source?", ["Breadth-first search", "Depth-first search", "Kruskal's algorithm", "Topological sorting alone"], 0, "BFS visits vertices in increasing distance layers in an unweighted graph."),
        ("Greedy choice and correctness", "A greedy algorithm makes what choice at each step?", ["A locally preferred choice justified by a correctness argument", "An arbitrary choice that always works", "Every possible choice before output", "A choice based only on input order"], 0, "Greedy methods commit to a local choice; correctness requires proving that such choices lead to a global optimum."),
        ("Dynamic programming and optimal substructure", "Dynamic programming is especially useful when a problem has overlapping subproblems and what other property?", ["Optimal substructure", "Only one possible input", "No repeated states", "A sorted output requirement"], 0, "DP stores solutions to repeated subproblems and combines them when an optimal solution has suitable substructure."),
    ]),
    "DL": ("Deep Learning & Neural Networks", [
        ("Neurons, layers, and activations", "Why does a neural network use nonlinear activation functions between layers?", ["To represent nonlinear input-output relationships", "To ensure every weight is positive", "To remove the need for training data", "To sort the feature values"], 0, "Without nonlinear activations, stacked linear layers collapse to a single linear transformation."),
        ("Loss functions and gradient-based training", "During backpropagation, what is propagated through the network?", ["Gradients of the loss with respect to parameters", "The final labels as source code", "The entire training dataset at once", "Only the model's layer names"], 0, "Backpropagation applies the chain rule to compute parameter gradients used by an optimizer."),
        ("Convolutional neural networks", "A convolutional layer is useful for images partly because it uses what?", ["Local receptive fields and shared filters", "A separate unrelated weight for every pixel pair", "Only a single constant output", "No trainable parameters"], 0, "Convolution exploits local structure and weight sharing to detect patterns across image positions."),
        ("Sequence models and attention", "In attention, a query is compared with keys to produce weights that determine what?", ["How strongly to combine the associated value vectors", "The image dimensions", "The optimizer's learning rate only", "Which training labels to delete"], 0, "Attention scores are normalized into weights used to combine values into a context representation."),
        ("Generalization and evaluation", "Why evaluate a trained neural network on held-out data?", ["To estimate performance on examples not used for fitting", "To increase training accuracy by definition", "To eliminate the need for validation", "To prove causal impact"], 0, "Held-out evaluation gives a less biased estimate of performance on unseen data, subject to sampling limits."),
    ]),
    "DevOps": ("DevOps & CI/CD Pipelines", [
        ("Version control and continuous integration", "What should a continuous-integration pipeline do after a change is pushed?", ["Build and run automated checks on the change", "Deploy to production without any checks by definition", "Rewrite the commit history randomly", "Store credentials in the source code"], 0, "CI automatically builds and validates changes so integration problems are found early."),
        ("Build artifacts and dependency management", "Why should a release pipeline identify the exact artifact it deploys?", ["To make releases traceable and reproducible", "To make source control unnecessary", "To guarantee a service has no defects", "To avoid versioning dependencies"], 0, "Artifact identity and provenance help ensure the tested build is the one actually released."),
        ("Deployment strategies and rollback", "A canary deployment initially routes a small share of traffic to a new version. Why?", ["To observe the change with limited exposure before wider rollout", "To remove health monitoring", "To duplicate all user data", "To prevent a rollback"], 0, "A canary reduces blast radius and provides evidence before increasing rollout."),
        ("Containers and infrastructure as code", "What is a key benefit of describing infrastructure as code?", ["Infrastructure changes can be versioned, reviewed, and applied consistently", "It makes cloud permissions unnecessary", "It guarantees hardware never fails", "It converts every service to a container"], 0, "IaC represents infrastructure configuration in reviewable, repeatable source-controlled definitions."),
        ("Monitoring, alerting, and reliability", "Which signal best indicates that users are experiencing failed requests?", ["Error rate", "Source-file line count", "Number of developers", "Container image filename length"], 0, "Request error rate is a service-level signal directly related to failed user operations."),
    ]),
    "JAVA": ("Java Application Development", [
        ("Java types, expressions, and JVM", "What does the Java compiler normally produce from a `.java` source file?", ["Bytecode for the JVM", "A database table", "A CPU-specific executable in every case", "An HTML page"], 0, "The Java compiler emits class-file bytecode that a JVM can interpret or compile further."),
        ("Classes, interfaces, and object-oriented design", "What does an interface primarily define in Java?", ["A contract of methods and constants that implementing types provide", "A concrete database connection", "A process scheduler", "A package manager lockfile"], 0, "An interface specifies a type contract that classes can implement, with modern Java also supporting default and static methods."),
        ("Collections and generics", "What is a key benefit of `List<String>` compared with a raw `List`?", ["Compile-time type checking for string elements", "Automatic sorting", "Thread safety in every operation", "Unlimited storage"], 0, "Generics express element types so incompatible values can be rejected during compilation."),
        ("Exceptions and resource management", "Why use try-with-resources for an AutoCloseable resource?", ["It closes the resource automatically when the block exits", "It suppresses every exception", "It makes the resource global", "It retries the operation forever"], 0, "Try-with-resources closes declared resources even when control leaves the block exceptionally."),
        ("Concurrency and thread safety", "Two threads update shared mutable state without coordination. What can occur?", ["A race condition", "Guaranteed serial execution", "Automatic database rollback", "A compile-time type conversion"], 0, "Unsynchronized concurrent access can interleave unpredictably and produce incorrect results."),
    ]),
    "MP": ("Microprocessors & Interfacing", [
        ("Processor architecture and instruction cycle", "What is the program counter used to hold?", ["The address of the next instruction to fetch", "The result of every arithmetic operation", "A peripheral's supply voltage", "The current stack contents"], 0, "The program counter tracks the instruction address used by the fetch sequence."),
        ("Addressing modes and assembly language", "In immediate addressing, where is an instruction's operand value provided?", ["Within the instruction itself", "Only in an external sensor", "At an unknown address selected later", "In the clock signal"], 0, "Immediate addressing encodes the operand value directly in the instruction."),
        ("Interrupts, timers, and event handling", "What is a common benefit of an interrupt-driven peripheral over constant polling?", ["The processor can do other work until the peripheral signals an event", "The peripheral no longer needs a driver", "The processor clock stops permanently", "Every event is handled with zero latency"], 0, "Interrupts can avoid repeated status checks, although handling still has latency and overhead."),
        ("Memory and I/O interfacing", "What does memory-mapped I/O mean?", ["Device registers occupy addresses in the processor's memory address space", "All device data is copied into source code", "The processor has no memory bus", "A device controls the program counter directly"], 0, "Memory-mapped devices are accessed through addresses and load/store operations in the shared address space."),
        ("Bus timing and peripheral communication", "Why do processor and peripheral interfaces use handshaking signals?", ["To coordinate data transfer when devices are not ready at exactly the same time", "To guarantee identical clock rates", "To encrypt every bus signal", "To eliminate address decoding"], 0, "Handshake signals coordinate transfer readiness and completion across components with different timing."),
    ]),
    "NLP": ("Natural Language Processing", [
        ("Text normalization and tokenization", "What does tokenization do in a text-processing pipeline?", ["Splits text into units such as words, subwords, or symbols", "Encrypts the sentence", "Assigns every word a correct meaning", "Removes all punctuation in every task"], 0, "Tokenization converts raw text into model-consumable units; the chosen scheme depends on the task and language."),
        ("Text representations and embeddings", "What is an embedding intended to represent?", ["A token or item as a learned numeric vector", "A guaranteed dictionary definition", "A syntax tree in plain text only", "A compressed audio waveform"], 0, "Embeddings map discrete items into vectors whose learned geometry can encode useful relationships."),
        ("Sequence models and language modelling", "A language model estimates what quantity for a token sequence?", ["A probability distribution over possible next tokens or sequences", "The exact author's identity", "The number of paragraphs in the source file", "A network route"], 0, "Language models learn statistical patterns that assign probabilities to token continuations."),
        ("Attention and transformer architecture", "Why can self-attention help represent relationships between distant tokens?", ["Each token can directly weight information from other positions", "It restricts every token to its immediate neighbor", "It removes positional information automatically", "It guarantees factual output"], 0, "Self-attention computes interactions across positions, subject to the architecture's context and positional encoding."),
        ("Evaluation, bias, and language variation", "Why should NLP evaluation include examples from different dialects or user groups?", ["Aggregate scores may hide uneven performance across groups", "Every group uses identical language", "It guarantees the model is unbiased", "It removes the need for human review"], 0, "Disaggregated evaluation can reveal performance gaps masked by an overall average."),
    ]),
    "OOPS": ("Object-Oriented Programming", [
        ("Classes, objects, and constructors", "In object-oriented programming, what is an object?", ["A runtime instance with state and behaviour defined by its type", "Only a source-code comment", "A network protocol", "A function parameter list"], 0, "An object is an instance that combines state with operations exposed by its class or type."),
        ("Encapsulation, inheritance, and composition", "What is a benefit of encapsulation?", ["It controls access to internal state through a defined interface", "It makes all data globally mutable", "It removes the need for types", "It guarantees an algorithm is optimal"], 0, "Encapsulation hides implementation details and protects invariants behind controlled operations."),
        ("Polymorphism and dynamic dispatch", "Polymorphism allows code to do what?", ["Use a common interface with behaviour varying by concrete type", "Run without any type or contract", "Guarantee every class has identical state", "Replace all objects with strings"], 0, "Polymorphism lets callers use a shared abstraction while implementations provide type-specific behaviour."),
        ("Abstraction and interface design", "A well-designed abstraction should primarily expose what?", ["The operations needed by callers while hiding irrelevant implementation details", "Every private field and internal algorithm", "Only memory addresses", "A copy of the source repository"], 0, "Abstraction presents a useful contract without requiring users to depend on internal details."),
        ("Exceptions and object invariants", "Why should a constructor validate values that an object requires to remain valid?", ["To establish the object's invariant at creation", "To avoid assigning any fields", "To guarantee the operating system cannot fail", "To make all methods static"], 0, "Construction is a natural boundary for validating state so methods can rely on established invariants."),
    ]),
    "SE": ("Software Engineering", [
        ("Requirements and acceptance criteria", "What makes an acceptance criterion useful?", ["It describes an observable condition for deciding whether a requirement is met", "It uses only vague terms such as 'fast'", "It specifies the programming language only", "It is written after release and never checked"], 0, "Observable criteria let stakeholders and testers determine whether delivered behaviour satisfies a requirement."),
        ("Architecture and modular design", "Why divide a system into modules with clear interfaces?", ["To limit coupling and make parts easier to change and test", "To ensure every module duplicates all data", "To eliminate integration", "To prevent any reuse"], 0, "Clear interfaces reduce dependencies and support independent implementation, testing, and maintenance."),
        ("Testing and verification", "What does a unit test usually verify?", ["A small component or function in isolation", "The entire production organization", "Every possible input for every program", "Only deployment billing"], 0, "Unit tests target small pieces of behaviour, often using controlled dependencies."),
        ("Version control and collaboration", "What is a pull request primarily used for in a team workflow?", ["Reviewing and discussing a proposed change before integration", "Replacing all automated tests", "Storing production secrets", "Guaranteeing the change is defect-free"], 0, "A pull request gives collaborators a place to inspect, discuss, and approve changes before merging."),
        ("Maintenance, quality, and lifecycle", "Why keep technical documentation current as software changes?", ["It helps future users and maintainers understand actual system behaviour", "It makes testing unnecessary", "It automatically fixes bugs", "It guarantees compatibility with every platform"], 0, "Accurate documentation reduces knowledge gaps, but it complements rather than replaces tests and review."),
    ]),
    "TOC": ("Theory of Computation", [
        ("Finite automata and regular languages", "A deterministic finite automaton has how many active states after reading a prefix?", ["Exactly one", "Any number simultaneously", "No states until input ends", "Exactly two"], 0, "A DFA's transition function maps each state-symbol pair to one next state."),
        ("Regular expressions and nondeterminism", "What is a standard relationship between NFAs and DFAs in language recognition power?", ["They recognize the same class of regular languages", "NFAs recognize every language", "DFAs cannot recognize finite languages", "NFAs require a stack"], 0, "NFAs and DFAs are equivalent in expressive power, though their state counts can differ."),
        ("Context-free grammars and parsing", "What does a context-free grammar generate?", ["Strings formed by repeatedly applying production rules", "Only machine code", "A set of IP routes", "A database transaction log"], 0, "A grammar generates strings by replacing nonterminals according to its productions."),
        ("Pushdown automata and stack memory", "What additional storage does a pushdown automaton use compared with a finite automaton?", ["A stack", "An unbounded random-access array", "A second input tape in every case", "A database index"], 0, "A stack gives a pushdown automaton memory useful for recognizing many context-free languages."),
        ("Turing machines and decidability", "A decision problem is decidable if there exists an algorithm that does what?", ["Halts on every input and returns the correct yes/no answer", "Returns an answer only for examples seen in training", "Never halts", "Uses a stack of fixed size only"], 0, "Decidability requires a procedure that terminates on all inputs with the correct answer."),
    ]),
    "WT": ("Web Technologies", [
        ("HTML structure and accessibility", "Why should an image that conveys information have meaningful alternative text?", ["Assistive technology can communicate the image's purpose", "It makes the image load without a network", "It compresses the file", "It replaces all visible text"], 0, "Alternative text conveys relevant image content to users who cannot perceive the image visually."),
        ("CSS layout and responsive design", "What does a responsive layout aim to do?", ["Adapt presentation to different viewport sizes and input contexts", "Force every screen to use the same fixed width", "Replace semantic HTML", "Encrypt page styles"], 0, "Responsive design adjusts layout and presentation so content works across different screen sizes."),
        ("JavaScript, DOM, and browser events", "What is the DOM in a browser?", ["A structured object representation of the document that scripts can inspect and update", "A network encryption algorithm", "A CSS file format", "A database server"], 0, "The DOM exposes document nodes and relationships through browser APIs."),
        ("HTTP requests and API design", "Which HTTP method is conventionally used to retrieve a resource without changing its state?", ["GET", "POST", "PATCH", "DELETE"], 0, "GET is intended for retrieval and is defined as a safe method by HTTP semantics."),
        ("Web security and input validation", "Where should a web application enforce authorization for a protected operation?", ["On the server, for every protected request", "Only by hiding a button in the browser", "Only in a CSS stylesheet", "In an image alt attribute"], 0, "Client-side controls can be bypassed; the server must enforce permissions on each request."),
    ]),
}

EXISTING_TOPIC_RULES = {
    "CN": [("IP-layer device", 2), ("Internet organized", 0), ("transport protocol", 3), ("Ethernet switch", 1), ("router decrements", 2), ("DNS commonly", 4), ("real-time voice", 3), ("Two hosts", 2)],
    "DBMS": [("primary key", 0), ("split repeated", 1), ("filters individual", 2), ("foreign key", 0), ("groups orders", 2), ("transaction", 3), ("index", 4), ("SQL by concatenating", 4)],
    "DSA": [("undo the most recent", 0), ("frequent reads by numeric", 1), ("breadth-first", 3), ("dictionary-like", 2), ("Binary search is applied", 4), ("scans a list", 4), ("hash table lookup", 2), ("unsorted array", 4)],
    "OS": [("What is a process", 0), ("distinction between two threads", 0), ("context switch", 1), ("virtual memory", 2), ("necessary conditions associated with deadlock", 3), ("round-robin", 1), ("extremely short time slice", 1), ("shared counter", 3)],
    "PY": [("items =", 0), ("return a new list", 1), ("scores.get", 2), ("unique hashable", 2), ("loop visits each", 3), ("enumerate(names)", 3), ("result = result +", 4), ("possibly missing numeric", 4)],
}

# Additional original items for learner-facing pilot quizzes. They are mapped
# to the authored topic outline and kept pending until an instructor reviews
# the answer key and rationale. These extend coverage; they are not copied
# from the linked course materials.
PILOT_ADDITIONS = [
    ("DSA", 1, "A singly linked list has a head pointer. Which operation can be done in O(1) time without searching for a key?", ["Insert a node immediately after the head", "Find the middle node", "Delete the last node in a singly linked list", "Find a value by its contents"], 0, "Once the head node is known, its next link can be updated directly. The other operations generally need traversal.", "easy"),
    ("DSA", 0, "A queue is implemented with a circular array. What condition should distinguish a full queue from an empty one when only front and rear indices are stored?", ["Use an additional count or reserved-slot convention", "Set both indices to -1 after every insertion", "Sort the elements after each operation", "Use the largest element as the rear marker"], 0, "Circular indices alone can coincide in both states; a count or a reserved-slot convention disambiguates them.", "intermediate"),
    ("DSA", 2, "In hash-table separate chaining, what is stored in a bucket when multiple keys map to the same index?", ["A collection of entries for that bucket", "Only the newest key; all others are lost", "A sorted copy of the entire table", "The table's load factor only"], 0, "Separate chaining stores colliding entries together in a per-bucket collection, such as a list.", "easy"),
    ("DSA", 3, "A depth-first search on a graph is implemented iteratively. Which structure naturally holds vertices whose exploration is still pending?", ["Stack", "Queue", "Sorted array", "Disjoint-set parent array"], 0, "A stack reproduces the last-discovered-first-explored behaviour of recursive DFS.", "easy"),
    ("DSA", 4, "Which property makes merge sort useful when equal-key records must retain their original relative order?", ["It can be implemented as a stable sort", "It always uses constant auxiliary memory", "It requires the input to be nearly sorted", "It compares each pair exactly once"], 0, "A standard merge procedure can choose the left item first on equal keys, preserving stability.", "intermediate"),
    ("DSA", 4, "An algorithm performs n passes, and pass i scans the first i elements. What is its total asymptotic running time?", ["O(n²)", "O(n)", "O(log n)", "O(n log n)"], 0, "The total work is 1 + 2 + ... + n, which grows quadratically.", "intermediate"),
    ("DSA", 4, "A greedy algorithm is proposed for an optimization problem. What is sufficient evidence that it is correct for all valid inputs?", ["A proof that each local choice preserves an optimal solution", "One successful sample run", "A lower runtime on one input", "A larger test dataset without an argument"], 0, "Greedy correctness requires a property-based proof, such as an exchange argument; examples alone are not a proof.", "intermediate"),

    ("PY", 0, "What is the main difference between a tuple and a list in Python?", ["A tuple is immutable; a list is mutable", "A tuple can contain only numbers", "A list cannot be iterated", "A tuple is always sorted"], 0, "Tuples are immutable containers, whereas lists support item assignment and other in-place changes.", "easy"),
    ("PY", 0, "What values does `list(range(2, 6))` produce?", ["[2, 3, 4, 5]", "[2, 3, 4, 5, 6]", "[1, 2, 3, 4, 5]", "[3, 4, 5, 6]"], 0, "The stop value is excluded, so range(2, 6) yields 2 through 5.", "easy"),
    ("PY", 1, "Why is a mutable list usually a poor default value for a Python function parameter?", ["The same list object can be reused across calls", "Python converts it to a tuple automatically", "The function cannot read list values", "It forces the function to run asynchronously"], 0, "Default expressions are evaluated once when the function is defined; mutations can persist between calls.", "intermediate"),
    ("PY", 2, "What does a `finally` block provide in a try/except statement?", ["A place for cleanup that runs whether or not an exception occurred", "A way to retry every failed operation forever", "A guarantee that exceptions are hidden", "A declaration of a new module"], 0, "A finally block is used for cleanup and normally executes as control leaves the try statement.", "intermediate"),
    ("PY", 3, "What is a practical benefit of a generator that yields values one at a time?", ["It can avoid storing the entire result sequence in memory", "It makes every computation constant time", "It automatically sorts yielded values", "It allows a function to return multiple times at once"], 0, "Generators produce values lazily, which can reduce memory use for large or streaming sequences.", "intermediate"),
    ("PY", 3, "For a NumPy array `a`, what does `a[a > 0]` commonly return?", ["A new array containing elements that satisfy the condition", "The first positive element only", "A Boolean scalar", "A sorted version of `a`"], 0, "Boolean indexing selects elements whose corresponding mask values are true.", "intermediate"),
    ("PY", 4, "A function is expected to receive a list of numeric scores. What is the safest first step before computing their mean?", ["Validate the input type and handle empty or invalid values", "Assume all callers always pass valid data", "Convert every value to a dictionary key", "Catch every exception and return zero silently"], 0, "Explicit validation and a defined empty-input policy make failures predictable and prevent misleading results.", "easy"),

    ("DBMS", 0, "A table has several candidate keys. Which one should be selected as the primary key?", ["One candidate key chosen to identify each row", "Any non-unique descriptive column", "A column that permits duplicate rows", "A nullable column with no uniqueness rule"], 0, "A primary key is selected from candidate keys and must uniquely identify rows under the schema's constraints.", "easy"),
    ("DBMS", 1, "A relation stores multiple phone numbers in one comma-separated cell. Which normalization concern does this most directly raise?", ["Values are not atomic under the intended relational model", "The table has too many primary keys", "Every query must use a full outer join", "The table cannot be indexed"], 0, "First normal form expects attribute values to be atomic relative to the chosen domain and schema.", "intermediate"),
    ("DBMS", 2, "Which join returns only rows with matching join keys in both input relations?", ["INNER JOIN", "CROSS JOIN", "LEFT JOIN with no match handling", "UNION ALL"], 0, "An inner join retains combinations satisfying the join predicate; unmatched rows are excluded.", "easy"),
    ("DBMS", 2, "In SQL, why does `column = NULL` fail to test whether a value is missing?", ["NULL uses three-valued logic; use `IS NULL`", "NULL is always converted to zero", "Equality is allowed only for primary keys", "The query must use GROUP BY"], 0, "Comparisons with NULL evaluate to UNKNOWN rather than true or false, so IS NULL is the proper predicate.", "intermediate"),
    ("DBMS", 3, "A transaction has made changes that should be kept permanently. Which command normally confirms them?", ["COMMIT", "ROLLBACK", "EXPLAIN", "REVOKE"], 0, "COMMIT makes the transaction's changes durable according to the database's transaction semantics.", "easy"),
    ("DBMS", 4, "Why can a B-tree index support efficient equality lookups and range scans?", ["Its keys are maintained in an ordered, balanced search structure", "It stores every table row in one unsorted bucket", "It removes the need to compare keys", "It encrypts each query result"], 0, "Balanced ordered keys allow traversal to a matching key and then through a contiguous key range.", "intermediate"),
    ("DBMS", 4, "Which database permission design follows least privilege for an application that only reads course records?", ["Grant SELECT on the required data only", "Grant database-owner access", "Share the administrator password", "Allow every operation on every database"], 0, "Least privilege limits the account to the specific read capability and resources the application needs.", "easy"),

    ("CN", 2, "What does a subnet mask help an IPv4 host determine?", ["Which address bits identify the network prefix", "The remote server's TLS certificate", "The TCP application payload length", "The Ethernet frame's checksum algorithm"], 0, "The mask identifies the network portion of an address and helps decide whether a destination is local.", "easy"),
    ("CN", 1, "On an IPv4 local network, what problem does ARP solve?", ["Finding a link-layer address associated with a local IPv4 address", "Resolving a domain name to a public key", "Choosing a TCP congestion window", "Assigning an application port"], 0, "ARP maps a local IPv4 next-hop address to a link-layer address such as an Ethernet MAC address.", "intermediate"),
    ("CN", 4, "Why is HTTP GET expected to be safe with respect to server state?", ["Its intended semantics retrieve a representation without requesting a state change", "It always encrypts the connection", "It guarantees the response is cached", "It cannot include a query string"], 0, "HTTP defines GET as a safe method: clients do not request a state-changing action, though servers can still have incidental effects such as logging.", "intermediate"),
    ("CN", 4, "What does TLS primarily provide for a properly authenticated HTTPS connection?", ["Encryption in transit and integrity, plus peer authentication", "Guaranteed application correctness", "Protection against every phishing site", "A faster route through IP routers"], 0, "TLS protects the channel with confidentiality and integrity and can authenticate the server using certificates.", "intermediate"),
    ("CN", 3, "What is the main purpose of TCP congestion control?", ["Limit sending rates in response to network congestion signals", "Resolve hostnames", "Assign MAC addresses", "Guarantee constant end-to-end delay"], 0, "TCP congestion control adapts the sender's rate to avoid overloading the network path.", "intermediate"),
    ("CN", 2, "What does network address translation commonly allow in a small IPv4 network?", ["Multiple private hosts to share a public IPv4 address for outbound connections", "A private host to skip routing", "A MAC address to become a domain name", "Every packet to avoid checksums"], 0, "NAT commonly translates internal address/port tuples to an externally routable address and port mapping.", "easy"),
    ("CN", 2, "A host has address 192.168.10.34/24. Which address is its subnet's network address?", ["192.168.10.0", "192.168.10.34", "192.168.10.255", "192.168.0.0"], 0, "A /24 prefix leaves the final octet for host bits; clearing those bits gives 192.168.10.0.", "intermediate"),

    ("OS", 0, "On Unix-like systems, what is a zombie process?", ["A terminated process whose exit status has not yet been collected by its parent", "A process that is permanently using all CPU cores", "A thread waiting for a mutex", "A process whose code is stored in a file"], 0, "After termination, a small process-table entry can remain until the parent collects the child's status.", "intermediate"),
    ("OS", 0, "Which resources are typically private to each thread within one process?", ["Its stack and CPU register context", "The process's entire address space", "All open files in every operating system", "The executable file on disk"], 0, "Threads in a process share many resources, while each has its own execution context including registers and stack.", "intermediate"),
    ("OS", 2, "In demand paging, when does the operating system normally load a page into memory?", ["When a reference causes a page fault and the page is not resident", "At every timer interrupt", "Only when the process exits", "Whenever the CPU performs integer addition"], 0, "Demand paging brings in a page when it is first accessed while absent from physical memory.", "intermediate"),
    ("OS", 3, "What does a counting semaphore represent in a synchronization design?", ["A count of available instances of a resource or permits", "The address of the next instruction", "The number of files in a directory only", "A page-table entry"], 0, "A counting semaphore tracks permits; wait and signal operations coordinate access to a finite number of resources.", "intermediate"),
    ("OS", 3, "Which strategy prevents deadlock by ensuring at least one necessary deadlock condition can never hold?", ["Deadlock prevention", "Deadlock detection only", "Time slicing", "Page replacement"], 0, "Prevention designs the system so one of the necessary conditions, such as hold-and-wait, is excluded.", "intermediate"),
    ("OS", 4, "In a Unix-like file system, what does an inode generally store?", ["File metadata and pointers to data blocks, not the filename itself", "Only a user's password", "A complete network packet", "The CPU scheduling queue"], 0, "The directory maps names to inode numbers; the inode stores metadata and references to file data.", "intermediate"),
    ("OS", 1, "Why does a context switch have overhead even if the scheduler is fast?", ["The system must save and restore execution state and may disturb caches", "It permanently copies the entire disk to RAM", "It disables all interrupts until reboot", "It makes every thread run in parallel"], 0, "Switching requires state management and can reduce cache/TLB locality, so it is not free.", "intermediate"),

    ("DSA", 0, "A linked queue keeps pointers to both its front and rear nodes. What is the usual time to enqueue at the rear?", ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 0, "With a rear pointer, linking a new node and advancing the rear pointer take constant time.", "easy"),
    ("DSA", 1, "A dynamic array occasionally copies its elements when capacity grows. Why can append still be amortized O(1)?", ["Geometric capacity growth spreads each resize cost across many later appends", "Every append copies exactly one element", "The array never changes capacity", "Binary search avoids copying"], 0, "Doubling capacity means each expensive copy is separated by a number of cheap appends proportional to the new capacity.", "intermediate"),
    ("DSA", 3, "In a binary search tree with distinct keys and the standard ordering invariant, what sequence does an in-order traversal produce?", ["Keys in ascending order", "Keys in insertion order", "Keys in breadth-first order", "Only leaf keys"], 0, "Visiting left subtree, node, then right subtree yields sorted keys under the BST invariant.", "easy"),
    ("PY", 1, "Given `values = [1, 2, 3, 4]`, what does `values[1:3]` produce?", ["[2, 3]", "[1, 2, 3]", "[2, 3, 4]", "[1, 3]"], 0, "A slice includes the start index and excludes the stop index, so indices 1 and 2 are selected.", "easy"),
    ("DBMS", 1, "An order table repeats a customer's address on every order, so one address change requires many updates. Which design benefit would normalization aim to provide?", ["Reduce update anomalies by storing each fact in an appropriate relation", "Ensure every query uses a Cartesian product", "Remove all candidate keys", "Make duplicate facts mandatory"], 0, "Separating facts according to their dependencies avoids repeated updates and inconsistent copies.", "intermediate"),
    ("DBMS", 3, "Two transactions read the same inventory value, then each writes a decrement based on that old value. What anomaly can cause one decrement to be lost?", ["Lost update", "Phantom read only", "Dirty schema", "Index fragmentation"], 0, "If conflicting read-modify-write operations are not coordinated, one write can overwrite the other's update.", "intermediate"),
    ("CN", 0, "What is a benefit of a layer offering a stable service interface to the layer above it?", ["A lower layer can change internally without requiring every upper layer to change", "Packets no longer need destinations", "Every layer must use identical headers", "Network failures become impossible"], 0, "Layering defines service boundaries that reduce coupling between protocol implementations.", "intermediate"),
    ("CN", 0, "In protocol encapsulation, what does a layer commonly add before passing data to a lower layer?", ["Protocol-specific control information in a header", "The recipient's password in plaintext", "A guarantee of delivery", "A copy of every routing table"], 0, "Encapsulation adds layer-specific control fields around payload data; the exact fields depend on the protocol.", "easy"),
    ("CN", 1, "A learning Ethernet switch receives a unicast frame for a destination MAC address not yet in its forwarding table. What does it commonly do within that VLAN?", ["Flood the frame out eligible ports except the ingress port", "Discard every frame until reboot", "Send it to the DNS server", "Rewrite the destination IP address"], 0, "With an unknown destination, a switch floods the frame within the VLAN while learning source MAC addresses.", "intermediate"),
    ("OS", 2, "What mapping does a process page table help the operating system maintain?", ["Virtual page numbers to physical frames and associated permissions", "File names to DNS records", "CPU instructions to source comments", "Disk sectors to usernames only"], 0, "Page tables translate virtual addresses to physical frames and carry access-control information for mappings.", "intermediate"),
    ("OS", 4, "What does a file permission check primarily determine?", ["Whether a user or process may perform an operation such as read, write, or execute", "Which CPU core runs a process next", "How a virtual page is translated", "Whether a TCP packet is retransmitted"], 0, "File permissions participate in access control for operations on file-system objects.", "easy"),
    ("OS", 4, "What is the purpose of a journaling file system's journal?", ["Record intended updates to help recover a consistent state after a crash", "Store every process's CPU registers permanently", "Replace file permissions with encryption", "Guarantee storage hardware never fails"], 0, "A journal records changes so recovery can replay or discard incomplete operations after an interruption, depending on the design.", "intermediate"),

    ("DE", 0, "In 4-bit two's-complement representation, what signed value does 1011 represent?", ["−5", "11", "−4", "5"], 0, "The sign bit is set; inverting 1011 and adding one gives magnitude 0101, so the value is −5.", "intermediate"),
    ("DE", 0, "Using Boolean algebra, how can `A + A′B` be simplified?", ["A + B", "AB", "A′ + B", "A′B"], 0, "The absorption identity A + A′B = (A + A′)(A + B) = A + B.", "intermediate"),
    ("DE", 1, "What is the sum output of a full adder with inputs A, B, and carry-in Cᵢ?", ["A XOR B XOR Cᵢ", "A AND B AND Cᵢ", "A OR B OR Cᵢ", "A XNOR B only"], 0, "The full-adder sum bit is the parity of its three inputs.", "intermediate"),
    ("DE", 1, "Why are adjacent 1-cells grouped in powers of two on a Karnaugh map?", ["Each valid group eliminates one or more changing variables", "It increases the number of literals", "It ensures every term contains every variable", "It converts a sequential circuit into an analogue one"], 0, "A power-of-two group of adjacent minterms differs in selected variables that can be eliminated from the simplified term.", "intermediate"),
    ("DE", 2, "For an active-high NOR SR latch, which input combination is normally the forbidden condition?", ["S=1 and R=1", "S=0 and R=0", "S=1 and R=0 only", "S=0 and R=1 only"], 0, "Driving both set and reset high makes both NOR outputs low and leaves an invalid/ambiguous state on release.", "intermediate"),
    ("DE", 2, "What does the hold-time requirement specify for a flip-flop input?", ["How long data must remain stable after the active clock edge", "The minimum time between power-on and reset", "The time for a counter to wrap", "The maximum number of clock pins"], 0, "Hold time is the interval after the sampling edge during which input data must remain stable.", "easy"),
    ("DE", 3, "What is propagation delay in a logic circuit?", ["The time between an input transition and the corresponding output response", "The number of inputs on a gate", "The DC supply voltage", "The time required to write source code"], 0, "Propagation delay measures how long a circuit takes to respond to a change at its input.", "easy"),
    ("DE", 3, "In a two-level sum-of-products circuit, what can cause a static-1 hazard?", ["Adjacent input cases that should stay high are not covered by a common implicant", "The output has no Boolean expression", "Every product term contains a complemented variable", "The input clock has too many edges"], 0, "Unequal path delays can briefly drive the output low if adjacent 1-cases lack a redundant covering implicant.", "intermediate"),
    ("DE", 4, "How many distinct output codes can an ideal 8-bit ADC represent?", ["256", "8", "128", "512"], 0, "An n-bit converter has 2ⁿ possible codes; 2⁸ equals 256.", "easy"),
    ("DE", 4, "How are the binary bits converted to Gray code?", ["Keep the most-significant bit, then XOR each adjacent pair of binary bits", "Invert every binary bit", "Add one to the binary value", "Reverse the bit order only"], 0, "Gray conversion copies the MSB and forms each lower Gray bit as XOR of adjacent binary bits.", "intermediate"),
]


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    courses = {row["course_code"]: row["course_name"] for row in read_csv(ROOT / "courses.csv")}
    question_rows = read_csv(ROOT / "practice_question_bank.csv")
    course_topics = {}
    generated_questions = []
    generated_codes = set(CORE) - set(EXISTING_TOPIC_RULES)
    generated_question_signatures = set()
    for course_index, (code, (course_name, items)) in enumerate(CORE.items()):
        if courses.get(code) != course_name:
            raise ValueError(f"Course title mismatch for {code}: {courses.get(code)!r} != {course_name!r}")
        course_topics[code] = [f"{course_name} - {item[0]}" for item in items]
        for question_index, (topic, prompt, options, answer, explanation) in enumerate(items):
            # Rotate correct-answer positions deterministically so generated
            # questions do not teach a predictable answer letter.
            balanced_options = list(options)
            target_answer = (course_index + question_index) % len(balanced_options)
            balanced_options[answer], balanced_options[target_answer] = balanced_options[target_answer], balanced_options[answer]
            signature = (code, prompt, tuple(balanced_options), str(target_answer), explanation)
            generated_question_signatures.add(signature)
            if code not in generated_codes:
                continue
            generated_questions.append({
                "course_id": code,
                "quiz_title": f"{course_name} focused practice",
                "quiz_topic": "Course-wide practice",
                "question_topic": f"{course_name} - {topic}",
                "prompt": prompt,
                "options_json": json.dumps(balanced_options, ensure_ascii=False),
                "answer_index": str(target_answer),
                "explanation": explanation,
                "difficulty": "mixed",
                "review_status": "pending",
                "reviewer_name": "",
                "reviewer_role": "",
                "source_url": "",
                "review_notes": "",
                "review_date": "",
            })

    # The five pre-existing pilot sets are mapped below; replace any generated
    # rows from an earlier builder revision before validating their counts.
    def question_signature(row):
        return (
            row["course_id"], row["prompt"], tuple(json.loads(row["options_json"])),
            str(int(row["answer_index"])), row["explanation"],
        )

    question_rows = [row for row in question_rows
                     if row["course_id"] not in generated_codes
                     and question_signature(row) not in generated_question_signatures]

    # Make reruns deterministic: discard a prior copy of these additions by
    # prompt before rebuilding them from this source file.
    pilot_addition_prompts = {(code, prompt) for code, _, prompt, *_ in PILOT_ADDITIONS}
    question_rows = [row for row in question_rows if (row["course_id"], row["prompt"]) not in pilot_addition_prompts]

    # Map the existing five pilot sets from taxonomy labels to concrete topics.
    for code, rules in EXISTING_TOPIC_RULES.items():
        matching = [row for row in question_rows if row["course_id"] == code]
        if len(matching) != len(rules):
            raise ValueError(f"Expected {len(rules)} existing questions for {code}, found {len(matching)}.")
        topics = course_topics[code]
        for row, (needle, topic_index) in zip(matching, rules):
            if needle.casefold() not in row["prompt"].casefold():
                raise ValueError(f"Unexpected prompt order for {code}; refusing to remap question topics.")
            row["question_topic"] = topics[topic_index]
            row["quiz_topic"] = "Course-wide practice"

    for addition_index, (code, topic_index, prompt, options, answer, explanation, difficulty) in enumerate(PILOT_ADDITIONS):
        topics = course_topics[code]
        balanced_options = list(options)
        target_answer = (addition_index + 1) % len(balanced_options)
        balanced_options[answer], balanced_options[target_answer] = balanced_options[target_answer], balanced_options[answer]
        question_rows.append({
            "course_id": code,
            "quiz_title": f"{courses[code]} focused practice",
            "quiz_topic": "Course-wide practice",
            "question_topic": topics[topic_index],
            "prompt": prompt,
            "options_json": json.dumps(balanced_options, ensure_ascii=False),
            "answer_index": str(target_answer),
            "explanation": explanation,
            "difficulty": difficulty,
            "review_status": "pending",
            "reviewer_name": "",
            "reviewer_role": "",
            "source_url": "",
            "review_notes": "Original Nebula draft; instructor review required.",
            "review_date": "",
        })

    question_rows.extend(generated_questions)

    topic_rows = read_csv(ROOT / "topics.csv")
    retained = [row for row in topic_rows if row["course_code"] not in CORE]
    for code, topics in course_topics.items():
        for index, topic_name in enumerate(topics, 1):
            retained.append({
                "topic_id": f"{code}_T{index}", "course_code": code,
                "topic_name": topic_name,
                "difficulty_level": "Beginner" if index <= 2 else "Intermediate",
                "estimated_hours": "3",
            })
    write_csv(ROOT / "topics.csv", ["topic_id", "course_code", "topic_name", "difficulty_level", "estimated_hours"], retained)

    course_rows = read_csv(ROOT / "courses.csv")
    for row in course_rows:
        if row["course_code"] in CORE:
            row["total_topics"] = str(len(course_topics[row["course_code"]]))
    write_csv(ROOT / "courses.csv", ["course_code", "course_name", "category", "total_topics"], course_rows)

    active_topic_ids = {row["topic_id"] for row in retained}
    core_topic_ids = {f"{code}_T{index}" for code, topics in course_topics.items() for index in range(1, len(topics) + 1)}
    prerequisites = [row for row in read_csv(ROOT / "topic_prerequisite.csv")
                     if row["topic_id"] in active_topic_ids and row["prerequisite_topic_id"] in active_topic_ids
                     and row["topic_id"] not in core_topic_ids and row["prerequisite_topic_id"] not in core_topic_ids]
    next_id = max((int(row["id"]) for row in prerequisites), default=0) + 1
    for code, topics in course_topics.items():
        # A simple recommended progression; it remains advisory in the planner.
        for index in range(2, len(topics) + 1):
            prerequisites.append({
                "id": str(next_id), "topic_id": f"{code}_T{index}",
                "prerequisite_topic_id": f"{code}_T{index - 1}",
                "prerequisite_type": "Recommended",
            })
            next_id += 1
    write_csv(ROOT / "topic_prerequisite.csv", ["id", "topic_id", "prerequisite_topic_id", "prerequisite_type"], prerequisites)

    write_csv(ROOT / "practice_question_bank.csv", list(question_rows[0]), question_rows)
    print(f"Updated {len(CORE)} legacy course outlines; added {len(generated_questions)} questions; preserved {len(question_rows) - len(generated_questions)} existing questions.")


if __name__ == "__main__":
    main()
