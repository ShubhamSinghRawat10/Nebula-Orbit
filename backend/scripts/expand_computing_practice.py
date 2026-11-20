"""Add original, topic-balanced questions to computing and engineering courses.

Coverage is guided by public subject/topic outlines from PrepInsta and
GeeksforGeeks. This file contains independently authored Nebula questions;
none of their question text or answer explanations is copied.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BANK = DATA_DIR / "practice_question_bank.csv"

# Each course has two new items for each canonical topic. Existing five-item
# baselines plus this pack produce 15 total with three per outline topic.
# tuple: prompt, correct answer, three distractors, explanation, difficulty
PACKS = {
    "OOPS": [
        [
            ("A constructor is called while creating an object. Which state should it establish?", "A valid initial state that satisfies the class invariants", ["A global state shared by every class", "A final output before any method runs", "A replacement for the object's type"], "Construction should establish the conditions that make the new object valid to use.", "easy"),
            ("A class has a private field and a public method that validates updates to it. Which design idea does this illustrate?", "Encapsulation", ["Multiple inheritance", "Dynamic linking", "Tail recursion"], "Encapsulation controls access to internal state through a defined interface.", "easy"),
        ],
        [
            ("A subclass needs a service from another class but should not inherit its entire interface. Which relationship is usually safer?", "Composition", ["Copying the other class's source into every method", "Making every member public", "Using a global variable instead"], "Composition delegates to a collaborator while keeping the composed class's public contract focused.", "intermediate"),
            ("A base class promises that every subtype can be used wherever the base is expected. What must a subtype preserve?", "The base class's behavioural contract", ["The base class's private memory layout", "The same constructor parameter names", "The same source-file location"], "Substitutability depends on preserving expected behaviour, including preconditions and postconditions.", "intermediate"),
        ],
        [
            ("A call through a base-class reference invokes the override selected by the object's runtime type. What enables this?", "Dynamic dispatch", ["Lexical scoping", "Static storage duration", "Operator precedence"], "Dynamic dispatch resolves an overridable method using the runtime object's type.", "easy"),
            ("Two unrelated types expose the same required interface. Which benefit does programming to that interface provide?", "Client code can depend on the contract instead of either concrete type", ["The types must share identical internal data", "The interface removes runtime errors", "The compiler merges both objects into one"], "A stable interface decouples a client from the implementation chosen behind it.", "intermediate"),
        ],
        [
            ("A payment service hides provider-specific APIs behind one operation such as charge(). Which design choice is this?", "An abstraction over provider details", ["A public exposure of every provider credential", "An inheritance requirement for all clients", "A guarantee that network calls cannot fail"], "The abstraction exposes the capability a client needs while hiding provider-specific mechanics.", "easy"),
            ("Why keep a public interface small and cohesive?", "Callers need fewer implementation details and have fewer ways to misuse the type", ["It guarantees the implementation has no dependencies", "It prevents future implementations", "It makes every operation constant-time"], "A focused interface limits coupling and communicates the intended use clearly.", "intermediate"),
        ],
        [
            ("A method temporarily acquires a file handle. What should happen if processing throws an exception?", "The handle should still be released through guaranteed cleanup", ["The handle should remain open for every caller", "The exception should be silently converted to success", "The process should skip all remaining cleanup"], "Resource cleanup must run on both normal and exceptional paths, using the language's scoped cleanup mechanism.", "easy"),
            ("An object must never have a negative balance. Where should this rule be enforced?", "At the state-changing boundary that preserves the object's invariant", ["Only in a UI label", "Only in a comment", "After exporting the object to a log"], "Enforcing an invariant wherever state changes prevents invalid objects from escaping into the rest of the program.", "intermediate"),
        ],
    ],
    "AI": [
        [
            ("In a search problem, what does a state-space graph represent?", "Reachable states and the actions that connect them", ["Only the final answer text", "The source-code call stack", "A database schema with no transitions"], "Search algorithms explore states and action transitions to find a goal or a lowest-cost path.", "easy"),
            ("A heuristic estimates remaining distance to a goal. For optimal A* search, what property is sufficient for tree search?", "It never overestimates the true remaining cost", ["It is always larger than the true cost", "It changes randomly at each visit", "It is defined only at goal states"], "An admissible heuristic is optimistic; with nonnegative costs it supports A* optimality in tree search.", "intermediate"),
        ],
        [
            ("A rule-based expert system concludes a diagnosis from stored facts. What is the inference engine's role?", "Apply rules to facts to derive conclusions", ["Draw the user interface", "Compress the training images", "Assign database disk blocks"], "Inference applies the knowledge base's rules to known facts to derive further facts or decisions.", "easy"),
            ("Two rules can derive conflicting conclusions from the same facts. What should the system define?", "A conflict-resolution policy", ["A larger screen resolution", "A new programming language", "A random answer on every run"], "Rule systems need explicit priorities or another policy to decide which applicable rule fires.", "intermediate"),
        ],
        [
            ("A model performs well on training examples but poorly on unseen data. Which issue is most likely?", "Overfitting", ["Underflow in the display driver", "A perfectly calibrated model", "A guaranteed causal relationship"], "Overfitting occurs when learned patterns fit training-specific noise and fail to generalize.", "easy"),
            ("Why should preprocessing be fit using only the training split?", "To prevent information from the evaluation data leaking into training", ["To ensure the test set has fewer rows", "To make all labels identical", "To remove the need for validation"], "Fitting transformations on all data can leak evaluation statistics and make reported performance optimistic.", "intermediate"),
        ],
        [
            ("A classifier is evaluated on a highly imbalanced dataset. Why may accuracy alone mislead?", "A majority-class prediction can score highly while missing the minority class", ["Accuracy is always negative for imbalanced data", "It measures inference latency only", "It requires a probability threshold of zero"], "When one class dominates, accuracy may hide poor recall or precision on the less common class.", "easy"),
            ("A threshold is chosen after repeatedly inspecting the test set. What is the main methodological risk?", "The test set has become part of model selection", ["The training data is encrypted", "The model has fewer parameters", "The labels become self-supervised"], "Repeated tuning to test results leaks information and invalidates the test set as an independent estimate.", "intermediate"),
        ],
        [
            ("A training dataset underrepresents one user group. What risk should be examined before deployment?", "Unequal error rates or harmful performance gaps across groups", ["The model's file extension", "Whether the dataset sorts alphabetically", "The font used in the dashboard"], "Coverage gaps can create group-dependent errors, so representative evaluation and impact analysis are needed.", "easy"),
            ("A model recommendation affects a high-impact decision. Which practice improves accountability?", "Record intended use, limitations, evaluation evidence, and a human review path", ["Hide the model's limitations", "Use training accuracy as the only evidence", "Remove all monitoring after release"], "Documentation, appropriate human oversight, and post-deployment monitoring help manage risk and explain decisions.", "intermediate"),
        ],
    ],
    "SE": [
        [
            ("A requirement says 'the dashboard should be fast.' What change makes it more testable?", "State a measurable response-time target and its measurement conditions", ["Add more adjectives", "Move it to a different document", "Replace it with a colour preference"], "A measurable threshold and context let a test determine whether the requirement is met.", "easy"),
            ("Why should acceptance criteria be agreed before implementation is declared complete?", "They make expected outcomes observable to both developers and stakeholders", ["They guarantee there will be no defects", "They replace all user research", "They make source control unnecessary"], "Shared acceptance criteria reduce ambiguity about what counts as satisfying a requirement.", "intermediate"),
        ],
        [
            ("A module changes frequently because it directly depends on several database vendors. Which architectural move reduces that coupling?", "Put a stable application-owned interface between the module and vendor adapters", ["Duplicate vendor code in every caller", "Make the module depend on all vendors at once", "Remove error handling"], "A stable abstraction and adapters isolate vendor-specific details from the rest of the application.", "intermediate"),
            ("A team splits a system into services. What property should guide the boundary?", "A cohesive responsibility with explicit contracts and manageable operational cost", ["The number of source files per developer", "A rule that every table gets its own service", "A goal of maximizing network calls"], "Service boundaries should align with cohesive capabilities while accounting for deployment and communication overhead.", "intermediate"),
        ],
        [
            ("A test verifies the behaviour of a function with dependencies replaced by fakes. What level is this?", "Unit testing", ["Acceptance testing", "Disaster-recovery testing", "Load testing"], "A unit test focuses on a small unit and controls its collaborators to isolate behaviour.", "easy"),
            ("A requirement is changed after a regression bug is fixed. What is the most useful test addition?", "A regression test that reproduces the changed or previously failing behaviour", ["A screenshot of the source code", "A test that only checks the branch name", "No test because the bug was fixed once"], "A regression test prevents the same failure from returning as the code evolves.", "easy"),
        ],
        [
            ("Why use a pull request for a change?", "It gives reviewers a focused diff and a place to discuss evidence before integration", ["It guarantees every change is correct", "It automatically documents every runtime decision", "It removes the need for branches"], "A pull request supports review and discussion but does not replace tests or guarantee correctness.", "easy"),
            ("A commit contains unrelated refactoring and a feature. Why split it when practical?", "Smaller coherent changes are easier to review, test, and revert", ["Git only supports one file per commit", "It makes merge conflicts impossible", "It hides the change from collaborators"], "A focused history improves traceability and makes a targeted rollback less risky.", "easy"),
        ],
        [
            ("A release introduces a severe fault. What is the purpose of a rollback plan?", "Restore a known-good version or mitigate impact while the cause is investigated", ["Prove the release could never fail", "Replace incident communication", "Erase all user data"], "Rollback is a recovery option that limits impact; it does not replace diagnosis or data-safety planning.", "easy"),
            ("A team wants to improve maintainability. Which signal is more useful than counting lines of code alone?", "Change failure rate and effort to safely modify or understand a component", ["The number of folders in the repository", "The colour of the IDE theme", "The total bytes in commit messages"], "Maintainability concerns the effort and risk of change; it should be assessed with relevant quality and delivery evidence.", "intermediate"),
        ],
    ],
    "WT": [
        [
            ("A form control has a visible label. Which markup relationship helps assistive technology identify it?", "Associate the label's for value with the control's id", ["Put the label in a CSS comment", "Use a placeholder as the only label", "Set the control's display to inline"], "An explicit label-control association exposes the control's accessible name and enlarges the clickable label target.", "easy"),
            ("Why prefer semantic elements such as main and nav when appropriate?", "They communicate document structure to browsers and assistive technologies", ["They automatically encrypt all content", "They guarantee a responsive layout", "They replace headings"], "Semantic HTML conveys landmarks and roles that help people and software navigate the page.", "easy"),
        ],
        [
            ("A two-column layout should collapse to one column on a narrow screen. Which CSS feature is designed for this?", "A media query that changes the layout at a breakpoint", ["A JavaScript alert on every resize", "An HTML comment", "A fixed-width image"], "Media queries adapt layout rules to viewport characteristics such as width.", "easy"),
            ("Why can minmax(0, 1fr) help a grid column containing long text?", "It allows the track to shrink below the min-content width instead of forcing overflow", ["It makes the column exactly zero pixels", "It disables grid placement", "It prevents text wrapping everywhere"], "A zero minimum permits the flexible track to shrink, while content can wrap or otherwise fit its container.", "intermediate"),
        ],
        [
            ("A click handler is attached to a button after the page loads. Which DOM operation commonly selects it by id?", "document.getElementById", ["window.fetchAllElements", "CSSStyleSheet.getResponse", "history.findNode"], "The DOM API document.getElementById retrieves the element with the specified id.", "easy"),
            ("A list is rendered from user-provided text. Why use textContent instead of assigning the value to innerHTML?", "It treats the input as text instead of parsing it as markup", ["It encrypts the text in transit", "It validates the user's identity", "It converts all strings to numbers"], "textContent avoids interpreting a user string as HTML, reducing a common DOM injection risk.", "intermediate"),
        ],
        [
            ("A client fetches a resource and expects the response body to contain JSON. What should it check before parsing?", "Whether the response status is acceptable and the body matches the expected format", ["Whether the URL contains a fragment", "Whether the page uses a serif font", "Whether the request was made from a button"], "HTTP fetch does not reject solely because of 4xx/5xx statuses; clients should check response status and handle parsing errors.", "intermediate"),
            ("An API creates a new resource successfully. Which HTTP status is commonly appropriate?", "201 Created", ["204 No Content in every case", "304 Not Modified", "418 I'm a teapot"], "201 indicates that a request created a resource; a Location header may identify it.", "easy"),
        ],
        [
            ("A backend receives a string where an integer is expected. What should it do before using the value in a query?", "Validate the type and range, then use a parameterized query", ["Concatenate it directly into SQL", "Trust it because it came from a browser", "Disable database constraints"], "Server-side validation and parameterized queries reduce injection and invalid-input risks.", "easy"),
            ("Why is output encoding context-specific?", "Different output contexts interpret characters differently, such as HTML, attributes, or JavaScript", ["All encodings are interchangeable", "Encoding is needed only for passwords", "It makes authorization checks redundant"], "Safe encoding depends on the output context; one generic escaping rule is not correct everywhere.", "intermediate"),
        ],
    ],
    "CD": [
        [
            ("A lexer reads `total = 7` and groups characters into identifiers, an operator, and a number. What are these groups called?", "Tokens", ["Basic blocks", "Stack frames", "Page faults"], "Lexical analysis turns a character stream into tokens, often attaching a token kind and value.", "easy"),
            ("A language allows `==` as one operator. Why should a lexer generally choose it over two `=` tokens when both rules match?", "The longer-match rule recognizes the intended multi-character token", ["It makes the parser context-free grammar regular", "It removes the need for tokenization", "It changes the source program's values"], "Lexers commonly use maximal munch so the longest valid token is selected at a position.", "intermediate"),
        ],
        [
            ("A grammar has a production E → E + T. What problem can this cause for a simple top-down predictive parser?", "Left recursion can make the parser recurse without consuming input", ["It forces every parse tree to be balanced", "It makes all tokens ambiguous by definition", "It prevents any bottom-up parser from working"], "Immediate left recursion must be transformed or specially handled for a basic recursive-descent parser.", "intermediate"),
            ("For a predictive parser, what does an LL(1) table use to choose a production?", "The current nonterminal and one lookahead token", ["Only the whole source file's byte length", "The previous program's output", "A machine-learning probability from the linker"], "LL(1) parsing selects a production from the nonterminal and a single lookahead symbol.", "easy"),
        ],
        [
            ("A compiler uses a symbol table while checking an identifier. Which information is commonly stored there?", "The identifier's declared attributes such as type and scope", ["Only the final executable's checksum", "The keyboard layout of the programmer", "A list of runtime network packets"], "Symbol tables associate names with information needed for semantic checks and later compilation phases.", "easy"),
            ("The parser accepts `x + true`, but the language requires numeric operands. Which phase should report the mismatch?", "Semantic analysis", ["Lexical analysis", "Link-time dead-code removal", "Disk scheduling"], "The token sequence and grammar may be valid while operand types violate the language's semantic rules.", "easy"),
        ],
        [
            ("Why convert source code into an intermediate representation (IR)?", "It provides a structured form that separates front-end parsing from later optimizations or targets", ["It guarantees the source has no errors", "It replaces all runtime libraries", "It stores source comments as machine instructions"], "An IR creates a useful boundary between language-specific analysis and machine-specific code generation.", "easy"),
            ("In a control-flow graph, what does a basic block represent?", "A straight-line instruction sequence with one entry and one exit", ["A file containing every function in a project", "A set of unrelated tokens", "A memory page shared by all processes"], "A basic block has no internal branch target or branch out except at its boundary.", "intermediate"),
        ],
        [
            ("When is a compiler optimization safe?", "When it preserves the program's observable behaviour under the language rules", ["Whenever it reduces source-code length", "Only when it changes every variable name", "When it removes all control flow"], "An optimization must preserve the semantics the language promises, including relevant side effects and exceptions.", "easy"),
            ("A compiler emits machine instructions for a target architecture. Which phase is primarily responsible?", "Code generation", ["Lexical analysis", "Source formatting", "Requirement elicitation"], "Code generation maps the compiler's intermediate representation to target instructions and calling conventions.", "easy"),
        ],
    ],
    "COA": [
        [
            ("For an n-bit unsigned binary word, what is its largest representable value?", "2ⁿ − 1", ["2ⁿ", "n²", "2n − 1"], "The bit patterns range from 0 through 2ⁿ−1, giving 2ⁿ distinct values.", "easy"),
            ("Why is sign extension used when widening a two's-complement signed value?", "To preserve its numeric value by copying the sign bit into new high-order bits", ["To turn it into unsigned magnitude", "To reverse the bit order", "To clear all negative values"], "Replicating the sign bit preserves the signed value when the word width increases.", "intermediate"),
        ],
        [
            ("What does an instruction set architecture specify to software?", "The programmer-visible instructions, registers, and related execution contract", ["The exact colour of the processor package", "The source code of every operating system", "The physical layout of every cache cell"], "The ISA is the interface between software and processor implementations.", "easy"),
            ("In a single-bus datapath, why may an instruction need multiple cycles?", "The shared bus cannot transfer several independent values at the same instant", ["The ALU cannot perform arithmetic", "Registers cannot store values", "The instruction has no opcode"], "A shared datapath resource creates scheduling constraints on transfers within one cycle.", "intermediate"),
        ],
        [
            ("A pipeline instruction depends on a result produced by the preceding instruction. What hazard is this?", "A data hazard", ["A syntax error", "A cache-capacity guarantee", "A page-table hit"], "A data dependency can prevent the next instruction from using an operand until it is available.", "easy"),
            ("Why can a branch cause a control hazard in a pipeline?", "The next instruction address may be unknown until the branch decision is resolved", ["The branch deletes the instruction register", "Branches cannot change the program counter", "The ALU loses its clock"], "The pipeline may fetch instructions from the wrong path before the branch outcome is known.", "intermediate"),
        ],
        [
            ("A cache hit occurs when what happens?", "The requested block is found in the cache", ["The requested block is deleted from main memory", "The CPU skips address translation", "The cache line has never been used"], "A hit means the requested data is present in the cache at lookup time.", "easy"),
            ("Which locality explains why recently accessed data may be accessed again soon?", "Temporal locality", ["Spatial locality", "Instruction alignment", "Write-through locality"], "Temporal locality is reuse of the same or nearby item over a short time interval.", "easy"),
        ],
        [
            ("Why does a device commonly use an interrupt instead of having the CPU poll it continuously?", "The device can signal when service is needed, allowing the CPU to do other work meanwhile", ["Interrupts remove the need for an operating system", "Polling always has lower latency", "Interrupts make every I/O operation synchronous"], "Interrupt-driven I/O avoids repeated status checks when the device has nothing to report.", "easy"),
            ("What is the purpose of a DMA controller in many systems?", "Transfer data between an I/O device and memory with limited CPU involvement", ["Compile device drivers", "Replace every CPU register", "Encrypt the instruction set"], "DMA can move blocks of data while reducing per-byte CPU work.", "intermediate"),
        ],
    ],
    "TOC": [
        [
            ("A DFA processes one input symbol at a time and has exactly one next state for each state-symbol pair. What follows?", "Its computation path is unique for each input", ["It must use a stack", "It accepts every string", "It can only process finite languages"], "Deterministic transitions define one run for a given input; acceptance depends on its final state.", "easy"),
            ("What does it mean for a language to be regular?", "Some finite automaton recognizes exactly its strings", ["It must contain every possible string", "It requires an unbounded stack", "It has a context-sensitive grammar only"], "Regular languages are precisely those recognized by finite automata and described by regular expressions.", "easy"),
        ],
        [
            ("In a regular expression, what does `a|b` conventionally denote?", "Either the symbol a or the symbol b", ["The string ab only", "Zero or more copies of a followed by b", "The empty language"], "Alternation denotes a choice between the expressions on either side.", "easy"),
            ("An NFA has two transitions on the same symbol from one state. Does that make its recognized language non-regular?", "No; every NFA has an equivalent DFA", ["Yes; NFAs recognize only context-free languages", "Yes; no automaton can have two transitions", "No; it means the language is empty"], "Nondeterminism does not increase the expressive power of finite automata.", "intermediate"),
        ],
        [
            ("A context-free grammar has S → aSb | ε. Which form of strings can it generate?", "aⁿbⁿ for n ≥ 0", ["All strings over {a,b}", "aⁿbᵐ for any unequal n and m only", "Prime-length strings of a"], "Each recursive use adds one a before and one b after; the empty production stops the recursion.", "intermediate"),
            ("What does a parse tree show for a context-free grammar?", "How a derivation expands grammar variables into the generated string", ["The runtime stack frames of the parser implementation only", "The shortest network route", "A set of transition costs"], "A parse tree records the hierarchical production choices used to derive a string.", "easy"),
        ],
        [
            ("What extra memory capability distinguishes a pushdown automaton from a finite automaton?", "An unbounded stack", ["A second input tape", "A database index", "A fixed number of extra states only"], "A pushdown automaton has stack memory, enabling recognition of many context-free languages.", "easy"),
            ("For balanced parentheses, what should an automaton push when it reads an opening parenthesis?", "A marker that records an unmatched opening symbol", ["A final accept state", "The entire remaining input", "A marker that erases all prior opens"], "The stack tracks unmatched opens so each close can remove one; acceptance also requires no unmatched opens remain.", "intermediate"),
        ],
        [
            ("What is a Turing machine's tape used to model?", "An unbounded read/write work space for a computation", ["A finite-state transition table only", "A sorted database table", "A network packet header"], "The tape provides the machine's general-purpose memory in the classical model.", "easy"),
            ("A language is decidable if there is a machine that does what for every input?", "Halts and answers membership correctly", ["Accepts members but may loop on nonmembers", "Runs in constant time", "Uses no memory"], "Decidability requires a total procedure that halts on both members and nonmembers.", "intermediate"),
        ],
    ],
    "C": [
        [
            ("In C, what does converting a negative signed integer to an unsigned type do?", "It yields the value congruent modulo one more than the unsigned type's maximum", ["It is always undefined behavior", "It clamps the value to zero", "It preserves the negative sign in the unsigned object"], "Conversion to an unsigned integer type is defined modulo 2ⁿ for an n-bit unsigned type.", "intermediate"),
            ("Why should a program avoid assuming that `int` is exactly 32 bits on every C implementation?", "The C standard permits implementation-defined integer widths subject to minimum ranges", ["The type is always 8 bits", "Integer types cannot represent negative values", "The compiler chooses a new width for each variable at runtime"], "Portable code relies on the guarantees of the language or uses exact-width types when available.", "easy"),
        ],
        [
            ("In C, what does `break` do inside a loop?", "Immediately exits the innermost enclosing loop", ["Skips only the current iteration", "Restarts the program", "Exits every function on the call stack"], "break transfers control out of the nearest enclosing loop or switch statement.", "easy"),
            ("What is the effect of `continue` in a `for` loop?", "It proceeds to the loop's iteration expression, then checks the condition", ["It exits the loop permanently", "It skips the condition forever", "It returns from the function"], "In a for loop, continue transfers to the iteration expression before the next condition check.", "intermediate"),
        ],
        [
            ("Why must a C string buffer include space for the terminating null character?", "String operations use `\\0` to identify the end of the string", ["The null byte stores the string length", "It is required after every array element", "It prevents all buffer overflows automatically"], "A C string is a sequence of characters terminated by a null character, which occupies a byte in the array.", "easy"),
            ("An array has 10 elements indexed from 0. Which index is outside its bounds?", "10", ["0", "5", "9"], "The valid indices are 0 through 9; index 10 is one past the last element and must not be dereferenced.", "easy"),
        ],
        [
            ("A function receives `int *p`. What does `*p = 4` do when p points to a valid int object?", "Stores 4 in the pointed-to integer", ["Changes p to point to address 4", "Returns the address of p", "Allocates a new integer automatically"], "The unary * operator dereferences the pointer to access the object it designates.", "easy"),
            ("What is a safe way for a C function to report both success and a computed integer result?", "Return a status and write the result through a validated output pointer", ["Return an uninitialized local variable", "Store the result in an unrelated global without documentation", "Return the address of a local variable"], "An output parameter can carry the result while a return value communicates status, provided the pointer contract is clear.", "intermediate"),
        ],
        [
            ("What happens to an automatic local variable when its block exits?", "Its lifetime ends", ["It becomes static automatically", "It is guaranteed to be zeroed", "It remains valid until the next reboot"], "A non-static automatic object exists only during execution of its enclosing block.", "easy"),
            ("Why can returning a pointer to a local automatic array cause undefined behavior?", "The array's lifetime ends when the function returns", ["Pointers cannot refer to arrays", "The array becomes global", "The compiler always moves it to the heap"], "After return, the local array no longer exists, so using the returned pointer is invalid.", "easy"),
        ],
    ],
    "CPP": [
        [
            ("Why should a C++ base class with virtual functions usually have a virtual destructor?", "Deleting a derived object through a base pointer must destroy the derived part correctly", ["It makes constructors virtual", "It disables dynamic dispatch", "It prevents stack allocation"], "A virtual destructor ensures destruction dispatches through the dynamic type when deleting via a base pointer.", "intermediate"),
            ("What does RAII associate a resource's lifetime with?", "The lifetime of an owning object", ["The order of source files alphabetically", "A global sleep timer", "A manual comment in the destructor's caller"], "RAII uses construction and destruction to acquire and release resources predictably.", "easy"),
        ],
        [
            ("In a function template, what does a type parameter allow?", "The function's implementation to be instantiated for compatible types", ["The compiler to ignore type checking", "A runtime type to change the source code", "The function to accept only one hard-coded type"], "Templates parameterize code over types or values and are instantiated when used with suitable arguments.", "easy"),
            ("Why can a template definition need to be visible at its point of instantiation?", "The compiler must generate the specialization from the definition", ["Templates execute only in the preprocessor", "The linker downloads missing source from the internet", "Type parameters are stored in the executable as source text"], "Most C++ template instantiation requires the definition to be available during compilation.", "intermediate"),
        ],
        [
            ("What is the main advantage of `std::vector` over a raw fixed-size array when the number of elements changes at runtime?", "It manages a resizable contiguous sequence and its storage", ["It guarantees constant-time insertion at every position", "It stores elements only on disk", "It removes the need to manage element types"], "A vector grows dynamically while providing contiguous storage and automatic lifetime management.", "easy"),
            ("What does `std::sort` require from the range supplied to it?", "A valid iterator range and an ordering consistent enough to meet its comparator requirements", ["A null-terminated string", "A database connection", "Elements that are already in reverse order"], "The algorithm operates on an iterator range and relies on a strict weak ordering for correct results.", "intermediate"),
        ],
        [
            ("A base pointer refers to a derived object, and a called method is virtual. Which implementation is selected?", "The override for the object's dynamic type", ["Always the base implementation", "The last function alphabetically", "The constructor with the most parameters"], "Virtual calls use dynamic dispatch when invoked through an appropriate base reference or pointer.", "easy"),
            ("Why mark a method `override` in a derived class?", "The compiler checks that it actually overrides a virtual base method", ["It makes the method private automatically", "It disables runtime dispatch", "It converts the method into a template"], "override catches signature mismatches that would otherwise accidentally declare a new method.", "easy"),
        ],
        [
            ("A move constructor transfers ownership from a temporary object. What should happen to the source object?", "It remains valid but may be in an unspecified state permitted by its type", ["It is automatically deleted from memory", "It must keep owning the transferred resource", "It becomes a copy of the destination"], "Moved-from objects must remain destructible and assignable unless a type documents stronger guarantees.", "intermediate"),
            ("Why catch an exception by `const` reference when handling a polymorphic exception object?", "It avoids slicing and unnecessary copying while preserving the dynamic type", ["It converts the exception to an integer", "It prevents stack unwinding", "It makes every exception recoverable"], "Catching by base value can slice derived information; a const reference preserves the thrown object's type.", "intermediate"),
        ],
    ],
    "JAVA": [
        [
            ("What does the Java Virtual Machine execute after Java source compilation?", "Bytecode", ["Raw SQL statements", "CSS rules", "C preprocessor macros"], "The Java compiler emits class-file bytecode for execution by a compatible JVM.", "easy"),
            ("Why should code use `BigDecimal` rather than binary floating point for exact decimal currency arithmetic?", "Decimal values such as 0.1 may not be represented exactly in binary floating point", ["BigDecimal is always faster", "Floating point cannot represent negative numbers", "BigDecimal automatically applies tax rules"], "Binary floating-point rounding can make decimal fractions inexact; decimal arithmetic can represent required decimal scales explicitly.", "intermediate"),
        ],
        [
            ("A Java interface declares a contract used by several unrelated classes. What does implementing the interface provide?", "A type-level promise to provide the declared operations", ["Shared object fields from every implementer", "Automatic database persistence", "A guarantee that methods never throw"], "Interfaces let clients depend on a common contract without requiring a shared implementation hierarchy.", "easy"),
            ("Why prefer immutable value objects for data that is shared across threads?", "Their state cannot be changed after construction, reducing synchronization hazards", ["They make all operations asynchronous", "They cannot be garbage collected", "They are always stored in the JVM stack"], "Immutability prevents concurrent callers from racing to update the object's state.", "intermediate"),
        ],
        [
            ("What is a benefit of Java generics such as `List<String>`?", "Compile-time type checking of elements without routine casts", ["Automatic encryption of list elements", "A guarantee that the list is thread-safe", "Storage of each element in a separate process"], "Generics express the element type and let the compiler catch incompatible operations.", "easy"),
            ("What can happen when an unchecked raw collection is assigned to a parameterized collection?", "A ClassCastException may occur later when an element is retrieved as the wrong type", ["The JVM rewrites every object safely", "All elements are removed at compile time", "The collection becomes immutable"], "Raw types bypass generic checks, shifting a possible type failure to runtime.", "intermediate"),
        ],
        [
            ("Which construct ensures a closeable resource is closed when its block exits, including on exceptions?", "try-with-resources", ["A `finally` comment", "A static initializer", "A synchronized modifier"], "try-with-resources closes each AutoCloseable resource automatically at the end of the statement.", "easy"),
            ("When should a method declare a checked exception rather than silently catch it?", "When callers can meaningfully handle or propagate the failure", ["Whenever a local variable is null", "To avoid validating inputs", "Only to improve performance"], "A checked exception makes a recoverable failure explicit in the API so callers can handle or propagate it.", "intermediate"),
        ],
        [
            ("Two threads update a shared counter with a read-increment-write sequence. What can occur without synchronization?", "A lost update due to a race condition", ["The counter is guaranteed to increment twice", "The JVM changes the counter's declared type", "The thread scheduler becomes deterministic"], "The compound operation is not atomic; interleaving can overwrite one thread's update.", "easy"),
            ("What does the `synchronized` monitor provide for a correctly shared Java object?", "Mutual exclusion and a happens-before relationship around monitor release/acquisition", ["A guarantee of fair scheduling", "A distributed lock across all computers", "A guarantee that the block cannot throw"], "Monitor synchronization provides mutual exclusion and memory-visibility ordering for threads using the same monitor.", "intermediate"),
        ],
    ],
    "DGA": [
        [
            ("An algorithm performs 3n² + 2n + 7 operations. What is its asymptotic growth class?", "Θ(n²)", ["Θ(n)", "Θ(log n)", "Θ(2ⁿ)"], "The quadratic term dominates as n grows, and the expression is bounded above and below by constants times n².", "easy"),
            ("Why distinguish worst-case complexity from average-case complexity?", "They describe different guarantees over inputs and distributions", ["They are always numerically identical", "Worst case counts source-code lines", "Average case is defined only for randomized algorithms"], "Worst-case analysis bounds every input of a given size, while average-case analysis depends on an input distribution.", "intermediate"),
        ],
        [
            ("Merge sort divides an input into halves and merges in linear time. What is its recurrence?", "T(n) = 2T(n/2) + Θ(n)", ["T(n) = T(n−1) + Θ(1)", "T(n) = 2T(n−1) + Θ(1)", "T(n) = T(n/2) + Θ(1)"], "Two half-size recursive sorts are followed by a linear merge.", "easy"),
            ("A divide-and-conquer algorithm makes one half-size recursive call and does constant extra work. What is its recurrence?", "T(n) = T(n/2) + Θ(1)", ["T(n) = 2T(n/2) + Θ(n)", "T(n) = T(n−1) + Θ(n)", "T(n) = nT(n) + Θ(1)"], "The recurrence includes one subproblem of half size and constant work outside the recursive call.", "intermediate"),
        ],
        [
            ("A breadth-first search on an unweighted graph finds what kind of shortest path?", "A path with the fewest edges from the source", ["A path with the fewest vertices in the whole graph", "A minimum spanning tree for weighted edges", "A longest simple path"], "BFS explores vertices in nondecreasing edge distance from the source in an unweighted graph.", "easy"),
            ("Why does Dijkstra's algorithm require nonnegative edge weights for its standard correctness argument?", "A settled vertex cannot later receive a cheaper path through a negative edge", ["It stores distances as strings", "It uses a stack rather than a queue", "It only works on trees"], "Negative edges can invalidate the greedy finalization of a distance when a later path reduces it.", "intermediate"),
        ],
        [
            ("A greedy algorithm is proposed for a problem. What is needed to justify its correctness?", "An argument that a locally chosen step can be part of some globally optimal solution", ["Evidence that it uses the fewest lines of code", "A benchmark on one input only", "A claim that dynamic programming is slower"], "A greedy-choice proof, often paired with an exchange argument or invariant, establishes global optimality.", "intermediate"),
            ("In a minimum spanning tree problem, why may a lightest edge crossing a cut be selected safely?", "The cut property guarantees some minimum spanning tree contains that edge", ["Every graph edge is a bridge", "The edge has the smallest endpoint label", "The graph must be directed"], "The cut property provides a correctness basis for algorithms such as Prim's and Kruskal's.", "intermediate"),
        ],
        [
            ("What does overlapping subproblems mean in dynamic programming?", "The recursive solution encounters the same subproblem states repeatedly", ["Every subproblem has a different input size", "The final answer is always a graph", "The algorithm must use recursion at runtime"], "Memoization or tabulation avoids recomputing repeated subproblems.", "easy"),
            ("What is the purpose of a base case in a dynamic-programming recurrence?", "Provide known values that stop the recurrence and anchor larger solutions", ["Increase recursion depth", "Remove the optimal-substructure requirement", "Sort the input before every lookup"], "Base cases initialize the recurrence so it can compute solutions for larger states.", "easy"),
        ],
    ],
    "CS": [
        [
            ("Which security property primarily prevents an unauthorized party from reading protected data?", "Confidentiality", ["Availability", "Non-repudiation", "Fault tolerance"], "Confidentiality limits information disclosure to authorized parties.", "easy"),
            ("A threat model is created before choosing controls. What does it help identify?", "Assets, trust boundaries, likely threats, and relevant attack paths", ["Only the product's colour palette", "A guaranteed list of every future vulnerability", "The source-control branch naming scheme"], "Threat modelling structures security analysis around what matters and how it may be attacked.", "intermediate"),
        ],
        [
            ("What is the security benefit of multi-factor authentication?", "An attacker must compromise more than one independent factor", ["It makes passwords impossible to phish", "It removes the need for authorization", "It encrypts every network packet automatically"], "MFA combines factors such as knowledge, possession, or inherence; it reduces some credential-only attacks but is not phishing-proof by itself.", "easy"),
            ("A user may view reports but must not edit them. Which control should the server enforce?", "Authorization for the requested action and resource", ["Authentication only", "A hidden UI button only", "Client-side input styling"], "Authentication establishes identity; authorization checks whether that identity may perform a specific action.", "easy"),
        ],
        [
            ("What security property does a cryptographic hash provide when used to verify a downloaded file?", "Evidence that the file matches the expected digest, assuming a trusted digest and secure hash", ["Confidentiality of the file contents", "Proof of who authored the file by itself", "Automatic correction of corrupted bytes"], "A matching strong hash can detect alteration relative to a trusted digest, but it does not alone authenticate the publisher.", "intermediate"),
            ("What does a digital signature allow a verifier to check?", "That the signed data was signed by the holder of a private key and was not altered", ["That the data is secret", "That the signer never made a mistake", "That the public key is trusted without validation"], "Signature verification binds integrity and key possession; identity trust still depends on key validation and context.", "intermediate"),
        ],
        [
            ("Why use a parameterized SQL query with untrusted input?", "The database treats the supplied value as data rather than executable SQL syntax", ["It encrypts the database file", "It automatically grants least privilege", "It prevents every denial-of-service attack"], "Parameter binding separates query structure from values and is a primary SQL-injection defense.", "easy"),
            ("A browser displays user-provided content. Which defense helps prevent stored cross-site scripting?", "Context-aware output encoding and safe DOM APIs", ["Hiding the content with CSS", "Checking the input only for a dot", "Disabling server logs"], "Untrusted content should be encoded for the output context; safe DOM sinks avoid interpreting it as executable markup.", "intermediate"),
        ],
        [
            ("After detecting a compromised account, why preserve relevant logs before cleanup?", "They may help establish scope, timeline, and affected systems", ["Logs guarantee the attacker can be identified", "They replace containment", "They make backups unnecessary"], "Evidence preservation supports investigation and response while containment proceeds safely.", "easy"),
            ("What should an incident response plan define before an incident occurs?", "Roles, escalation paths, containment steps, communications, and evidence handling", ["A promise that no incident will happen", "A public copy of all credentials", "A rule to delete every log automatically"], "Predefined responsibilities and procedures reduce confusion during time-sensitive response.", "intermediate"),
        ],
    ],
    "CC": [
        [
            ("A team consumes a managed platform runtime but does not manage the underlying virtual machines. Which service model is closest?", "Platform as a Service (PaaS)", ["Bare-metal colocation", "Infrastructure as a Service only", "On-premises desktop support"], "PaaS abstracts much of the runtime and infrastructure operations while the customer deploys application code.", "easy"),
            ("In a cloud service model, which responsibility usually remains with the customer for every model?", "Protecting their identities, data, and configuration choices", ["Replacing the provider's physical disks", "Repairing the provider's data-centre power system", "Maintaining the provider's global backbone"], "The provider/customer responsibility split varies, but customers retain responsibility for their own data, identities, and usage configuration.", "intermediate"),
        ],
        [
            ("A private cloud is reserved for one organization, while a public cloud serves multiple customers. What design concern is central to multi-tenancy?", "Isolating each tenant's data and operations", ["Giving every tenant the same credentials", "Removing all resource quotas", "Disabling identity checks between tenants"], "Multi-tenant platforms must enforce isolation and authorization across shared infrastructure.", "easy"),
            ("Why might a workload use a hybrid deployment?", "Some components remain in a private environment while others use public cloud resources", ["It eliminates all network communication", "It requires every service to run on one laptop", "It guarantees zero operational overhead"], "Hybrid models combine environments to meet needs such as existing systems, regulation, or variable capacity.", "easy"),
        ],
        [
            ("What is the main distinction between a virtual machine and a container?", "A VM virtualizes hardware with a guest OS; a container generally shares the host kernel", ["A container always includes a separate physical CPU", "A VM cannot run an operating system", "Containers are database tables"], "Containers isolate processes while sharing the host kernel, whereas VMs run guest operating systems atop virtualized hardware.", "easy"),
            ("Why are containers often useful for packaging an application?", "They bundle the application and its user-space dependencies into a repeatable image", ["They guarantee the application has no vulnerabilities", "They eliminate the need for configuration", "They reserve a dedicated physical server automatically"], "A container image can make application dependencies more consistent across environments, but it still needs secure configuration and operation.", "easy"),
        ],
        [
            ("A service automatically adds instances when demand rises and removes them when demand falls. Which property is this?", "Elasticity", ["Immutability", "Confidentiality", "Serializability"], "Elasticity adjusts resources to changing demand over time.", "easy"),
            ("Why is multi-zone deployment used for availability?", "It can keep a service reachable when one failure domain becomes unavailable", ["It prevents all software defects", "It makes every request strongly consistent", "It removes the need for backups"], "Redundancy across failure domains can improve availability, though applications must also handle failover and data consistency.", "intermediate"),
        ],
        [
            ("A cloud storage bucket contains private records. Which configuration is the safest default?", "Deny public access and grant only required identities the needed permissions", ["Allow anonymous writes", "Share an administrator key with every service", "Disable audit events"], "Private-by-default access and least privilege reduce accidental disclosure and misuse.", "easy"),
            ("Why should cloud API credentials be stored in a managed secret store or protected environment configuration?", "It limits exposure and supports controlled rotation without embedding secrets in source code", ["It makes the credential public to every browser", "It removes the need to restrict permissions", "It guarantees the secret can never be stolen"], "Secret-management controls reduce accidental disclosure and help rotation, while access and monitoring still matter.", "easy"),
        ],
    ],
    "BD": [
        [
            ("A distributed dataset is split into partitions by customer ID. What is a key design trade-off?", "Partitioning enables parallelism but can create skew or expensive cross-partition work", ["Partitioning guarantees every query is constant time", "It removes the need for storage", "It makes all records identical"], "Partition design affects parallel execution, data balance, and the cost of operations that span partitions.", "intermediate"),
            ("Why can a distributed system replicate data in addition to partitioning it?", "To improve availability or read locality at the cost of coordination and consistency concerns", ["To ensure only one machine stores any data", "To eliminate network latency", "To avoid every form of failure"], "Replication can improve resilience and locality but requires policies for synchronization and conflicting updates.", "intermediate"),
        ],
        [
            ("In MapReduce, what does the reduce stage typically do?", "Aggregate values grouped under the same intermediate key", ["Render a web page", "Assign CPU instructions to a pipeline", "Encrypt every input before mapping"], "Reducers process each key and its associated values to produce aggregated output.", "easy"),
            ("Why is a combiner sometimes used before the shuffle?", "It performs a local partial aggregation to reduce data transferred across the network", ["It changes the meaning of every key", "It replaces the final reducer in all cases", "It guarantees exactly-once external side effects"], "A combiner can reduce intermediate data volume when the aggregation operation permits it.", "intermediate"),
        ],
        [
            ("An event arrives late but carries an event-time timestamp from earlier. Which concept helps a stream processor reason about progress?", "A watermark", ["A database foreign key", "A CPU cache line", "A CSS breakpoint"], "A watermark estimates that events earlier than a point in event time are unlikely to arrive, subject to the system's policy.", "intermediate"),
            ("Why distinguish processing time from event time?", "Processing time reflects when the system handles data; event time reflects when the event occurred", ["They are two names for a partition key", "Event time is always identical across time zones", "Processing time is available only in batch jobs"], "Event-time semantics support analyses based on the time of the real-world event despite variable arrival delays.", "easy"),
        ],
        [
            ("A pipeline silently drops malformed records. What should a data-quality process do?", "Measure, quarantine, and make the handling of rejected records observable", ["Treat the dropped rows as valid without tracking", "Delete the input source", "Change the schema to accept every value"], "Observable validation and quarantine make data loss measurable and support investigation or correction.", "easy"),
            ("Why attach lineage metadata to a derived dataset?", "It helps trace which sources and transformations produced the data", ["It guarantees the source data is correct", "It compresses each record", "It determines the user's password"], "Lineage supports reproducibility, debugging, impact analysis, and governance.", "easy"),
        ],
        [
            ("A nightly report scans all records, while a dashboard needs updates within seconds. Which architecture may fit these two latency needs?", "A batch path for the report and a stream-processing path for the dashboard", ["A single manual spreadsheet for both", "A client-side cache with no data pipeline", "A compiler pass"], "Batch and stream processing address different latency and completeness needs; a design may combine them deliberately.", "intermediate"),
            ("Why should a big-data platform choose consistency and latency trade-offs per workload instead of by slogan?", "Different queries and failure conditions have different correctness and freshness requirements", ["All systems require identical semantics", "Low latency always proves correct results", "A distributed store cannot expose consistency choices"], "Workload requirements determine acceptable staleness, coordination cost, and failure behavior.", "intermediate"),
        ],
    ],
    "MP": [
        [
            ("During the fetch phase, what does a program counter normally contain?", "The address used to locate the next instruction", ["The most recent sensor value", "A permanent copy of the whole program", "The current stack's maximum size"], "The program counter tracks the instruction-fetch position, with exact update timing defined by the architecture.", "easy"),
            ("What is the purpose of an instruction register?", "Hold the instruction currently being decoded or executed", ["Store all external interrupts permanently", "Replace the address bus", "Count clock cycles since power-on only"], "The instruction register retains the fetched instruction for control and execution stages.", "easy"),
        ],
        [
            ("In immediate addressing, where is an operand value commonly found?", "Inside the instruction encoding itself", ["Only in an external device register", "At an address computed from a pointer chain", "In a later program's output file"], "Immediate addressing encodes a constant operand as part of the instruction.", "easy"),
            ("What does an assembler do with a symbolic label used as a branch target?", "Resolve the label to an address or relocation value", ["Convert the label into a physical interrupt", "Run the target instruction at assembly time", "Encrypt the whole program"], "Assemblers build symbol information to translate labels into machine-level addresses or relocations.", "intermediate"),
        ],
        [
            ("A device asserts an interrupt line. What does the processor generally need to do before servicing it?", "Save enough execution context and transfer control to the appropriate handler", ["Erase all program memory", "Disable every clock permanently", "Convert the interrupt into a source-code comment"], "The interrupt mechanism preserves execution state and dispatches to a handler according to the architecture's rules.", "easy"),
            ("Why use a timer interrupt in a periodic control task?", "It can trigger service at recurring intervals without busy-waiting", ["It guarantees exact timing despite all interrupt latency", "It replaces the system clock", "It prevents priority inversion automatically"], "A timer can schedule periodic work efficiently, though actual response has latency and jitter limits.", "intermediate"),
        ],
        [
            ("What does memory-mapped I/O mean?", "Device registers occupy addresses accessed through the memory address space", ["Every device is stored as a file on disk", "I/O operations require no bus", "The CPU cannot access normal memory"], "Memory-mapped devices are controlled through reads and writes to assigned address ranges.", "easy"),
            ("Why decode only the intended address range for a peripheral?", "So unrelated accesses do not accidentally select the device", ["To make all addresses alias the same register", "To remove the need for address lines", "To increase the number of CPU opcodes"], "Address decoding ensures that only matching bus transactions reach the peripheral.", "easy"),
            ("A status register is mapped at address 0x4000. Why might the device documentation warn against a read-modify-write operation on it?", "Reading the register may have side effects or its bits may change asynchronously", ["Mapped registers cannot be read", "The address is necessarily a ROM location", "The CPU must convert the register to source code first"], "Device registers can have special read/write semantics; software should follow the peripheral contract rather than assume ordinary RAM behavior.", "intermediate"),
        ],
        [
            ("Why does a synchronous peripheral interface specify setup and hold times?", "Signals must remain stable around the sampling clock edge", ["The bus must contain executable code", "The processor needs to change its instruction set", "The device must use an analogue address"], "Setup and hold requirements constrain signal timing so the receiving device can sample reliably.", "intermediate"),
            ("What is bus arbitration used for when multiple bus masters request access?", "Choose which requester may use the shared bus", ["Translate source code into opcodes", "Allocate file-system directories", "Measure the program's algorithmic complexity"], "Arbitration coordinates competing masters to avoid conflicting simultaneous transfers.", "easy"),
        ],
    ],
    "DL": [
        [
            ("What does a neuron compute before applying its activation function?", "A weighted sum of inputs plus a bias", ["A sorted copy of the training set", "A database join", "A random label with no parameters"], "A standard artificial neuron applies an activation to an affine combination of its input values.", "easy"),
            ("Why can a nonlinear activation be important between neural-network layers?", "It allows stacked layers to represent nonlinear functions", ["It guarantees that training converges globally", "It removes the need for data", "It converts all weights to integers"], "Without nonlinearities, composing linear layers remains a linear transformation and cannot model general nonlinear relationships.", "intermediate"),
        ],
        [
            ("For a binary classifier with logits, why is cross-entropy loss commonly used?", "It penalizes predicted probabilities that assign low likelihood to the true class", ["It measures only model file size", "It guarantees no class imbalance", "It sorts examples by timestamp"], "Cross-entropy evaluates the probability assigned to the observed label and provides a differentiable training objective.", "easy"),
            ("What does gradient descent do to model parameters?", "Updates them in a direction that locally reduces the loss", ["Sets every parameter to zero", "Selects a new training label", "Proves the loss has a unique global minimum"], "Gradient-based optimization uses derivatives to choose parameter updates; it does not generally guarantee a global optimum for deep models.", "easy"),
        ],
        [
            ("Why are convolutional layers useful for image inputs?", "They apply shared local filters that can detect spatial patterns", ["They require each pixel to have a unique full dense layer", "They remove image dimensions", "They guarantee rotation invariance"], "Convolutions reuse kernels across positions and capture local structure; invariances depend on data and architecture.", "easy"),
            ("What effect does stride greater than one typically have in a convolution?", "It reduces the spatial resolution of the output", ["It increases the number of input channels automatically", "It reverses every pixel", "It makes the operation recurrent"], "A larger stride moves the filter farther between applications and usually yields fewer output positions.", "intermediate"),
        ],
        [
            ("What problem do positional encodings address in a transformer?", "Self-attention alone does not inherently encode token order", ["The model cannot represent word embeddings", "The optimizer cannot compute gradients", "The vocabulary must be sorted alphabetically"], "Positional information lets a transformer distinguish sequences whose token sets are the same but order differs.", "easy"),
            ("In an attention operation, what do query-key scores primarily determine?", "How strongly each position attends to other positions", ["The batch size at inference", "The number of CPU cores", "The target vocabulary's spelling"], "Attention weights are computed from query-key compatibility and used to combine value representations.", "intermediate"),
        ],
        [
            ("A model is evaluated repeatedly on the same validation set while many hyperparameters are tuned. What risk increases?", "Overfitting to the validation set", ["The model becomes an unsupervised learner", "The training set becomes larger", "The labels are automatically corrected"], "Repeated selection based on validation results can adapt the model to that set, reducing its value as an unbiased estimate.", "easy"),
            ("Why report performance on a held-out test set only after model selection is complete?", "To preserve an independent estimate of generalization", ["To use the test set for every gradient update", "To guarantee a better score", "To avoid documenting the dataset"], "A test set should remain untouched by tuning so it can provide a final evaluation estimate.", "intermediate"),
        ],
    ],
    "NLP": [
        [
            ("Why does tokenization need to match the model's expected vocabulary and conventions?", "Different token boundaries change the input sequence and token IDs", ["Tokenization changes the source language's grammar", "Every tokenizer produces identical tokens", "It determines the model's optimizer"], "Tokenization is part of the model input contract; mismatched rules can make otherwise valid text map incorrectly.", "easy"),
            ("What is a common trade-off of subword tokenization?", "It handles rare words through smaller units but may split words into unintuitive pieces", ["It guarantees one token per word", "It prevents unknown sequences by using a token per character only", "It removes the need for embeddings"], "Subword vocabularies balance sequence length and coverage but can create splits that are less linguistically natural.", "intermediate"),
        ],
        [
            ("What does an embedding represent?", "A token or item as a learned numeric vector", ["A human-readable grammar rule only", "A lossless archive of the original document", "A fixed hardware address"], "Embeddings map discrete symbols into vector spaces where models can compute learned relationships.", "easy"),
            ("Why should a text classifier's train and inference pipelines use the same normalization rules?", "A mismatch can change token IDs or features seen by the model", ["Normalization controls the network's physical memory", "It makes evaluation labels unnecessary", "The model cannot read text otherwise"], "Preprocessing consistency ensures inference inputs follow the same representation assumptions used during training.", "easy"),
        ],
        [
            ("In a next-token language model, what target is usually used for each context position?", "The following token in the sequence", ["The document's file size", "A random unrelated class", "The preceding paragraph's font"], "Causal language modelling trains the model to predict the next token from preceding context.", "easy"),
            ("Why mask future tokens in a causal language model during training?", "To prevent the prediction at a position from using information that should be unknown", ["To anonymize the training corpus", "To make every attention score zero", "To remove the vocabulary"], "A causal mask enforces the autoregressive condition by blocking attention to future positions.", "intermediate"),
        ],
        [
            ("What does self-attention allow a token representation to do?", "Combine information from other positions in the same sequence", ["Change the order of the original file on disk", "Update the model weights during inference automatically", "Translate every token one-to-one"], "Self-attention forms context-aware representations by weighting information from positions in the sequence.", "easy"),
            ("Why split attention into multiple heads in a transformer?", "Different heads can learn distinct representation subspaces or relationships", ["It guarantees each head understands a separate language", "It removes all quadratic attention cost", "It prevents the model from using position information"], "Multiple heads provide parallel attention projections, though their learned roles are not guaranteed to be perfectly distinct.", "intermediate"),
        ],
        [
            ("A language model scores lower on one dialect than another. Which evaluation practice is most informative?", "Report performance on representative, appropriately consented slices and analyze error patterns", ["Remove the lower-scoring group from all reports", "Assume one aggregate score explains every user", "Change the labels until the scores match"], "Slice-based evaluation can expose quality gaps, while dataset coverage, consent, and limitations must be documented.", "intermediate"),
            ("Why might BLEU or another automatic metric be insufficient for judging generated text alone?", "It may not capture factuality, usefulness, or all valid paraphrases", ["Automatic metrics cannot process numbers", "It proves that every output is safe", "It measures only training time"], "Text metrics are proxies and should be paired with task-specific human or factuality checks when appropriate.", "easy"),
        ],
    ],
    "DevOps": [
        [
            ("What does a continuous-integration pipeline commonly do after a change is proposed?", "Build the change and run automated checks", ["Deploy every change to all users without checks", "Rotate every user's password", "Delete the source branch"], "CI builds and tests changes early so integration problems are visible before release.", "easy"),
            ("Why keep a build reproducible from a clean checkout?", "It helps verify that source and declared dependencies are sufficient to produce the artifact", ["It guarantees the code is bug-free", "It removes the need for version control", "It makes deployment permissions public"], "A clean reproducible build improves traceability and helps detect undeclared local dependencies.", "easy"),
        ],
        [
            ("Why pin or lock dependency versions for a release build?", "To make the resolved dependency set more predictable and reviewable", ["To ensure every dependency is the newest version", "To prevent vulnerability updates forever", "To hide dependencies from the build log"], "A lock file records resolved versions; teams should still update and audit dependencies deliberately.", "easy"),
            ("What is a software bill of materials useful for?", "Listing software components and dependencies for tracking and risk response", ["Replacing application tests", "Storing user passwords", "Guaranteeing every component has no vulnerabilities"], "An SBOM supports inventory and vulnerability triage but does not itself prove software is secure.", "intermediate"),
        ],
        [
            ("What is the main idea of a canary deployment?", "Release to a small portion of traffic or users, observe, then expand if healthy", ["Deploy only to a disconnected laptop", "Replace the database before building", "Disable monitoring during rollout"], "A canary limits initial exposure and uses operational signals to guide a gradual rollout.", "easy"),
            ("Why should rollback procedures account for database schema changes?", "A code rollback may not be safe if the new schema is incompatible with the old version", ["Database schemas cannot be versioned", "A rollback always deletes records", "Schema changes never affect applications"], "Expand-and-contract migrations and backward-compatible changes reduce risk during mixed-version deployments.", "intermediate"),
        ],
        [
            ("What is a benefit of declaring infrastructure in code?", "Changes can be reviewed, versioned, and applied consistently", ["It removes all cloud permissions", "It prevents configuration drift automatically in every system", "It makes the infrastructure impossible to change"], "Infrastructure as code makes desired configuration explicit and reviewable; drift still needs detection and control.", "easy"),
            ("Why keep a container image immutable after it is built?", "The same artifact can be promoted through environments without rebuilding different contents", ["It guarantees the image contains no secrets", "It disables patching", "It changes the image into a virtual machine"], "Promoting an unchanged image improves artifact identity and reduces environment-specific build differences.", "intermediate"),
        ],
        [
            ("A latency alert fires when a service's p95 exceeds its agreed limit. What kind of signal is p95?", "A percentile of observed request latency", ["A measure of source-code size", "A database privilege", "An average that ignores the slowest requests"], "The 95th percentile is a tail-latency statistic: 95 percent of observed requests are at or below that value.", "easy"),
            ("Why define an error budget from a service-level objective?", "It makes the reliability trade-off between changes and user impact explicit", ["It guarantees zero downtime", "It eliminates incident reviews", "It is a count of unused CPU cores"], "An error budget quantifies tolerated unreliability relative to the objective and can guide release decisions.", "intermediate"),
        ],
    ],
    "BC": [
        [
            ("Why link a block to the previous block's cryptographic hash?", "A change to an earlier block can make later links fail verification", ["It makes all ledger data confidential", "It prevents valid new blocks from being added", "It replaces consensus"], "Hash links provide tamper evidence across the chain, but do not alone prevent rewriting or guarantee correctness.", "easy"),
            ("What does a Merkle root summarize?", "The leaves of a hash tree in a compact value that supports membership proofs", ["A wallet's private key", "The blockchain's network address", "A consensus voting schedule"], "Merkle trees let a verifier check inclusion using a logarithmic-size proof without receiving every leaf.", "intermediate"),
        ],
        [
            ("What problem does a consensus protocol address in a distributed ledger?", "How participants agree on an accepted order or state despite delays and failures", ["How to make every node identical hardware", "How to remove cryptographic keys", "How to guarantee every transaction is private"], "Consensus rules coordinate agreement about ledger state; their guarantees depend on the protocol's assumptions.", "easy"),
            ("Why do many proof-of-work protocols require a costly nonce search?", "To make block production expensive to manipulate while verification remains comparatively cheap", ["To encrypt every transaction", "To prove the sender's legal identity", "To remove the need for validation rules"], "Proof of work establishes a resource cost for proposing blocks; it does not make all attacks impossible.", "intermediate"),
        ],
        [
            ("A smart contract call reverts. What is the usual state effect of the failed transaction's execution?", "Its state changes are rolled back, though the transaction may still consume a fee", ["The contract source code is deleted", "Every validator loses its key", "The whole chain returns to genesis"], "Transaction execution is atomic with respect to state changes on common smart-contract platforms, while fees may still be charged.", "intermediate"),
            ("Why should a smart contract validate caller-provided values even if the UI also validates them?", "The contract may be called directly without using that UI", ["The UI can change blockchain consensus", "Contract input is always trusted", "Validation belongs only in documentation"], "On-chain entry points must enforce their own invariants because callers are not limited to one interface.", "easy"),
        ],
        [
            ("In a public-key signature system, which key should a wallet keep secret?", "The private key", ["The public key", "The hash algorithm name", "The transaction's public identifier"], "The private key authorizes signatures; the public key can be shared for verification.", "easy"),
            ("What does possession of a private key prove by itself?", "Control of that key, not necessarily the real-world identity of its holder", ["A legally verified name", "That every transaction is correct", "That the key was never copied"], "Key control is not identity proof unless a trusted process binds the key to an identity.", "intermediate"),
        ],
        [
            ("Why can a public blockchain have difficulty reversing an erroneous transaction?", "Its append-only replicated state and consensus rules do not provide a central undo authority", ["All blockchains delete their history every hour", "Every transaction is encrypted from all validators", "A hash function restores the prior state automatically"], "Reversibility depends on protocol and governance; many public ledgers prioritize append-only history over discretionary rollback.", "easy"),
            ("What is a smart-contract reentrancy risk?", "External control returns into a contract before its earlier operation has safely finalized state", ["A hash collision changes the network protocol", "A miner reads the source-code comments", "A wallet loses its display theme"], "Reentrancy can exploit unsafe call ordering; checks-effects-interactions and guarded patterns help mitigate it.", "intermediate"),
        ],
    ],
    "ECE01": [
        [
            ("What happens to the depletion region of a silicon PN junction under forward bias?", "Its barrier is reduced and the depletion region narrows", ["It widens without limit", "It becomes a perfect conductor", "The junction loses both carrier types"], "Forward bias reduces the built-in barrier, allowing substantial majority-carrier injection.", "easy"),
            ("A diode is reverse-biased well below breakdown. Which current is normally expected in the idealized model?", "Approximately zero", ["A large forward diffusion current", "A current increasing linearly without limit", "A current equal to the load current by definition"], "The ideal diode blocks reverse current below breakdown; real devices have a small leakage current.", "easy"),
        ],
        [
            ("In the forward-active region of an NPN BJT, how are its two junctions biased?", "Base-emitter forward-biased and base-collector reverse-biased", ["Both reverse-biased", "Both forward-biased", "Base-emitter reverse-biased and base-collector forward-biased"], "Forward-active operation uses a forward-biased emitter junction and a reverse-biased collector junction.", "easy"),
            ("For a BJT, current gain β is defined approximately as the ratio of which currents in common-emitter operation?", "Collector current to base current", ["Base current to collector current", "Emitter voltage to collector voltage", "Collector resistance to emitter resistance"], "In the active region, β=I_C/I_B for the common-emitter current gain definition.", "easy"),
        ],
        [
            ("Why does a MOSFET gate draw very little steady-state DC current in the ideal insulated-gate model?", "The gate is insulated from the channel by a dielectric", ["The source is disconnected", "The channel contains no charge", "The drain is always at zero volts"], "The insulating gate dielectric blocks a DC conduction path, although real devices have leakage and gate capacitance.", "easy"),
            ("What mainly controls channel conduction in an enhancement-mode MOSFET?", "The gate-to-source voltage relative to the threshold voltage", ["The gate's physical colour", "The drain's wire length only", "The substrate's file format"], "Gate voltage controls inversion charge in the channel; conduction also depends on drain bias and device parameters.", "easy"),
        ],
        [
            ("A small-signal transistor model is normally applied around what operating condition?", "A chosen DC bias or quiescent point", ["The device's packaging temperature only", "A point where all terminals are shorted", "An arbitrary point outside the device characteristics"], "Small-signal models linearize the device response near a specified bias point.", "easy"),
            ("Why include an emitter resistor in a BJT bias circuit?", "It provides local feedback that can reduce sensitivity to transistor gain and temperature variation", ["It guarantees infinite voltage gain", "It removes the need for a supply", "It changes an NPN into a PNP device"], "An emitter resistor provides negative feedback that can improve bias stability, with a trade-off in gain or headroom.", "intermediate"),
        ],
        [
            ("What is the operating principle of an LED?", "Electron-hole recombination emits photons", ["Magnetic induction emits sound waves", "A reverse-biased junction stores a digital file", "Thermal expansion creates coherent radio waves"], "An LED emits light when carriers recombine radiatively in a forward-biased semiconductor junction.", "easy"),
            ("How does a photodiode commonly convert incident light into an electrical signal?", "Photons generate carriers that contribute to photocurrent", ["It converts light directly into mechanical torque", "It stores light as permanent charge without a circuit", "It amplifies light using a transformer"], "Absorbed photons create electron-hole pairs, producing a measurable photocurrent under suitable bias or photovoltaic operation.", "easy"),
        ],
    ],
    "ECE02": [
        [
            ("An amplifier's bandwidth is measured between which commonly defined frequencies?", "Its lower and upper cutoff frequencies", ["Its DC supply limits only", "The frequencies of its input connectors", "The sampling rate of a digital oscilloscope"], "Bandwidth is commonly the frequency interval between specified lower and upper response limits, often the −3 dB points.", "easy"),
            ("What typically contributes to reduced gain at high frequencies in a transistor amplifier?", "Device and wiring capacitances", ["The transistor's colour code", "An increase in source resistance to infinity by definition", "A lower ambient light level"], "Junction and parasitic capacitances create frequency-dependent poles that reduce high-frequency gain.", "intermediate"),
        ],
        [
            ("What is a common effect of negative feedback on a voltage amplifier?", "It reduces gain sensitivity to component variations", ["It makes the output unrelated to the input", "It guarantees an unstable circuit", "It removes all frequency limits"], "Negative feedback can trade some gain for improved stability, linearity, and predictable closed-loop behaviour.", "easy"),
            ("Why check phase margin in a feedback amplifier?", "It indicates how close the loop is to oscillatory instability at unity loop gain", ["It measures the supply voltage directly", "It determines the transistor's package size", "It is the number of input terminals"], "Phase margin is a stability measure based on loop phase near the unity-gain crossover.", "intermediate"),
        ],
        [
            ("For an ideal inverting op-amp with input resistor R_in and feedback resistor R_f, what is the closed-loop voltage gain?", "−R_f/R_in", ["R_f/R_in", "1 + R_f/R_in", "R_in − R_f"], "With the non-inverting input grounded, the ideal inverting configuration has gain −R_f/R_in.", "easy"),
            ("Why is the inverting input called a virtual ground in this ideal circuit?", "Negative feedback holds its voltage near the grounded non-inverting input without a direct ground connection", ["It is connected to ground through a zero-ohm wire", "It has infinite current flowing into it", "The op-amp output is always zero"], "With negative feedback and linear operation, the high open-loop gain drives the input differential voltage near zero while input current remains approximately zero.", "intermediate"),
        ],
        [
            ("For sustained sinusoidal oscillation in a feedback oscillator, what loop condition is required at the oscillation frequency?", "The loop phase is 0° modulo 360° and the loop magnitude is unity", ["The loop phase is 90° and magnitude is zero", "The amplifier must have no feedback", "The output must equal the supply voltage"], "The Barkhausen condition states a unity loop gain with net phase shift of an integer multiple of 360° at the oscillation frequency.", "intermediate"),
            ("What role does a frequency-selective network play in an oscillator?", "It helps select the frequency at which the feedback condition is met", ["It eliminates the active device", "It stores the complete output waveform permanently", "It prevents any loop gain"], "The network provides frequency-dependent attenuation and phase shift that favour oscillation at a selected frequency.", "easy"),
        ],
        [
            ("In an ideal Class B push-pull stage, approximately how much of a cycle does each output device conduct?", "180°", ["0°", "90°", "360°"], "Each Class B device conducts for roughly half a cycle; practical crossover distortion and biasing require further analysis.", "easy"),
            ("Why is a Class AB output stage biased slightly above the Class B cutoff point?", "To reduce crossover distortion around the zero crossing", ["To force both devices off for the entire cycle", "To make the load resistance infinite", "To remove all power dissipation"], "A small quiescent current keeps both devices conducting slightly around crossover, improving linearity at the cost of idle dissipation.", "intermediate"),
        ],
    ],
    "ECE03": [
        [
            ("A discrete-time sequence x[n] is shifted to x[n−3]. In which direction is it shifted?", "Three samples to the right", ["Three samples to the left", "It is reversed in time", "It is scaled in amplitude by three"], "Replacing n with n−3 delays a sequence by three sample positions.", "easy"),
            ("A continuous-time signal x(t) becomes x(2t). What happens to its time scale?", "It is compressed by a factor of two", ["It is expanded by a factor of two", "Its amplitude doubles", "It is shifted right by two seconds"], "A time argument scale factor greater than one compresses the signal in time.", "easy"),
        ],
        [
            ("For an LTI system, what output is produced by an input x and impulse response h?", "Their convolution", ["Their pointwise maximum", "Their ratio at every sample", "The derivative of h only"], "An LTI system's response is convolution of its input with its impulse response.", "easy"),
            ("What does it mean for a system to be time-invariant?", "A time shift in the input produces the same time shift in the output", ["The output is always constant", "The system cannot store energy", "The impulse response must be periodic"], "Time invariance means system behaviour does not change with an absolute shift in time.", "easy"),
        ],
        [
            ("For continuous-time signals, what does convolution with the unit impulse δ(t) return?", "The original signal", ["The signal's time reversal", "A zero signal for every input", "The signal's Fourier series coefficients"], "The unit impulse is the identity element for convolution: x(t)*δ(t)=x(t).", "easy"),
            ("Why is impulse response useful for describing an LTI system?", "It determines the system's response to any suitable input through convolution", ["It lists every possible input explicitly", "It gives the system's source code", "It applies only to nonlinear systems"], "For an LTI system, the impulse response fully characterizes its input-output behaviour under standard assumptions.", "intermediate"),
        ],
        [
            ("What kind of signal is naturally represented by a Fourier series?", "A periodic signal", ["Only a finite binary word", "A signal with no frequency components", "A random variable without time dependence"], "Fourier series represents periodic signals as weighted harmonically related sinusoidal components.", "easy"),
            ("What does the magnitude spectrum of a Fourier transform describe?", "The magnitude of each frequency component in the signal representation", ["Only the time-domain peak location", "A system's source-code complexity", "The number of samples in a memory block"], "The transform expresses frequency content; its magnitude shows component strength while phase contains timing information.", "easy"),
        ],
        [
            ("For a discrete-time sequence, which transform is commonly used to analyze its frequency-domain behaviour and system poles?", "The Z-transform", ["The Laplace transform only", "The spatial Fourier series only", "The Hamming code"], "The Z-transform is the discrete-time counterpart used for sequence and LTI-system analysis.", "easy"),
            ("For a causal continuous-time LTI system, what does a stable system's pole condition require in the usual rational Laplace-domain model?", "All poles lie in the open left half-plane", ["All poles lie in the open right half-plane", "There are no poles or zeros", "Every pole lies on the imaginary axis"], "For a causal rational system, BIBO stability requires poles strictly in the left half-plane; boundary cases require separate treatment.", "intermediate"),
        ],
    ],
    "ECE04": [
        [
            ("A band-limited signal has maximum frequency f_max. What minimum ideal sampling rate avoids aliasing under the Nyquist criterion?", "At least 2f_max", ["At least f_max/2", "Exactly f_max/4", "Any rate if the samples are stored as integers"], "The ideal Nyquist criterion requires a sampling frequency at least twice the highest frequency component, with practical guard margins often needed.", "easy"),
            ("What is aliasing in sampled signals?", "Different continuous-time frequencies become indistinguishable after sampling", ["A quantizer adds one extra bit", "A carrier is amplified without modulation", "A codeword gains a parity bit"], "Undersampling causes spectral replicas to overlap, making distinct input frequencies map to the same sampled sequence.", "easy"),
        ],
        [
            ("What does a line code define in a digital baseband link?", "How bits or symbols are represented by signal levels or transitions over time", ["How database rows are normalized", "How a compiler parses expressions", "How a receiver authenticates a user"], "Line coding maps digital symbols to a physical waveform suitable for transmission and timing recovery.", "easy"),
            ("Why is clock recovery important at a receiver?", "It helps determine when to sample each transmitted symbol", ["It encrypts the bit stream", "It increases the channel bandwidth automatically", "It removes the need for synchronization"], "The receiver needs timing information to sample symbols near their intended decision instants.", "intermediate"),
        ],
        [
            ("In binary phase-shift keying, what signal property represents the bit choice?", "The carrier phase", ["The cable's length", "The antenna's colour", "The data packet's file name"], "BPSK conveys the binary symbol through one of two carrier phase states.", "easy"),
            ("Compared with a binary modulation using one bit per symbol, what can a 16-QAM symbol carry ideally?", "Four bits", ["One bit", "Two bits", "Sixteen bits"], "A 16-point constellation has log₂16=4 bits of information per symbol before coding overhead.", "easy"),
        ],
        [
            ("In a binary detection problem, what generally happens to error probability when signal-to-noise ratio increases, all else equal?", "It decreases", ["It must increase", "It is unchanged by definition", "It becomes exactly zero at any finite SNR"], "Higher SNR makes the received signal distributions more separable, reducing error probability for a fixed optimal detector.", "easy"),
            ("Why does coherent detection require a carrier phase reference?", "The receiver uses phase-aligned information to make the symbol decision", ["It converts symbols into SQL statements", "It eliminates channel noise", "It allows the transmitter to omit timing"], "Coherent demodulation compares the received signal against a synchronized reference; phase error can degrade decisions.", "intermediate"),
        ],
        [
            ("According to Shannon's capacity formula, what happens to channel capacity as signal-to-noise ratio increases while bandwidth is fixed?", "Capacity increases", ["Capacity decreases to zero", "Capacity is independent of SNR", "Capacity becomes negative"], "C=B log₂(1+SNR), so capacity increases monotonically with SNR for fixed positive bandwidth.", "intermediate"),
            ("What is the purpose of adding structured redundancy in a channel code?", "Enable detection or correction of some transmission errors", ["Increase the source message's meaning", "Guarantee correction of any number of errors", "Remove the need for a decoder"], "Channel codes add controlled redundancy so a decoder can detect or correct errors within the code's capabilities.", "easy"),
        ],
    ],
    "ECE05": [
        [
            ("What does the divergence of an electric flux density field describe locally?", "Net outward flux per unit volume", ["The field's rotation around a point", "The electric potential's reference value", "The speed of a charged particle"], "Divergence measures local source or sink strength; Gauss's law relates electric flux divergence to charge density.", "intermediate"),
            ("Which theorem relates the surface integral of a vector field over a closed surface to its volume divergence integral?", "The divergence theorem (Gauss's theorem)", ["Stokes' theorem only", "The binomial theorem", "The convolution theorem"], "The divergence theorem equates outward flux through a closed surface with the volume integral of divergence.", "easy"),
        ],
        [
            ("In electrostatic equilibrium, what is the electric field inside an ideal conductor?", "Zero", ["Infinite", "Equal to the magnetic field", "Always equal to the surface charge density"], "Free charges redistribute until the electrostatic field within the conductor is zero.", "easy"),
            ("At an electrostatic conductor surface, what is true of the electric field's tangential component in equilibrium?", "It is zero at the surface", ["It is always larger than the normal component", "It reverses on every point", "It must equal the magnetic flux"], "A nonzero tangential electric field would drive surface charges, contradicting electrostatic equilibrium.", "intermediate"),
        ],
        [
            ("What does the magnetic field around a long straight current-carrying wire form?", "Concentric circles around the wire", ["Straight radial lines from the wire", "A uniform field parallel to the wire everywhere", "A field that exists only at the wire's ends"], "The right-hand rule gives circular magnetic-field lines around a straight current.", "easy"),
            ("What does the Biot–Savart law relate to a magnetic field contribution?", "A current element, its geometry, and distance/direction to the observation point", ["Only electric potential and temperature", "A dielectric constant and clock period", "The source code and memory size"], "The Biot–Savart law gives the field contribution from a current element with inverse-square distance dependence and directional geometry.", "intermediate"),
        ],
        [
            ("Which Maxwell equation states that the divergence of magnetic flux density is zero?", "Gauss's law for magnetism", ["Gauss's law for electricity", "Faraday's law", "Ampère's circuital law only"], "∇·B=0 expresses the absence of isolated magnetic monopoles in classical electromagnetism.", "easy"),
            ("What term did Maxwell add to Ampère's law to account for changing electric fields?", "Displacement current", ["Magnetic charge density", "A resistive voltage drop", "The Poynting vector"], "The displacement-current term completes the law for time-varying fields and supports electromagnetic-wave propagation.", "intermediate"),
        ],
        [
            ("In a uniform plane wave in a lossless medium, what is the relationship between electric-field magnitude E and magnetic-field magnitude H?", "E/H equals the medium's intrinsic impedance", ["E/H is always zero", "E/H equals the wave's wavelength", "E and H must point in the same direction"], "The field ratio is the intrinsic impedance η; E, H, and propagation direction are mutually perpendicular for a plane wave.", "intermediate"),
            ("What does the characteristic impedance of an ideal lossless transmission line equal?", "The square root of inductance per unit length divided by capacitance per unit length", ["The product of resistance and frequency", "The ratio of line length to signal amplitude", "The inverse of propagation velocity"], "For an ideal lossless line, Z₀=√(L′/C′), where L′ and C′ are per-unit-length inductance and capacitance.", "intermediate"),
        ],
    ],
    "EE01": [
        [
            ("At a node, the algebraic sum of currents is zero. Which law is being applied?", "Kirchhoff's current law", ["Faraday's law", "Lenz's law", "The maximum power theorem"], "KCL follows from conservation of charge at a node.", "easy"),
            ("In a series circuit with ideal components, what is common to all elements?", "The same current", ["The same voltage across each element", "The same resistance", "The same power"], "A single series path carries the same current through each component.", "easy"),
        ],
        [
            ("Thevenin's theorem replaces a linear two-terminal network by which equivalent?", "A voltage source in series with a resistance or impedance", ["A current source in series with an ideal voltage source", "A capacitor in parallel with every load", "An open circuit for every load"], "The Thevenin equivalent is an open-circuit voltage in series with the equivalent source resistance/impedance.", "easy"),
            ("For a linear network, what does superposition allow an analyst to do?", "Sum the separate responses caused by each independent source", ["Add all resistors as if they were voltage sources", "Ignore dependent sources", "Replace a nonlinear device without approximation"], "Superposition applies to linear circuits; independent sources are considered one at a time while other independent sources are deactivated appropriately.", "intermediate"),
        ],
        [
            ("In a series RC circuit after a DC step, what is the capacitor voltage immediately before the step if it was uncharged?", "Zero", ["Equal to the supply instantly", "Infinite", "Equal to the resistor voltage for all time"], "Capacitor voltage cannot change instantaneously in the ideal circuit, so it begins at its initial value of zero.", "easy"),
            ("For a first-order RC circuit, what is the time constant?", "R times C", ["R divided by C", "C divided by R", "R plus C"], "The RC time constant τ=RC has units of seconds and sets the exponential response rate.", "easy"),
            ("After one time constant, how much of a first-order step response's total final change has approximately occurred?", "63.2%", ["10%", "50%", "99.9%"], "For a first-order response, the fraction is 1−e⁻¹, approximately 0.632 after one time constant.", "intermediate"),
        ],
        [
            ("In sinusoidal steady state, what does an inductor's impedance equal?", "jωL", ["1/(jωL)", "R−jωC", "ω/L"], "For the phasor convention e^{jωt}, an ideal inductor has impedance jωL.", "easy"),
            ("In a purely resistive AC circuit, what is the phase difference between voltage and current?", "Zero", ["90°", "180°", "It varies with frequency"], "For an ideal resistor, voltage and current are in phase.", "easy"),
        ],
        [
            ("For a two-port network, what do the port variables describe?", "Voltage and current at each of two terminal pairs", ["Two independent power stations", "The two largest resistors only", "A source and a ground node with no output"], "A two-port models electrical behaviour at an input port and an output port using terminal variables.", "easy"),
            ("For reciprocal two-port parameters, which condition holds for Z parameters?", "z₁₂ = z₂₁", ["z₁₁ = 0", "z₁₂ = −z₂₁ for every network", "All four Z parameters are equal"], "Reciprocity in Z parameters requires equal transfer impedances z₁₂ and z₂₁.", "intermediate"),
        ],
    ],
    "EE02": [
        [
            ("In an ideal transformer, how is the secondary-to-primary voltage ratio related to turns?", "V₂/V₁ = N₂/N₁", ["V₂/V₁ = N₁/N₂", "V₂/V₁ = N₁N₂", "Voltage is independent of turns"], "For an ideal transformer, induced voltage is proportional to winding turns.", "easy"),
            ("When referred from the secondary to the primary, a load resistance is scaled by what factor?", "(N₁/N₂)²", ["N₁/N₂", "N₂/N₁", "(N₁N₂)²"], "Impedance referral uses the square of the turns ratio, with the chosen direction determining the ratio.", "intermediate"),
        ],
        [
            ("In a DC motor, what is the role of back EMF?", "It opposes the applied voltage and limits armature current as speed rises", ["It increases current without limit", "It reverses the field winding permanently", "It converts mechanical energy into stored charge only"], "The generated back EMF opposes the supply and is proportional to motor speed and flux.", "easy"),
            ("Why is a starter used for many DC motors at startup?", "Back EMF is initially small, so a current-limiting measure is needed", ["The armature resistance is infinite at standstill", "The motor has no magnetic field at startup", "The starter increases the supply frequency"], "At standstill, back EMF is near zero; without current limiting the armature current can be excessive.", "easy"),
        ],
        [
            ("The synchronous speed of an AC machine depends on supply frequency and what machine quantity?", "Number of poles", ["Rotor resistance only", "Bearing diameter", "Stator colour"], "Synchronous speed is n_s=120f/P in rpm, where f is frequency and P is pole count.", "easy"),
            ("An induction motor rotor turns slightly below synchronous speed in motoring operation. What is this difference expressed as a fraction called?", "Slip", ["Power factor", "Turns ratio", "Crest factor"], "Slip is the relative difference between synchronous speed and rotor speed.", "easy"),
        ],
        [
            ("In a synchronous generator, what primarily sets the generated EMF magnitude under a simple model?", "Field excitation and rotational speed", ["The load's paint colour", "The shaft's bearing lubricant only", "The number of connected lamps only"], "Generated EMF depends on magnetic flux and electrical frequency; excitation controls flux in a synchronous machine.", "easy"),
            ("What does synchronizing a generator to a grid require before closing the breaker?", "Matching voltage magnitude, frequency, phase sequence, and phase angle", ["Matching only the generator's physical size", "Setting frequency to zero", "Opening all protection relays"], "Safe synchronization requires the generated voltage to align sufficiently with the grid in magnitude, frequency, sequence, and phase.", "intermediate"),
        ],
        [
            ("Why is a transformer open-circuit test commonly performed at rated voltage?", "To estimate core loss and no-load branch parameters", ["To measure full-load copper loss only", "To determine rotor slip", "To test a motor's braking torque"], "With the secondary open, input power at rated voltage is dominated by core loss, supporting no-load parameter estimation.", "intermediate"),
            ("What does machine efficiency compare?", "Useful output power to input power", ["Reactive power to apparent power only", "Rotor speed to pole count", "Copper mass to core mass"], "Efficiency is output power divided by input power, with losses accounting for the difference.", "easy"),
        ],
    ],
    "EE03": [
        [
            ("Why does a power system's load curve change over the day?", "Consumer demand varies with time and activity", ["The number of transmission towers changes hourly", "Generation frequency is chosen by each appliance", "All loads have constant power at all times"], "Demand varies with human and industrial activity, creating daily and seasonal load patterns.", "easy"),
            ("What does a spinning reserve provide to a power system?", "Available generation capacity that can respond to a sudden imbalance", ["A permanent increase in transmission resistance", "A replacement for frequency control", "A way to disconnect every generator"], "Spinning reserve is synchronized capacity that can increase output to help cover disturbances or forecast error.", "intermediate"),
        ],
        [
            ("Why is a transmission line's inductance relevant to its operation?", "It contributes to voltage drop and reactive power behaviour", ["It changes the conductor's chemical element", "It eliminates capacitance", "It sets the load's energy tariff"], "Line inductance affects series reactance, voltage regulation, and reactive power flow.", "easy"),
            ("For a short transmission line model, which line parameter is often neglected compared with a long line model?", "Shunt capacitance", ["Series resistance", "Series inductance", "Load current"], "Short-line approximations commonly neglect shunt capacitance while retaining series impedance.", "intermediate"),
        ],
        [
            ("In a power-flow study, what does a bus voltage magnitude and angle describe?", "The electrical state used to calculate injections and line flows", ["The physical height of a transmission pole", "The generator's fuel composition", "The insulation colour code"], "Bus voltage phasors form the network state from which active/reactive injections and branch flows are calculated.", "easy"),
            ("Which bus in a standard load-flow formulation balances the system's active-power mismatch and sets the angle reference?", "The slack (swing) bus", ["Every PQ bus equally", "A disconnected bus", "The bus with the largest load only"], "The slack bus provides a reference angle and adjusts its generation to cover modeled losses and mismatch.", "intermediate"),
        ],
        [
            ("What does a protective relay do when it detects a fault condition within its zone?", "Signals circuit breakers to isolate the affected part", ["Increases the fault current intentionally", "Changes the system frequency permanently", "Replaces all grounding conductors"], "Protection detects abnormal conditions and initiates isolation to limit damage and maintain system stability.", "easy"),
            ("Why are current transformers used in protection and metering circuits?", "They provide a scaled current and isolation for instruments and relays", ["They increase line voltage to transmission level", "They eliminate all measurement error", "They store fault energy indefinitely"], "A CT reproduces primary current at a standard secondary level while providing galvanic isolation, subject to burden and accuracy limits.", "easy"),
        ],
        [
            ("In economic dispatch, what is the basic objective for generators meeting a fixed demand?", "Minimize total operating cost subject to generation and system constraints", ["Maximize transmission losses", "Run every generator at its maximum regardless of demand", "Minimize the number of buses"], "Economic dispatch allocates generation to meet demand at minimum cost while satisfying operational constraints.", "easy"),
            ("Why does a grid operator maintain frequency close to its nominal value?", "Frequency reflects active-power balance and is important for synchronized equipment", ["It determines the colour of insulators", "It removes line reactance", "It is unrelated to generation and load"], "Frequency deviations indicate imbalance between generation and demand and can affect equipment and system operation.", "intermediate"),
        ],
    ],
    "EE04": [
        [
            ("What is the main switching role of an IGBT in a power converter?", "Control high-power current by switching between conducting and blocking states", ["Store all energy without losses", "Measure rotor position optically", "Replace the load's insulation"], "An IGBT is a controllable power semiconductor switch used in converter circuits.", "easy"),
            ("Why must a power switch's voltage and current ratings include suitable design margin?", "Real operation includes transients, thermal effects, and tolerances beyond nominal values", ["Datasheets contain no limits", "A larger rating makes switching loss exactly zero", "Margin removes the need for protection"], "Voltage and current stresses vary during switching and faults, so design margins and protection are required.", "intermediate"),
        ],
        [
            ("What does the firing angle control in a phase-controlled rectifier?", "The point in each AC cycle at which the controlled device begins conducting", ["The transformer's turns ratio", "The load's resistance", "The semiconductor's package type"], "Changing the firing angle changes the conduction interval and average DC output.", "easy"),
            ("What is a freewheeling diode used for with an inductive load?", "Provide a path for load current when the main switch turns off", ["Short the supply permanently", "Increase the switching frequency to infinity", "Measure the diode's junction temperature"], "The diode maintains current continuity for an inductive load and can limit voltage transients.", "easy"),
        ],
        [
            ("What is the function of a buck converter?", "Step down a DC input voltage to a lower regulated DC output", ["Convert DC directly into a higher-frequency AC output only", "Step up an AC frequency", "Convert mechanical torque into digital data"], "An ideal buck converter has an average output below its input, controlled by switching duty ratio.", "easy"),
            ("In an ideal continuous-conduction buck converter, what is the approximate output-to-input voltage ratio?", "D", ["1/D", "1−D only for every topology", "D²+1"], "For an ideal buck in continuous conduction, V_out/V_in≈D, where D is switch duty ratio.", "intermediate"),
        ],
        [
            ("What does pulse-width modulation vary to control the average output of a switching inverter?", "The fraction of each switching period for which a switch is on", ["The DC link's chemical composition", "The load's physical length", "The number of phases in the utility grid"], "PWM controls the output waveform by changing pulse widths according to a modulation signal.", "easy"),
            ("Why use dead time between complementary inverter switch commands?", "To reduce the risk of both devices in a leg conducting simultaneously", ["To force the DC bus to zero volts", "To create a permanent short circuit", "To eliminate the need for gate drivers"], "Dead time prevents shoot-through in a half-bridge, though it can introduce distortion that requires compensation.", "intermediate"),
        ],
        [
            ("Why can a variable-frequency drive control an AC motor's speed?", "It changes the supply frequency and coordinates voltage to control the rotating field", ["It changes the motor's pole count mechanically in every cycle", "It eliminates the motor's magnetic field", "It controls only the paint on the motor"], "Motor synchronous speed depends on frequency and pole count; drive control varies frequency and voltage appropriately.", "easy"),
            ("What is one reason a converter may include an input filter?", "Reduce switching ripple or electromagnetic interference reaching the source", ["Increase all harmonics", "Replace semiconductor switches", "Guarantee unity efficiency"], "Filters attenuate ripple and conducted emissions, with size and stability trade-offs.", "easy"),
        ],
    ],
    "EE05": [
        [
            ("A system block diagram shows a signal path and feedback path. What does a transfer function usually relate for an LTI system with zero initial conditions?", "Output transform to input transform", ["Input current to source resistance only", "The source-code length to file size", "A time delay to an unrelated voltage"], "The transfer function is the ratio Y(s)/U(s) under zero initial conditions for an LTI model.", "easy"),
            ("Why combine blocks in a feedback diagram into an equivalent transfer function?", "To simplify analysis of the relationship between reference, output, and internal signals", ["To remove physical components from the actual plant", "To guarantee the system is stable", "To assign a new unit to time"], "Block reduction provides an algebraic model for analysis but does not by itself prove stability or performance.", "easy"),
        ],
        [
            ("For a stable first-order system's step response, what does the time constant indicate?", "How quickly the response approaches its final value", ["The system's steady-state input voltage only", "The number of poles on the right half-plane", "The sensor's calibration date"], "The time constant sets the exponential response rate; for a standard first-order system, about 63% of the final change occurs after one time constant.", "easy"),
            ("What is steady-state error?", "The remaining difference between desired and actual output after transient effects have settled", ["The initial condition alone", "The sum of all controller gains", "A measurement error that grows without bound by definition"], "Steady-state error measures the long-term tracking difference for a specified input and system.", "easy"),
        ],
        [
            ("For a continuous-time LTI system, where must all poles lie for asymptotic stability in the usual rational model?", "In the open left half of the s-plane", ["In the open right half of the s-plane", "On the positive real axis", "At infinity only"], "A rational continuous-time system is asymptotically stable when all poles are strictly in the left half-plane.", "easy"),
            ("What does the Routh-Hurwitz criterion determine without explicitly calculating polynomial roots?", "The number of roots in the right half-plane", ["The exact values of all time-domain samples", "The controller's source code", "The number of physical sensors"], "The Routh array provides a stability test and counts right-half-plane roots through sign changes in its first column.", "intermediate"),
        ],
        [
            ("In a root-locus plot, what does each branch show as gain varies?", "The location of a closed-loop pole", ["A sensor's physical trajectory", "The frequency response of an open circuit only", "The sampling pattern of a digital camera"], "Root locus traces closed-loop pole locations as a scalar loop gain changes.", "easy"),
            ("What does phase margin assess in a feedback system?", "Relative stability near the unity-gain crossover frequency", ["The steady-state output amplitude only", "The number of controller parameters", "The plant's heat capacity"], "Phase margin estimates the additional phase lag before the loop reaches the −180° instability condition at unity gain.", "intermediate"),
        ],
        [
            ("What is the proportional term in a PID controller based on?", "The current error", ["The integral of all past errors only", "The derivative of the actuator position only", "A fixed value unrelated to the reference"], "The proportional contribution is Kp times the present control error.", "easy"),
            ("Why can integral action reduce steady-state error but also risk overshoot or windup?", "It accumulates error over time, and the accumulated term can grow while the actuator is saturated", ["It differentiates sensor noise only", "It removes feedback", "It forces the plant poles to zero"], "Integral action corrects persistent error, but saturation can let the integrator accumulate excessive command unless anti-windup is used.", "intermediate"),
        ],
    ],
    "ME01": [
        [
            ("Which thermodynamic property is intensive?", "Temperature", ["Total mass", "Total volume", "Total internal energy"], "An intensive property does not depend on the amount of material; temperature is intensive.", "easy"),
            ("For a pure substance at saturation, what condition relates its liquid and vapour phases?", "They coexist at the saturation pressure and temperature", ["They must have different chemical compositions", "The liquid must be at absolute zero", "The phases cannot exchange energy"], "At saturation, liquid and vapour phases coexist in equilibrium at corresponding saturation conditions.", "intermediate"),
        ],
        [
            ("For a closed system with heat added Q and work done by the system W, what is the first-law change in internal energy?", "ΔU = Q − W", ["ΔU = W − Q", "ΔU = QW", "ΔU = Q + W for this sign convention"], "With heat into the system positive and work by the system positive, the first law is ΔU=Q−W.", "easy"),
            ("Why is enthalpy useful in steady-flow devices such as turbines and compressors?", "It combines internal energy with flow work", ["It is always equal to kinetic energy", "It removes the need to account for mass flow", "It applies only to closed systems"], "Specific enthalpy h=u+pv incorporates flow work, simplifying energy balances for open systems.", "intermediate"),
        ],
        [
            ("For an isolated system, what does the second law say about entropy?", "It cannot decrease for a real process", ["It must be zero at every state", "It always decreases during heat transfer", "It equals pressure times volume"], "The entropy of an isolated system remains constant for a reversible process and increases for an irreversible one.", "easy"),
            ("What is the Kelvin-Planck statement of the second law concerned with?", "The impossibility of converting heat from a single reservoir completely into cyclic work", ["The conservation of mass in a nozzle", "The equation of state for an ideal gas", "The maximum velocity of a turbine blade"], "A cyclic heat engine cannot take heat from only one reservoir and convert it entirely into work.", "intermediate"),
        ],
        [
            ("What is the coefficient of performance of a refrigerator?", "Heat removed from the cold space divided by work input", ["Work input divided by heat rejected in every definition", "Net work output divided by fuel mass", "Cold-space temperature divided by pressure"], "For a refrigerator, COP_R=Q_L/W_in for a cycle over the same interval.", "easy"),
            ("Why is a reversible engine's efficiency an upper bound between two fixed-temperature reservoirs?", "It produces the maximum possible work for those reservoirs under the stated conditions", ["It has zero energy input", "It violates the second law", "It must use a particular fuel"], "The Carnot principle bounds the efficiency of any engine operating between the same thermal reservoirs.", "intermediate"),
        ],
        [
            ("What does exergy measure relative to a specified environment?", "The maximum useful work obtainable as a system comes to equilibrium with that environment", ["The total mass in a system", "The system's absolute temperature only", "The amount of energy that cannot change form"], "Exergy quantifies work potential relative to a reference environment; irreversibilities destroy exergy.", "intermediate"),
            ("Why can two systems with the same energy have different exergy?", "Their energy quality and departure from the reference environment can differ", ["Energy is never conserved", "Exergy is independent of state", "One system must have no entropy"], "Exergy depends on how much of the energy can become useful work relative to the environment.", "intermediate"),
        ],
    ],
    "ME02": [
        [
            ("In a static fluid of density ρ, how does pressure change with depth h below a free surface?", "It increases by ρgh", ["It decreases by ρgh", "It is independent of depth", "It changes by h/ρg"], "Hydrostatic gauge pressure at depth h is ρgh for a fluid of constant density.", "easy"),
            ("What does Pascal's law state for a confined fluid at rest?", "An applied pressure change is transmitted throughout the fluid", ["Only shear stress is transmitted", "Pressure is zero at every point", "The fluid's density doubles"], "In a confined fluid at rest, a pressure change is transmitted undiminished throughout the fluid.", "easy"),
        ],
        [
            ("For steady incompressible flow through a pipe with no branches, what continuity relation applies?", "A₁V₁ = A₂V₂", ["A₁/V₁ = A₂/V₂", "A₁ + V₁ = A₂ + V₂", "A₁V₂ = A₂V₁ for all sections"], "Conservation of mass gives constant volumetric flow rate A V for steady incompressible flow.", "easy"),
            ("What does the linear momentum equation relate for a control volume?", "Net external force to the rate of change of momentum flow and accumulation", ["Pressure to temperature only", "Heat transfer to entropy generation only", "Mass to electrical resistance"], "The momentum balance equates external forces to momentum-flux changes plus accumulation.", "intermediate"),
        ],
        [
            ("Along an ideal streamline with no shaft work or losses, what does Bernoulli's equation express?", "Conservation of pressure, elevation, and velocity head", ["Conservation of electrical charge only", "A constant temperature at every point", "The relation between stress and strain"], "Bernoulli's equation is an energy relation for steady incompressible inviscid flow along a streamline under its assumptions.", "easy"),
            ("Why may applying Bernoulli's equation across a pump require an added term?", "The pump adds mechanical energy to the fluid", ["The fluid cannot have velocity", "The pump removes all pressure", "The equation applies only to gases"], "Real pump head adds energy, so the extended energy equation includes a pump-head term and losses.", "intermediate"),
        ],
        [
            ("What does the Darcy-Weisbach equation estimate for pipe flow?", "Head loss due to friction along a pipe", ["The water's chemical composition", "The pump's electrical current only", "The pipe's thermal expansion"], "The Darcy-Weisbach relation gives friction head loss using a friction factor, length-to-diameter ratio, and velocity head.", "easy"),
            ("In fully developed laminar flow through a circular pipe, what is the Darcy friction factor in terms of Reynolds number?", "64/Re", ["Re/64", "0.3164 Re^−0.25 exactly for laminar flow", "It is always 1"], "For laminar pipe flow, the Darcy friction factor is 64/Re; distinguish it from the Fanning factor.", "intermediate"),
        ],
        [
            ("What is the defining flow condition at a solid no-slip wall for a viscous fluid?", "Fluid velocity equals the wall velocity at the surface", ["Fluid velocity is infinite at the wall", "Pressure must equal zero", "Density must be zero"], "The no-slip condition sets the fluid velocity equal to that of the solid boundary.", "easy"),
            ("What does dimensional analysis help engineers do?", "Form dimensionless groups and reduce the number of independent variables in a model", ["Eliminate all experimental measurements", "Guarantee turbulent flow", "Convert every equation into a linear one"], "Dimensional analysis identifies similarity parameters and helps design experiments or scale models.", "intermediate"),
        ],
    ],
    "ME03": [
        [
            ("For a linearly elastic material under uniaxial loading, what is Young's modulus?", "Normal stress divided by normal strain", ["Shear force divided by span", "Strain divided by temperature in every material", "Moment divided by area"], "In the linear elastic range, E=σ/ε for uniaxial normal loading.", "easy"),
            ("For isotropic linear elasticity, what does Poisson's ratio describe?", "The negative ratio of lateral strain to axial strain under uniaxial loading", ["The ratio of axial stress to area", "A material's mass per unit volume", "The ratio of bending moment to shear force"], "Poisson's ratio relates lateral contraction or expansion to axial strain, with a negative sign by convention.", "intermediate"),
        ],
        [
            ("A uniform bar carries an axial force P over area A. What is its average normal stress?", "P/A", ["PA", "A/P", "P + A"], "Average axial stress is the internal axial force divided by the cross-sectional area.", "easy"),
            ("A fully restrained bar is heated uniformly. What kind of stress can develop?", "Thermal stress because free expansion is prevented", ["No stress in any circumstance", "Only torsional stress", "A pressure independent of material properties"], "If expansion is restrained, thermal strain cannot occur freely and internal stress develops based on material and restraint conditions.", "intermediate"),
        ],
        [
            ("In a beam, what is the relationship between the change in shear force and distributed load under a common sign convention?", "The derivative of shear is related to the negative distributed load", ["Shear is always equal to the load times beam length", "Bending moment is independent of shear", "The load equals beam deflection"], "Beam differential relations connect load, shear, and moment; sign conventions determine the sign, commonly dV/dx=−w.", "intermediate"),
            ("What does the area under a shear-force diagram over a beam segment give?", "The change in bending moment over that segment", ["The beam's density", "The maximum axial stress directly", "The support settlement"], "Since dM/dx=V under a common convention, integrating shear gives the moment change.", "easy"),
        ],
        [
            ("For an elastic beam in pure bending, where is normal bending stress zero?", "At the neutral axis", ["At the outermost fibre only", "At the support reaction", "At every point in the beam"], "The linear bending stress distribution crosses zero at the neutral axis.", "easy"),
            ("For a rectangular beam section under vertical shear, where is transverse shear stress typically largest?", "At the neutral axis", ["At the top and bottom free surfaces", "At every point equally", "Only at the beam ends"], "For a rectangular section, the transverse shear distribution is parabolic and peaks at the neutral axis.", "intermediate"),
        ],
        [
            ("For a circular shaft under elastic torsion, what happens to shear stress with radius?", "It increases linearly from zero at the centre to a maximum at the surface", ["It is maximum at the centre and zero at the surface", "It is uniform for all radii", "It changes only with shaft colour"], "For a circular shaft, τ=Tr/J, so shear stress is proportional to radius.", "easy"),
            ("What is Euler's critical buckling load for an ideal slender column with pinned ends?", "π²EI/L²", ["EI/L", "πEI L", "Aσ_y independent of length"], "For a pin-ended ideal column, Euler's critical load is π²EI/L², subject to slenderness and ideal assumptions.", "intermediate"),
        ],
    ],
    "ME04": [
        [
            ("Why is a riser used in a casting mould?", "Supply molten metal to compensate for shrinkage during solidification", ["Increase the pattern's surface finish only", "Remove all mould gas automatically", "Control the cutting speed"], "A riser acts as a reservoir that feeds metal as the casting contracts during solidification.", "easy"),
            ("What is a cold shut casting defect?", "A seam formed when two metal streams fail to fuse properly", ["A cavity caused only by tool wear", "A heat-treatment phase", "An intentional machining allowance"], "Cold shut occurs when fronts of molten metal meet but do not fuse adequately, often due to low temperature or poor flow.", "easy"),
        ],
        [
            ("In metal forming, what is the main effect of plastic deformation?", "The material undergoes permanent shape change beyond its elastic recovery", ["The material returns fully to its original shape", "Only its temperature changes", "It becomes a fluid at every load"], "Plastic deformation remains after unloading once stress exceeds the elastic range.", "easy"),
            ("Why is lubrication used in many metal-forming operations?", "To reduce friction, tool wear, and required forming force", ["To increase surface adhesion without limit", "To remove the need for a die", "To change the metal's atomic number"], "Lubrication reduces interface friction and can improve surface quality and tool life.", "easy"),
        ],
        [
            ("In a basic turning operation, what is cutting speed?", "The relative surface speed between the workpiece and cutting edge", ["The tool's feed per revolution", "The workpiece's diameter divided by its mass", "The spindle's bearing temperature"], "Cutting speed is the surface velocity at the cutting zone, commonly related to spindle speed and workpiece diameter.", "easy"),
            ("What does tool wear generally do to cutting performance if left unchecked?", "It can increase cutting forces and degrade dimensional or surface quality", ["It makes the tool sharper indefinitely", "It eliminates heat generation", "It improves tolerance automatically"], "Wear changes tool geometry and contact, often increasing forces, temperature, and quality variation.", "easy"),
        ],
        [
            ("In fusion welding, what happens at the joint?", "The base material is locally melted, with or without filler material", ["The joint is made only by an adhesive layer", "The parts are connected without any heat or pressure", "The surfaces are ground until they disappear"], "Fusion welding joins materials by melting at the joint; filler may or may not be used.", "easy"),
            ("Why can a heat-affected zone have properties different from the parent metal?", "The thermal cycle changes its microstructure without melting that region", ["It is always chemically identical at every scale", "It experiences no temperature change", "It is removed from every welded part"], "The heat-affected zone undergoes welding thermal cycles that can alter grain structure and properties.", "intermediate"),
        ],
        [
            ("How does a typical powder-bed fusion process build a part?", "Selectively fuse regions of a powder layer, then add successive layers", ["Machine the entire part from a casting only", "Fill a mould with liquid and rotate it", "Join sheets using only adhesive"], "Powder-bed fusion forms a part by selectively melting or sintering material layer by layer.", "easy"),
            ("Why does additive manufacturing often require support structures?", "Overhangs and thermal stresses may need support during the build", ["Every part must be hollow", "Supports increase the design's chemical purity", "The process cannot build vertical walls"], "Supports can hold overhangs, conduct heat, and reduce distortion; requirements depend on process and orientation.", "intermediate"),
        ],
    ],
    "ME05": [
        [
            ("What is a kinematic pair?", "A connection between links that constrains their relative motion", ["A gear and its lubricant only", "Two forces with equal magnitude", "A control algorithm without mechanisms"], "Kinematic pairs define permitted relative motion between connected links.", "easy"),
            ("For a planar mechanism, what does one degree of freedom mean?", "One independent input coordinate specifies its configuration", ["The mechanism has only one link", "It cannot move", "Every link moves independently"], "A one-DOF mechanism's configuration can be determined from one independent generalized coordinate.", "easy"),
        ],
        [
            ("In planar rigid-body motion, what is the velocity of a point relative to another point on the same body?", "The body's angular velocity crossed with the relative position vector", ["The relative position divided by angular acceleration", "The same as zero for every rotating body", "Independent of angular velocity"], "Rigid-body velocity satisfies v_B=v_A+ω×r_B/A.", "intermediate"),
            ("Why does the acceleration of a point rotating about a fixed centre include a centripetal term?", "Its velocity direction changes as it moves around the centre", ["Its speed must always increase", "Gravity vanishes in rotation", "The angular velocity is necessarily zero"], "The radial centripetal acceleration has magnitude ω²r and points toward the centre, even at constant angular speed.", "easy"),
        ],
        [
            ("For two external meshing gears, how do their rotation directions compare?", "They rotate in opposite directions", ["They rotate in the same direction", "One gear remains stationary by definition", "Direction depends only on tooth colour"], "Contact between external gear teeth reverses rotation direction.", "easy"),
            ("For an ideal gear pair, what is the speed ratio magnitude related to?", "The inverse ratio of tooth counts", ["The sum of their radii", "The square of the shaft length", "The input torque alone"], "Angular speed is inversely proportional to gear tooth count for a meshing pair, with sign set by geometry.", "easy"),
        ],
        [
            ("Why are rotating masses balanced?", "To reduce unbalanced centrifugal forces and vibrations", ["To increase the shaft's eccentricity", "To eliminate gravity", "To change the gear ratio"], "Balancing reduces resultant inertia forces and moments that cause vibration and bearing loads.", "easy"),
            ("A rotating mass is balanced by another mass in the same plane. What must their mass-radius products satisfy?", "They must be equal in magnitude and opposite in angular direction", ["They must have equal radii regardless of mass", "Their radii must sum to zero", "Their products must be perpendicular in the same direction"], "Single-plane static balance requires the vector sum of m r to be zero.", "intermediate"),
        ],
        [
            ("What is the primary purpose of a flywheel in an engine or press?", "Smooth cyclic speed variation by storing and releasing rotational energy", ["Regulate the mean speed under changing load by itself", "Convert AC current to DC", "Eliminate all torque fluctuations"], "A flywheel exchanges kinetic energy to reduce speed fluctuations within a cycle.", "easy"),
            ("What does a governor primarily regulate in a prime mover?", "Mean speed as load changes", ["The cyclic fluctuation within one revolution only", "The shaft's material composition", "The bearing clearance"], "A governor adjusts energy input to keep mean speed near its set point as load varies.", "easy"),
        ],
    ],
    "CE01": [
        [
            ("For a simply supported beam under vertical loading, which reactions are found first using equilibrium?", "Support force components and any support moments allowed by the model", ["Concrete compressive strength", "The beam's thermal conductivity", "The maximum deflection without solving the system"], "Statics equations determine support reactions for a statically determinate idealization.", "easy"),
            ("A pin support in a planar beam model can resist which actions?", "Horizontal and vertical forces, but no reaction moment", ["A reaction moment only", "No reaction forces", "A torsional couple in every model"], "An ideal pin restrains translation but permits rotation, so it supplies force reactions but no moment reaction.", "easy"),
        ],
        [
            ("For a prismatic linear-elastic beam, which relation links curvature to bending moment?", "EI times curvature equals bending moment", ["EA times curvature equals shear force", "GJ times curvature equals axial load", "Curvature is independent of stiffness and moment"], "Euler-Bernoulli beam theory gives M=EIκ under its assumptions and a chosen sign convention.", "intermediate"),
            ("Why does a cantilever's free end commonly show its largest deflection under a uniform load?", "Deflection accumulates along the beam from the fixed boundary toward the free end", ["The free end has an ideal moment restraint", "The load is always zero there", "Beam theory forces deflection to be uniform"], "The boundary conditions and integrated curvature generally produce maximum displacement at the free end for this loading.", "easy"),
        ],
        [
            ("What does an influence line show for a response quantity at a fixed point in a structure?", "How that response changes as a unit load moves across the structure", ["How temperature changes with time at one point", "The material's stress-strain curve", "The shape of a moving vehicle"], "An influence line plots a response such as reaction, shear, or moment as a unit load position varies.", "easy"),
            ("Why are influence lines useful for bridge analysis?", "They help identify load positions that maximize a response", ["They determine the bridge's paint colour", "They replace all structural safety factors", "They ensure every load is static"], "Moving-load placement can be chosen using influence-line ordinates to locate critical effects.", "easy"),
        ],
        [
            ("What makes a planar structure statically indeterminate?", "Unknown reactions or internal forces exceed the independent equilibrium equations", ["It has no supports", "Every member is rigid", "It is made from more than one material"], "A statically indeterminate system requires compatibility and constitutive relations in addition to equilibrium.", "easy"),
            ("Why can a redundant support change internal forces even when equilibrium still holds?", "Compatibility and stiffness determine how load is shared among restraints", ["Equilibrium does not apply to redundant structures", "The load vanishes at the extra support", "Support forces are always equal"], "Redundant reactions depend on deformation compatibility and member stiffness as well as equilibrium.", "intermediate"),
        ],
        [
            ("In the direct stiffness method, what does a structural stiffness matrix relate?", "Nodal forces to nodal displacements", ["Temperature to concrete colour", "Material density to beam span only", "Strain to chemical composition"], "The assembled global stiffness matrix relates the vector of nodal forces to nodal displacements.", "easy"),
            ("Why must support boundary conditions be applied before solving for nodal displacements?", "They constrain rigid-body motion and represent known supports", ["They increase the number of unknowns", "They change the material's Young's modulus", "They remove the need for loads"], "Boundary conditions remove unsupported rigid-body modes and define the system's supported behaviour.", "intermediate"),
        ],
    ],
    "CE02": [
        [
            ("What does the liquid limit of a fine-grained soil represent?", "A consistency boundary between liquid-like and plastic behaviour", ["The maximum particle diameter in gravel", "The soil's saturated unit weight", "The depth of the water table"], "The liquid limit is an Atterberg limit marking a transition in consistency of fine-grained soil.", "easy"),
            ("Why are grain-size distribution and Atterberg limits used in soil classification?", "They summarize particle sizes and plasticity behaviour", ["They directly measure the building's total load", "They determine the concrete mix colour", "They eliminate the need for site investigation"], "Gradation and plasticity characteristics help classify soils and anticipate engineering behaviour.", "easy"),
        ],
        [
            ("What does a compaction test relate for a specified compactive effort?", "Dry unit weight to water content", ["Permeability to sample colour", "Bearing capacity to wind speed", "Void ratio to air temperature only"], "A compaction curve shows dry density versus water content for a given compactive effort.", "easy"),
            ("At optimum moisture content in a standard compaction curve, what is attained for that effort?", "Maximum dry unit weight", ["Zero air voids in every soil", "Minimum possible particle size", "Maximum permeability by definition"], "The optimum moisture content corresponds to peak dry density for the specified compaction energy.", "easy"),
        ],
        [
            ("According to Darcy's law for saturated soil, seepage discharge is proportional to which quantity?", "Hydraulic gradient", ["The square of soil colour", "The inverse of porosity in all cases", "Atmospheric pressure only"], "Darcy's law gives discharge Q=k i A for laminar flow through saturated soil.", "easy"),
            ("What is a flow net used to estimate in seepage analysis?", "Flow quantity and pore-water pressure/head distribution", ["Concrete compressive strength", "Traffic volume", "The soil's mineral age"], "A flow net represents equipotential lines and flow lines for estimating seepage and pressure head.", "intermediate"),
        ],
        [
            ("In saturated soil, what is effective stress approximately equal to?", "Total stress minus pore-water pressure", ["Pore pressure minus total stress", "Total stress plus void ratio", "Unit weight times permeability only"], "Terzaghi's effective stress principle for saturated soil is σ′=σ−u.", "easy"),
            ("What does primary consolidation describe in saturated fine-grained soil?", "Volume decrease as excess pore pressure dissipates and effective stress rises", ["Immediate elastic rebound without drainage", "Chemical cementation of all grains", "The formation of a new water table"], "Primary consolidation is time-dependent settlement associated with drainage and dissipation of excess pore pressure.", "intermediate"),
        ],
        [
            ("In the Mohr-Coulomb shear strength model, what do c and φ represent?", "Cohesion intercept and friction angle", ["Consolidation time and permeability", "Compaction energy and void ratio", "Cement content and pore pressure"], "The criterion is commonly written τ_f=c+σ′ tanφ, using effective normal stress for drained conditions.", "easy"),
            ("Why does footing width influence ultimate bearing capacity in classical shallow-foundation models?", "The failure mechanism and surcharge/soil-weight contributions depend on geometry", ["Width changes gravity", "Soil strength becomes independent of stress", "A wider footing always has zero settlement"], "Bearing-capacity terms include geometry and overburden effects; actual design also considers settlement and code factors.", "intermediate"),
        ],
    ],
    "CE03": [
        [
            ("In chain surveying, why should survey lines be selected to form well-conditioned triangles?", "Small angular or linear errors then have less effect on plotted positions", ["Triangles eliminate the need to measure distance", "A chain cannot be used on straight lines", "It ensures every point is at the same elevation"], "Well-conditioned geometry reduces error amplification during plotting and checks.", "intermediate"),
            ("What is the main purpose of a compass traverse?", "Measure a connected sequence of lines using lengths and bearings", ["Measure only the soil's water content", "Determine concrete strength without samples", "Map only underground utilities"], "A traverse uses connected survey lines whose lengths and directions establish control.", "easy"),
        ],
        [
            ("In differential levelling, what does a backsight reading help determine?", "The height of instrument from a known benchmark elevation", ["The horizontal angle to a distant star", "The soil's friction angle", "The traffic speed on a road"], "A backsight on a point of known reduced level gives the instrument height.", "easy"),
            ("What do contour lines connect on a topographic map?", "Points having equal elevation", ["Points with equal horizontal distance from north", "Locations of equal soil colour", "Points with equal rainfall in every season"], "A contour is a line of constant elevation relative to the map datum.", "easy"),
        ],
        [
            ("Why adjust a closed traverse when its measured angles or coordinates do not close exactly?", "To distribute small observational errors consistently across the traverse", ["To force the survey onto a different datum", "To remove all measurements", "To make every line length identical"], "Adjustment distributes closure error according to a suitable method and observation quality assumptions.", "intermediate"),
            ("What is a common first check for a closed polygon traverse?", "Compare the computed angular sum with its theoretical sum", ["Compare every line to a river depth", "Check the pavement skid number", "Verify the building's concrete age"], "The sum of interior angles for an n-sided plane polygon is (n−2)×180°; observed closure is checked against it.", "easy"),
        ],
        [
            ("What does a total station combine in common surveying practice?", "Electronic angle measurement, distance measurement, and onboard computation", ["A soil compactor and water pump", "A GNSS satellite and a concrete mixer", "A levelling staff and traffic signal"], "A total station measures angles and electronic distances and can calculate coordinates from observations.", "easy"),
            ("Why is a backsight orientation used when setting up a total station?", "It establishes the instrument's horizontal reference direction", ["It determines the prism's chemical composition", "It sets the atmospheric pressure to zero", "It replaces the need to centre over a station"], "A known backsight provides an orientation reference for measured horizontal directions.", "easy"),
        ],
        [
            ("What does GNSS positioning estimate from satellite signals?", "Receiver position and clock offset from measured signal travel times", ["Soil shear strength", "Road friction coefficient", "Structural damping ratio"], "GNSS uses pseudorange measurements from satellites to estimate position and receiver clock bias.", "intermediate"),
            ("Why are multiple satellite observations needed for a 3D GNSS position?", "They provide enough independent geometric constraints to solve position and receiver clock offset", ["Each satellite measures a different soil layer", "One satellite transmits the entire map", "Satellite count determines the receiver's battery size"], "A standard standalone solution needs at least four independent satellite pseudoranges to solve three coordinates and clock bias.", "intermediate"),
        ],
    ],
    "CE04": [
        [
            ("What does a piezometer measure at a point in a liquid system?", "Pressure head relative to the liquid column", ["Velocity head only", "The fluid's viscosity directly", "The pipe's outside diameter"], "A piezometer indicates static pressure head for a suitable liquid and pressure range.", "easy"),
            ("Why is a differential manometer useful?", "It measures pressure difference between two points using fluid-column balance", ["It measures only temperature", "It eliminates gravity", "It determines a pump's electrical efficiency"], "A manometer relates pressure difference to hydrostatic column differences and fluid densities.", "easy"),
        ],
        [
            ("What does continuity require for steady incompressible flow in a closed conduit with no branches?", "The volume flow rate is constant along the conduit", ["The velocity is constant regardless of area", "The pressure is constant", "The fluid density increases downstream"], "Mass conservation gives A V constant for steady incompressible flow along a single streamtube.", "easy"),
            ("What does the momentum equation help calculate in a pipe bend?", "The resultant force needed to change the fluid's momentum direction", ["The material's Young's modulus", "The water's boiling point only", "The pipe's paint thickness"], "Turning a flowing stream changes momentum, producing forces on the bend and supports.", "intermediate"),
        ],
        [
            ("Why include minor-loss coefficients for fittings in a pipe network?", "Fittings cause local energy losses in addition to straight-pipe friction", ["They account only for fluid density", "They remove the need for pipe length", "They represent the pump's shaft work"], "Bends, valves, entrances, and other fittings create local losses often expressed as K V²/(2g).", "easy"),
            ("What is the hydraulic grade line?", "Elevation plus pressure head along the flow", ["Elevation plus velocity head only", "Pipe length plus diameter", "Pressure divided by fluid temperature"], "The HGL is z+p/γ; the energy grade line also includes velocity head.", "intermediate"),
        ],
        [
            ("For a given channel geometry, what happens at critical flow?", "Specific energy is at a minimum for the discharge", ["The flow depth is always zero", "The Froude number is always zero", "The water surface is necessarily horizontal"], "Critical depth separates subcritical and supercritical regimes and corresponds to minimum specific energy at fixed discharge.", "intermediate"),
            ("For open-channel flow, what does a Froude number below one indicate?", "Subcritical flow", ["Supercritical flow", "Critical flow exactly", "No flow"], "Fr<1 indicates subcritical flow, where gravity-wave celerity exceeds the mean flow speed.", "easy"),
        ],
        [
            ("In a pump, what is the purpose of a priming operation for a centrifugal pump?", "Remove air and fill the casing/suction line with liquid before starting", ["Increase the impeller diameter while running", "Drain the reservoir", "Set the motor's pole count"], "Priming establishes a liquid-filled passage so a centrifugal pump can develop suction and head.", "easy"),
            ("What does a Venturi meter infer from pressure measurements?", "Flow rate using the pressure difference created by a constriction", ["Soil consolidation rate", "The channel's sediment age", "The fluid's colour"], "A Venturi meter uses continuity and energy relations between a larger section and throat to estimate discharge.", "easy"),
        ],
    ],
    "CE05": [
        [
            ("Why is an origin-destination study useful in highway planning?", "It describes travel demand between locations and helps evaluate network needs", ["It measures pavement bitumen content directly", "It replaces geometric design", "It determines soil plasticity"], "O-D data helps understand trip patterns and forecast demand for transport planning.", "easy"),
            ("Why should a highway alignment consider both terrain and design standards?", "They affect safety, earthwork, cost, and achievable operating conditions", ["They determine the vehicle's engine size", "They eliminate the need for drainage", "They set the road's legal ownership"], "Alignment balances geometric standards with topography, environmental impacts, safety, and construction cost.", "intermediate"),
        ],
        [
            ("What is stopping sight distance intended to provide?", "Enough visible road distance for a driver to perceive, react, and stop safely", ["A distance for overtaking only", "The length of a bridge expansion joint", "The spacing between traffic signals in every case"], "SSD accounts for perception-reaction travel and braking under assumed speed and friction conditions.", "easy"),
            ("Why is superelevation provided on a horizontal highway curve?", "To help counter lateral acceleration and reduce reliance on tire friction", ["To increase longitudinal grade", "To drain a bridge foundation only", "To make the curve's radius zero"], "Cross-slope banking helps balance centrifugal effect for a design speed and curve radius.", "easy"),
        ],
        [
            ("What does the California Bearing Ratio (CBR) test estimate for pavement design?", "A soil or granular material's resistance to penetration relative to a standard material", ["The asphalt's ignition temperature", "The concrete's electrical conductivity", "The road's traffic signal cycle"], "CBR is an empirical penetration-resistance index used in pavement design methods.", "easy"),
            ("Why is adequate pavement drainage important?", "Water can weaken pavement layers and subgrade support", ["It increases traffic volume", "It changes the highway's geometric alignment", "It removes the need for compaction"], "Excess water can reduce strength, promote stripping or pumping, and accelerate pavement distress.", "easy"),
        ],
        [
            ("For a simple traffic-flow model, how are flow q, density k, and space-mean speed v related?", "q = kv", ["q = k + v", "q = k/v", "q = k²v²"], "Flow is the product of density and space-mean speed when consistent units and definitions are used.", "easy"),
            ("Why can increasing traffic density beyond a critical level reduce flow?", "Congestion lowers average speed enough to outweigh the increase in vehicles per distance", ["Vehicles become lighter", "Road length decreases", "The traffic signal changes wavelength"], "On the congested branch of the fundamental diagram, speed falls sharply as density rises, so flow can drop.", "intermediate"),
        ],
        [
            ("What is a key purpose of a railway track's ballast layer?", "Distribute loads, provide drainage, and help hold sleepers in position", ["Power the locomotive", "Replace the rails", "Measure wheel speed"], "Ballast supports and stabilizes the track structure while facilitating drainage and maintenance.", "easy"),
            ("Why are airport runway orientation and length selected using site and aircraft data?", "Wind, elevation, temperature, and aircraft performance affect safe takeoff and landing", ["Runways must point toward magnetic north in every case", "Aircraft use identical performance at all sites", "Orientation is chosen only by terminal architecture"], "Runway planning considers wind coverage and aircraft operating requirements, alongside terrain and safety constraints.", "intermediate"),
        ],
    ],
    "IT01": [
        [
            ("Which set best describes common components of an information system?", "People, processes, data, and technology", ["Only computers and monitors", "Only a network and an internet connection", "Only managers and spreadsheets"], "Information systems combine people, processes, data, and technology to support organizational work.", "easy"),
            ("Why is data governance part of an information-system design?", "It defines how data is owned, protected, maintained, and used", ["It chooses the monitor resolution", "It replaces all business processes", "It guarantees that all data is correct"], "Governance assigns responsibilities and controls for data across its lifecycle.", "intermediate"),
        ],
        [
            ("A point-of-sale system records each completed purchase. Which type of system is it?", "A transaction processing system", ["A compiler", "A geographic coordinate system", "A content delivery network"], "Transaction processing systems capture and process routine operational events.", "easy"),
            ("What does a decision-support system typically provide to a manager?", "Analysis and models for exploring decision alternatives", ["A guarantee that every decision is optimal", "Only a permanent archive of raw events", "A replacement for all organizational policies"], "Decision-support tools help analyze information and alternatives; decision authority remains with people.", "easy"),
        ],
        [
            ("What is a typical role of an enterprise resource planning system?", "Coordinate information and workflows across functions using shared data", ["Route packets between autonomous networks", "Compile source code into machine instructions", "Measure a building's elevation"], "ERP systems integrate processes such as finance, inventory, and procurement around shared business data.", "easy"),
            ("Why can a shared ERP data model reduce duplicate data entry?", "Different functions can use consistent records for the same business entities", ["It removes the need for access control", "It forces each department to keep separate copies", "It guarantees every record is current without updates"], "Shared records can reduce redundancy, though data quality and permissions still need governance.", "intermediate"),
            ("An ERP rollout finds that sales and inventory use different product identifiers. What should the implementation team prioritize?", "Agree on governed master-data definitions and map legacy records before migration", ["Allow every department to keep an undocumented identifier", "Remove validation so any code is accepted", "Copy the conflicting records into every module unchanged"], "Shared enterprise processes depend on consistent master data; migration mapping and ownership should resolve conflicts before the new workflow relies on them.", "intermediate"),
        ],
        [
            ("During systems analysis, why document the current workflow before proposing a replacement?", "It reveals actual needs, constraints, and failure points that the design must address", ["It guarantees the current workflow is efficient", "It lets the team skip stakeholder interviews", "It determines the product's colour palette"], "As-is analysis provides evidence about users, process steps, and constraints before design choices are made.", "easy"),
            ("What is the purpose of a use case?", "Describe interactions between an actor and a system to achieve a goal", ["List every database index", "Specify a processor's pinout", "Replace the need for acceptance criteria"], "Use cases capture goal-oriented interactions and can help derive functional requirements and tests.", "easy"),
        ],
        [
            ("What does an IT service-level agreement (SLA) usually specify?", "Measurable service commitments and how they are assessed", ["The source code of every service", "A promise of zero incidents under all conditions", "A list of employees' personal passwords"], "An SLA defines service commitments such as availability or response targets and their measurement context.", "easy"),
            ("Why use change management for a production IT service?", "Assess risk, authorize changes, and coordinate implementation and rollback", ["Prevent all future updates", "Make every change invisible to users", "Replace monitoring with approvals"], "Change management reduces avoidable disruption by reviewing scope, risk, timing, communication, and recovery.", "intermediate"),
        ],
    ],
    "IT02": [
        [
            ("What is the role of a physical transmission medium in a data-communication system?", "Carry a signal between a transmitter and receiver", ["Choose the application's user permissions", "Store the network's routing table permanently", "Convert every message into source code"], "A medium provides the physical path over which an electrical, optical, or radio signal propagates.", "easy"),
            ("Why can a twisted pair reduce interference compared with two untwisted wires?", "The twists help cancel induced noise and reduce electromagnetic coupling", ["It increases the signal's information content", "It makes the cable immune to every source of noise", "It removes the need for a receiver"], "Twisting balances exposure to external fields, improving common-mode noise rejection; it does not eliminate all interference.", "intermediate"),
        ],
        [
            ("In digital communication, what does a line code map?", "Bit values to signal levels or transitions over time", ["IP addresses to domain names", "Database rows to tables", "Source code to test plans"], "Line coding defines a baseband waveform representation for transmitted bits.", "easy"),
            ("What is the purpose of multiplexing?", "Share a communication channel among multiple signals or data streams", ["Increase the number of errors intentionally", "Make every receiver use the same address", "Replace the physical medium"], "Multiplexing combines streams for transmission over a shared resource, with a method for separating them at the receiver.", "easy"),
        ],
        [
            ("A parity bit is appended to a block of data. What can simple parity detect?", "Any odd number of bit flips in the protected block", ["Every even number of bit flips", "The location of every error", "All burst errors of arbitrary length"], "A parity check changes when an odd number of bits flip, but cannot locate errors and misses even-weight patterns.", "intermediate"),
            ("What does a cyclic redundancy check (CRC) use to detect many transmission errors?", "Polynomial division over binary data", ["A human-readable checksum sentence", "A network route chosen by shortest path", "A public-key signature for confidentiality"], "CRC encodes a remainder from polynomial arithmetic and detects many common burst and random error patterns.", "intermediate"),
        ],
        [
            ("What is the purpose of a router's forwarding table?", "Select an outgoing interface or next hop for a packet", ["Store the content of every web page", "Assign electrical voltage to a cable", "Authenticate an application's users"], "A router consults forwarding information to choose where to send a packet next.", "easy"),
            ("How does a switch commonly learn which port leads to a source MAC address?", "By observing the source MAC address on received frames", ["By reading the destination IP's DNS record", "By measuring packet temperature", "By querying a public certificate authority"], "A learning switch records source MAC addresses and their incoming ports, subject to aging and VLAN context.", "easy"),
        ],
        [
            ("What does a data-link protocol provide on a local link?", "Framing and link-level delivery functions such as addressing or error detection", ["A guarantee of end-to-end application correctness", "A replacement for IP routing", "A guarantee that a host has no malware"], "Link-layer protocols define local frame delivery and related medium-specific functions; upper layers provide additional services.", "easy"),
            ("Why can retransmission improve reliability but reduce throughput on a lossy link?", "Some capacity is spent sending frames again instead of new payload", ["Retransmission makes the channel wider", "It removes propagation delay", "It decreases the number of transmitted bits"], "Retries recover some losses but consume airtime or bandwidth and add delay.", "intermediate"),
        ],
    ],
    "IT03": [
        [
            ("Why might an organization use a storage array with redundancy?", "To improve availability or protect against some drive failures", ["To guarantee that data never needs backup", "To make every read execute on a CPU", "To eliminate the need for access control"], "Redundant storage can tolerate specified hardware failures, but it does not replace independent backups or security controls.", "easy"),
            ("What is a key trade-off when choosing between faster local storage and lower-cost object storage?", "Latency, access pattern, durability, and cost requirements differ", ["All storage types have identical performance", "Object storage can store only images", "Local storage is always safer from failure"], "Storage tiers trade latency and access semantics against cost, scale, and resilience characteristics.", "intermediate"),
        ],
        [
            ("What does a hypervisor do?", "Manage virtual machines and allocate virtualized hardware resources", ["Compile web pages into HTML", "Route application requests by URL only", "Replace the host's physical memory"], "A hypervisor provides the execution and resource-isolation layer for virtual machines.", "easy"),
            ("How does a typical container differ from a virtual machine?", "A container shares the host kernel while isolating processes and user space", ["A container always runs a separate guest kernel", "A VM shares the host process namespace by definition", "Containers cannot include application dependencies"], "Containers generally use OS-level isolation and share a kernel; VMs virtualize hardware and run guest operating systems.", "easy"),
        ],
        [
            ("What does an incident-management process primarily aim to restore?", "Normal service operation as quickly and safely as possible", ["The development team's meeting schedule", "Every deleted email", "A user's browser cache"], "Incident management prioritizes restoring service and minimizing impact; root-cause work may continue separately.", "easy"),
            ("Why categorize incidents by impact and urgency?", "To prioritize response and route work to appropriate teams", ["To determine which user caused the incident", "To make every incident equal priority", "To remove incident records"], "A consistent priority model supports triage, escalation, and expectation setting.", "easy"),
        ],
        [
            ("What does an availability objective usually measure?", "The proportion of time a service meets a defined usable condition", ["The number of files in a release", "The maximum database size only", "The amount of code written each day"], "Availability measures depend on the defined service condition, measurement window, and exclusions.", "easy"),
            ("Why preserve a timeline during incident response?", "It helps correlate events, actions, and recovery results", ["It guarantees attribution to a person", "It replaces monitoring data", "It hides the incident from stakeholders"], "A timeline supports coordination and later analysis, particularly when many people and systems are involved.", "easy"),
        ],
        [
            ("What is the purpose of capacity planning?", "Ensure resources can meet expected demand with suitable headroom and cost", ["Guarantee demand never changes", "Avoid measuring utilization", "Replace service-level objectives"], "Capacity planning forecasts demand and evaluates resource needs, constraints, cost, and resilience.", "easy"),
            ("Why test a disaster-recovery plan instead of relying only on written procedures?", "A test reveals whether people, systems, data, and dependencies can actually recover", ["A document guarantees recovery time", "Testing permanently prevents disasters", "Recovery plans apply only to hardware"], "Exercises validate assumptions, responsibilities, recovery objectives, and technical procedures under realistic conditions.", "intermediate"),
        ],
    ],
    "IT04": [
        [
            ("What is the browser's same-origin policy primarily intended to restrict?", "Certain cross-origin script access to data and resources", ["All requests to the same origin", "Every use of HTML forms", "The server's ability to receive HTTP"], "The same-origin policy limits how scripts from one origin can interact with resources from another, with controlled cross-origin mechanisms available.", "intermediate"),
            ("Why should a web application load JavaScript and styles from a deliberate, controlled set of sources?", "It reduces exposure to unexpected third-party code execution", ["It guarantees that every script is bug-free", "It removes the need for authentication", "It makes the page work without a browser"], "Restricting resource sources can reduce injection impact, though it must be paired with safe coding and dependency controls.", "intermediate"),
        ],
        [
            ("Why keep a web application's rendering separate from its data-fetching logic?", "It can make state handling, testing, and UI changes easier to reason about", ["The browser requires every request in a different file", "It guarantees zero network failures", "It prevents the server from returning JSON"], "Separating responsibilities can improve maintainability and testability when the boundaries remain clear.", "easy"),
            ("What should a single-page application do when a user refreshes a nested client-side route?", "The hosting setup should serve the app entry point for that route or the server should handle the route", ["Return an empty file", "Change the route to an external site", "Delete the browser history"], "Client-side routes need a server fallback or matching server routes so refreshes can load the application.", "easy"),
        ],
        [
            ("Why should an API return a clear error status and a stable error shape?", "Clients can handle failures predictably without parsing arbitrary server text", ["It prevents all network errors", "It makes authorization unnecessary", "It hides whether a request succeeded"], "A documented error contract lets clients distinguish validation, authorization, conflict, and server failures.", "easy"),
            ("What is a common reason to make a POST operation idempotent with an idempotency key?", "A client retry should not create duplicate effects after an uncertain network outcome", ["To make the request body public", "To increase the number of database writes", "To bypass server-side validation"], "An idempotency key lets a server recognize retries and avoid repeating a non-idempotent operation.", "intermediate"),
        ],
        [
            ("What does API versioning help manage?", "Changes to an API contract while supporting existing clients", ["The physical age of a server", "The order of CSS rules", "A user's password complexity"], "Versioning or compatibility policies allow an API to evolve without unexpectedly breaking consumers.", "easy"),
            ("Why validate an API response against a schema in an integration test?", "It detects contract changes that clients may not handle", ["It proves the response is always factually correct", "It encrypts the response", "It replaces authorization testing"], "Schema checks detect structural contract drift but do not by themselves verify every semantic or security property.", "intermediate"),
        ],
        [
            ("Why is server-side authorization required even when a UI hides an admin button?", "A client can call the API directly without using the UI", ["Browsers cannot run scripts", "CSS controls database permissions", "A hidden button encrypts the route"], "The server must enforce permissions on every protected operation because client-side controls are not a security boundary.", "easy"),
            ("What does HTTPS provide for a web connection when certificates are correctly validated?", "Encryption in transit and authentication of the server endpoint", ["Protection from every malicious script", "Confidentiality after data reaches the server", "A guarantee that the website's content is honest"], "TLS protects the connection against network observation and tampering and authenticates the endpoint through certificate validation; it does not ensure server-side safety.", "intermediate"),
        ],
    ],
    "CSE_AIML01": [
        [
            ("In a state-space search problem, what does a goal test determine?", "Whether the current state satisfies the target condition", ["Whether the source code compiles", "The cost of every possible action", "The number of training examples"], "A goal test identifies whether a search node represents a solution.", "easy"),
            ("Why should a search problem define its transition model explicitly?", "It specifies which states can result from each action", ["It selects the computer's clock speed", "It removes the need for a goal test", "It guarantees a unique solution"], "The transition model defines the successors available from a state and action.", "easy"),
        ],
        [
            ("What does uniform-cost search prioritize?", "The lowest accumulated path cost so far", ["The fewest characters in the state name", "The deepest node", "The highest heuristic estimate only"], "Uniform-cost search expands a frontier node with minimum path cost g(n).", "easy"),
            ("A* search evaluates a node using which standard function?", "f(n)=g(n)+h(n)", ["f(n)=g(n)−h(n)", "f(n)=h(n)/g(n)", "f(n)=g(n)h(n) for every problem"], "A* combines the known cost-to-date g(n) with an estimated remaining cost h(n).", "easy"),
        ],
        [
            ("In a constraint-satisfaction problem, what does a variable's domain contain?", "The values that variable may take", ["The full list of search algorithms", "Only the final answer", "The cost of a CPU instruction"], "A CSP defines variables, domains, and constraints over allowed assignments.", "easy"),
            ("Why can the minimum-remaining-values heuristic help choose a CSP variable?", "It selects a variable with the fewest legal values left, exposing failure early", ["It chooses the variable with the longest name", "It guarantees every assignment succeeds", "It removes all constraints"], "MRV is a fail-fast heuristic that prioritizes the most constrained unassigned variable.", "intermediate"),
        ],
        [
            ("What does a knowledge base in a logic-based AI system contain?", "Facts and rules expressed in a representation used for reasoning", ["Only the rendered user interface", "A copy of the processor's microcode", "Random values without relationships"], "A knowledge base stores declarative information from which an inference procedure can derive conclusions.", "easy"),
            ("What is the role of unification in first-order logic inference?", "Find substitutions that make two expressions match", ["Sort the input data by file size", "Choose an operating system process", "Encrypt a theorem"], "Unification computes variable substitutions that allow predicates or terms to be matched.", "intermediate"),
        ],
        [
            ("In adversarial game search, what does minimax assume about the opponent?", "The opponent chooses actions that minimize the maximizing player's outcome", ["The opponent chooses randomly in every state", "The opponent cannot observe the board", "The opponent always maximizes the same utility"], "Minimax models optimal play by alternating maximizing and minimizing choices.", "easy"),
            ("Why does alpha-beta pruning preserve minimax's final decision?", "It skips branches that cannot change the outcome under the current bounds", ["It changes all leaf utilities to zero", "It expands every possible state twice", "It replaces the evaluation function with a random one"], "Alpha-beta pruning removes branches provably irrelevant to the backed-up minimax value.", "intermediate"),
        ],
    ],
    "CSE_AIML02": [
        [
            ("Why split data into training and test sets before fitting a predictive model?", "To estimate performance on examples not used for fitting", ["To make all labels equally common", "To eliminate the need for feature definitions", "To guarantee a high test score"], "A held-out test set gives an estimate of generalization if it is not used for model selection.", "easy"),
            ("What information leakage occurs if a target-derived feature is included among model inputs?", "The model receives information unavailable at prediction time", ["The test set has fewer examples", "The model cannot calculate a loss", "The labels become unsupervised"], "Leakage lets training use information that would not be legitimately available when making real predictions.", "intermediate"),
        ],
        [
            ("In linear regression, what does L2 regularization penalize?", "The squared magnitudes of model coefficients", ["The number of test examples", "The prediction labels only", "The training time in seconds"], "Ridge-style L2 regularization adds a penalty proportional to the sum of squared coefficients.", "easy"),
            ("Why standardize features before using a regularized linear model?", "Feature scale can affect the relative strength of coefficient penalties", ["It makes every target equal to zero", "It guarantees independent features", "It removes the need for validation"], "Regularization acts on coefficients, so differently scaled features can receive uneven effective penalization.", "intermediate"),
        ],
        [
            ("For a binary classifier, what does recall measure for the positive class?", "The fraction of actual positives that are correctly identified", ["The fraction of predicted positives that are correct", "The fraction of all examples that are negative", "The number of model parameters"], "Recall is TP/(TP+FN); it measures coverage of the actual positive cases.", "easy"),
            ("Why should precision and recall be considered together when selecting a classifier threshold?", "Changing the threshold often trades off false positives against false negatives", ["They are always equal", "They measure only training time", "The threshold cannot affect either metric"], "Precision and recall respond differently to threshold changes, so the preferred balance depends on the application.", "intermediate"),
        ],
        [
            ("Why can a random forest reduce variance compared with one deep decision tree?", "It averages diverse trees trained on resampled data and feature subsets", ["It removes every decision boundary", "It uses no training examples", "It guarantees no bias"], "Ensembling decorrelated trees can reduce variance; it does not eliminate bias or guarantee optimal performance.", "intermediate"),
            ("What is one purpose of feature subsampling in a random forest?", "Encourage tree diversity by limiting features considered at splits", ["Ensure every tree is identical", "Remove all categorical variables", "Make the forest deterministic across every seed"], "Random feature subsets decorrelate trees and can improve ensemble averaging.", "easy"),
        ],
        [
            ("What does k-means minimize during clustering?", "Within-cluster sum of squared distances to centroids", ["The number of input features", "The classification error against labels", "The largest distance between any two data points"], "K-means optimizes the sum of squared Euclidean distances from points to assigned cluster centroids.", "easy"),
            ("Why run k-means with different initial centroids?", "The objective can converge to different local minima depending on initialization", ["It changes the definition of Euclidean distance", "It guarantees the best possible clustering", "It converts an unsupervised task into supervised learning"], "K-means is sensitive to initialization; multiple starts can find a lower objective but do not guarantee a global optimum.", "intermediate"),
        ],
    ],
    "CSE_AIML03": [
        [
            ("What does a neural-network activation function add between linear layers?", "Nonlinearity", ["A database transaction", "A fixed label for each input", "A guarantee of global optimization"], "Without nonlinear activations, stacked affine layers still represent only an affine mapping.", "easy"),
            ("Why initialize all neurons in a layer with identical weights cautiously?", "They may receive identical gradients and learn redundant features", ["It makes the loss function disappear", "It changes the input labels", "It guarantees the model will overfit"], "Symmetric initialization can keep neurons equivalent; appropriate random initialization helps break symmetry.", "intermediate"),
        ],
        [
            ("What does backpropagation compute?", "Gradients of the loss with respect to model parameters using the chain rule", ["The exact global minimum for every network", "The test-set labels", "The training examples' storage locations"], "Backpropagation efficiently applies the chain rule through the network to compute parameter gradients.", "easy"),
            ("What can an excessively large learning rate cause during gradient-based training?", "Updates may overshoot and fail to converge", ["The model becomes a nearest-neighbor classifier", "The training set is duplicated", "The loss is guaranteed to decrease every step"], "Large steps can jump across a minimum or diverge; the learning rate needs suitable tuning or scheduling.", "easy"),
        ],
        [
            ("What does a convolutional filter share across image positions?", "The same learned weights", ["A separate full parameter matrix at every pixel", "The image's labels", "A different coordinate system for each batch"], "Convolution uses weight sharing so the same kernel detects local patterns at different positions.", "easy"),
            ("Why can pooling or strided convolution reduce computation in later image layers?", "They reduce spatial resolution and the number of activations", ["They increase image resolution without added computation", "They guarantee translation invariance", "They eliminate all channels"], "Downsampling reduces feature-map size, though it can lose spatial detail and does not guarantee invariance.", "intermediate"),
        ],
        [
            ("In a recurrent neural network, what does the hidden state carry forward?", "A learned summary of prior sequence context", ["The complete future sequence", "The optimizer's source code", "A fixed class label for every time step"], "The hidden state allows information from earlier positions to influence later sequence computations.", "easy"),
            ("What does self-attention allow a sequence model to compute?", "Contextual representations using relationships among sequence positions", ["A single fixed embedding independent of context", "The exact grammar of every language", "A sorted sequence of token IDs"], "Self-attention weights information from positions in a sequence to form context-dependent representations.", "easy"),
        ],
        [
            ("What does dropout do during training in a neural network?", "Randomly disable selected activations to discourage co-adaptation", ["Delete the validation set", "Change every target label", "Set all model weights permanently to zero"], "Dropout masks activations during training; inference typically uses the full network with appropriate scaling.", "easy"),
            ("Why monitor latency and memory after deploying a deep model?", "The production workload and hardware constraints can differ from offline training", ["Model accuracy automatically measures resource use", "Inference always uses the training GPU", "Deployment removes all input variability"], "Operational evaluation needs latency, memory, throughput, and quality measurements under realistic serving conditions.", "intermediate"),
        ],
    ],
    "CSE_AIML04": [
        [
            ("Why might a tokenizer normalize text before splitting it into tokens?", "Consistent forms can reduce superficial variation in the model input", ["Normalization guarantees the sentence is true", "It translates every text into English", "It removes the need for a vocabulary"], "Normalization can standardize selected variations, but the right policy depends on language and task.", "easy"),
            ("What is a trade-off of lowercasing all input text?", "It can reduce vocabulary size but erase case distinctions such as names or acronyms", ["It always improves every NLP task", "It changes the token order", "It encrypts the text"], "Lowercasing reduces some lexical variation but can discard meaningful capitalization cues.", "intermediate"),
        ],
        [
            ("In a causal language model, what is the next-token objective?", "Predict the next token from preceding context", ["Predict every future token while reading none of the context", "Classify the document's file type only", "Reconstruct the training labels from a test set"], "Autoregressive language modelling estimates a distribution over the next token conditioned on prior tokens.", "easy"),
            ("Why can perplexity be compared only cautiously across tokenizers?", "Different tokenization changes the sequence units and the metric's scale", ["Perplexity is independent of tokenization", "Tokenizers change the model's network depth", "It is a measure of GPU temperature"], "Perplexity depends on token probabilities and segmentation, so scores across different tokenization schemes may not be directly comparable.", "intermediate"),
        ],
        [
            ("What does a word embedding map a token to?", "A dense numeric vector", ["A database primary key only", "A syntactic parse tree in every model", "A guaranteed human-readable definition"], "Embeddings represent discrete tokens as vectors learned or specified for computation.", "easy"),
            ("Why can contextual embeddings represent the same word differently in different sentences?", "Its representation depends on surrounding tokens", ["The vocabulary assigns a new word ID every time", "The model ignores the sentence", "The vector is a fixed spelling string"], "Contextual encoders use surrounding tokens to produce representations that reflect a word's usage.", "easy"),
        ],
        [
            ("In named-entity recognition, what is sequence tagging used to predict?", "A label for each token or span, such as person or organization", ["A single image class", "A database index for the document", "The next network packet"], "Sequence tagging assigns structured labels across tokens, often using a scheme such as BIO.", "easy"),
            ("Why can macro-averaged F1 be informative for imbalanced sequence labels?", "It gives each label equal weight in the average", ["It ignores all rare labels", "It is identical to accuracy in every dataset", "It measures only inference speed"], "Macro averaging computes a metric per class and averages equally, highlighting minority-label performance.", "intermediate"),
        ],
        [
            ("What does positional encoding provide to self-attention?", "Information about token order or position", ["The training labels", "A guarantee of correct translation", "The model's optimizer state"], "Self-attention alone is permutation-equivariant; positional information lets a model use sequence order.", "easy"),
            ("Why is the causal attention mask triangular in an autoregressive transformer?", "It blocks each position from attending to future tokens", ["It removes all attention between adjacent words", "It enforces a fixed vocabulary order", "It prevents the model from using context"], "A causal mask prevents information leakage from future positions when predicting a sequence left to right.", "intermediate"),
        ],
    ],
    "CSE_CYBER01": [
        [
            ("What is a threat model used to document?", "Assets, adversaries, trust boundaries, threats, and assumptions", ["Only the software's logo", "A guarantee that attacks cannot happen", "The source-code indentation style"], "Threat modelling organizes security analysis around system assets, boundaries, attacker capabilities, and likely threats.", "easy"),
            ("Which security goal is concerned with preventing unauthorized modification of information?", "Integrity", ["Availability", "Confidentiality", "Usability"], "Integrity concerns preserving accuracy and preventing unauthorized alteration.", "easy"),
        ],
        [
            ("What is the difference between authentication and authorization?", "Authentication verifies identity; authorization decides permitted actions", ["They are identical checks", "Authorization encrypts a password", "Authentication defines the database schema"], "Identity verification and permission checking are separate steps and should both be enforced where needed.", "easy"),
            ("Why is least privilege useful for an operating-system service account?", "A compromise exposes fewer capabilities and resources", ["It makes the account a system administrator", "It removes the need to patch the service", "It guarantees the account cannot be misused"], "Limiting privileges reduces the potential impact of bugs or credential compromise.", "easy"),
        ],
        [
            ("Why isolate a process with a restricted OS account or sandbox?", "Limit the resources and operations available if that process is compromised", ["Make its code impossible to execute", "Increase its access to every device", "Disable all logging"], "OS isolation and least privilege can contain the impact of compromised applications.", "easy"),
            ("What does a secure boot chain attempt to verify?", "Each boot stage before handing control to the next trusted stage", ["The application's user reviews", "The network's available bandwidth", "The keyboard layout"], "Secure boot uses cryptographic verification to establish trust across boot components, depending on platform configuration.", "intermediate"),
        ],
        [
            ("Why is a parameterized query an effective SQL-injection defense?", "It separates SQL structure from supplied data values", ["It encrypts the database at rest", "It removes authorization checks", "It validates every business rule automatically"], "Parameter binding prevents input from being interpreted as part of the SQL command structure.", "easy"),
            ("What should a web server do with untrusted content before rendering it into HTML?", "Encode it for the correct output context or use a safe text API", ["Trust it if a user is signed in", "Insert it directly into a script block", "Remove authentication for the page"], "Context-aware output encoding prevents data from being interpreted as executable markup or script.", "intermediate"),
        ],
        [
            ("Why include security checks in a continuous integration pipeline?", "Find vulnerable dependencies and unsafe changes before release", ["Guarantee that a system has no vulnerabilities", "Replace incident response", "Automatically make all deployments public"], "Automated checks can catch some issues early, but they do not prove a system is secure.", "easy"),
            ("What is the value of a security code review for a sensitive change?", "A reviewer can inspect trust boundaries, authorization, validation, and failure paths", ["It guarantees zero future defects", "It replaces monitoring", "It hides the diff from the author"], "Security-focused review examines risks that generic formatting or unit tests may not catch.", "intermediate"),
        ],
    ],
    "CSE_CYBER02": [
        [
            ("What is a key property of a secure block-cipher mode beyond having a strong block cipher?", "It must use keys, nonces or IVs, and padding according to the mode's requirements", ["It must repeat the same plaintext block directly", "It must use a fixed nonce for every message", "It removes the need for authentication"], "Secure use depends on the mode and correct nonce/IV handling; encryption alone may not authenticate data.", "intermediate"),
            ("Why should an encryption nonce not be reused with the same key in modes that require uniqueness?", "Reuse can reveal relationships or compromise confidentiality", ["The key becomes longer", "It invalidates DNS records", "The ciphertext becomes plaintext by definition"], "Nonce reuse can catastrophically weaken some stream and counter-based modes; follow the scheme's requirements.", "intermediate"),
        ],
        [
            ("In RSA, which key is used to encrypt a message for a recipient in the basic public-key scheme?", "The recipient's public key", ["The sender's public key only", "The recipient's private key", "A shared password stored in the message"], "A sender uses the recipient's public key so only the matching private key can decrypt, under the scheme's assumptions.", "easy"),
            ("What does Diffie-Hellman key exchange let two parties establish over a public channel?", "A shared secret, assuming appropriate parameters and authentication", ["A digital signature without private keys", "A public DNS name", "A secret that is automatically authenticated against a man-in-the-middle"], "Diffie-Hellman derives a shared secret but needs authentication to prevent active man-in-the-middle attacks.", "intermediate"),
        ],
        [
            ("What does a cryptographic hash function produce?", "A fixed-length digest of input data", ["A reversible encrypted copy", "A private key", "A guarantee of author identity"], "A cryptographic hash maps arbitrary-length input to a fixed-size digest and is designed for properties such as collision resistance.", "easy"),
            ("What is the purpose of a message authentication code (MAC)?", "Provide integrity and authenticity using a shared secret key", ["Encrypt data with no key", "Prove a public identity without a trust system", "Compress a file losslessly"], "A MAC lets parties sharing a secret verify message integrity and origin within that shared-key relationship.", "easy"),
        ],
        [
            ("What does TLS primarily provide for a properly configured client-server connection?", "Confidentiality and integrity in transit plus server authentication", ["Protection against all compromised endpoints", "A guarantee that the application data is correct", "A replacement for access control"], "TLS protects the channel and authenticates the server identity according to certificate validation; endpoint and application security remain necessary.", "easy"),
            ("Why is certificate hostname validation important in TLS?", "It checks that the certificate is valid for the intended server name", ["It checks the web page's factual accuracy", "It encrypts the user's hard drive", "It proves the server has no vulnerabilities"], "Without hostname validation, a client may accept a valid certificate issued for a different server.", "intermediate"),
        ],
        [
            ("Why rotate a compromised cryptographic key and revoke its prior trust?", "Prevent continued acceptance of signatures or access using a key no longer considered safe", ["Make the key's old ciphertext disappear", "Guarantee no data was exposed", "Increase the key's bit length retroactively"], "Rotation and revocation limit future use but cannot undo prior exposure or recover already disclosed data.", "easy"),
            ("What is a protocol downgrade attack?", "An attacker causes peers to use a weaker protocol version or security option", ["A user changes the screen resolution", "A key is rotated to a stronger algorithm", "A network route becomes shorter"], "Downgrade attacks exploit negotiation to weaken protections unless protocols prevent or detect the downgrade.", "intermediate"),
        ],
    ],
    "CSE_CYBER03": [
        [
            ("Why centralize logs from critical hosts and services?", "Correlate activity across systems and preserve records outside a compromised host", ["Guarantee every attack is detected", "Reduce the number of events to zero", "Replace system backups"], "Central log collection supports correlation and can protect records from local tampering, with access and retention controls.", "easy"),
            ("What does a detection alert's false-positive rate describe?", "The fraction of benign cases incorrectly flagged as positive", ["The fraction of attacks detected", "The time it takes to patch a host", "The number of log sources"], "False-positive rate concerns benign instances classified as alerts; interpretation depends on the evaluated population.", "intermediate"),
        ],
        [
            ("What is an indicator of compromise (IOC)?", "An observable artifact or pattern associated with potentially malicious activity", ["A guarantee that a system is clean", "A software license", "A change-request approval"], "IOCs such as hashes, domains, or behaviors support investigation but may be incomplete or change over time.", "easy"),
            ("Why should an IOC match be treated as an investigative signal rather than final proof?", "Indicators can be shared, reused, stale, or triggered in benign contexts", ["All indicators are encrypted", "No IOC can ever be accurate", "A match automatically confirms an attacker identity"], "Context and corroborating evidence are needed because indicators are not conclusive on their own.", "intermediate"),
        ],
        [
            ("What is a common first priority after confirming an active compromise?", "Contain the affected systems while preserving evidence and limiting business impact", ["Delete every log immediately", "Publish credentials publicly", "Ignore affected systems until the next audit"], "Containment reduces harm; responders should coordinate it with evidence preservation and recovery needs.", "easy"),
            ("Why perform a lessons-learned review after an incident?", "Identify control and process improvements based on evidence", ["Assign blame without investigation", "Guarantee no future incidents", "Delete the incident record"], "A blameless evidence-based review can improve controls, detection, and response processes.", "easy"),
        ],
        [
            ("Why prioritize a vulnerability using both severity and context?", "Exploitability, exposure, asset criticality, and existing controls affect actual risk", ["Every high-severity issue has identical business impact", "Severity scores prove exploitation occurred", "Context makes patching unnecessary"], "Risk-based prioritization considers technical severity with the system's exposure and business context.", "intermediate"),
            ("What is the purpose of a vulnerability re-scan after remediation?", "Verify the finding is no longer present under the tested conditions", ["Prove the system has no other weaknesses", "Replace change approval", "Generate a new vulnerability automatically"], "A re-scan checks whether a specific finding was addressed; scope and scanner limitations still apply.", "easy"),
        ],
        [
            ("Why preserve chain-of-custody details for digital evidence?", "Document who handled evidence and how it was transferred or stored", ["Change the evidence to match a report", "Guarantee the evidence proves intent", "Make evidence available to every user"], "A chain of custody supports integrity and accountability by recording handling and transfers.", "easy"),
            ("Why hash a forensic image at acquisition and after transfer?", "Compare digests to detect accidental or unauthorized changes", ["Recover deleted files automatically", "Prove the device owner committed an offence", "Encrypt the evidence without a key"], "Matching cryptographic hashes provide evidence that the image has not changed between checked points.", "intermediate"),
        ],
    ],
    "CSE_CYBER04": [
        [
            ("What is the purpose of an asset inventory in cybersecurity risk work?", "Identify what needs protection and who is responsible for it", ["List every possible attack in advance", "Replace access control", "Measure only website traffic"], "An asset inventory supports scope, ownership, criticality, and prioritization of risk treatment.", "easy"),
            ("Why classify data by sensitivity?", "Apply appropriate handling, access, retention, and protection controls", ["Make all data public", "Remove the need for encryption", "Guarantee that data is accurate"], "Classification helps match safeguards and handling requirements to data sensitivity and impact.", "easy"),
        ],
        [
            ("In a simple qualitative risk model, what factors commonly contribute to risk?", "Likelihood and impact", ["Screen size and file type", "CPU brand and office location only", "Number of source-code comments"], "Risk analysis commonly combines likelihood and consequence, with organization-specific methods and assumptions.", "easy"),
            ("Why distinguish inherent risk from residual risk?", "Residual risk remains after selected controls are applied", ["Inherent risk is always zero", "Residual risk is the same as a vulnerability count", "Controls affect only inherent risk"], "Inherent risk is assessed before controls; residual risk is the remaining exposure after treatment.", "intermediate"),
        ],
        [
            ("What does a security policy provide to an organization?", "Approved rules and expectations for protecting information and systems", ["A technical guarantee against every attack", "A replacement for procedures and controls", "A list of public encryption keys"], "A policy sets direction and responsibilities; standards, procedures, and controls operationalize it.", "easy"),
            ("Why review whether a security control is effective after deployment?", "A control may be poorly implemented, bypassed, or mismatched to the risk", ["Deployment guarantees effectiveness", "The control's name proves it works", "Review removes the need for incident response"], "Effectiveness should be validated using evidence, monitoring, and reassessment against the intended threat.", "intermediate"),
        ],
        [
            ("What is a recovery time objective (RTO)?", "The target maximum time to restore a service after disruption", ["The maximum acceptable data loss measured in time", "The average age of a server", "The number of recovery staff"], "RTO specifies a recovery-time target; RPO separately concerns acceptable data loss in time.", "easy"),
            ("Why test business continuity plans with relevant teams and dependencies?", "Recovery can fail if roles, communications, suppliers, or procedures are untested", ["A plan works automatically when stored as a PDF", "Testing guarantees zero disruption", "Dependencies do not affect continuity"], "Exercises reveal coordination and dependency gaps before a real disruption.", "easy"),
        ],
        [
            ("Why should privacy impact be considered before collecting new personal data?", "Collection creates obligations and risks that should be limited to a justified purpose", ["More data is always safer", "Privacy applies only after a breach", "A consent checkbox removes all obligations"], "Data minimization and purpose limitation reduce exposure and support responsible processing.", "easy"),
            ("What does data minimization mean in privacy-aware design?", "Collect and retain only data needed for a stated purpose", ["Delete all operational logs immediately", "Collect every possible attribute just in case", "Share personal data by default"], "Minimization limits collection and retention to what is necessary for the declared use.", "easy"),
        ],
    ],
    "AERO01": [
        [
            ("For a low-speed airfoil operating in a subsonic incompressible regime, what does the Kutta condition select at the trailing edge?", "A flow that leaves the sharp trailing edge smoothly", ["A stagnation point at the leading edge", "A shock that spans the chord", "A zero-pressure condition over the entire surface"], "The Kutta condition selects the physically observed circulation for which flow departs smoothly from a sharp trailing edge.", "intermediate"),
            ("Why is a two-dimensional airfoil model only an approximation for a finite wing?", "It omits spanwise flow and wingtip-vortex effects", ["It assumes air has no density", "It cannot represent pressure differences", "It includes the fuselage by definition"], "A finite wing develops tip vortices and spanwise flow, producing induced drag and a different lift distribution from an infinite-span section.", "intermediate"),
        ],
        [
            ("In ideal incompressible potential flow, what does circulation around an airfoil help determine?", "The net lift per unit span through the circulation-lift relation", ["The fuel mass flow through the engine", "The material yield stress", "The aircraft's electrical load"], "Under the idealized assumptions, the Kutta–Joukowski relation links circulation to lift per unit span.", "intermediate"),
            ("Why can potential-flow theory alone fail to predict profile drag accurately?", "It neglects viscous boundary layers and separation losses", ["It assumes the wing has finite span", "It includes chemical combustion", "It directly solves turbulent heat transfer"], "Inviscid potential flow is useful for pressure and lift estimates, but viscous effects are needed to explain skin friction and separation drag.", "intermediate"),
        ],
        [
            ("What happens to a laminar boundary layer when it transitions to turbulence over a smooth plate?", "Mixing increases and wall shear generally rises", ["The velocity at the wall becomes nonzero", "The fluid becomes inviscid", "The boundary layer disappears"], "Turbulent mixing transports momentum toward the wall, typically increasing skin-friction drag while making the layer more resistant to some adverse pressure gradients.", "intermediate"),
            ("Why does an adverse pressure gradient promote boundary-layer separation?", "Near-wall fluid loses streamwise momentum and may reverse", ["The free stream becomes perfectly stagnant", "The wall becomes a slip surface", "Density must become zero"], "A rising pressure in the flow direction decelerates low-momentum near-wall fluid and can cause reversed flow and separation.", "intermediate"),
        ],
        [
            ("Across a normal shock in a supersonic stream, which quantity decreases for a calorically perfect gas?", "Mach number", ["Static pressure", "Static temperature", "Entropy"], "A normal shock raises pressure, temperature, and entropy while reducing the downstream Mach number to subsonic for the usual upstream range.", "intermediate"),
            ("What is the main role of a converging-diverging nozzle in a supersonic propulsion flow?", "Accelerate subsonic flow to sonic conditions at the throat and then to supersonic speed when expanded", ["Keep flow speed constant at every station", "Convert all kinetic energy into shaft work", "Guarantee zero pressure thrust at any exit pressure"], "A choked throat followed by a diverging section can accelerate the gas supersonically when the pressure ratio and geometry support the intended expansion.", "intermediate"),
        ],
        [
            ("Why does induced drag increase as a finite wing's lift coefficient increases, with other conditions fixed?", "The stronger trailing vortex system tilts the lift vector rearward more", ["The wing's wetted area becomes zero", "The free-stream density must fall", "The wingtip vortices cancel completely"], "Finite-wing lift creates downwash and a rearward component of aerodynamic force; induced drag scales approximately with lift coefficient squared in the basic model.", "intermediate"),
            ("A wing's aspect ratio is increased while planform area and lift are held fixed. What is the usual effect on induced drag?", "It decreases in the ideal finite-wing relation", ["It becomes independent of lift", "It increases without bound", "It converts entirely into skin friction"], "For a given lift and efficiency factor, induced drag varies inversely with aspect ratio, although structural and practical constraints also matter.", "intermediate"),
        ],
    ],
    "AGRI01": [
        [
            ("A soil sample has gravimetric water content of 0.20 and dry bulk density of 1.5 Mg/m³. What is its approximate volumetric water content?", "0.30 m³/m³", ["0.13 m³/m³", "0.20 m³/m³", "1.70 m³/m³"], "Volumetric content is gravimetric content multiplied by bulk density relative to water density: 0.20 × 1.5 ≈ 0.30.", "intermediate"),
            ("For a given soil, what does field capacity approximate?", "Water remaining after rapid gravitational drainage has largely subsided", ["The water content at complete oven drying", "The total pore volume regardless of water", "The water content at permanent wilting for every crop"], "Field capacity is an operational estimate of water retained after free drainage; its measured value depends on soil and method.", "easy"),
        ],
        [
            ("Why can a high-intensity storm produce more runoff on a crusted bare field than on a well-covered field?", "Crusting lowers infiltration while bare soil is exposed to raindrop impact", ["Crop residue always increases rainfall intensity", "Cover eliminates all soil pores", "Runoff depends only on field temperature"], "Surface sealing can reduce infiltration, while residue and vegetation intercept raindrops and often help preserve surface structure.", "intermediate"),
            ("In the Universal Soil Loss Equation, what does the cover-management factor represent?", "The relative effect of vegetation and management on soil loss", ["The catchment's annual rainfall total only", "The soil's particle density", "The channel's hydraulic radius"], "The C factor represents how crop cover and management alter erosion relative to a reference condition.", "intermediate"),
        ],
        [
            ("In a watershed water balance, which term represents water leaving the basin as streamflow?", "Runoff or discharge at the outlet", ["Interception storage only", "Soil bulk density", "Crop leaf-area index"], "A basin water balance accounts for precipitation, evapotranspiration, runoff, and changes in storage over a stated period.", "easy"),
            ("Why is a hydrograph useful after a rainfall event?", "It shows how stream discharge changes over time", ["It gives the soil's particle-size distribution", "It measures pump efficiency directly", "It maps crop nutrient concentration"], "A hydrograph describes the time response of discharge and helps analyze peak flow, lag, and recession.", "easy"),
        ],
        [
            ("What is the purpose of a well's drawdown test?", "Estimate aquifer and well response from pumping and water-level observations", ["Determine a crop's seed germination rate", "Measure the density of irrigation water", "Select the colour of a casing"], "Pumping tests relate discharge and drawdown over time to hydraulic properties and well performance, subject to test assumptions.", "intermediate"),
            ("Why should well spacing consider aquifer properties and pumping schedules?", "Nearby cones of depression can interfere and reduce available drawdown", ["Wells always increase the aquifer's storage coefficient", "Spacing controls rainfall at the site", "Interference occurs only in surface canals"], "Pumping wells can interact through overlapping drawdown fields, so spacing and operating patterns affect yield and sustainability.", "intermediate"),
        ],
        [
            ("What is a primary purpose of a grassed waterway on an agricultural slope?", "Convey concentrated runoff at a non-erosive velocity", ["Store all groundwater permanently", "Increase flow velocity to scour sediment", "Replace field drainage in every soil"], "A vegetated waterway stabilizes a natural drainage path and safely conveys runoff when designed for expected flows.", "easy"),
            ("Why are contour bunds laid approximately along contour lines?", "They slow surface flow and encourage temporary detention and infiltration", ["They direct all runoff straight downslope", "They increase the slope length", "They prevent any water from entering the soil"], "Contour-aligned barriers interrupt overland flow and can reduce erosion when spacing, outlet, and maintenance are appropriate.", "intermediate"),
        ],
    ],
    "CHE01": [
        [
            ("A closed rigid vessel receives heat. Which energy-balance term is zero for the vessel boundary?", "Boundary work", ["Heat transfer", "Change in internal energy", "Mass of the contents"], "For a rigid closed vessel, boundary displacement is zero, so boundary work is zero; heat transfer may still change internal energy.", "easy"),
            ("For a steady-flow device with negligible kinetic and potential energy changes, which energy terms are central to its balance?", "Enthalpy, heat, and work", ["Only internal energy and boundary displacement", "Only entropy and volume", "Only chemical potential and surface tension"], "The steady-flow first law is written using enthalpy flow and heat/work interactions when kinetic and potential terms are negligible.", "intermediate"),
        ],
        [
            ("For an isolated system, what does the second law say about total entropy in a real process?", "It cannot decrease", ["It must always remain zero", "It is equal to heat divided by temperature for every process", "It decreases whenever friction is present"], "The entropy of an isolated system stays constant for a reversible process and increases for an irreversible one.", "easy"),
            ("Why is entropy generation nonnegative for a physically realizable process?", "It accounts for irreversibilities such as friction, mixing, and finite-temperature heat transfer", ["It represents energy created from nothing", "It is a measure of total system mass", "It forces every process to be isothermal"], "Entropy generation is nonnegative by the second law and is positive when irreversibilities occur.", "intermediate"),
        ],
        [
            ("For a pure substance inside the saturation dome, what do quality values between zero and one describe?", "The mass fraction that is vapour in a saturated liquid-vapour mixture", ["The fraction of the vessel occupied by a solid", "The ratio of pressure to temperature", "The fraction of energy converted to work"], "Vapour quality is the vapour mass divided by total mixture mass; it is defined for a two-phase liquid-vapour mixture.", "easy"),
            ("Why are steam tables or property equations used in cycle analysis?", "They provide thermodynamic properties needed to evaluate state changes and balances", ["They replace conservation laws", "They specify equipment purchase prices", "They guarantee a cycle is reversible"], "Property data connect measured state variables to enthalpy, entropy, and other quantities used in energy and cycle calculations.", "easy"),
        ],
        [
            ("At fixed temperature and pressure, what condition characterizes phase equilibrium between two phases of a pure substance?", "Their specific Gibbs free energies are equal", ["Their densities must be equal", "Their volumes must be equal", "Their entropies must both be zero"], "For a pure substance at phase equilibrium, chemical potential, equivalent to molar Gibbs free energy, is equal across coexisting phases.", "intermediate"),
            ("A liquid mixture is heated at constant pressure until its first bubble forms. What state has been reached?", "The bubble point", ["The critical point", "The triple point", "The dew point of a vapour mixture"], "The bubble point is the condition at which a liquid mixture begins to form vapour at the specified pressure and composition.", "easy"),
        ],
        [
            ("Why is the thermal efficiency of a heat engine less than one?", "Some energy must be rejected to a lower-temperature reservoir", ["Energy conservation does not apply to engines", "Every engine has zero heat input", "Work output is always negative"], "The second law prevents a cyclic heat engine from converting all absorbed heat into work; some heat rejection is required.", "easy"),
            ("For an ideal gas turbine cycle, what is the usual effect of increasing compressor pressure ratio beyond its optimum for fixed turbine inlet temperature?", "Net work can eventually fall because compressor work rises", ["Compressor work becomes zero", "The cycle becomes a refrigeration cycle automatically", "Turbine inlet temperature must become infinite"], "Increasing pressure ratio raises both turbine work and compressor work; for fixed limits, net work has an optimum rather than increasing without bound.", "intermediate"),
        ],
    ],
    "AI_DS01": [
        [
            ("A count of support tickets per hour is being modeled. Which distribution is a reasonable starting point when events occur independently at a stable average rate?", "Poisson distribution", ["Uniform distribution over all real numbers", "Bernoulli distribution with a continuous outcome", "Normal distribution restricted to integers without approximation"], "The Poisson model is commonly used for counts over a fixed interval under an approximately constant rate and independent-event assumptions.", "intermediate"),
            ("A measurement has a strongly right-skewed distribution. Which summary is usually less affected by a few extreme high values?", "The median", ["The arithmetic mean", "The maximum", "The sum of all observations"], "The median depends on rank and is more robust to extreme values than the mean for skewed data.", "easy"),
        ],
        [
            ("Why should a confidence interval for a population mean use a standard error rather than the population standard deviation?", "The standard error describes uncertainty in the estimated sample mean", ["The standard deviation is always zero for a sample", "A confidence interval estimates every individual value", "Standard error removes all sampling bias"], "The standard error quantifies sampling variability of an estimator; it does not correct bias or describe the spread of individual observations.", "intermediate"),
            ("A random sample is enlarged while the data-generating process and variance remain stable. What generally happens to the standard error of the sample mean?", "It decreases approximately in proportion to the inverse square root of sample size", ["It grows linearly with sample size", "It becomes identical to the sample maximum", "It remains exactly equal to the population mean"], "For independent observations with finite variance, the standard error of the mean is sigma divided by the square root of n.", "intermediate"),
        ],
        [
            ("A hypothesis test produces p = 0.03. At significance level 0.05, what is the conventional decision?", "Reject the null hypothesis under the test assumptions", ["Prove the alternative hypothesis is certainly true", "Show that the effect is practically large", "Prove that the null has a 3% probability of being true"], "A p-value at or below alpha leads to rejection in the specified test; it is not the posterior probability that the null is true or a measure of effect size.", "intermediate"),
            ("If many hypotheses are tested independently at 0.05 with no true effects, what risk increases?", "At least one false positive across the family of tests", ["Every test becomes perfectly powered", "The type-I error rate becomes zero", "The sample variance must increase"], "Repeated unadjusted testing increases family-wise false-positive risk; correction or a planned analysis can control it.", "intermediate"),
        ],
        [
            ("A correlation between study time and test score is observed. Which conclusion is justified by correlation alone?", "The variables vary together in the observed data, but causation is not established", ["More study time definitely caused every score increase", "There can be no confounding", "The relationship must be linear outside the observed range"], "Correlation describes association; confounding, reverse causation, selection, and other factors can explain it.", "easy"),
            ("What does a regression residual represent for an observation?", "Observed response minus model-predicted response", ["The model's intercept", "The predictor's sample variance", "The response variable's population size"], "A residual is the difference between the observed outcome and the fitted value for that observation.", "easy"),
        ],
        [
            ("A field experiment randomizes plots to fertilizer treatments and blocks plots by soil type. What is the main benefit of blocking?", "It accounts for a known source of variation and can improve precision", ["It removes the need for random assignment", "It guarantees that treatment effects are identical", "It makes the sample size irrelevant"], "Blocking groups similar experimental units before randomization, helping control nuisance variability without replacing random assignment.", "intermediate"),
            ("Why should an experiment define its primary outcome before looking at results?", "It reduces the risk of selectively reporting whichever outcome looks most favourable", ["It guarantees a significant result", "It removes measurement error", "It makes a control group unnecessary"], "Pre-specification improves interpretability and limits selective analysis, while transparent reporting should still describe exploratory findings.", "intermediate"),
        ],
    ],
    "AUTO01": [
        [
            ("In an ideal Otto cycle, heat addition is modeled as occurring at what condition?", "Constant volume", ["Constant pressure", "Constant temperature", "Zero entropy"], "The ideal Otto cycle models spark-ignition engine heat addition at constant volume.", "easy"),
            ("For the ideal Otto cycle, what is the main thermodynamic effect of increasing compression ratio, with specific-heat ratio fixed?", "Thermal efficiency increases", ["Thermal efficiency becomes zero", "The cycle has no compression work", "Exhaust temperature must equal ambient temperature"], "The ideal Otto efficiency rises with compression ratio under its simplified assumptions; real knock, heat transfer, and losses constrain designs.", "intermediate"),
        ],
        [
            ("What is a principal purpose of fuel injection timing in a compression-ignition engine?", "Control the start and rate of combustion relative to piston motion", ["Set tyre pressure", "Change the gear ratio", "Control cabin lighting"], "Injection timing and rate shape ignition delay, pressure rise, emissions, and torque in a diesel engine.", "easy"),
            ("Why can poor air-fuel mixing increase particulate emissions in a diesel engine?", "Locally fuel-rich zones can burn incompletely", ["All oxygen is converted into nitrogen", "The fuel becomes a lubricant", "Combustion temperature is always zero"], "Nonuniform mixing can create rich regions that favour soot formation; injection, air motion, and after-treatment influence emissions.", "intermediate"),
        ],
        [
            ("Brake-specific fuel consumption compares fuel flow with which output?", "Brake power delivered at the engine shaft", ["Vehicle paint area", "Coolant volume only", "Engine displacement without operating conditions"], "BSFC is fuel mass flow per unit brake power, allowing fuel-use comparison at stated operating points.", "easy"),
            ("Why must an engine emissions test report its operating cycle or load condition?", "Emissions depend on speed, load, temperature, and transient operation", ["Emissions are identical at every operating point", "The cycle determines the vehicle's colour", "Load affects only tyre wear"], "Engine-out and tailpipe emissions vary with operating conditions, so a defined test cycle is needed for meaningful comparisons.", "intermediate"),
        ],
        [
            ("In a parallel hybrid vehicle, what can the electric machine do during regenerative braking?", "Convert part of the vehicle's kinetic energy into electrical energy for storage", ["Create energy without reducing vehicle motion", "Increase brake-pad temperature to store energy", "Eliminate the need for a battery"], "Regenerative braking recovers some kinetic energy through the motor-generator, subject to battery, traction, and power limits.", "easy"),
            ("Why can a hybrid supervisory controller switch between engine and electric drive modes?", "To balance efficiency, requested power, battery limits, and emissions", ["To make the battery capacity infinite", "To remove all mechanical losses", "To keep engine speed fixed for every road condition"], "Energy management selects operating modes subject to driver demand, component constraints, and efficiency objectives.", "intermediate"),
        ],
        [
            ("Why is a dynamometer calibration sweep conducted across engine speed and load?", "It maps torque, fuel use, and emissions over the operating range", ["It measures only the vehicle's exterior dimensions", "It guarantees every road condition is reproduced exactly", "It replaces the need for sensor calibration"], "A controlled speed-load map characterizes engine performance and helps calibrate control strategies; it does not capture every real-world transient.", "easy"),
            ("During powertrain calibration, a knock sensor reports repeated knock under high load. Which response is generally appropriate for a spark-ignition control strategy?", "Retard ignition timing within calibrated protection limits", ["Advance timing without limit", "Disable all temperature monitoring", "Increase spark energy until knock disappears"], "Retarding spark can reduce knock tendency, while the calibration must also respect torque, exhaust temperature, and component protection constraints.", "intermediate"),
        ],
    ],
    "BIOTECH01": [
        [
            ("Which organelle is the main site of oxidative phosphorylation in a typical eukaryotic cell?", "Mitochondrion", ["Golgi apparatus", "Lysosome", "Nucleolus"], "The inner mitochondrial membrane houses the electron-transport chain and ATP synthase in most eukaryotic cells.", "easy"),
            ("What is one key function of the rough endoplasmic reticulum?", "Synthesize and begin processing proteins destined for secretion or membranes", ["Replicate chromosomal DNA", "Digest extracellular cellulose in every animal cell", "Generate the mitotic spindle"], "Ribosomes on rough ER translate many proteins that enter the secretory pathway or become membrane proteins.", "easy"),
        ],
        [
            ("A cell takes up a molecule against its concentration gradient using ATP. Which process is involved?", "Active transport", ["Simple diffusion", "Osmosis only", "Passive filtration"], "Moving a solute uphill against its electrochemical gradient requires energy directly or indirectly.", "easy"),
            ("A ligand binds a cell-surface receptor and triggers an intracellular phosphorylation cascade. What is this sequence called?", "Signal transduction", ["DNA replication", "Protein denaturation", "Vesicle sedimentation"], "Signal transduction converts receptor activation into downstream biochemical responses inside the cell.", "easy"),
        ],
        [
            ("During which cell-cycle phase is genomic DNA replicated?", "S phase", ["G1 phase", "G2 phase", "Cytokinesis"], "DNA synthesis occurs during S phase, followed by preparation for mitosis in G2.", "easy"),
            ("Why do spindle-assembly checkpoints delay anaphase when chromosomes are not properly attached?", "They reduce the chance of unequal chromosome segregation", ["They increase mutation rate deliberately", "They stop all transcription permanently", "They duplicate centrosomes after cytokinesis"], "The checkpoint restrains anaphase until kinetochores are attached appropriately, helping maintain chromosome number.", "intermediate"),
        ],
        [
            ("Which cytoskeletal filament is most directly associated with muscle contraction together with myosin?", "Actin microfilaments", ["Intermediate filaments", "Microtubules", "Peptidoglycan fibres"], "Actin filaments interact with myosin motors to generate force in muscle and other contractile systems.", "easy"),
            ("What is the main structural role of microtubules in a mitotic cell?", "Form spindle fibres that help move chromosomes", ["Store the cell's genetic code", "Catalyze peptide-bond formation", "Create the phospholipid bilayer"], "Microtubule dynamics assemble the spindle and support chromosome movement during cell division.", "easy"),
        ],
        [
            ("What is a common role of caspases in apoptosis?", "Execute regulated protein cleavage steps that dismantle the cell", ["Copy DNA during S phase", "Synthesize membrane phospholipids only", "Transport oxygen in blood"], "Initiator and executioner caspases activate a proteolytic cascade during programmed cell death.", "intermediate"),
            ("Why can loss of normal apoptosis contribute to cancer development?", "Abnormal cells may survive when they should be removed", ["It forces all cells into senescence", "It prevents DNA replication in healthy tissue", "It eliminates every immune response"], "Failure of cell-death controls can allow damaged or oncogenic cells to persist and accumulate further changes.", "intermediate"),
        ],
    ],
    "BIOMED01": [
        [
            ("What is the main function of epithelial tissue lining an exchange surface?", "Provide a selective interface for protection, absorption, or exchange", ["Generate all skeletal movement", "Store the entire body's genetic information", "Produce bone marrow in every organ"], "Epithelia form organized barriers and exchange surfaces whose functions depend on location and specialization.", "easy"),
            ("Why does connective tissue often contain extracellular matrix?", "The matrix provides structural support and influences cell behaviour", ["It replaces all cell membranes", "It carries action potentials in every tissue", "It prevents cells from receiving nutrients"], "Collagen, elastin, and other matrix components provide mechanical properties and biochemical cues to cells.", "easy"),
        ],
        [
            ("Which chamber pumps oxygenated blood into the systemic circulation?", "Left ventricle", ["Right atrium", "Right ventricle", "Left atrium"], "The left ventricle ejects oxygenated blood through the aorta to the systemic circulation.", "easy"),
            ("What does an electrocardiogram primarily record at the body surface?", "Voltage differences associated with cardiac electrical activity", ["Direct blood pressure inside each chamber", "Blood oxygen concentration in the lungs", "Mechanical valve area in square centimetres"], "An ECG records potentials produced by cardiac depolarization and repolarization as seen through surface electrodes.", "easy"),
        ],
        [
            ("What is the main purpose of alveolar ventilation?", "Bring fresh air to alveoli for gas exchange", ["Pump blood through systemic arteries", "Filter glucose from urine", "Generate skeletal muscle force"], "Alveolar ventilation replenishes gas in alveoli and helps maintain oxygen and carbon-dioxide gradients for exchange.", "easy"),
            ("Why does carbon dioxide diffuse from pulmonary capillary blood into alveolar gas under normal conditions?", "Its partial pressure is higher in blood than in alveolar gas", ["Its molecular mass is lower in the alveolus", "Alveolar gas has no nitrogen", "The lungs actively pump CO2 through the membrane"], "Gas diffusion follows partial-pressure gradients across the alveolar-capillary barrier.", "intermediate"),
        ],
        [
            ("What creates the resting membrane potential in excitable cells?", "Ion concentration gradients and selective membrane permeability", ["A permanent absence of ions", "Only the cell's mechanical stiffness", "The number of red blood cells nearby"], "Unequal ion distributions and selective permeability, maintained by transport processes, generate membrane voltage.", "intermediate"),
            ("What does an EMG electrode measure when placed over a muscle?", "Electrical activity associated with motor-unit activation", ["The muscle's blood glucose directly", "Bone mineral density", "The exact force of every individual fibre without calibration"], "Surface or needle EMG detects summed electrical potentials; it is not a direct measurement of muscle force.", "easy"),
        ],
        [
            ("Negative feedback in physiological regulation generally acts to do what?", "Counteract a deviation from a regulated range", ["Amplify every deviation indefinitely", "Prevent all sensor activity", "Convert all signals into hormones"], "Negative feedback reduces the initial disturbance and helps maintain a regulated variable near its operating range.", "easy"),
            ("Why should physiological sensor data be interpreted with the measurement context and signal quality?", "Motion, placement, noise, and calibration can mimic or distort biological changes", ["Sensors always report the underlying cause directly", "Filtering makes all measurements exact", "A signal's units are irrelevant"], "Physiological measurements are affected by acquisition conditions and artifacts, so signal quality and context matter before inference.", "intermediate"),
        ],
    ],
    "ENV01": [
        [
            ("Why does dissolved oxygen often decrease when organic pollution enters a water body?", "Microbial decomposition consumes oxygen", ["Organic matter converts all water to ozone", "The pH must become exactly seven", "Dissolved salts disappear"], "Decomposers use oxygen while breaking down biodegradable organic material, potentially lowering dissolved-oxygen levels.", "easy"),
            ("A water sample is buffered. What does buffering resist?", "Large changes in pH when small amounts of acid or base are added", ["Any change in water temperature", "All evaporation", "The formation of dissolved ions"], "A buffer contains a conjugate acid-base pair that moderates pH changes over a range of added acid or base.", "easy"),
        ],
        [
            ("In an acid-base titration, what does the equivalence point indicate?", "Stoichiometrically equivalent amounts of titrant and analyte have reacted", ["The solution contains no ions", "The pH is always exactly seven", "The sample has reached its boiling point"], "The equivalence point follows reaction stoichiometry; its pH depends on acid and base strengths and is not always neutral.", "intermediate"),
            ("In a redox reaction, what happens to the species that is oxidized?", "It loses electrons", ["It gains electrons", "It must gain a proton only", "Its oxidation state is unchanged"], "Oxidation is electron loss and an increase in oxidation state; reduction is electron gain.", "easy"),
        ],
        [
            ("What does biochemical oxygen demand estimate in a water sample?", "Oxygen used by microorganisms while degrading biodegradable organic matter under the test conditions", ["The total dissolved salt mass", "The water's instantaneous flow velocity", "The amount of all toxic metals regardless of speciation"], "BOD is an operational measure of oxygen demand from microbial decomposition over a specified test period and conditions.", "easy"),
            ("Why can a high chemical oxygen demand value be a concern for a receiving water body?", "Oxidizable substances can contribute to oxygen depletion", ["It proves that every compound is biodegradable", "It measures only suspended-sediment size", "It guarantees high dissolved oxygen"], "COD measures oxygen-equivalent oxidizable material; high loads can deplete oxygen, though COD does not identify compounds or their biodegradability.", "intermediate"),
        ],
        [
            ("How can excess bioavailable phosphorus contribute to eutrophication in a freshwater lake?", "It can stimulate algal growth and later oxygen depletion during decay", ["It removes all nitrogen from the atmosphere", "It stops photosynthesis in every plant", "It converts dissolved oxygen directly into phosphorus"], "Nutrient enrichment can increase primary production; decomposition of resulting biomass can consume dissolved oxygen.", "easy"),
            ("Why can a dense algal bloom cause low dissolved oxygen at night?", "Respiration continues while photosynthesis stops without light", ["Algae produce oxygen only in darkness", "Water becomes chemically inert at night", "The lake's pressure becomes zero"], "Respiration and decomposition consume oxygen continuously, while photosynthetic oxygen production is absent at night.", "intermediate"),
        ],
        [
            ("Why should sample containers and preservation methods match the analyte being measured?", "Some analytes can react, volatilize, adsorb, or change concentration after collection", ["All analytes are stable indefinitely", "Preservation changes the sampling location", "Containers determine the legal limit"], "Correct containers, preservation, temperature, and holding time help maintain sample integrity for the intended analysis.", "intermediate"),
            ("What does a field blank help detect in environmental sampling?", "Contamination introduced during handling, transport, or field procedures", ["The true concentration at every site", "The instrument's response to a calibration standard", "Whether a watershed has a floodplain"], "A field blank is exposed to sampling conditions without the target sample and helps identify contamination from collection and handling.", "easy"),
        ],
    ],
    "MME01": [
        [
            ("How many atoms are associated with the conventional face-centred cubic unit cell?", "Four", ["One", "Two", "Six"], "Eight corner atoms contribute one atom in total and six face-centred atoms contribute three, for four atoms per conventional FCC cell.", "intermediate"),
            ("What is a dislocation in a crystalline solid?", "A line defect in the arrangement of atoms", ["A liquid droplet trapped between grains", "A point charge in a vacuum", "A perfectly periodic plane with no defect"], "Dislocations are line defects whose motion enables plastic deformation in crystalline materials.", "easy"),
        ],
        [
            ("Why does diffusion in a solid generally become faster as temperature rises?", "More atoms have sufficient thermal energy to overcome activation barriers", ["The lattice spacing becomes exactly zero", "Diffusion no longer depends on defects", "The material loses all chemical potential gradients"], "Diffusion coefficients commonly follow an Arrhenius-type temperature dependence because atomic jumps require activation energy.", "intermediate"),
            ("What is the usual direction of net diffusion when a concentration gradient exists?", "From higher concentration toward lower concentration", ["Only from lower to higher concentration without energy input", "Perpendicular to every gradient", "Only through a vacuum"], "Fickian diffusion produces net flux down a concentration gradient, with the magnitude depending on the diffusivity.", "easy"),
        ],
        [
            ("A binary alloy contains 40 wt% B in a two-phase region with phase compositions 20 wt% B and 60 wt% B. What fraction of the phase richer in B is predicted by the lever rule?", "0.50", ["0.20", "0.40", "0.80"], "The fraction of the B-rich phase is (40−20)/(60−20) = 0.50 by the lever rule.", "intermediate"),
            ("At a eutectic composition and temperature in a binary system, what transformation occurs on cooling?", "One liquid transforms into two solid phases", ["One solid transforms into a gas", "Two liquids form at constant pressure", "A single liquid remains stable below the eutectic temperature"], "The eutectic reaction is liquid transforming into two solid phases at the eutectic temperature and composition.", "easy"),
        ],
        [
            ("In a cast alloy, why can a steep thermal gradient and rapid interface growth affect the solidification structure?", "They influence nucleation, dendrite spacing, and segregation patterns", ["They eliminate heat flow", "They make every grain chemically identical", "They prevent any phase transformation"], "Thermal gradient and interface velocity influence solidification morphology and microsegregation, subject to alloy and process conditions.", "intermediate"),
            ("What is the main purpose of homogenization heat treatment after casting?", "Reduce composition gradients caused by microsegregation", ["Create additional porosity", "Increase the number of inclusions", "Replace all grains with liquid at room temperature"], "A sufficiently high-temperature hold permits diffusion to reduce chemical segregation, within limits set by melting and coarsening risks.", "easy"),
        ],
        [
            ("What does the yield strength of a ductile metal mark in a tensile test?", "The onset of significant permanent plastic deformation", ["The point where elastic strain first occurs", "The temperature at which it melts", "The maximum density of the specimen"], "Yield strength identifies a stress level associated with the start of non-negligible plastic deformation under the test definition.", "easy"),
            ("Why can a sharp crack reduce the load a component can safely carry?", "The crack tip concentrates stress and can drive fracture", ["The crack makes the component perfectly ductile", "The crack removes all residual stress", "The crack increases the cross-section"], "Stress intensity near a crack tip can reach a material's fracture resistance before the nominal section stress reaches yield.", "intermediate"),
        ],
    ],
    "CE02": [
        [
            ("What does the liquid limit of a fine-grained soil indicate in the Atterberg limits framework?", "The water content at the transition between plastic and liquid consistency", ["The water content at oven dry condition", "The maximum particle size in a sieve test", "The density of mineral grains"], "The liquid limit is an index water content associated with a consistency transition defined by a standard test method.", "easy"),
            ("Why is the plasticity index useful for characterizing a fine-grained soil?", "It measures the water-content range over which the soil behaves plastically", ["It gives the soil's permeability directly", "It measures the specific gravity of solids", "It equals the soil's degree of saturation"], "Plasticity index is liquid limit minus plastic limit and describes the plastic consistency range.", "easy"),
        ],
        [
            ("In a standard compaction test, what is the purpose of plotting dry density against water content?", "Identify optimum moisture content and maximum dry density for the applied effort", ["Find the soil's liquid limit only", "Determine groundwater chemistry", "Measure consolidation settlement directly"], "The compaction curve shows how water content affects dry density for a specified compactive effort.", "easy"),
            ("Why does adding a small amount of water often improve compaction of a dry soil?", "Water helps particles rearrange under compactive effort", ["Water permanently removes all air voids", "Water changes sand grains into clay", "Water eliminates the need for compaction"], "At low moisture content, lubrication can help particles pack more densely; excessive water eventually reduces achievable dry density.", "intermediate"),
        ],
        [
            ("According to Darcy's law for saturated soil, what primarily controls discharge through a specimen?", "Hydraulic conductivity, cross-sectional area, and hydraulic gradient", ["Only the soil colour", "Only the length of the grain names", "The liquid limit multiplied by temperature"], "For laminar saturated flow through soil, Darcy discharge is proportional to conductivity, area, and hydraulic gradient.", "easy"),
            ("What is the hydraulic gradient across a soil layer?", "Head loss per unit length along the flow path", ["Water content divided by dry density", "Void ratio multiplied by grain size", "The total head at the outlet only"], "Hydraulic gradient is the change in total head over the corresponding flow distance.", "easy"),
        ],
        [
            ("In a saturated soil below the water table, which stress is carried by the soil skeleton in Terzaghi's effective-stress principle?", "Total stress minus pore-water pressure", ["Total stress plus pore-water pressure", "Pore-water pressure only", "Dry unit weight multiplied by porosity"], "Effective stress sigma-prime equals total stress sigma minus pore pressure u for the simplified saturated-soil relation.", "intermediate"),
            ("Why does consolidation settlement occur in a saturated fine-grained layer after loading?", "Pore pressure dissipates as water drains and effective stress increases", ["Soil grains evaporate", "The applied total stress becomes zero", "The void ratio increases without drainage"], "As excess pore-water pressure dissipates, the soil skeleton carries more effective stress and compresses over time.", "intermediate"),
        ],
        [
            ("In a drained direct-shear test, what is obtained from the failure envelope?", "Shear strength parameters for the tested soil under the stated conditions", ["The soil's thermal conductivity only", "The grain-size curve", "The groundwater recharge rate"], "The measured peak or critical shear stress versus normal stress can define parameters for an idealized strength envelope.", "easy"),
            ("Why should bearing-capacity calculations consider groundwater level?", "Water changes effective stresses and soil unit weights near the foundation", ["Groundwater determines concrete colour", "The water table changes the foundation plan area automatically", "It has no influence on soil behaviour"], "Pore pressure and submerged unit weight affect the effective-stress conditions used in many bearing-capacity formulations.", "intermediate"),
        ],
    ],
    "MINING01": [
        [
            ("What distinguishes a mineral from a rock in introductory geology?", "A mineral has a characteristic composition and ordered structure; a rock is an aggregate of minerals or mineraloids", ["A rock is always liquid", "A mineral must contain organic tissue", "A rock has no geological origin"], "Minerals are naturally occurring solids with characteristic chemical and crystal properties; rocks are aggregates with variable mineral composition.", "easy"),
            ("What is a fault in a geological structure?", "A fracture along which measurable displacement has occurred", ["A horizontal change in mineral colour only", "A sedimentary grain-size class", "A laboratory weighing error"], "Faults are fractures with relative movement of the rock masses on either side.", "easy"),
        ],
        [
            ("How can hydrothermal fluids form an ore deposit?", "They transport dissolved elements and precipitate minerals when conditions change", ["They prevent all chemical reactions", "They turn every host rock into coal", "They remove metals from every magma"], "Changes in temperature, pressure, pH, redox state, or fluid mixing can cause ore minerals to precipitate from hydrothermal fluids.", "intermediate"),
            ("Why are stratiform ore bodies often associated with particular sedimentary horizons?", "Mineralization may be linked to depositional conditions or later fluid flow along a layer", ["Sedimentary layers have no chemical variation", "Ore minerals can form only in the atmosphere", "All ore deposits are younger than the present land surface"], "Some deposits are syngenetic with sedimentation or epigenetic but controlled by permeable or reactive strata; origin must be interpreted from evidence.", "intermediate"),
        ],
        [
            ("Why should a geological field map record both observation location and orientation data for planar structures?", "The measurements allow structural attitudes and spatial relationships to be interpreted", ["They determine the rock's market price", "They replace sample description", "They remove all uncertainty from mapping"], "Locations and strike/dip observations support cross-sections and structural interpretation, with uncertainty recorded where appropriate.", "easy"),
            ("What is a representative channel sample intended to estimate?", "Grade variation across a defined exposure or interval", ["The total mine ventilation rate", "The age of every mineral grain exactly", "The density of a drilling fluid"], "A channel sample is collected across a measured interval to characterize grade, subject to sampling and analytical uncertainty.", "easy"),
        ],
        [
            ("What is the main purpose of geophysical exploration before drilling?", "Identify subsurface contrasts that may help target follow-up investigation", ["Prove an economic reserve with no drilling or sampling", "Measure mineral prices directly", "Replace geological interpretation"], "Geophysical anomalies reflect physical-property contrasts and guide targeting; they do not uniquely identify ore without geological follow-up.", "easy"),
            ("Why can airborne magnetic data help map some geological structures?", "Magnetic minerals create spatial variations in the measured magnetic field", ["All rocks have identical magnetic properties", "Magnetic surveys directly measure ore grade", "The Earth's magnetic field is absent over mineral deposits"], "Magnetic susceptibility and remanent magnetization vary between rocks, so anomalies can reveal contacts or structures but are not unique.", "intermediate"),
        ],
        [
            ("What is a mineral resource estimate based on?", "Geological evidence and sampling interpreted with stated confidence and assumptions", ["A single unverified surface fragment", "Commodity price alone", "A mine plan without geological data"], "Resource classification relies on geological knowledge, sampling, and confidence in continuity; economic extraction is a separate consideration.", "easy"),
            ("Why is cut-off grade used in reserve or resource evaluation?", "It defines the grade threshold used to distinguish material considered for economic reporting under assumptions", ["It measures the mine's air velocity", "It guarantees every block will be profitable", "It sets the mineral's atomic number"], "Cut-off grade depends on costs, recovery, price, and reporting assumptions; it is not an intrinsic constant of the deposit.", "intermediate"),
        ],
    ],
    "PETRO01": [
        [
            ("What is a sedimentary basin in petroleum geoscience?", "A region where sediment accumulates and may be buried and preserved over geological time", ["A temporary surface puddle", "A mineral crystal with no stratigraphy", "A volcanic vent by definition"], "Sedimentary basins preserve successions whose burial and thermal histories can support petroleum-system development.", "easy"),
            ("Why does a petroleum-system assessment consider source, reservoir, seal, trap, and timing together?", "Successful accumulation requires generation, migration, storage, and retention to coincide", ["Each element acts independently of geological time", "A source rock alone guarantees a commercial field", "The seal must always be younger than production"], "A working petroleum system depends on connected elements and processes with suitable timing and preservation.", "intermediate"),
        ],
        [
            ("What happens during thermal maturation of organic-rich source rock?", "Buried organic matter transforms with heat and time to generate hydrocarbons", ["All minerals instantly become gas", "Organic carbon is removed only by surface erosion", "The source rock becomes a reservoir without porosity"], "Maturation depends on burial, temperature, time, and organic matter type, with oil and gas generation across thermal windows.", "easy"),
            ("Why is vitrinite reflectance used in basin studies?", "It is an indicator of the thermal maturity experienced by organic matter", ["It directly measures reservoir permeability", "It identifies the current fluid pressure exactly", "It gives the present oil price"], "Vitrinite reflectance is a commonly used maturity proxy, interpreted alongside other thermal and geochemical evidence.", "intermediate"),
        ],
        [
            ("What is effective porosity in a reservoir-rock context?", "The connected pore space available for fluid storage and flow", ["The total volume of mineral grains", "The fraction of the rock made only of clay", "The pore pressure divided by depth"], "Effective porosity excludes isolated pores that do not contribute to connected storage and flow under the measurement definition.", "easy"),
            ("Why can water saturation be high in a porous reservoir rock?", "Porosity stores fluids, while saturation describes the fraction of pore volume occupied by each fluid", ["Porosity and saturation are the same quantity", "High saturation means the rock has no pores", "Saturation measures grain density only"], "Porosity is a fraction of bulk rock volume; saturation is a fraction of pore volume occupied by a particular fluid.", "easy"),
        ],
        [
            ("What role does a cap rock play above a petroleum accumulation?", "Its low permeability helps impede upward fluid escape", ["It generates seismic waves for logging", "It increases reservoir pore volume automatically", "It replaces the need for a structural or stratigraphic trap"], "A seal limits vertical migration, while a trap provides geometry and closure needed to retain hydrocarbons.", "easy"),
            ("Why must trap formation generally precede or overlap hydrocarbon charge?", "A trap must exist when hydrocarbons migrate for accumulation and retention to occur", ["The source rock cannot mature after deposition", "Migration only occurs through impermeable rock", "Timing has no bearing on accumulation"], "If charge occurs before a trap or seal is effective, hydrocarbons may escape rather than accumulate.", "intermediate"),
        ],
        [
            ("On a well log, why can a gamma-ray curve help distinguish shale-rich intervals from many clean sandstones?", "Shales commonly contain more naturally radioactive potassium, uranium, or thorium-bearing material", ["Gamma ray directly measures porosity only", "Clean sandstone always emits no radiation", "The tool measures oil viscosity"], "Natural gamma response often helps identify shale content, though mineralogy and uranium enrichment can complicate interpretation.", "intermediate"),
            ("Why correlate multiple well logs with stratigraphic markers rather than compare one curve alone?", "Multiple curves and markers help distinguish lithology, fluids, and equivalent horizons", ["A single log uniquely identifies every rock and fluid", "Correlation removes depth uncertainty entirely", "All wells have identical log responses"], "Integrated log interpretation uses complementary measurements and geological context to correlate intervals while accounting for uncertainty.", "intermediate"),
        ],
    ],
    "TEXTILE01": [
        [
            ("Which natural fibre is primarily composed of cellulose?", "Cotton", ["Wool", "Silk", "Nylon"], "Cotton is a cellulose-based seed fibre; wool and silk are protein fibres and nylon is synthetic.", "easy"),
            ("Which property is especially important when selecting a fibre for a high-moisture absorbent textile?", "Moisture regain and liquid uptake behaviour", ["Only the fibre's colour name", "Its magnetic permeability", "The number of loom pedals"], "Absorbent applications depend on fibre chemistry, structure, wetting, and moisture transport.", "easy"),
        ],
        [
            ("Why can increased polymer-chain orientation improve tensile properties of a manufactured fibre?", "More chains align with the loading direction and transfer load effectively", ["It removes all intermolecular forces", "It turns the polymer into a ceramic", "It guarantees unlimited elongation"], "Drawing can align polymer chains and improve strength and modulus, though excessive orientation can reduce extensibility.", "intermediate"),
            ("What is a common effect of increasing crystallinity in a polymer fibre?", "It can improve stiffness and dimensional stability while affecting dye uptake", ["It eliminates the polymer's molecular structure", "It makes all fibres biodegradable instantly", "It removes the need for testing"], "Crystalline regions generally restrict chain mobility and influence mechanical, thermal, and dyeing properties.", "intermediate"),
        ],
        [
            ("Why is fibre fineness measured when assessing textile raw material?", "It affects yarn count, handle, coverage, and processing behaviour", ["It determines the fibre's atomic number", "It gives the exact fabric price", "It is identical to staple length"], "Fineness is a mass-per-length measure that influences how fibres pack and behave during spinning and fabric formation.", "easy"),
            ("What is a purpose of a standard conditioning atmosphere before textile testing?", "Reduce the effect of variable moisture and temperature on measured properties", ["Make every fibre chemically identical", "Remove all natural fibre variation", "Increase sample mass by adding liquid water"], "Textile properties can depend on moisture and temperature, so controlled conditioning improves comparability and repeatability.", "easy"),
        ],
        [
            ("Why are short fibres often blended before spinning?", "Blending can combine desired properties and improve consistency of the feed", ["It guarantees no fibre breakage", "It changes the fibres into continuous filaments", "It removes the need for drafting"], "Blending distributes fibres from different lots or types to achieve target quality and processing behaviour, subject to blend control.", "easy"),
            ("In a blow-room line, what is a key purpose of opening and cleaning?", "Separate fibre tufts and remove a portion of trash before downstream processing", ["Weave the final fabric", "Dye each fibre molecule permanently", "Measure the finished garment size"], "Opening presents smaller tufts for cleaning and mixing while avoiding excessive fibre damage.", "easy"),
        ],
        [
            ("Why are technical textiles selected by performance requirements rather than appearance alone?", "Their application may depend on strength, filtration, thermal, or protective functions", ["Technical textiles never use fibres", "Appearance determines tensile strength completely", "All technical products are disposable"], "Engineering applications specify functional properties such as load bearing, filtration, insulation, or protection.", "easy"),
            ("When comparing a recycled-fibre option with a virgin fibre, what should a sustainability assessment include?", "Lifecycle impacts, durability, processing, supply chain, and end-of-life routes", ["Only the fibre's colour", "Only the recycled-content label", "An assumption that recycling always has zero impact"], "A defensible comparison uses a defined lifecycle boundary and examines impacts and trade-offs rather than relying on one attribute.", "intermediate"),
        ],
    ],
    "PROD01": [
        [
            ("In a linear-programming model, what does the objective function represent?", "The quantity to maximize or minimize subject to constraints", ["A list of decision-variable names only", "A guarantee that all variables are integers", "The graphical layout of the factory"], "The objective expresses the model's performance measure, such as cost or profit, as a function of decision variables.", "easy"),
            ("Why must units be consistent across a linear-programming constraint?", "The summed quantities must represent comparable dimensions", ["Units determine the number of optimal solutions", "All variables must be measured in currency", "Units can replace feasibility checks"], "Dimensional consistency is necessary for constraints to represent valid resource or requirement relationships.", "easy"),
        ],
        [
            ("In the simplex method, what does a basic feasible solution correspond to geometrically?", "A vertex of the feasible polytope", ["Any point outside the constraints", "The centre of every feasible region", "A direction with no decision variables"], "Linear-programming extreme-point solutions correspond to vertices, and simplex moves between adjacent bases under its assumptions.", "intermediate"),
            ("In a maximization model, what can a positive shadow price for a resource constraint indicate locally?", "Increasing that resource limit could improve the objective within the allowable range", ["The constraint is irrelevant in every scenario", "The model has no feasible solution", "Every variable should be set to zero"], "A shadow price gives a local marginal objective change for a right-hand-side change while the current basis remains valid.", "intermediate"),
        ],
        [
            ("What does a balanced transportation model require when total supply differs from total demand?", "Add a dummy source or destination with an appropriate balancing amount", ["Delete all supply constraints", "Set every shipping cost to zero", "Ignore the imbalance and keep the model unchanged"], "A dummy row or column balances totals; its costs encode the chosen interpretation of surplus or unmet demand.", "easy"),
            ("Why does a standard assignment problem use binary decision variables?", "Each worker-task pairing is either selected or not selected", ["A worker can be assigned fractionally to every task by definition", "Binary values represent travel time", "They force all costs to be equal"], "Binary variables model discrete assignment decisions, usually with one assignment per worker and one per task.", "easy"),
        ],
        [
            ("In a basic economic order quantity model, what trade-off determines the order quantity?", "Ordering cost versus inventory holding cost", ["Machine colour versus packaging size", "Only the supplier's postal code", "Demand uncertainty versus tax rate in every model"], "EOQ balances fixed ordering cost against holding cost under simplifying assumptions such as stable demand and lead time.", "easy"),
            ("Why is safety stock held in an inventory system?", "To buffer against demand or lead-time variability", ["To eliminate all storage cost", "To replace the reorder point", "To ensure obsolete items are retained"], "Safety stock provides protection against uncertainty, with the chosen level reflecting service goals and variability.", "easy"),
        ],
        [
            ("In a PERT network, what does the critical path determine?", "The minimum project completion time under the activity-duration estimates", ["The cheapest supplier automatically", "The maximum number of parallel workers", "The project's accounting year"], "The critical path is the longest-duration path through the precedence network and sets the earliest possible project finish.", "easy"),
            ("If an activity on the critical path is delayed and no schedule recovery is made, what is the usual effect?", "The project completion date is delayed", ["The project duration decreases", "An unrelated activity becomes shorter automatically", "The dependency network disappears"], "Critical-path activities have zero total float in the basic CPM schedule, so their delay generally delays the project unless mitigated.", "easy"),
        ],
    ],
    "AERO02": [
        [
            ("Why idealize a complex airframe as a set of load paths before calculating member stress?", "It clarifies how applied forces transfer through the structure to supports", ["It eliminates the need to identify loads", "It proves every member is in pure tension", "It makes material properties irrelevant"], "A load-path idealization helps identify the forces and boundary conditions that structural models must represent.", "easy"),
            ("What is a free-body diagram used for in aircraft structural analysis?", "Show external loads and reactions on an isolated component", ["Display only paint thickness", "Determine fatigue life without stress data", "Replace the equations of equilibrium"], "A free-body diagram defines the forces and moments acting on an isolated body for equilibrium analysis.", "easy"),
        ],
        [
            ("For a slender beam in elastic bending, where is normal stress largest in magnitude?", "At the outer fibres farthest from the neutral axis", ["At the neutral axis", "At the centroid regardless of section shape", "It is constant through the depth"], "Elastic bending stress varies linearly with distance from the neutral axis and reaches its largest magnitude at the extreme fibres.", "easy"),
            ("Why are shear-flow calculations useful for a thin-walled airframe section?", "They estimate how shear force is carried along the walls", ["They calculate electrical current in avionics", "They set the fuel's octane rating", "They eliminate torsion from every section"], "Shear flow describes shear force per unit length in thin-walled members and is used in sizing webs and joints.", "intermediate"),
        ],
        [
            ("Why can a fastener group fail even when each fastener's average shear load seems acceptable?", "Load eccentricity can create unequal fastener forces and local bearing stresses", ["All fasteners always share load equally", "Fastener material has no bearing strength", "The joint carries no moment"], "Eccentricity and flexibility redistribute load; bearing, bypass, net-section, and fastener failure modes also require checks.", "intermediate"),
            ("What is the purpose of a doubler around a structural cut-out?", "Reinforce and redistribute load around the interrupted load path", ["Increase aerodynamic drag intentionally", "Seal a fuel tank without a sealant", "Remove all stress concentration"], "A suitably designed doubler restores stiffness and transfers loads around a cut-out, though stress concentrations still need assessment.", "easy"),
        ],
        [
            ("What is the main concern when a thin compression panel buckles below the material's yield stress?", "Loss of stability can reduce its load-carrying capacity", ["The panel has gained unlimited strength", "Fatigue cracks must disappear", "The material's elastic modulus becomes infinite"], "Thin elements can buckle elastically before material yield, so local and global stability must be checked.", "intermediate"),
            ("How does a stiffener commonly improve a thin panel's compression performance?", "It reduces unsupported panel width and increases buckling resistance", ["It removes all compressive stress", "It makes the panel infinitely thick", "It prevents any thermal expansion"], "Stiffeners divide a panel into shorter subpanels and contribute to section stiffness, improving stability within design limits.", "easy"),
        ],
        [
            ("Why is fatigue damage assessed under repeated aircraft loading even when peak stress is below yield?", "Cracks can initiate and grow under cyclic stress over many flights", ["Elastic materials cannot crack", "Yield stress applies only to ceramics", "Repeated loading removes all defects"], "Fatigue is a cyclic-damage process and can cause crack growth at stress levels below monotonic yield strength.", "easy"),
            ("What does damage-tolerance design assume about a structural component?", "A flaw may exist, so inspection intervals and residual strength must be managed", ["No flaw can ever form", "Inspection is unnecessary after manufacture", "A crack always arrests immediately"], "Damage tolerance combines detectable flaw assumptions, crack-growth behaviour, inspection capability, and residual-strength requirements.", "intermediate"),
        ],
    ],
    "AERO03": [
        [
            ("In a steady level coordinated turn, what provides the centripetal acceleration?", "The horizontal component of lift", ["The vertical component of thrust only", "Weight acting horizontally", "Drag acting toward the turn centre"], "Banking tilts lift; its horizontal component supplies centripetal force while its vertical component balances weight in a steady level turn.", "intermediate"),
            ("What is load factor in a manoeuvre?", "The ratio of aerodynamic lift to aircraft weight", ["The ratio of fuel to wing area", "The ratio of thrust to drag only", "The number of landing gears"], "Load factor is commonly defined as lift divided by weight and indicates structural and physiological loading.", "easy"),
        ],
        [
            ("For static longitudinal stability, what pitching-moment response is desirable after a small positive angle-of-attack disturbance?", "A restoring nose-down pitching moment", ["A continuing nose-up moment", "No moment under any disturbance", "A yawing moment only"], "Positive static longitudinal stability requires the moment slope with angle of attack to be restoring under the chosen sign convention.", "intermediate"),
            ("What is the usual role of the horizontal tail in longitudinal trim?", "Provide a balancing pitching moment about the centre of gravity", ["Generate all aircraft lift", "Control engine fuel pressure", "Cancel the aircraft's weight"], "The tail force and moment balance wing, fuselage, and propulsion contributions for the selected trimmed condition.", "easy"),
        ],
        [
            ("Which equations govern rigid-body aircraft translation and rotation in a basic flight-dynamics model?", "Newton's force and moment equations", ["Kirchhoff's voltage laws only", "The ideal-gas equation alone", "The heat-diffusion equation only"], "Flight mechanics applies force and moment balance to the aircraft's mass and inertia to obtain equations of motion.", "easy"),
            ("Why is a body-axis coordinate system useful for deriving aircraft equations of motion?", "It describes translational and rotational rates relative to the aircraft", ["It makes every aerodynamic force constant", "It removes gravity from all frames", "It directly gives geographic longitude"], "Body axes simplify representation of aircraft-fixed forces, angular rates, and control inputs.", "intermediate"),
        ],
        [
            ("In a linearized short-period mode, which motion is most strongly associated with the mode?", "Rapid angle-of-attack and pitch-rate response", ["Slow fuel consumption", "A pure roll oscillation with no pitch motion", "Ground-track curvature only"], "The short-period longitudinal mode is a relatively fast pitch/angle-of-attack oscillation compared with the phugoid.", "intermediate"),
            ("What is Dutch roll primarily?", "A coupled yawing and rolling oscillation", ["A pure vertical translation", "A steady climb with no oscillation", "A longitudinal engine surge"], "Dutch roll couples lateral-directional yaw and roll motion and is influenced by directional and dihedral stability.", "easy"),
        ],
        [
            ("On a V-n diagram, what does the manoeuvre boundary represent?", "Load-factor limits associated with aerodynamic stall and structural constraints", ["Fuel temperature limits only", "The runway's length", "The maximum cabin pressure"], "A V-n diagram relates airspeed and load factor, showing stall and structural boundaries for manoeuvre limits.", "easy"),
            ("Why does a gust envelope matter in aircraft structural design?", "Atmospheric vertical gusts can create loads distinct from pilot-commanded manoeuvres", ["Gusts affect only ground handling", "It sets the aircraft's paint scheme", "Gust loads are always zero at cruise"], "Design envelopes account for gust-induced load increments across relevant speeds and atmospheric conditions.", "intermediate"),
        ],
    ],
    "AERO04": [
        [
            ("For a jet engine, what is the basic origin of net thrust?", "The change in momentum of the engine flow plus pressure thrust", ["The fuel tank's weight alone", "The wing's lift vector", "The exhaust's temperature without flow"], "Momentum flux change and any exit-pressure mismatch with ambient produce thrust in a control-volume description.", "easy"),
            ("Why does a turbofan often perform efficiently at subsonic transport speeds?", "Its bypass flow accelerates a large mass of air by a smaller velocity change", ["It produces thrust without moving air", "It has no compressor", "It converts all fuel energy directly to lift"], "For a given thrust, accelerating a larger mass flow by a lower velocity increment can improve propulsive efficiency at subsonic speed.", "intermediate"),
        ],
        [
            ("What is the function of a gas-turbine combustor?", "Add heat to compressed air while maintaining a stable flame and acceptable pressure loss", ["Extract all turbine work from the flow", "Compress inlet air mechanically", "Convert exhaust into liquid fuel"], "The combustor raises gas temperature through fuel burning while limiting pressure loss and maintaining flame stability.", "easy"),
            ("Why are compressor stages used in an axial gas turbine?", "Each stage raises pressure progressively with manageable blade loading", ["To lower pressure to ambient at every row", "To replace the turbine", "To prevent any mass flow"], "Multiple stages achieve the required pressure ratio while respecting aerodynamic and mechanical limits.", "easy"),
        ],
        [
            ("What does compressor surge describe?", "A system-level unstable flow condition with large pressure/flow oscillations and possible reversal", ["A normal steady operating point at maximum efficiency", "Combustion in the fuel tank", "A type of turbine cooling hole"], "Surge is an instability of the compressor and connected system, potentially causing severe oscillations and flow reversal.", "intermediate"),
            ("Why does turbine cooling allow higher gas temperatures than the blade material could tolerate uncooled?", "Coolant lowers blade metal temperature while hot gas supplies the cycle energy", ["Cooling removes the need for strength", "It makes the gas temperature equal to zero", "It prevents oxidation under every condition"], "Film and internal cooling manage component temperature, but create efficiency, durability, and manufacturing trade-offs.", "intermediate"),
        ],
        [
            ("What condition is required for a converging nozzle to choke?", "The pressure ratio must be sufficient for sonic flow at the throat", ["The nozzle must contain liquid fuel only", "The exit area must be smaller than zero", "The gas must have zero temperature"], "A critical pressure ratio produces Mach 1 at the minimum-area throat; further downstream expansion depends on nozzle geometry and back pressure.", "intermediate"),
            ("Why is combustor residence time important?", "The mixture needs enough time for stable and sufficiently complete combustion", ["It determines the wing loading", "It eliminates compressor work", "It fixes the propeller diameter"], "Combustion stability, efficiency, emissions, and combustor size depend in part on residence time and mixing.", "easy"),
        ],
        [
            ("Why does a propeller's blade angle generally need to vary along the radius?", "Local rotational speed changes with radius, so blade pitch is adjusted to maintain suitable aerodynamic incidence", ["Air density is always zero at the hub", "The tip is stationary relative to the aircraft", "The blade carries no aerodynamic load"], "Tangential speed increases with radius, so twist helps maintain an appropriate angle of attack over the blade.", "intermediate"),
            ("In a rocket engine, why does a nozzle accelerate the combustion products?", "Thermal and pressure energy is converted into directed exhaust kinetic energy", ["The nozzle creates oxidizer from nothing", "The exhaust is compressed to zero speed", "The rocket relies on atmospheric oxygen for all thrust"], "A rocket carries propellant and accelerates its exhaust through a nozzle; thrust does not require atmospheric air.", "easy"),
        ],
    ],
    "AGRI02": [
        [
            ("What does crop evapotranspiration represent in irrigation planning?", "Water lost through crop transpiration and evaporation from the soil surface", ["Only deep percolation below the root zone", "Only water stored in canal banks", "The total rainfall measured outside the field"], "Crop evapotranspiration combines transpiration and soil evaporation and is a key component of crop water requirement.", "easy"),
            ("Why is effective rainfall subtracted when estimating net irrigation requirement?", "It supplies part of the crop's water demand", ["It increases crop evapotranspiration", "It measures pump discharge", "It equals all rainfall regardless of runoff"], "Effective rainfall is the portion of precipitation stored in the root zone and available to meet crop demand.", "easy"),
        ],
        [
            ("What is the main purpose of a field-channel layout in surface irrigation?", "Deliver water to field units at suitable rates and elevations", ["Increase soil salinity", "Remove crop rows", "Measure groundwater depth only"], "A field-channel network conveys the required discharge to irrigation units while accounting for topography and control.", "easy"),
            ("Why can furrow irrigation be unsuitable on a highly erodible steep slope without careful design?", "Fast concentrated flow may detach and transport soil", ["It eliminates infiltration", "It prevents water from reaching roots", "It increases the field's contour length to zero"], "Slope and flow rate influence erosive shear; furrow length, grade, and inflow need to be selected to limit erosion and runoff.", "intermediate"),
        ],
        [
            ("Why is a pump characteristic curve compared with a system curve?", "Their intersection indicates the operating point for the installed system", ["It proves that the pump never cavitates", "It measures crop yield directly", "It determines the soil's texture"], "The pump head-flow curve and system head requirement together establish the approximate operating flow and head.", "intermediate"),
            ("What is a common consequence of operating a centrifugal pump far from its best-efficiency point?", "Higher vibration, losses, or mechanical loading may occur", ["The pump efficiency becomes exactly 100%", "The required head becomes zero", "The impeller stops interacting with water"], "Off-design operation can increase hydraulic losses and vibration and may reduce reliability depending on the pump and system.", "easy"),
        ],
        [
            ("What is the purpose of subsurface drainage in a waterlogged field?", "Lower excess water and improve aeration in the root zone", ["Raise the water table to the soil surface", "Increase ponding duration", "Replace all crop water supply"], "Drainage removes excess water to improve root-zone aeration and manage salinity where appropriately designed.", "easy"),
            ("Why does drain spacing depend on soil hydraulic conductivity and drainage depth?", "These properties control how quickly groundwater moves toward drains", ["They determine the crop's seed colour", "They are unrelated to water movement", "They set the canal's concrete strength"], "Spacing equations depend on the soil's ability to transmit water and the target water-table depth and boundary conditions.", "intermediate"),
        ],
        [
            ("What does application efficiency compare in irrigation?", "Water stored usefully in the root zone with water delivered or applied", ["Crop price with pump cost", "Canal length with field width", "Rainfall intensity with soil colour"], "Application efficiency indicates the fraction of applied water stored in the target root zone, under a stated definition.", "easy"),
            ("Why schedule irrigation using soil moisture or crop demand rather than a fixed calendar alone?", "Weather and soil-water depletion vary over time", ["Crop water use is identical every day", "A calendar changes soil texture", "Sensors eliminate the need for field checks"], "Demand-based scheduling accounts for weather, crop stage, soil storage, and rainfall, while measurements themselves need calibration and context.", "intermediate"),
        ],
    ],
    "AGRI03": [
        [
            ("Why is drawbar power important when selecting a tractor for a tillage operation?", "It represents useful pulling power available at the drawbar", ["It is the crop's photosynthetic power", "It measures the tractor's paint area", "It is identical to engine displacement"], "Drawbar power is the product of drawbar pull and travel speed and is relevant for tractive field operations.", "easy"),
            ("Why can matching implement width to available tractor power improve field work?", "It avoids excessive speed loss, overload, or underuse of the tractor", ["It guarantees zero fuel consumption", "It makes soil resistance disappear", "It eliminates turning time"], "A suitable match considers draft, power, speed, soil, and field efficiency rather than nominal width alone.", "intermediate"),
        ],
        [
            ("What is wheel slip in a tractor?", "The difference between theoretical wheel travel and actual travel under load", ["The tractor's fuel evaporation rate", "The angle between two crop rows", "The difference between front and rear paint colours"], "Wheel slip expresses the loss of travel due to tyre deformation and soil interaction under traction.", "easy"),
            ("Why can excessive wheel slip reduce field efficiency?", "Part of the engine power is spent deforming soil and tyres instead of productive travel", ["It increases the implement's working width", "It removes all rolling resistance", "It makes the tractor travel farther per revolution"], "High slip wastes tractive effort and can damage soil; suitable ballast, tyres, pressure, and implement load help manage it.", "intermediate"),
        ],
        [
            ("What is the main function of a mouldboard plough?", "Cut, lift, and invert a furrow slice", ["Plant individual seeds at a set depth", "Spray a measured pesticide dose", "Harvest grain from standing crops"], "A mouldboard plough cuts and inverts soil, burying residue but potentially increasing erosion risk if misused.", "easy"),
            ("Why use a seedbed cultivator after primary tillage?", "Prepare a finer, level seedbed and control shallow weeds", ["Increase deep compaction", "Replace seed metering", "Remove the need for planting depth control"], "Secondary tillage can break clods and prepare the planting zone, but excessive passes may degrade soil structure.", "easy"),
        ],
        [
            ("What does a seed metering mechanism control in a planter?", "The rate and spacing at which seed is delivered", ["The soil's bulk density across the farm", "The engine's compression ratio", "The field's irrigation water quality"], "Metering determines seed rate and spacing, while the opener and depth-control system place seed in soil.", "easy"),
            ("Why should a pesticide sprayer be calibrated before field application?", "To deliver a known application rate at the intended travel speed and pressure", ["To increase drift intentionally", "To avoid checking nozzle condition", "To determine crop maturity"], "Calibration relates nozzle flow, spacing, pressure, and travel speed to application volume and helps avoid under- or over-application.", "intermediate"),
        ],
        [
            ("How is theoretical field capacity commonly estimated for an implement?", "Working width multiplied by travel speed", ["Fuel tank volume divided by tyre pressure", "Engine torque multiplied by crop height", "Field area multiplied by soil moisture"], "Theoretical field capacity is width times speed with unit conversion; actual capacity is lower because of turns, overlap, and delays.", "easy"),
            ("Why is field efficiency less than one in real machinery operations?", "Turning, adjustment, overlap, and downtime reduce productive coverage", ["Theoretical capacity includes these delays exactly", "All machines stop only at field boundaries", "The field has no measurable area"], "Field efficiency compares actual with theoretical capacity and reflects operational losses and nonproductive time.", "easy"),
        ],
    ],
    "AGRI04": [
        [
            ("Why are crop moisture content and bulk density measured before designing a post-harvest handling line?", "They affect drying load, storage volume, and material flow", ["They determine the crop's genetic code", "They replace quality inspection", "They set the field's rainfall total"], "Moisture and bulk density influence storage capacity, drying energy, and equipment throughput.", "easy"),
            ("Why can bruising during handling reduce marketable crop quality?", "Mechanical damage can accelerate deterioration and microbial entry", ["It increases the crop's shelf life universally", "It removes all moisture from the crop", "It prevents respiration"], "Impact damage can injure tissues, increase respiration, and create sites for infection and quality loss.", "easy"),
        ],
        [
            ("What is the purpose of grading produce after cleaning?", "Separate lots by defined quality, size, or maturity criteria", ["Increase field moisture content", "Mix all grades into an unlabelled batch", "Measure only the storage-room temperature"], "Grading classifies produce using agreed attributes to support consistent packaging, pricing, and processing.", "easy"),
            ("Why should a grain cleaner use screens and airflow matched to the crop?", "Separation depends on particle size, density, and aerodynamic properties", ["All contaminants have identical dimensions", "Airflow removes only water vapour", "Screening changes the grain's variety"], "Screen apertures and air velocity are selected to separate impurities while minimizing good-product loss.", "intermediate"),
        ],
        [
            ("On a wet basis, moisture content is defined as water mass divided by what?", "Total wet sample mass", ["Dry solid mass only", "Container mass only", "Air volume in the dryer"], "Wet-basis moisture content uses water mass divided by total sample mass; dry basis uses dry-solids mass instead.", "easy"),
            ("Why does drying slow as a crop approaches its equilibrium moisture content with the surrounding air?", "The vapour-pressure driving force for moisture removal becomes small", ["The crop's mass becomes infinite", "Air stops moving in every dryer", "The crop absorbs no heat"], "As product moisture approaches equilibrium with the air at its temperature and humidity, the net moisture-transfer driving force declines.", "intermediate"),
        ],
        [
            ("Why is controlled-atmosphere storage used for some produce?", "Gas composition can slow respiration and ripening", ["It makes refrigeration unnecessary in all cases", "It sterilizes every product instantly", "It increases oxygen to unlimited levels"], "Managing oxygen and carbon dioxide can reduce metabolic rates for suitable commodities, but conditions must avoid physiological injury.", "intermediate"),
            ("What is a major purpose of cold-chain temperature control?", "Slow biological and chemical deterioration from harvest to use", ["Increase microbial growth", "Replace packaging and hygiene", "Make all produce nonperishable"], "Lowering temperature can slow respiration and microbial growth, but the required range depends on the commodity and chilling sensitivity.", "easy"),
        ],
        [
            ("What does a food-process mass balance help determine?", "Material input, product, by-product, and loss quantities", ["The crop's genetic diversity", "Only the colour of equipment", "The field's soil classification"], "A mass balance accounts for material flows around a process boundary and supports capacity and yield calculations.", "easy"),
            ("Why is reducing post-harvest losses a system-level problem?", "Losses can occur during harvesting, handling, storage, transport, and processing", ["Only processing temperature matters", "Losses occur only before harvest", "Packaging makes all upstream handling irrelevant"], "Loss prevention needs coordinated equipment, handling, storage, transport, and quality practices across the chain.", "easy"),
        ],
    ],
    "AI_DS02": [
        [
            ("Why preserve the source schema and ingestion timestamp when loading a dataset?", "They support lineage, reproducibility, and interpretation of later changes", ["They improve image resolution", "They eliminate the need for validation", "They make every record immutable by default"], "Source metadata and event times help explain where records came from and when they entered the pipeline.", "easy"),
            ("When should a data pipeline use a schema registry or versioned schema contract?", "When producers and consumers need controlled, compatible schema evolution", ["Only after all data has been deleted", "To replace access control", "To ensure the schema never changes"], "Versioned contracts make compatibility expectations explicit as datasets evolve across services.", "intermediate"),
        ],
        [
            ("What is a key difference between a relational database and a document store?", "A relational system organizes data around tables and relations; a document store commonly stores nested documents", ["Relational databases cannot index data", "Document stores cannot store text", "Relational databases require every value to be an image"], "The models differ in how structure and relationships are represented; actual capabilities vary by product.", "easy"),
            ("Why choose a unique key for a record in a distributed data store?", "It enables reliable identification, updates, and deduplication", ["It guarantees global ordering", "It encrypts the record", "It removes network partitions"], "A stable key helps identify the same entity across retries and distributed processing.", "easy"),
        ],
        [
            ("What is a common role of the transform step in ETL?", "Convert and validate source data into a target-ready representation", ["Route internet packets", "Create backups without reading data", "Set the physical location of a sensor"], "Transformation applies cleaning, type conversion, mapping, and business rules before loading the target.", "easy"),
            ("Why quarantine records that fail data-quality checks instead of silently dropping them?", "They can be inspected, corrected, and reconciled without corrupting trusted outputs", ["It guarantees every source is correct", "It prevents all schema changes", "It increases the number of valid records automatically"], "A quarantine path supports diagnosis and recovery while preserving the distinction between accepted and rejected data.", "intermediate"),
        ],
        [
            ("Which workload is a natural fit for batch processing?", "Recomputing yesterday's aggregate from a bounded set of records", ["Reacting to each event with millisecond latency", "Controlling a motor's real-time feedback loop", "A protocol handshake that must complete now"], "Batch processing handles finite collections on a schedule; latency-sensitive event reactions usually need streaming or online processing.", "easy"),
            ("Why can a stream-processing system use event time rather than only processing time?", "Events may arrive late or out of order relative to when they occurred", ["Event time avoids clocks entirely", "Processing time identifies the physical sensor exactly", "Event time guarantees no duplicate messages"], "Event-time windows model when events happened; watermarks and lateness policies handle delayed arrivals.", "intermediate"),
        ],
        [
            ("Why is an idempotent data-ingestion step useful when jobs are retried?", "Repeating the same input does not create duplicate effects", ["It guarantees input data is true", "It removes the need for monitoring", "It prevents a job from failing"], "Idempotency helps retries recover from uncertain failures without duplicating outputs.", "easy"),
            ("What should a pipeline alert on in addition to process crashes?", "Freshness, volume, quality, and latency deviations", ["Only the colour of a dashboard", "The number of developers in a room", "Every record's text length regardless of context"], "Data reliability also depends on timely and complete outputs and expected quality, not merely a running process.", "intermediate"),
        ],
    ],
    "AI_DS03": [
        [
            ("Why keep a test set separate from training and model-selection data?", "It estimates performance on held-out data after choices are finalized", ["It increases training size without limit", "It selects hyperparameters repeatedly", "It guarantees future performance never changes"], "Repeatedly using a test set for choices leaks information and makes the final estimate optimistic.", "easy"),
            ("When is stratified splitting especially useful for classification?", "When class proportions should be kept similar across splits", ["When labels are continuous and uniformly spaced", "When the data is already ordered by answer", "When every class has one example"], "Stratification preserves approximate label proportions when that is appropriate for the sampling design.", "easy"),
        ],
        [
            ("What does regularization do in a linear model?", "Penalize model complexity to discourage overly large coefficients", ["Increase every coefficient without limit", "Replace the response variable", "Guarantee that all features are causal"], "L1 or L2 penalties constrain coefficient magnitude and can reduce overfitting, with different effects on sparsity.", "easy"),
            ("Why standardize features before applying many regularized linear models?", "A common penalty should not treat features differently only because their units differ", ["It removes the target labels", "It guarantees a linear relationship", "It changes classification into clustering"], "Scaling makes coefficient penalties more comparable across features with different measurement units.", "intermediate"),
        ],
        [
            ("In a decision tree, what does a split aim to do?", "Partition examples to improve a chosen impurity or loss criterion", ["Encrypt every feature", "Make every leaf contain all classes equally", "Remove the need for validation"], "Tree splitting selects feature thresholds or categories that reduce impurity or objective loss under the chosen criterion.", "easy"),
            ("Why can a random forest generalize better than a single deep tree?", "Averaging diverse trees can reduce variance", ["It guarantees zero bias", "It uses no training data", "It ensures every tree has identical errors"], "Bagging and feature randomness encourage diversity, and averaging often stabilizes predictions though it does not guarantee improvement in all settings.", "intermediate"),
        ],
        [
            ("What does k-means minimize for a fixed number of clusters?", "Within-cluster squared distances to assigned centroids", ["The number of input rows", "Classification error against unseen labels", "The total number of features"], "K-means iteratively assigns observations and updates centroids to reduce within-cluster sum of squares.", "easy"),
            ("Why can principal component analysis help visualize high-dimensional data?", "It projects data onto directions with high variance", ["It guarantees class separation", "It creates new ground-truth labels", "It preserves every pairwise distance exactly"], "PCA provides a linear projection maximizing variance in successive orthogonal components, not necessarily class separability.", "intermediate"),
        ],
        [
            ("A model fits training data very well but performs poorly on validation data. What is a likely issue?", "Overfitting", ["Underfitting", "A perfect calibration", "A missing target variable in training"], "A large generalization gap often indicates the model has learned noise or overly specific patterns.", "easy"),
            ("For an imbalanced binary classification problem, why can precision-recall metrics be more informative than accuracy alone?", "They expose false-positive and false-negative trade-offs for the positive class", ["Accuracy is always undefined", "They ignore the confusion matrix", "They prove that the minority class is unimportant"], "Accuracy can be dominated by the majority class; precision and recall reveal behavior on the positive class at a selected threshold.", "intermediate"),
        ],
    ],
    "AI_DS04": [
        [
            ("Which visual encoding is usually most accurate for comparing values across categories?", "Position along a common scale", ["Area of unrelated decorative icons", "Colour hue with no legend", "Perspective depth without a scale"], "Position on a shared axis supports precise comparisons more reliably than area or decorative encodings.", "easy"),
            ("Why use a sequential colour palette for an ordered magnitude?", "Lightness or saturation can communicate progression from low to high", ["It assigns unrelated hues to hide order", "It removes the need for a legend", "It implies nominal categories only"], "Sequential palettes communicate ordered values; diverging palettes are useful when there is a meaningful midpoint.", "easy"),
        ],
        [
            ("What is the main purpose of an exploratory scatter plot?", "Inspect association, clusters, trends, and unusual observations between two variables", ["Prove that one variable causes another", "Show exact values for millions of points without overlap", "Replace data cleaning"], "Scatter plots support exploratory inspection but do not establish causal relationships by themselves.", "easy"),
            ("Why might a logarithmic axis be appropriate for a strongly right-skewed positive measure?", "It can show orders of magnitude while compressing large values", ["It turns negative values into valid ratios automatically", "It guarantees normally distributed data", "It makes every gap equal in the original units"], "Log scales can reveal multiplicative patterns across positive values, but need clear labels and careful interpretation.", "intermediate"),
        ],
        [
            ("Why should an error bar identify what uncertainty it represents?", "Intervals may show standard deviation, standard error, or a confidence interval with different meanings", ["All error bars mean the same thing", "Error bars prove causality", "The interval label changes the observations"], "A visual interval must state its statistical definition and construction so viewers can interpret it correctly.", "easy"),
            ("What can a confidence interval communicate alongside a point estimate?", "Sampling uncertainty under the model and procedure used", ["The exact range of all future observations", "The probability that the parameter changes after publication", "A guarantee of unbiased measurement"], "A confidence interval reflects uncertainty under its assumptions; it is not a prediction interval or a guarantee against bias.", "intermediate"),
        ],
        [
            ("Why should a dashboard place its highest-priority measures where users can find them quickly?", "Visual hierarchy reduces search effort and supports the intended task", ["It guarantees the metric is correct", "It removes the need for context", "It makes every chart equally important"], "Layout and hierarchy help users locate decision-relevant information, while definitions and data quality remain essential.", "easy"),
            ("When is a filter control most useful on a dashboard?", "When users need to inspect a relevant subset without changing the underlying metric definition", ["When the data should be hidden permanently", "When it changes the source values silently", "When all users need the same static view"], "Filters support exploration when their scope and effects are clear and do not obscure comparability.", "intermediate"),
        ],
        [
            ("What should a chart's alternative text describe for a screen-reader user?", "The chart's purpose, key pattern, and relevant values or comparisons", ["Only the file name", "The colour palette without the data", "A decorative description unrelated to the findings"], "Useful alternative text conveys the chart's message and important comparisons rather than just its visual appearance.", "easy"),
            ("Why include units and a clear baseline on a quantitative chart?", "They help readers interpret magnitudes and avoid misleading comparisons", ["They make the dataset confidential", "They remove the need for axis labels", "They guarantee no data errors exist"], "Units and visible scales provide context; truncated or inconsistent axes can exaggerate visual differences.", "easy"),
        ],
    ],
    "AUTO02": [
        [
            ("What does a pneumatic tyre's slip angle describe in a simple vehicle model?", "The difference between the wheel heading and its direction of travel", ["The tyre's tread depth", "The difference between engine and wheel speed", "The vehicle's longitudinal grade"], "Slip angle is the angle between the wheel plane and the velocity direction and is related to lateral tyre force.", "easy"),
            ("Why does a tyre force not increase indefinitely with slip angle?", "The contact patch saturates and may approach sliding", ["Tyre friction becomes infinite", "The wheel loses all vertical load", "Slip angle becomes identical to camber"], "Tyre force is nonlinear and saturates as the contact patch approaches its friction limit.", "intermediate"),
        ],
        [
            ("During braking, what is the primary purpose of anti-lock braking control?", "Prevent sustained wheel lock while maintaining controllability", ["Increase engine torque", "Guarantee the shortest stop on every surface", "Disable the service brakes"], "ABS modulates brake pressure to help prevent lockup; stopping distance still depends on surface, tyre, and system conditions.", "easy"),
            ("Why can load transfer increase front-axle normal force during deceleration?", "The centre of gravity height and longitudinal acceleration create a pitching moment", ["The vehicle's mass increases", "The road becomes level", "The tyres stop generating force"], "Longitudinal load transfer is related to deceleration, centre-of-gravity height, wheelbase, and mass.", "intermediate"),
            ("Why can ABS fail to shorten stopping distance on loose gravel even while maintaining steering control?", "Wheel slip may build loose material ahead of a locked tyre, affecting deceleration", ["ABS removes the vehicle's mass", "Gravel has no friction", "ABS increases engine power"], "On some loose surfaces, a locked wheel can build a wedge that changes stopping distance; ABS prioritizes controllability and performance varies by surface.", "intermediate"),
        ],
        [
            ("What is the purpose of a spring-damper suspension system?", "Support the body and control oscillatory motion after road disturbances", ["Maintain engine combustion", "Generate steering angle", "Eliminate all tyre deflection"], "Springs support loads and store energy; dampers dissipate energy to control body and wheel oscillations.", "easy"),
            ("What can an excessively soft damper cause after a road bump?", "Prolonged oscillations and reduced body control", ["Zero suspension travel", "Instantly higher tyre friction", "No movement of the sprung mass"], "Insufficient damping allows oscillations to persist, though too much damping can also worsen ride or road holding.", "intermediate"),
        ],
        [
            ("What does understeer mean in a steady cornering comparison?", "The vehicle needs increasing steering angle as lateral acceleration rises", ["The rear tyres always lose contact", "The steering wheel turns without changing path", "The vehicle's mass moves to zero"], "Understeer gradient describes how steering demand changes with lateral acceleration; the definition assumes a stated operating range.", "easy"),
            ("Why is Ackermann steering geometry used at low speeds?", "Inner and outer front wheels follow different turning radii", ["Both wheels must have equal road-wheel angle in every turn", "It controls engine valve timing", "It eliminates tyre scrub at all speeds and loads"], "Ackermann geometry approximates the differing wheel angles needed for pure rolling around a common turn centre.", "intermediate"),
        ],
        [
            ("What is the yaw rate of a vehicle?", "The rate of rotation about its vertical axis", ["The rate of wheel rotation about the axle", "The vertical suspension velocity", "The rate of engine fuel injection"], "Yaw rate measures angular velocity around the vehicle's vertical axis.", "easy"),
            ("Why can electronic stability control apply an individual wheel brake?", "Create a corrective yaw moment when the vehicle deviates from the intended path", ["Increase tyre diameter", "Change the road friction coefficient", "Replace the steering system"], "Selective braking can generate a stabilizing yaw moment, within tyre-force and system limits.", "intermediate"),
        ],
    ],
    "AUTO03": [
        [
            ("What is the primary function of a clutch in a manual-transmission vehicle?", "Connect or disconnect engine torque from the gearbox input", ["Control tyre pressure", "Change the engine's compression ratio", "Measure road gradient"], "The clutch allows torque transfer to be engaged or interrupted, enabling starts and gear changes.", "easy"),
            ("Why is controlled clutch slip used during vehicle launch?", "It allows engine speed and vehicle speed to transition smoothly", ["It eliminates all friction", "It locks every gear simultaneously", "It reduces the vehicle's wheelbase"], "Frictional slip permits gradual torque transfer at launch but creates heat and wear if prolonged.", "easy"),
        ],
        [
            ("In a simple gear pair, what does a larger reduction ratio generally do to output speed and torque?", "Reduce speed and increase torque, neglecting losses", ["Increase both speed and torque without power input", "Reduce torque to zero", "Change only the shaft material"], "A reduction trades rotational speed for torque while approximately conserving power before losses.", "easy"),
            ("What is a key purpose of synchronizers in a manual gearbox?", "Match gear and shaft speeds before the dog teeth engage", ["Cool the engine coolant", "Measure differential temperature", "Provide continuously variable ratio"], "Synchronizers reduce speed difference to enable smoother engagement and lower impact during shifting.", "easy"),
        ],
        [
            ("What does an open differential allow during a turn?", "Left and right drive wheels to rotate at different speeds", ["Both wheels to have different axle torque under all conditions", "The engine to stop rotating", "The vehicle to turn without tyre forces"], "An open differential accommodates different wheel speeds; torque distribution is constrained by available traction.", "easy"),
            ("Why can a limited-slip differential improve traction on uneven surfaces?", "It can transfer more usable torque to a wheel with better grip", ["It makes all tyres frictionless", "It removes the need for a final drive", "It forces both wheels to have zero speed difference always"], "A limited-slip mechanism resists excessive speed difference and can improve torque utilization, depending on its design.", "intermediate"),
        ],
        [
            ("How does a belt-type continuously variable transmission change ratio?", "By changing the effective radii of the drive and driven pulleys", ["By adding fixed gear pairs only", "By varying tyre pressure", "By moving the crankshaft into the cabin"], "A CVT varies pulley working radii so the ratio can change continuously over its design range.", "easy"),
            ("Why must a CVT control clamping force on its pulley system?", "It must transmit torque without excessive belt or chain slip", ["To increase aerodynamic lift", "To reduce fuel octane", "To change the battery chemistry"], "Adequate clamping force transfers torque, while excessive force increases losses and component stress.", "intermediate"),
        ],
        [
            ("Why is transmission efficiency evaluated over a range of ratios and loads?", "Losses vary with speed, torque, temperature, and operating point", ["Efficiency is always constant for every condition", "Only the gear colour affects efficiency", "Load has no effect on friction"], "Gear mesh, bearing, churning, and hydraulic losses change across the operating map.", "easy"),
            ("What should guide selection between a multi-speed gearbox and a CVT for a vehicle application?", "Duty cycle, efficiency, torque capacity, cost, and drivability requirements", ["Only the dashboard font", "The number of doors alone", "A rule that CVTs suit every vehicle"], "Transmission choice is an application trade-off that depends on performance needs, losses, durability, controls, and cost.", "intermediate"),
        ],
    ],
    "AUTO04": [
        [
            ("Why do vehicles use multiple electrical voltage domains or buses?", "Different loads have different power, safety, and communication requirements", ["All electronics require the same current", "It removes the need for fuses", "It makes every signal analog"], "Vehicle electrical architectures segment power and communication according to loads, safety, and design constraints.", "easy"),
            ("What is a common role of a vehicle ground return?", "Complete an electrical circuit back to its source", ["Provide a second data payload", "Increase battery voltage automatically", "Measure wheel alignment"], "A return path completes the circuit; ground topology and bonding also affect noise and fault behaviour.", "easy"),
        ],
        [
            ("What does a thermistor sensor commonly use to infer temperature?", "A temperature-dependent change in electrical resistance", ["A change in wheelbase", "A fuel pressure pulse only", "The vehicle's GPS coordinates"], "Thermistors change resistance with temperature, with calibration and circuit design needed for measurement.", "easy"),
            ("Why might an engine controller use a Hall-effect sensor for crank position?", "It can detect a magnetic target without requiring physical contact", ["It measures coolant chemistry directly", "It creates mechanical timing marks", "It works only with optical fibres"], "A Hall sensor detects magnetic-field changes from a target and can provide a robust position or speed signal.", "easy"),
        ],
        [
            ("What is the role of an engine control unit (ECU)?", "Read sensor inputs and command actuators according to control logic", ["Act as the vehicle's fuel tank", "Replace the mechanical brakes", "Measure tyre tread depth continuously"], "An ECU processes inputs and executes calibrated control strategies for engine functions.", "easy"),
            ("Why does a body control module often manage functions such as lighting and door locks?", "These functions share low-power electronic control and vehicle network interfaces", ["They determine combustion timing", "They control only high-voltage traction current", "They replace every sensor"], "A body controller coordinates convenience and body electrical functions, with exact boundaries varying by vehicle architecture.", "easy"),
        ],
        [
            ("What is a benefit of a differential communication bus such as CAN in a vehicle?", "It supports robust multi-node communication over a shared bus", ["It provides mechanical torque to wheels", "It guarantees that messages can never be delayed", "It replaces all electrical power wiring"], "CAN uses differential signalling and arbitration to support communication among multiple vehicle nodes; it does not carry actuator power.", "intermediate"),
            ("Why read diagnostic trouble codes with freeze-frame data?", "The snapshot can show operating conditions when a fault was detected", ["It guarantees the named component is defective", "It measures engine compression directly", "It clears the fault without repair"], "Codes and context guide diagnosis but do not prove a particular part failed; testing is still needed.", "easy"),
        ],
        [
            ("What does a functional-safety process aim to manage in a vehicle electronic system?", "Risks arising from malfunctioning behaviour of safety-related functions", ["All cybersecurity threats by itself", "Fuel economy only", "Routine styling changes"], "Functional safety addresses hazards caused by system malfunctions through lifecycle risk analysis and safety measures.", "intermediate"),
            ("Why confirm a suspected electrical fault with measurements before replacing an ECU?", "The fault may be caused by wiring, power, ground, connectors, or another component", ["ECUs never fail", "A diagnostic code always names the failed part exactly", "Replacement automatically repairs open circuits"], "Structured fault diagnosis checks supply, ground, connections, signals, and related components before module replacement.", "easy"),
        ],
    ],
    "BIOMED02": [
        [
            ("What is the role of a biopotential electrode at the skin interface?", "Convert ionic current in tissue into an electronic signal in the measurement circuit", ["Generate the heart's electrical activity", "Measure blood glucose without a sensing element", "Replace the amplifier"], "Electrodes couple ionic potentials in tissue to electronic instrumentation; interface impedance and motion affect signal quality.", "easy"),
            ("Why use a conductive gel with many surface ECG electrodes?", "Reduce contact impedance and improve electrical coupling", ["Increase electrode polarization indefinitely", "Block the cardiac signal", "Sterilize the ECG amplifier"], "Gel improves contact and lowers impedance, although preparation and electrode type also matter.", "easy"),
        ],
        [
            ("What does the QRS complex mainly represent in a surface ECG?", "Ventricular depolarization", ["Atrial repolarization only", "Ventricular filling pressure", "Respiratory airflow"], "The QRS complex corresponds primarily to ventricular depolarization; atrial repolarization is usually obscured by it.", "easy"),
            ("Why is EEG commonly recorded with multiple scalp electrodes?", "Spatially distributed channels help observe patterns of brain electrical activity", ["Each electrode measures a separate neuron exactly", "It directly images brain anatomy", "It measures only blood oxygen"], "EEG channels sample voltage differences across the scalp and provide limited spatial information about summed neural activity.", "intermediate"),
        ],
        [
            ("Why include an instrumentation amplifier near a biopotential input?", "It amplifies a small differential signal while rejecting common-mode voltage", ["It converts ECG into ultrasound", "It eliminates all electrode noise", "It creates patient isolation by itself"], "A high-input-impedance instrumentation amplifier with high common-mode rejection is useful for small differential biopotentials.", "easy"),
            ("What is the purpose of electrical isolation in patient-connected equipment?", "Limit hazardous current paths between the patient circuit and other electrical domains", ["Increase patient leakage current", "Remove the need for risk assessment", "Improve image resolution"], "Isolation barriers are part of patient-safety design, but compliance also requires leakage, creepage, clearance, and system-level assessment.", "intermediate"),
        ],
        [
            ("What does a thermocouple produce when its junctions are at different temperatures?", "A voltage related to the temperature difference", ["A direct digital image", "A mechanical displacement only", "A constant resistance at all temperatures"], "The Seebeck effect generates thermoelectric voltage related to junction temperature difference and material properties.", "easy"),
            ("Why might a pulse oximeter use two wavelengths of light?", "Oxyhaemoglobin and deoxyhaemoglobin absorb light differently", ["To measure blood pressure directly", "To avoid detecting pulsatile blood", "To eliminate all motion artifacts"], "Red and infrared absorption differences in pulsatile arterial blood support an estimate of oxygen saturation, subject to limitations.", "easy"),
        ],
        [
            ("Why is electrical medical equipment classified and tested for applied-part protection?", "The patient connection can create special shock hazards", ["Applied parts determine the hospital floor plan", "It guarantees clinical accuracy", "It removes the need for maintenance"], "Applied-part classification and testing address patient leakage and shock risk according to intended connection and use.", "intermediate"),
            ("What is an important first response if a biomedical instrument shows an unexplained measurement drift?", "Check calibration status, leads, sensor condition, and acquisition setup", ["Ignore the reading and alter the patient record", "Increase gain until the value looks normal", "Replace the patient sensor without checking"], "Troubleshooting should verify calibration and the full signal path before interpreting a drifting measurement clinically.", "easy"),
        ],
    ],
    "BIOMED03": [
        [
            ("What does biocompatibility mean for a material in a particular medical application?", "It performs with an appropriate host response for its intended use", ["It is chemically inert in every environment", "It cannot ever cause an adverse response", "It is approved for every implant"], "Biocompatibility is application- and exposure-specific; no material is universally safe for every use.", "easy"),
            ("Why distinguish cytotoxicity testing from a full implant evaluation?", "A cell assay covers only one aspect of biological response and does not reproduce the whole use context", ["Cell tests directly measure long-term clinical success", "Implants never contact tissue", "Cytotoxicity is a mechanical property"], "Biological evaluation considers contact type, duration, degradation, mechanical function, and other relevant endpoints beyond a single assay.", "intermediate"),
        ],
        [
            ("Why use a control material and positive/negative controls in a biocompatibility assay?", "They help distinguish test-material effects from assay failure or baseline response", ["They remove the need for validated methods", "They make all test materials identical", "They guarantee clinical approval"], "Controls check assay performance and help interpret observed responses within the test's scope.", "intermediate"),
            ("What does a material's surface chemistry influence at a tissue interface?", "Protein adsorption and subsequent cell and biological interactions", ["Only the implant's colour", "The patient's genetic code", "The device's battery voltage"], "Surface chemistry and topography influence protein adsorption, cell attachment, and subsequent host response.", "easy"),
        ],
        [
            ("Why are titanium alloys commonly considered for load-bearing implants?", "They combine useful strength, corrosion resistance, and biocompatibility in many applications", ["They dissolve immediately in body fluid", "They have zero elastic modulus", "They eliminate stress shielding in every design"], "Titanium alloys are used for many implants, but alloy choice and design must still address fatigue, wear, osseointegration, and modulus mismatch.", "easy"),
            ("What is a common design concern for an absorbable polymer implant?", "Its degradation rate should be compatible with tissue healing and mechanical support needs", ["It must never change molecular weight", "It should release unlimited monomer", "Its strength is independent of degradation"], "Degradation kinetics and strength retention should match the application while breakdown products remain appropriately tolerated.", "intermediate"),
        ],
        [
            ("Why are porous scaffolds used in some tissue-engineering applications?", "They can support cell infiltration, nutrient transport, and tissue ingrowth", ["They prevent all fluid transport", "They replace all biological signals", "They make mechanical testing unnecessary"], "Pore architecture can aid transport and ingrowth, while porosity also affects mechanical strength and must be optimized.", "easy"),
            ("What is one role of a ceramic such as hydroxyapatite in a bone-related biomaterial?", "Provide a bioactive calcium-phosphate surface that can support bone bonding", ["Act as a flexible electrical cable", "Replace collagen in every tissue", "Prevent all mineral dissolution"], "Hydroxyapatite resembles the mineral phase of bone and can support bioactivity, though brittleness limits some structural uses.", "intermediate"),
        ],
        [
            ("What can fretting wear at an implant interface produce?", "Debris that may contribute to inflammation and component loosening", ["A guaranteed increase in bone strength", "A permanent reduction in friction to zero", "An increase in implant diameter"], "Micromotion can produce wear debris and inflammatory responses, potentially contributing to osteolysis and loosening.", "intermediate"),
            ("Why test an implant under cyclic loading rather than only a single static load?", "Repeated loads can cause fatigue damage even below a one-time failure load", ["Static testing measures fatigue life exactly", "Cyclic loading never occurs in the body", "It eliminates corrosion"], "Implants experience repeated service loads; fatigue evaluation complements static strength assessment and considers the use environment.", "easy"),
        ],
    ],
    "BIOMED04": [
        [
            ("What physical process produces X-rays in a typical diagnostic tube?", "Electrons accelerated toward a target produce bremsstrahlung and characteristic radiation", ["Radiofrequency spin excitation", "Ultrasound reflection", "Visible-light fluorescence only"], "An X-ray tube generates bremsstrahlung and characteristic photons when energetic electrons interact with the anode target.", "easy"),
            ("Why does collimation improve a radiographic image and reduce exposure?", "It limits the irradiated field and reduces scatter reaching the detector", ["It increases the patient area exposed", "It changes X-rays into sound", "It removes all attenuation"], "Collimation reduces irradiated volume and scatter, improving contrast and limiting unnecessary exposure.", "easy"),
        ],
        [
            ("How does computed tomography reconstruct a cross-sectional image?", "Combine projection measurements acquired at multiple angles", ["Use one photograph without attenuation data", "Measure only body temperature", "Use magnetic resonance without gradients"], "CT reconstruction uses X-ray projections from many angles to estimate spatial attenuation within a slice or volume.", "easy"),
            ("What is a CT voxel value commonly related to?", "X-ray attenuation relative to a reference scale", ["The tissue's electrical potential", "The scanner's acoustic frequency", "A direct count of cells"], "CT values such as Hounsfield units represent reconstructed attenuation relative to water under defined calibration.", "intermediate"),
        ],
        [
            ("What physical property is measured in pulse-echo ultrasound imaging?", "Time and amplitude of reflected acoustic waves", ["The body's magnetic susceptibility", "X-ray attenuation only", "The tissue's electrical resistance"], "The system sends acoustic pulses and processes echoes to infer depth and acoustic impedance boundaries.", "easy"),
            ("Why does higher ultrasound frequency generally improve spatial resolution but reduce penetration depth?", "Attenuation typically increases with frequency", ["Higher frequency removes all scattering", "Sound travels infinitely fast in tissue", "Frequency changes tissue density"], "Higher frequency shortens wavelength but is attenuated more strongly in tissue, creating a resolution-penetration trade-off.", "intermediate"),
        ],
        [
            ("What is the main signal source for conventional proton MRI?", "Radiofrequency response of hydrogen nuclei in a magnetic field", ["X-ray fluorescence from calcium", "Reflected ultrasound from air", "Thermal radiation from tissue"], "MRI excites and receives signals from nuclear spins, most commonly hydrogen protons, using magnetic fields and RF coils.", "easy"),
            ("Why are magnetic-field gradients used in MRI?", "Encode spatial position into the received signal", ["Generate ionizing radiation", "Replace the main magnetic field", "Measure blood glucose directly"], "Gradient fields vary magnetic field with position, enabling spatial encoding during acquisition.", "easy"),
        ],
        [
            ("What does spatial resolution describe in a medical image?", "The ability to distinguish nearby structures", ["The scanner's purchase price", "The patient's heart rate", "The number of image colours only"], "Spatial resolution concerns separability of nearby features and depends on sampling, optics or reconstruction, motion, and noise.", "easy"),
            ("Why apply the ALARA principle in ionizing-radiation imaging?", "Keep exposure as low as reasonably achievable while obtaining needed diagnostic information", ["Use the highest dose for every scan", "Avoid justification of an imaging exam", "Eliminate image-quality considerations"], "Radiation protection balances justification and optimization so dose is minimized without compromising necessary clinical information.", "easy"),
        ],
    ],
    "BIOTECH02": [
        [
            ("Which interaction most directly stabilizes an alpha helix in a protein?", "Hydrogen bonds between backbone groups", ["Covalent bonds between every side chain", "Ionic bonds to the solvent only", "Phosphodiester bonds between amino acids"], "An alpha helix is stabilized primarily by hydrogen bonds between backbone carbonyl and amide groups.", "easy"),
            ("Why do hydrophobic amino-acid side chains often cluster inside a soluble globular protein?", "The hydrophobic effect favours exclusion from water", ["They form DNA base pairs", "They always carry a positive charge", "They increase solvent entropy by remaining exposed"], "Burial of nonpolar surface can reduce disruption of water structure; protein folding also reflects many other interactions.", "intermediate"),
        ],
        [
            ("In Michaelis-Menten kinetics, what does Km represent under the simplest model?", "The substrate concentration at half the maximum reaction rate", ["The enzyme concentration at zero rate", "The product concentration at equilibrium", "The maximum rate divided by temperature"], "For the basic Michaelis-Menten equation, rate equals half Vmax when substrate concentration equals Km.", "easy"),
            ("What is a competitive inhibitor's characteristic effect in the simple reversible model?", "It increases apparent Km without changing Vmax", ["It lowers Vmax and Km equally", "It increases Vmax without affecting Km", "It permanently destroys all substrate"], "A competitive inhibitor competes at the active site and can be overcome by high substrate in the ideal model.", "intermediate"),
        ],
        [
            ("What is the primary role of glycolysis?", "Convert glucose to pyruvate while producing ATP and reduced electron carriers", ["Synthesize DNA from amino acids", "Oxidize fatty acids inside the nucleus", "Convert oxygen directly into glucose"], "Glycolysis converts one glucose to pyruvate with net ATP and NADH production in the cytosol.", "easy"),
            ("Why is beta-oxidation important in lipid metabolism?", "It removes two-carbon units from fatty acids as acetyl-CoA", ["It polymerizes glucose into glycogen", "It converts amino acids directly into DNA", "It synthesizes triglycerides from water only"], "Beta-oxidation shortens fatty acyl-CoA and generates acetyl-CoA, NADH, and FADH2.", "easy"),
        ],
        [
            ("What is the role of ATP synthase in oxidative phosphorylation?", "Use a proton-motive force to synthesize ATP from ADP and phosphate", ["Hydrolyse DNA to release oxygen", "Pump glucose into the nucleus", "Convert carbon dioxide into amino acids directly"], "ATP synthase couples proton flow across a membrane to ATP synthesis.", "easy"),
            ("What happens to oxygen at the end of the mitochondrial electron-transport chain?", "It accepts electrons and protons to form water", ["It donates carbon atoms to glucose", "It becomes ATP directly", "It is converted into nitrogen gas"], "Molecular oxygen is the terminal electron acceptor in aerobic respiration and is reduced to water.", "easy"),
        ],
        [
            ("How can a single amino-acid substitution disrupt protein function?", "It can alter folding, stability, binding, or catalytic residues", ["It always deletes the entire chromosome", "It cannot affect a protein after translation", "It changes every amino acid in the cell"], "A substitution's effect depends on location and chemistry; it may be neutral or alter structure and function.", "easy"),
            ("Why can a protein domain be considered a useful unit of structure?", "It can form a relatively compact region with a recognizable structural or functional role", ["Every domain is exactly one amino acid", "Domains occur only in membrane lipids", "A domain has no relationship to protein folding"], "Many domains fold as semi-independent units and can contribute specific binding or catalytic functions.", "intermediate"),
        ],
    ],
    "BIOTECH03": [
        [
            ("In a monohybrid cross between two heterozygotes under complete dominance, what genotype ratio is expected?", "1:2:1", ["3:1", "9:3:3:1", "1:1"], "A heterozygote-by-heterozygote cross produces one homozygous dominant, two heterozygous, and one homozygous recessive genotype.", "easy"),
            ("When is a test cross useful in classical genetics?", "To infer an unknown dominant phenotype's genotype by crossing with a homozygous recessive", ["To sequence an entire genome", "To measure protein concentration", "To determine chromosome number from a karyotype only"], "Offspring phenotypes from a test cross can distinguish homozygous dominant from heterozygous parents under Mendelian assumptions.", "easy"),
        ],
        [
            ("What is the function of DNA polymerase during replication?", "Extend a new DNA strand using a template and nucleotide substrates", ["Join amino acids into a protein", "Remove every intron from RNA", "Translate codons at a ribosome"], "DNA polymerases synthesize DNA in the 5-prime to 3-prime direction using a template and primer.", "easy"),
            ("Why are mismatch-repair proteins important after DNA replication?", "They correct some incorrectly paired bases that escape polymerase proofreading", ["They initiate translation", "They synthesize the cell membrane", "They convert all DNA into RNA"], "Mismatch repair improves replication fidelity by recognizing and removing certain mispaired bases.", "easy"),
        ],
        [
            ("What is the role of RNA polymerase in transcription?", "Synthesize RNA from a DNA template", ["Synthesize proteins from amino acids", "Replicate the entire chromosome", "Degrade all messenger RNA"], "RNA polymerase reads a DNA template and forms an RNA transcript.", "easy"),
            ("What is the purpose of 5-prime capping on many eukaryotic mRNAs?", "Support mRNA stability, processing, and translation initiation", ["Mark the transcript for immediate DNA replication", "Remove the poly-A tail", "Convert uracil to thymine"], "The cap participates in protection from degradation and recruitment of processing and translation machinery.", "intermediate"),
        ],
        [
            ("What does a ribosome do during translation?", "Decode mRNA codons and catalyse peptide-bond formation", ["Copy DNA into DNA", "Splice genomic introns", "Generate a lipid bilayer"], "Ribosomes coordinate codon recognition by tRNAs with peptide synthesis.", "easy"),
            ("How can an operon regulate several bacterial genes together?", "A shared regulatory region controls transcription of a polycistronic RNA", ["Each gene must have a separate nucleus", "It edits proteins after secretion", "It prevents RNA polymerase from binding any DNA"], "An operon places related genes under shared transcriptional control, enabling coordinated expression.", "intermediate"),
        ],
        [
            ("What is a missense mutation?", "A nucleotide change that alters an encoded amino acid", ["A change that always removes an entire chromosome", "A substitution that creates no DNA change", "A mutation confined to a lipid"], "A missense variant changes a codon so that a different amino acid is incorporated.", "easy"),
            ("Why can recombination increase genetic variation in a population?", "It creates new combinations of alleles", ["It makes all offspring genetically identical", "It prevents segregation", "It removes every mutation"], "Crossing over and independent assortment create new allele combinations in gametes.", "easy"),
        ],
    ],
    "BIOTECH04": [
        [
            ("What is the main function of a bacterial cell wall?", "Provide structural support and resist osmotic pressure", ["Store the bacterial chromosome outside the cell", "Synthesize ATP only in every bacterium", "Perform mitosis with a spindle"], "The bacterial wall helps maintain shape and prevent osmotic lysis; composition varies among groups.", "easy"),
            ("Why are bacterial ribosomes targeted by some antibiotics?", "They differ sufficiently from eukaryotic cytosolic ribosomes for selective inhibition", ["Bacteria do not make proteins", "Human cells have no ribosomes", "Ribosomes are part of the cell wall"], "Differences in bacterial and eukaryotic ribosomes enable selective drug targets, though toxicity and resistance remain concerns.", "intermediate"),
        ],
        [
            ("During which growth phase does a well-inoculated bacterial culture often show its highest specific growth rate under stable conditions?", "Exponential phase", ["Lag phase", "Stationary phase", "Death phase"], "In exponential phase, cells divide at a relatively constant maximal rate under the given conditions.", "easy"),
            ("Why can a chemostat maintain cells in a steady growth state?", "Fresh medium enters while culture leaves at a controlled dilution rate", ["It prevents nutrients from entering", "It removes all cells continuously", "It has no defined volume"], "A chemostat balances feed and outflow; dilution rate and limiting nutrient influence steady-state growth.", "intermediate"),
        ],
        [
            ("What is a plasmid in many bacteria?", "An extrachromosomal DNA molecule that can replicate independently", ["A ribosomal protein", "A membrane lipid", "A viral capsid in every cell"], "Plasmids are typically separate replicons and can carry accessory genes, though their biology varies.", "easy"),
            ("Why use a selectable marker in a cloning experiment?", "Identify cells that likely received the vector under the selection conditions", ["Guarantee the insert sequence is correct", "Replace DNA ligase", "Measure cell size directly"], "A selectable marker enriches for transformants, but insert presence and sequence still require verification.", "intermediate"),
        ],
        [
            ("What is a common first-line physical barrier against infection in the human body?", "Intact skin and mucosal surfaces", ["Antibodies in every cell nucleus", "Platelets that digest all viruses", "Bone mineral only"], "Skin and mucosal surfaces provide physical and chemical barriers before adaptive immune responses are engaged.", "easy"),
            ("Why can bacterial endotoxin trigger a strong inflammatory response?", "Lipopolysaccharide can activate innate immune receptors", ["It is a human antibody", "It blocks all cytokine signalling", "It is a plant chlorophyll molecule"], "LPS from Gram-negative bacteria is detected by innate immune pathways and can promote inflammatory signalling.", "intermediate"),
        ],
        [
            ("Why is sterilization validation important for a reusable laboratory or production item?", "It provides evidence that the defined process achieves the required microbial reduction", ["It guarantees every possible process is identical", "It replaces cleaning", "It makes packaging unnecessary"], "Validation demonstrates that the specified sterilization cycle works for the load and configuration; cleaning and handling remain important.", "easy"),
            ("What does antimicrobial resistance mean?", "A microorganism can survive or grow despite a drug concentration that would inhibit a susceptible strain", ["Every antibiotic is ineffective against every organism", "A host becomes immune to all medicines", "A bacterium has lost its genome"], "Resistance is a microbial trait that reduces susceptibility and can spread through mutation or gene transfer.", "easy"),
        ],
    ],
    "BIOTECH05": [
        [
            ("For a process stream, what does a steady-state material balance imply when there is no reaction or accumulation?", "Total mass flow in equals total mass flow out", ["Energy flow must be zero", "Every component has the same mass fraction", "The stream has no volume"], "At steady state without reaction, accumulation is zero and total mass conservation requires inlet and outlet flow to balance.", "easy"),
            ("Why include biomass and substrate consumption in a bioreactor material balance?", "They determine growth yield and remaining nutrient concentrations", ["They set the reactor's colour", "They replace the energy balance", "They make volume irrelevant"], "Biomass, substrate, and product balances help quantify conversion, yield, and process performance.", "easy"),
        ],
        [
            ("Why is a stirred-tank bioreactor commonly equipped with an impeller?", "Mixing improves bulk homogeneity and gas-liquid mass transfer", ["It sterilizes the feed by itself", "It removes the need for sensors", "It fixes the organism's genotype"], "Agitation supports mixing and transfer, but speed must balance oxygen transfer, shear, and energy input.", "easy"),
            ("What is a typical advantage of a packed-bed bioreactor with immobilized cells?", "High cell retention and potentially high volumetric productivity", ["No pressure drop ever occurs", "Cells cannot be damaged", "It requires no flow control"], "Immobilized biomass can reach high retention, while diffusion limits, clogging, and pressure drop may constrain operation.", "intermediate"),
        ],
        [
            ("Why validate an autoclave cycle with indicators and load-specific procedures?", "Steam penetration and microbial lethality depend on the load and arrangement", ["All loads heat identically", "Indicators set the process temperature", "Validation removes the need for records"], "Sterilization effectiveness depends on time, temperature, steam quality, packaging, and load configuration.", "intermediate"),
            ("What is aseptic technique intended to prevent during sterile bioprocess operation?", "Introduction of unwanted microorganisms into the process", ["Any oxygen transfer", "The target organism from growing", "Nutrient consumption"], "Aseptic operation protects the process from contaminating organisms through validated barriers and procedures.", "easy"),
        ],
        [
            ("Why can oxygen transfer become a limiting factor during scale-up of an aerobic fermentation?", "Gas-liquid transfer does not necessarily increase in proportion to vessel volume", ["Oxygen has no solubility in water", "Microbes stop consuming oxygen at scale", "Impeller speed has no effect on transfer"], "Scale-up changes geometry, power input, mixing time, and interfacial area, so oxygen-transfer capacity may not keep pace with demand.", "intermediate"),
            ("What does the volumetric oxygen-transfer coefficient kLa combine?", "A liquid-side transfer coefficient and gas-liquid interfacial area per volume", ["The organism's DNA length and cell count", "The feed pH and temperature only", "The vessel height and product colour"], "kLa represents volumetric gas-liquid mass-transfer capacity and depends on fluid, gas, agitation, and geometry.", "intermediate"),
        ],
        [
            ("Why is centrifugation commonly used in downstream processing?", "Separate suspended cells or particles from a liquid by density and centrifugal force", ["Sequence the product DNA", "Change protein primary structure", "Sterilize every dissolved impurity"], "Centrifugation separates particles from fluid based on sedimentation behaviour; it does not remove dissolved contaminants by itself.", "easy"),
            ("What is a common purpose of chromatography in product purification?", "Separate molecules based on differences in interactions with stationary and mobile phases", ["Increase reactor oxygen transfer", "Measure tractor field capacity", "Eliminate the need for quality control"], "Chromatographic methods exploit binding, size, charge, or hydrophobicity differences to separate target molecules from impurities.", "easy"),
        ],
    ],
    "CERAMIC01": [
        [
            ("Why are ionic and covalent bonds common in many engineering ceramics?", "They provide strong atomic bonding and high-temperature stability", ["They make every ceramic electrically conductive", "They eliminate all defects", "They prevent crystal formation"], "Strong directional or ionic bonding contributes to ceramics' stiffness, high melting temperatures, and often brittle behaviour.", "easy"),
            ("What is a coordination number in a crystal structure?", "The number of nearest neighbouring atoms or ions around a reference site", ["The number of phases in a phase diagram", "The grain size in micrometres", "The number of furnace cycles"], "Coordination number describes local neighbour geometry and depends on crystal structure and ionic size ratios.", "easy"),
        ],
        [
            ("What does a phase diagram show at equilibrium?", "Stable phases as functions of variables such as temperature and composition", ["The exact crack path in every specimen", "The production cost at each furnace speed", "The colour of a powder before mixing"], "Equilibrium phase diagrams map phase stability under defined thermodynamic conditions.", "easy"),
            ("What does the lever rule estimate in a two-phase region of a binary diagram?", "The relative amounts of the coexisting phases", ["The grain-boundary angle", "The heating rate", "The pore-size distribution"], "The lever rule uses tie-line endpoints and overall composition to estimate equilibrium phase fractions.", "intermediate"),
        ],
        [
            ("Why is a narrow powder particle-size distribution useful in some ceramic forming processes?", "It can improve packing consistency and reduce variability in green density", ["It guarantees zero porosity after firing", "It removes the need for a binder", "It changes the ceramic's chemical formula"], "Particle-size distribution affects packing and flow, though ideal breadth depends on the forming process and powder shape.", "intermediate"),
            ("What is agglomeration in a ceramic powder?", "Clustering of smaller particles into larger secondary groups", ["A phase transformation to liquid", "The growth of a finished component", "A method for measuring dielectric constant"], "Agglomerates can affect flow, packing, and defect formation unless controlled during powder processing.", "easy"),
        ],
        [
            ("What is the main driving force for sintering a compacted ceramic powder?", "Reduction of surface energy through neck growth and densification", ["Creation of additional free surface", "Increase of every pore's volume", "A change in gravity"], "Sintering lowers system surface energy as particles bond and pores shrink, driven by diffusion and other transport mechanisms.", "intermediate"),
            ("Why can excessive grain growth during sintering be undesirable?", "It can reduce properties or trap pores and create microstructural nonuniformity", ["It always raises toughness", "It eliminates the need for densification", "It prevents diffusion"], "Grain growth can proceed faster than densification under some conditions and may degrade strength or reliability.", "intermediate"),
        ],
        [
            ("Why do many ceramics show low tensile ductility at room temperature?", "Limited dislocation motion and sensitivity to flaws promote brittle fracture", ["They contain no chemical bonds", "They flow like viscous liquids", "Their elastic modulus is always zero"], "Strong bonding and limited plastic deformation make many ceramics flaw-sensitive and brittle under tensile loading.", "easy"),
            ("What does thermal-shock resistance depend on besides thermal expansion?", "Thermal conductivity, elastic modulus, strength, geometry, and heat-transfer conditions", ["Only the component's colour", "Only the room's humidity", "The number of ceramic phases without properties"], "Thermal gradients create stress; conductivity, expansion, stiffness, strength, geometry, and heat-transfer rate all influence resistance.", "intermediate"),
        ],
    ],
    "CERAMIC02": [
        [
            ("Why remove oversized contaminants from ceramic raw materials before milling?", "They can damage equipment and create defects in the final body", ["They improve batch homogeneity automatically", "They increase glaze colour accuracy", "They prevent powder handling"], "Screening and inspection reduce tramp material that can impair equipment and product quality.", "easy"),
            ("What is a purpose of blending ceramic powders before forming?", "Achieve a more uniform composition and distribution of additives", ["Create uncontrolled segregation", "Eliminate all moisture measurements", "Increase particle size without limit"], "Mixing helps distribute constituents and additives so the formed body has more consistent properties.", "easy"),
        ],
        [
            ("What is slip casting based on?", "A ceramic suspension drains or deposits solids against a porous mould", ["Metal is injected into a heated die", "A yarn is twisted into a fibre", "A glass sheet is stretched by rollers only"], "In slip casting, mould suction or filtration removes liquid and builds a shaped ceramic layer.", "easy"),
            ("Why is binder burnout controlled during ceramic firing?", "Rapid gas evolution can cause cracks, blisters, or internal defects", ["The binder becomes the main crystal phase", "It eliminates the need for sintering", "It increases the green body's water content"], "Heating rate and atmosphere during organic removal must limit pressure buildup and damage to the compact.", "intermediate"),
        ],
        [
            ("Why dry a formed ceramic body gradually when moisture gradients are possible?", "Uneven shrinkage can create stresses and cracking", ["Drying always expands every region equally", "It makes capillary pressure zero", "It prevents later phase formation"], "Moisture gradients produce differential shrinkage and tensile stresses that can crack a green body.", "easy"),
            ("What does a firing schedule control in ceramic processing?", "Temperature, time, and atmosphere through drying, reactions, and densification", ["Only the product's shipping route", "The powder's original mine location", "The final inspection staff count"], "A firing cycle controls heat-up, hold, and cooling conditions that govern reactions, shrinkage, microstructure, and defects.", "easy"),
        ],
        [
            ("What is one purpose of a ceramic glaze?", "Create a glassy surface layer that can improve appearance and surface properties", ["Turn the body into a metal", "Replace all body firing", "Prevent any thermal expansion"], "Glazes can provide a sealed or decorative surface and modify chemical and wear behaviour, subject to fit and firing.", "easy"),
            ("Why should glaze thermal expansion be matched reasonably to the ceramic body?", "Mismatch can create residual stress, crazing, or shivering", ["It changes the body's atomic number", "It guarantees the glaze is transparent", "It prevents glaze melting"], "Expansion mismatch during cooling can place the glaze in tension or compression and cause defects.", "intermediate"),
        ],
        [
            ("A fired ceramic tile shows warpage. Which process issue is a plausible contributor?", "Nonuniform drying or firing shrinkage", ["Uniform temperature and shrinkage everywhere", "A perfectly symmetric support", "A change in the product label"], "Differential moisture loss, temperature, density, or support can cause nonuniform shrinkage and warpage.", "easy"),
            ("Why use statistical process monitoring for ceramic firing?", "Detect drift in cycle conditions before it produces a large defect batch", ["Guarantee that no defect can ever occur", "Replace furnace calibration", "Remove the need to record kiln loads"], "Control charts and process records can reveal variation in temperature profile, atmosphere, and product response.", "intermediate"),
        ],
    ],
    "CERAMIC03": [
        [
            ("What property makes a refractory suitable for high-temperature furnace lining?", "Ability to maintain required chemical and mechanical performance at service temperature", ["Ability to melt below room temperature", "Maximum electrical conductivity in every case", "Zero resistance to slag"], "Refractory selection depends on service temperature, load, atmosphere, and chemical exposure rather than a single property.", "easy"),
            ("Why is thermal conductivity considered when choosing a furnace refractory?", "It affects heat loss, lining temperature gradients, and energy use", ["It sets the furnace's fuel chemistry", "It determines the steel's carbon content directly", "It replaces mechanical strength"], "Thermal conductivity influences insulation performance and temperature distribution through the lining.", "easy"),
        ],
        [
            ("Why can basic and acidic refractories react with incompatible slags?", "Their oxide chemistries can form lower-melting reaction products", ["Slag has no chemical composition", "All refractories are chemically identical", "Only room humidity causes corrosion"], "Chemical compatibility is crucial; reactions with slag can dissolve or weaken the lining.", "intermediate"),
            ("What does slag basicity indicate in a simplified oxide ratio?", "The relative amount of basic oxides compared with acidic oxides", ["The refractory's grain size", "The furnace's rotation speed", "The glass's annealing time"], "Basicity is an empirical descriptor, often based on oxide ratios, used to assess slag-refractory compatibility.", "easy"),
        ],
        [
            ("What is annealing in glass forming intended to do?", "Relieve internal stresses by controlled cooling through the strain range", ["Rapidly quench the glass to maximum residual stress", "Increase the glass's carbon content", "Create a metallic grain structure"], "Annealing allows stresses to relax through a controlled temperature-time schedule.", "easy"),
            ("Why is the glass transition range important during cooling?", "Viscosity changes rapidly and stress relaxation becomes progressively slower", ["The glass turns into a gas", "Density becomes zero", "Crystallization is guaranteed"], "Near the glass transition, viscosity rises and stress relaxation times increase, so cooling rate affects residual stress.", "intermediate"),
        ],
        [
            ("Why is a refractory lining vulnerable to thermal shock during rapid cycling?", "Temperature gradients create transient stresses that can exceed its strength", ["Uniform temperatures create no strain", "Thermal expansion is always zero", "The refractory becomes infinitely ductile"], "Rapid heating or cooling creates gradients and stress, with resistance depending on material properties and geometry.", "easy"),
            ("How can adding a suitable aggregate or microstructure improve thermal-shock tolerance?", "It may deflect cracks or reduce effective stiffness and stress concentration", ["It makes thermal gradients impossible", "It guarantees zero porosity", "It removes the need for expansion joints"], "Microstructure and composite design can improve crack resistance, though they must also meet chemical and load requirements.", "intermediate"),
        ],
        [
            ("Why are refractory bricks arranged with joints and expansion allowances?", "Accommodate thermal expansion and reduce uncontrolled cracking", ["Increase slag infiltration deliberately", "Make every brick carry zero load", "Prevent all furnace heat transfer"], "Joints and expansion provisions accommodate movement and help manage stress in a hot lining.", "easy"),
            ("When assessing a glass or refractory process, why measure both temperature uniformity and residence time?", "Product transformations and properties depend on the full thermal history", ["Only the furnace colour matters", "Residence time always equals material density", "Uniformity is unrelated to quality"], "Thermal history influences viscosity, reactions, annealing, and final properties across the product.", "easy"),
        ],
    ],
    "CERAMIC04": [
        [
            ("Why are silicon nitride and silicon carbide considered for some structural ceramic components?", "They can retain useful strength and wear performance at elevated temperatures", ["They are always ductile at room temperature", "They dissolve in every coolant", "They have no covalent bonding"], "These ceramics can provide high-temperature strength and wear resistance, though fracture toughness and processing remain design concerns.", "easy"),
            ("Why is fracture toughness important in structural ceramics?", "It indicates resistance to crack extension under stress", ["It measures electrical capacitance only", "It is the same as density", "It eliminates flaw sensitivity"], "Fracture toughness characterizes resistance to crack growth; ceramics remain sensitive to flaw size and distribution.", "easy"),
        ],
        [
            ("What property makes barium titanate useful in some electronic ceramics?", "High dielectric permittivity with field- and temperature-dependent behaviour", ["Perfect optical transparency in every form", "Zero polarization", "High fuel value"], "Ferroelectric barium titanate is used in capacitors because of its dielectric response, which depends on composition and conditions.", "intermediate"),
            ("What does a piezoelectric ceramic do under mechanical stress?", "Develop an electrical polarization or voltage", ["Produce a magnetic field only", "Melt at room temperature", "Convert all stress directly into heat"], "Piezoelectric materials couple mechanical deformation and electrical polarization; the converse effect also occurs.", "easy"),
        ],
        [
            ("Why is hydroxyapatite considered for some bone-contact applications?", "Its chemistry resembles the mineral component of bone and can support bioactivity", ["It is a flexible elastomer", "It is used only as a battery electrolyte", "It prevents all tissue attachment"], "Hydroxyapatite can support bone bonding, but brittleness and application-specific performance must be considered.", "easy"),
            ("Why combine a bioceramic coating with a metallic implant substrate?", "Gain a bioactive surface while retaining structural support from the metal", ["Remove all interface stresses", "Make the implant biodegradable instantly", "Eliminate the need for coating adhesion tests"], "A coating can provide surface bioactivity, but adhesion, wear, fatigue, and dissolution require assessment.", "intermediate"),
        ],
        [
            ("What is a common role of fibres in a ceramic-matrix composite?", "Bridge or deflect cracks and improve damage tolerance", ["Make the matrix completely liquid", "Remove all thermal gradients", "Eliminate the need for interface design"], "Fibre reinforcement can improve toughness through bridging and deflection, with behaviour depending on the interface and architecture.", "easy"),
            ("Why control the fibre-matrix interface in a ceramic composite?", "Load transfer and crack deflection depend on interface bonding", ["The interface has no mechanical effect", "It sets the component's paint colour", "It converts ceramic into glass automatically"], "An interface that is too weak or too strong can impair load transfer or toughness; the target depends on composite design.", "intermediate"),
        ],
        [
            ("What does X-ray diffraction help identify in a ceramic specimen?", "Crystalline phases and lattice-related diffraction patterns", ["The exact fracture toughness without testing", "The specimen's electrical wiring", "The furnace's fuel flow directly"], "XRD patterns support phase identification and structural analysis; quantitative results depend on preparation and method.", "easy"),
            ("Why examine a ceramic fracture surface using microscopy?", "Identify origins, pores, inclusions, or other features associated with failure", ["Measure the sample's pH exactly", "Determine all service loads without records", "Prove there were no manufacturing defects"], "Fractography can reveal likely origins and mechanisms but should be interpreted with loading and processing evidence.", "intermediate"),
        ],
    ],
    "CHE02": [
        [
            ("In a static fluid, how does pressure change with depth?", "It increases with depth according to fluid density and gravity", ["It decreases linearly with viscosity only", "It is independent of elevation", "It becomes zero below the surface"], "Hydrostatic pressure variation follows dp/dz=-rho g for a fluid at rest under the stated coordinate convention.", "easy"),
            ("Why use dimensional analysis before designing a scale-up experiment?", "It identifies dimensionless groups that organize the governing variables", ["It replaces conservation laws", "It proves geometric similarity alone is sufficient", "It removes every empirical coefficient"], "Buckingham Pi analysis reduces variables to dimensionless groups, helping identify similarity requirements and useful correlations.", "intermediate"),
        ],
        [
            ("What does the continuity equation express for steady incompressible flow through a pipe?", "Volumetric flow rate is conserved along the flow path without leakage", ["Pressure is constant at every point", "Temperature must be zero", "Viscosity is infinite"], "Mass conservation with constant density gives Q=A v constant for steady incompressible flow.", "easy"),
            ("What does a control-volume momentum balance help calculate in a pipe bend?", "Resultant force associated with changes in momentum and pressure forces", ["The chemical formula of the fluid", "The pipe's colour", "The fluid's boiling point only"], "Momentum balance relates external forces to momentum-flux changes across the control-volume boundary.", "intermediate"),
        ],
        [
            ("For fully developed laminar flow in a circular pipe, how does pressure drop scale with volumetric flow rate?", "Directly proportional to flow rate", ["Inversely proportional to flow rate squared", "Independent of pipe radius and flow", "Directly proportional to the square root of density only"], "Hagen–Poiseuille flow gives a linear pressure-drop relation with flow rate under Newtonian, laminar, fully developed assumptions.", "intermediate"),
            ("Why are local losses included in a pipe-network pressure balance?", "Fittings, valves, and entrances dissipate mechanical energy", ["They create energy from nothing", "They eliminate wall friction", "They change the fluid into a solid"], "Bends, valves, expansions, and other fittings create additional losses beyond straight-pipe friction.", "easy"),
        ],
        [
            ("What does a pump's shutoff head refer to?", "The head developed at zero flow under the specified test condition", ["The maximum flow at zero head", "The total pipe length", "The fluid's vapour pressure"], "Shutoff head is the pump head at zero discharge; operating away from this point depends on the system curve.", "easy"),
            ("Why is a Venturi meter often chosen over a sharp-edged orifice for lower permanent pressure loss?", "Its gradual geometry reduces separation and energy dissipation", ["It has no pressure drop at all", "It measures temperature without flow", "It requires zero calibration"], "The gradual converging-diverging passage typically has lower permanent loss, while both devices infer flow from a pressure difference.", "intermediate"),
        ],
        [
            ("What is fluidization in a packed bed?", "A condition where upward fluid drag supports particles and the bed behaves like a fluid", ["A process that freezes every particle", "A condition with no flow through the bed", "A solid-state phase transformation"], "At minimum fluidization, drag balances effective particle weight and the bed begins to expand and move.", "easy"),
            ("Why can pressure drop level off near minimum fluidization as gas flow increases?", "The bed expands so additional drag is balanced by increased void space and particle motion", ["The gas flow becomes zero", "The particles become weightless", "The bed loses all porosity"], "In a fluidized regime, pressure drop is approximately related to bed weight per area, while the bed expands with higher flow.", "intermediate"),
        ],
    ],
    "CHE03": [
        [
            ("For one-dimensional steady conduction through a plane wall, what does Fourier's law relate?", "Heat flux to thermal conductivity and temperature gradient", ["Mass flux to concentration only", "Pressure drop to pipe diameter", "Reaction rate to catalyst area"], "Fourier's law describes conductive heat flux proportional to the negative temperature gradient.", "easy"),
            ("What is thermal resistance for a plane wall of thickness L and area A?", "L divided by kA", ["kL divided by A", "A divided by kL", "L times A times k"], "For steady one-dimensional conduction through a uniform wall, R=L/(kA), assuming the stated geometry and properties.", "intermediate"),
        ],
        [
            ("What is the purpose of a Nusselt-number correlation in convection analysis?", "Estimate convective heat transfer using dimensionless flow and geometry groups", ["Determine molecular weight directly", "Replace the energy balance", "Measure surface roughness without flow data"], "Nusselt correlations relate convection to Reynolds, Prandtl, and geometry-dependent conditions.", "easy"),
            ("Why must the flow regime and geometry match a convection correlation's validity range?", "The empirical relation depends on the conditions under which it was developed", ["All correlations are universal", "Heat transfer is independent of flow", "The correlation sets the fluid's chemical identity"], "Using a correlation outside its regime or geometry can produce unreliable heat-transfer estimates.", "intermediate"),
        ],
        [
            ("What does emissivity compare for a real surface?", "Its emitted thermal radiation with that of a blackbody at the same temperature", ["Its density with water", "Its heat capacity with latent heat", "Its reflectivity with its thickness only"], "Emissivity is a surface radiation property relative to a blackbody under specified spectral and directional conditions.", "easy"),
            ("Why do radiation heat-transfer calculations often use absolute temperature to the fourth power?", "Blackbody emissive power follows the Stefan-Boltzmann relation", ["Conduction follows a fourth-power law", "Temperature in Celsius has an absolute zero at freezing", "Convection is always proportional to T to the fourth"], "The Stefan-Boltzmann law uses absolute temperature; net exchange also depends on emissivity and view factors.", "intermediate"),
        ],
        [
            ("For a counter-current heat exchanger, why is the log-mean temperature difference used?", "It represents the changing local temperature driving force along the exchanger", ["It assumes zero heat transfer", "It measures only pressure drop", "It ignores inlet and outlet temperatures"], "The LMTD integrates the varying terminal temperature differences under steady exchanger assumptions.", "easy"),
            ("What does the overall heat-transfer coefficient account for?", "Combined thermal resistances on both sides and through the separating wall", ["Only the fluid density", "The chemical reaction equilibrium", "The exchanger's purchase cost"], "U combines convection, wall conduction, and fouling resistances on a defined area basis.", "intermediate"),
        ],
        [
            ("During nucleate boiling, what role do bubbles at the heated surface play?", "They promote mixing and high heat-transfer rates before critical heat flux", ["They prevent all liquid contact", "They lower wall temperature below saturation automatically", "They eliminate latent heat"], "Nucleate boiling can yield high heat transfer, but excessive heat flux may approach a transition to film boiling.", "intermediate"),
            ("Why can film boiling reduce heat-transfer coefficient compared with nucleate boiling?", "A vapour layer can insulate the surface from the liquid", ["The liquid becomes a perfect conductor", "Latent heat becomes infinite", "The surface stops receiving energy"], "A stable vapour film adds thermal resistance and can lower heat transfer despite high wall temperature.", "intermediate"),
        ],
    ],
    "CHE04": [
        [
            ("According to Fick's first law, what drives molecular diffusion in a binary mixture?", "A concentration gradient", ["A pressure gradient only in every system", "The vessel's colour", "A temperature gradient only"], "Fick's law relates diffusive flux to the negative concentration gradient for a simple formulation.", "easy"),
            ("What does a mass-transfer coefficient relate in a film model?", "Flux to a concentration driving force", ["Heat flux to a temperature gradient", "Pressure to vessel volume", "Reaction enthalpy to catalyst colour"], "A film coefficient expresses flux proportional to the concentration difference across a defined transfer resistance.", "easy"),
        ],
        [
            ("What is the purpose of an equilibrium-stage model?", "Represent contact where exiting phases are assumed to reach equilibrium", ["Assume no mass transfer occurs", "Model only chemical reaction kinetics", "Set every stage temperature to zero"], "An ideal equilibrium stage simplifies separation analysis by assuming phases leaving the stage are in equilibrium.", "easy"),
            ("Why may the number of actual trays exceed the theoretical stage count?", "Real contacting does not reach equilibrium on each tray", ["Actual trays have no liquid", "Equilibrium stages violate mass conservation", "The feed rate is always zero"], "Tray efficiency accounts for nonideal mass transfer and mixing; actual hardware needs more stages than the ideal count.", "intermediate"),
        ],
        [
            ("In distillation, what does relative volatility indicate?", "How readily one component separates from another through vapour-liquid equilibrium", ["The liquid's viscosity compared with water only", "The column's mechanical vibration", "The mass of the reboiler"], "Relative volatility compares component equilibrium ratios and is a measure of separation difficulty under the stated conditions.", "easy"),
            ("Why does increasing reflux ratio often increase distillation separation at a fixed stage count?", "It increases internal liquid-vapour contacting and separation driving capacity", ["It removes all stages", "It eliminates reboiler duty", "It makes the feed composition irrelevant"], "More reflux can improve separation for a given stage count but increases energy use and has diminishing returns.", "intermediate"),
        ],
        [
            ("In gas absorption, what is the role of a solvent?", "Transfer a soluble gas component from the gas phase into the liquid", ["Supply the gas feed's mechanical power", "Prevent interfacial contact", "Convert all gases into solids"], "Absorption uses a liquid solvent to remove a solute from a gas stream by interphase mass transfer.", "easy"),
            ("Why is solvent regeneration often included after gas absorption?", "Recover or reuse solvent and release the absorbed solute", ["Increase solvent contamination", "Prevent all heat transfer", "Remove the absorber from the process"], "Regeneration reverses or shifts the equilibrium to recover solvent and concentrate the separated solute.", "easy"),
        ],
        [
            ("What is the basic idea behind liquid-liquid extraction?", "A solute distributes between two immiscible liquid phases", ["A solid dissolves in a gas only", "A membrane filters by molecular weight alone", "The solvent remains in one phase with no solute"], "Extraction relies on partitioning of a solute between immiscible liquid phases, followed by phase separation.", "easy"),
            ("Why can drying rate fall during the falling-rate period?", "Internal moisture diffusion or bound-water movement becomes limiting", ["The material has no moisture left at the start", "The air stops flowing by definition", "The surface temperature is always zero"], "As free surface moisture is depleted, internal transport and binding can limit evaporation rate.", "intermediate"),
        ],
    ],
    "CHE05": [
        [
            ("For a first-order reaction, how does rate depend on reactant concentration?", "Directly proportional to concentration", ["Independent of concentration", "Proportional to concentration squared", "Inversely proportional to temperature only"], "A first-order rate law has rate proportional to the first power of the reactant concentration under the model.", "easy"),
            ("What does an Arrhenius plot of ln(k) versus reciprocal absolute temperature estimate from its slope?", "Activation energy divided by the negative gas constant", ["The reactor volume", "The equilibrium conversion", "The catalyst particle density"], "For k=A exp(-Ea/RT), ln(k) versus 1/T has slope -Ea/R.", "intermediate"),
        ],
        [
            ("In a batch reactor, how does composition change with time?", "The contents react without continuous feed or product withdrawal during the reaction period", ["The reactor has no accumulation", "Only the feed composition changes", "The reactor must operate at steady state"], "A batch reactor is unsteady and closed to material flow during the reaction interval, aside from any stated additions or removals.", "easy"),
            ("What is a characteristic feature of a well-mixed continuous stirred-tank reactor?", "The reactor contents are at the same composition as the outlet", ["There is no mixing", "The outlet never leaves", "The concentration changes along a plug-flow path"], "For an ideal CSTR, complete mixing makes reactor contents and outlet composition equal.", "easy"),
        ],
        [
            ("For a constant-volume batch reactor, what is the design relation between time and conversion?", "It follows from integrating the rate law with concentration expressed as conversion", ["It is independent of kinetics", "It equals the pipe pressure drop", "It requires no initial concentration"], "Batch design integrates species accumulation with the kinetic rate over the desired conversion range.", "intermediate"),
            ("For a first-order reaction in an ideal plug-flow reactor, what does increasing residence time generally do?", "Increase conversion toward completion", ["Decrease conversion to zero", "Make the rate constant negative", "Remove the reactant before entering"], "At fixed kinetics and conditions, longer residence time permits more reaction and higher conversion for a first-order PFR.", "easy"),
        ],
        [
            ("Why can an exothermic reactor develop a hot spot?", "Heat generation can locally exceed heat removal", ["Reactants absorb no heat", "The reaction rate is zero at all temperatures", "The vessel has no energy balance"], "Temperature-dependent kinetics and nonuniform heat transfer can create local heat-generation maxima.", "intermediate"),
            ("What is one reason to use staged cooling or quench between exothermic reactor beds?", "Limit temperature rise and maintain selectivity or catalyst stability", ["Increase the reactor's pressure drop without control", "Remove all products permanently", "Make the reaction endothermic"], "Interstage cooling controls temperature and can protect selectivity, catalyst, and equipment.", "easy"),
        ],
        [
            ("What does a catalyst do to a reaction pathway?", "Provide an alternative pathway with a different activation barrier", ["Change the reaction's equilibrium constant", "Change the overall stoichiometry", "Get consumed in every catalytic cycle"], "A catalyst changes kinetics by offering another pathway and is regenerated overall; it does not change equilibrium for fixed conditions.", "easy"),
            ("Why can a broad residence-time distribution affect conversion in a nonideal reactor?", "Some material exits earlier or later than the ideal mean residence time", ["All molecules have identical histories", "It changes the feed's molecular formula", "It removes the rate law"], "Real flow nonideality gives fluid elements different contact times, affecting conversion relative to ideal reactor models.", "intermediate"),
        ],
    ],
    "DAIRY01": [
        [
            ("Why is milk described as an oil-in-water emulsion as well as a colloidal system?", "Fat globules are dispersed in an aqueous phase with proteins and minerals", ["Water droplets are dispersed in a continuous fat phase only", "Milk contains no dissolved substances", "The phases are chemically identical"], "Milk is a complex dispersion with fat globules, casein micelles, and dissolved constituents in an aqueous continuous phase.", "easy"),
            ("Why does milk density change with fat content?", "Fat and serum have different densities, so composition affects the mixture density", ["Fat has the same density as water under all conditions", "Density depends only on the container shape", "Fat changes the gravitational constant"], "Milk composition, temperature, and entrained air influence measured density; fat generally has lower density than skim serum.", "easy"),
        ],
        [
            ("What is casein in milk?", "A family of phosphoproteins that associate into micelles", ["A milk sugar", "A triglyceride only", "A vitamin dissolved in the fat phase"], "Caseins form colloidal micelles with calcium phosphate and are major milk proteins.", "easy"),
            ("Why can acidification cause casein coagulation near its isoelectric region?", "Electrostatic repulsion decreases and micelles aggregate", ["The proteins become carbohydrates", "Fat globules dissolve into water", "Lactose crystallizes into DNA"], "Near casein's isoelectric region, reduced charge repulsion promotes aggregation and precipitation.", "intermediate"),
        ],
        [
            ("What does homogenization do to milk fat globules?", "Reduces their size and helps limit creaming", ["Removes all fat", "Converts fat into lactose", "Sterilizes milk by itself"], "Homogenization disrupts fat globules into smaller droplets with altered surface coverage, reducing creaming.", "easy"),
            ("Why can fat oxidation produce rancid flavours in dairy products?", "Oxidation forms compounds with undesirable odours and tastes", ["It converts all proteins into starch", "It removes dissolved oxygen permanently", "It increases lactose sweetness without by-products"], "Lipid oxidation can create aldehydes, ketones, and other compounds associated with rancid notes.", "intermediate"),
        ],
        [
            ("What is lactose?", "The principal disaccharide sugar in milk", ["A casein micelle", "A fatty acid", "A mineral salt"], "Lactose is a glucose-galactose disaccharide and the major carbohydrate in milk.", "easy"),
            ("Why can calcium and phosphate balance affect dairy processing behaviour?", "They influence protein-micelle stability and mineral equilibria", ["They determine the animal's species directly", "They replace heat treatment", "They remove water from milk"], "Mineral equilibria influence casein micelles, gelation, heat stability, and processing response.", "intermediate"),
        ],
        [
            ("Why can heat treatment change milk protein functionality?", "Heating can denature whey proteins and alter their interactions", ["Proteins are immune to temperature", "Heat converts all protein into lactose", "It removes every mineral"], "Whey-protein denaturation and interactions with casein can alter viscosity, gelation, and heat stability.", "easy"),
            ("What is the purpose of monitoring oxidation-reduction conditions during dairy processing?", "Redox state can influence flavour stability and chemical changes", ["It sets packaging dimensions", "It determines milk's atomic number", "It replaces microbial testing"], "Oxygen and redox conditions can affect lipid oxidation, vitamins, pigments, and flavour quality.", "intermediate"),
        ],
    ],
    "DAIRY02": [
        [
            ("Why is raw milk rapidly cooled after reception at a processing plant?", "Lower temperature slows microbial growth before further processing", ["It increases microbial growth", "It removes all dissolved minerals", "It homogenizes fat automatically"], "Rapid cooling limits microbial multiplication and quality deterioration before processing.", "easy"),
            ("What does clarification remove from incoming milk?", "Some suspended physical impurities", ["All lactose molecules", "All dissolved salts", "Every microorganism under all conditions"], "Clarification removes sediment and other particulates but is not a sterilization step.", "easy"),
        ],
        [
            ("What is the main objective of pasteurization?", "Destroy specified pathogens and reduce spoilage organisms while preserving product quality", ["Make a product sterile in every package", "Remove all water", "Increase microbial counts"], "Pasteurization uses a validated time-temperature treatment to achieve public-health and quality objectives, but is not equivalent to sterilization.", "easy"),
            ("Why is the holding tube in a continuous pasteurizer sized for the minimum flow condition?", "Every product element must receive at least the required holding time", ["It increases the product's fat content", "It sets the farm's milk yield", "It removes the need for temperature measurement"], "The holding section is designed to ensure minimum residence time at the specified treatment temperature.", "intermediate"),
        ],
        [
            ("What does homogenization reduce in milk?", "Fat-globule size and the tendency for cream separation", ["The number of water molecules", "The milk's protein content to zero", "The need for cooling"], "Homogenization reduces fat-globule size and modifies the interface, helping stabilize the emulsion.", "easy"),
            ("In a cream separator, what principle enables fat-rich cream to separate from skim milk?", "Centrifugal force acting on density differences", ["Magnetic attraction of lactose", "Diffusion through a membrane only", "Evaporation of all water"], "A centrifugal separator accelerates separation of phases with different densities.", "easy"),
        ],
        [
            ("Why are starter cultures used in yoghurt production?", "They ferment lactose and produce acid and flavour compounds", ["They remove all proteins", "They prevent any microbial activity", "They convert milk fat into minerals"], "Yoghurt cultures acidify milk and develop characteristic texture and flavour through fermentation.", "easy"),
            ("Why control fermentation endpoint pH?", "It influences gel structure, flavour, and post-acidification", ["It determines the package barcode", "It eliminates the need for refrigeration", "It guarantees no culture survives"], "Acidification endpoint affects casein gelation, sensory properties, and stability during storage.", "intermediate"),
        ],
        [
            ("Why use clean-in-place systems in dairy plants?", "Clean internal equipment surfaces without routine dismantling", ["Add product flavour automatically", "Replace hygienic design", "Guarantee sterilization without validation"], "CIP circulates cleaning solutions through equipment; cycle design and validation remain necessary.", "easy"),
            ("Why verify detergent concentration, temperature, flow, and contact time in CIP?", "Cleaning effectiveness depends on their combined action", ["One variable alone determines all cleaning", "They control milk genetics", "They replace inspection and records"], "CIP performance depends on chemical action, temperature, mechanical flow, time, and equipment geometry.", "intermediate"),
        ],
    ],
    "DAIRY03": [
        [
            ("Why can raw milk support rapid bacterial growth if held warm?", "It contains water and nutrients suitable for many microorganisms", ["It contains no nutrients", "Bacteria cannot grow in liquids", "Milk is sterile at the farm by definition"], "Milk's composition supports microbial growth, so temperature control and hygienic handling matter.", "easy"),
            ("Why is a total plate count useful in raw-milk quality monitoring?", "It provides an indicator of the culturable microbial load under the test conditions", ["It identifies every pathogen individually", "It measures milk fat directly", "It proves the product is sterile"], "A plate count is an operational hygiene indicator, not a complete pathogen screen or sterility proof.", "easy"),
        ],
        [
            ("What is a starter culture in fermented dairy production?", "A selected microbial population added to drive a controlled fermentation", ["A chemical cleaning agent", "A milk-fat separator", "A packaging film"], "Starter cultures provide predictable acidification and product characteristics when handled under suitable conditions.", "easy"),
            ("Why may a mixed starter culture be used instead of a single strain?", "Different organisms can contribute complementary acidification and flavour functions", ["It guarantees no phage risk", "It removes all process control", "It prevents fermentation"], "Mixed cultures can provide complementary metabolism, but compatibility and stability must be managed.", "intermediate"),
        ],
        [
            ("Why is incubation temperature controlled during yoghurt fermentation?", "Culture growth rate and acid production depend on temperature", ["Temperature affects only package printing", "All cultures grow at identical rates at every temperature", "It prevents pH change"], "Temperature influences microbial growth, acidification rate, and the balance among starter organisms.", "easy"),
            ("What does over-acidification during fermentation commonly cause?", "Excess sourness and possible texture or whey-separation defects", ["The product becomes less acidic", "No change to flavour", "Sterility of the product"], "Continued acid production after the desired endpoint can impair sensory and physical quality.", "easy"),
        ],
        [
            ("Why is a validated heat treatment used to control milk-borne pathogens?", "It reduces viable pathogens to a specified level under defined conditions", ["It guarantees that no pathogen can ever be present later", "It removes all milk solids", "It replaces sanitation"], "Heat treatment reduces microorganisms according to process lethality; post-process contamination remains possible.", "easy"),
            ("Why distinguish spoilage organisms from pathogens in dairy microbiology?", "Spoilage can reduce quality while a pathogen may cause illness even without obvious spoilage", ["Every spoilage organism causes disease", "Pathogens always create a visible odour", "The groups are identical"], "Pathogenic hazards and quality spoilage are different concerns and require different detection and control strategies.", "intermediate"),
        ],
        [
            ("Why use environmental swabs in a dairy facility sanitation program?", "Assess whether cleaning and hygiene controls are effective on relevant surfaces", ["Measure milk protein directly", "Determine the product's shelf price", "Replace all in-process monitoring"], "Environmental monitoring can reveal harborage or sanitation failures when sampling sites and actions are defined.", "easy"),
            ("What should happen when a sanitation verification result is unsatisfactory?", "Investigate, correct the cause, and document follow-up verification", ["Ignore it if the equipment looks clean", "Release all product automatically", "Change the result to pass"], "Corrective action and documented verification are needed to restore control and assess product impact.", "easy"),
        ],
    ],
    "DAIRY04": [
        [
            ("What does a dairy-plant heat balance help quantify?", "Heat input, recovery, product heating, and losses around process equipment", ["Only the product's colour", "The bacteria's genome", "The facility's property tax"], "A heat balance accounts for energy flows and supports equipment sizing and utility analysis.", "easy"),
            ("Why include both sensible and latent heat when estimating evaporation duty?", "The feed warms and part of its water changes phase", ["Only the pump consumes energy", "Evaporation has no phase change", "Temperature and mass are unrelated"], "Evaporation duty includes sensible heating and latent heat of vaporization, with losses and concentration effects as relevant.", "intermediate"),
        ],
        [
            ("Why is a vapour-compression refrigeration cycle used in dairy cold storage?", "It removes heat from a low-temperature space and rejects it at a higher temperature", ["It creates cold without work input", "It sterilizes product by pressure", "It converts milk solids into refrigerant"], "The refrigeration cycle uses work to move heat from the refrigerated space to the surroundings.", "easy"),
            ("What does coefficient of performance (COP) compare for a refrigerator?", "Cooling effect with work input", ["Work input with product mass", "Pressure with viscosity", "Condenser area with room height"], "COP is the desired cooling effect divided by required work for a stated operating condition.", "easy"),
        ],
        [
            ("Why are sanitary pumps and smooth product-contact piping important in dairy systems?", "They support cleanability and reduce contamination or product-retention sites", ["They increase product residence time without control", "They replace all process monitoring", "They are used to introduce leaks"], "Hygienic design avoids crevices and dead legs and supports effective cleaning and drainage.", "easy"),
            ("Why consider pressure drop when sizing a dairy transfer pump?", "It determines the head and power needed to deliver the required flow", ["It changes the milk's species", "It sets the product's protein sequence", "It guarantees no cavitation"], "Piping friction and elevation contribute to system head, while available suction conditions must also be checked for cavitation.", "intermediate"),
        ],
        [
            ("How should a heat exchanger be selected for a viscous dairy product?", "Consider viscosity, fouling, heat transfer, cleanability, and product sensitivity", ["Use only the lowest-cost material", "Ignore pressure drop", "Assume all products have water-like properties"], "Equipment selection balances thermal performance with product rheology, fouling, cleaning, and quality constraints.", "intermediate"),
            ("Why is a regenerative section used in some dairy heat-treatment systems?", "Recover heat from hot treated product to preheat incoming product", ["Create uncontrolled contamination", "Eliminate the holding tube", "Remove all cooling capacity"], "Regeneration improves energy efficiency through heat exchange between outgoing and incoming streams, while maintaining separation and safety controls.", "easy"),
        ],
        [
            ("Why keep clean and process areas separated in a dairy plant layout?", "Reduce cross-contamination risk and support hygienic product flow", ["Increase product traffic through dirty zones", "Make cleaning impossible", "Replace worker training"], "Zoning and flow design reduce opportunities for contamination and support separation of raw and treated product.", "easy"),
            ("Why provide adequate floor drainage in wet processing areas?", "Remove wash water and limit pooling that can support contamination or slip hazards", ["Increase humidity intentionally", "Replace wastewater treatment", "Keep solids permanently on the floor"], "Proper grading and drainage limit standing water and support sanitation and worker safety.", "easy"),
        ],
    ],
    "ENERGY01": [
        [
            ("In a Rankine cycle, what is the main role of the condenser?", "Reject heat and condense turbine exhaust steam for return to the feed system", ["Compress steam to boiler pressure", "Add fuel to the working fluid", "Increase turbine inlet entropy without heat transfer"], "The condenser rejects heat to a sink and returns vapour to liquid for pumping back through the cycle.", "easy"),
            ("Why does pump work usually remain relatively small in a vapour power cycle?", "Liquid water has a much smaller specific volume than steam", ["The pump handles no pressure rise", "The condenser operates at zero pressure", "The turbine supplies no work"], "Compressing liquid requires less specific work than compressing a vapour over a comparable pressure range.", "intermediate"),
        ],
        [
            ("What is the purpose of excess air in a combustion boiler?", "Improve mixing and help achieve more complete fuel oxidation", ["Reduce oxygen below stoichiometric level deliberately", "Eliminate flue gas", "Convert ash into fuel"], "Some excess air helps ensure combustion completion, but too much increases stack heat loss and can lower efficiency.", "easy"),
            ("Why is boiler blowdown performed?", "Control dissolved and suspended solids concentration in boiler water", ["Increase scale formation", "Remove all steam from the turbine", "Raise fuel moisture"], "Blowdown removes concentrated boiler water to manage impurities and protect heat-transfer surfaces.", "easy"),
        ],
        [
            ("What is the purpose of a heat-recovery steam generator in a combined cycle plant?", "Use gas-turbine exhaust heat to generate steam for a steam cycle", ["Cool the exhaust without recovering energy", "Compress natural gas to the pipeline", "Replace the gas turbine's compressor"], "The HRSG recovers high-temperature exhaust energy to produce steam for additional power generation.", "easy"),
            ("Why can a combined-cycle plant achieve higher efficiency than a simple gas-turbine cycle?", "It converts part of the exhaust heat into additional useful work", ["It burns no fuel", "It has no thermodynamic losses", "It eliminates the condenser"], "A bottoming steam cycle recovers energy that would otherwise leave with the gas-turbine exhaust.", "intermediate"),
        ],
        [
            ("What does cogeneration or CHP produce from one fuel input?", "Useful heat and electricity or mechanical power", ["Only cooling water", "Fuel and oxygen from nothing", "Electricity with no heat rejection"], "Combined heat and power captures both electrical/mechanical output and useful thermal energy.", "easy"),
            ("Why evaluate total useful energy utilization for a cogeneration system?", "Electrical efficiency alone misses the value of recovered process heat", ["Heat has no energy content", "It removes the need for a system boundary", "It guarantees every heat stream is useful"], "A CHP assessment includes useful thermal output and its quality, not just electrical conversion efficiency.", "intermediate"),
        ],
        [
            ("Why establish a baseline before conducting an industrial energy audit?", "It provides a reference for comparing consumption and savings", ["It proves every proposed measure will work", "It sets electricity frequency", "It removes the need for metering"], "A baseline, adjusted for relevant operating conditions, supports credible energy-performance comparisons.", "easy"),
            ("What does a specific energy consumption metric compare?", "Energy use with a defined unit of production or service", ["Energy price with workforce size only", "Fuel volume with ambient colour", "Power factor with plant height"], "Specific energy consumption normalizes energy against output, but the process boundary and product mix should be defined.", "easy"),
        ],
    ],
    "ENERGY02": [
        [
            ("What does the photovoltaic effect do in a solar cell?", "Convert absorbed light into electrical charge separation", ["Store heat in a phase-change material", "Rotate a turbine directly", "Convert electricity into sunlight"], "Photons generate charge carriers in a semiconductor junction that can drive current through an external circuit.", "easy"),
            ("Why does the maximum-power point of a PV module vary with irradiance and cell temperature?", "Both conditions change the current-voltage characteristic", ["PV output is fixed after installation", "Temperature only changes the frame colour", "Irradiance has no effect on photocurrent"], "Irradiance primarily affects current and temperature affects voltage and efficiency, shifting the I-V curve and maximum-power point.", "intermediate"),
        ],
        [
            ("What is a solar thermal collector designed to do?", "Transfer incident solar energy as heat to a working fluid", ["Generate semiconductor carriers only", "Store electricity in a flywheel", "Convert wind into pressure"], "Solar thermal collectors absorb radiation and deliver heat to a fluid for heating or power applications.", "easy"),
            ("Why can thermal storage improve a solar-thermal system's usefulness?", "It shifts collected heat to periods when sunlight is unavailable or demand differs", ["It guarantees continuous solar input", "It removes all heat loss", "It replaces the collector"], "Storage buffers the timing mismatch between solar availability and thermal demand, with finite capacity and losses.", "intermediate"),
        ],
        [
            ("What does the power available in a wind stream scale with, for a fixed rotor swept area?", "The cube of wind speed", ["The square root of wind speed", "Wind speed to the fourth power", "It is independent of wind speed"], "Wind power through area is proportional to one-half rho A v cubed before turbine conversion limits.", "intermediate"),
            ("Why can a wind turbine not extract all kinetic energy from the incoming wind?", "Air must retain downstream velocity to continue passing through the rotor", ["The blades cannot rotate", "The generator consumes all wind", "The Betz limit applies only to solar panels"], "The Betz limit reflects the momentum constraint that flow cannot be brought to rest at the rotor plane.", "easy"),
        ],
        [
            ("What is anaerobic digestion used for in bioenergy systems?", "Convert biodegradable organic matter into biogas under oxygen-limited conditions", ["Burn metals to produce methane", "Convert solar radiation directly into hydrogen", "Remove all carbon from biomass without products"], "Anaerobic microbes produce methane-rich biogas from suitable organic feedstocks.", "easy"),
            ("Why assess feedstock moisture and composition before selecting a bioenergy process?", "They affect conversion route, energy yield, and handling requirements", ["They determine the grid frequency", "Every biomass feedstock behaves identically", "They remove the need for emissions controls"], "Moisture, ash, carbon content, and biodegradability influence thermochemical or biochemical conversion.", "intermediate"),
        ],
        [
            ("Why does inverter-based renewable generation need grid synchronization and control?", "It must deliver power with compatible voltage, frequency, and phase behaviour", ["It changes the grid's geographic area", "It removes all protection requirements", "It makes storage unnecessary"], "Grid-tied converters synchronize and regulate output while meeting protection and power-quality requirements.", "easy"),
            ("How can battery storage support a grid with variable renewable generation?", "Shift energy across time and provide selected fast-response services", ["Generate primary energy indefinitely", "Eliminate transmission constraints", "Guarantee constant renewable output"], "Storage can shift energy and provide services, subject to power, energy, efficiency, duration, and degradation limits.", "intermediate"),
        ],
    ],
    "ENERGY03": [
        [
            ("What does a battery's state of charge estimate?", "Remaining charge or energy relative to a defined usable capacity", ["The battery's exact future lifetime", "Its terminal colour", "The grid's nominal frequency"], "SOC is an estimate of stored charge or energy relative to a reference capacity and depends on estimation method.", "easy"),
            ("Why does battery capacity fade with cycling and calendar time?", "Electrochemical side reactions and material changes reduce usable capacity", ["The battery gains infinite active material", "Capacity is a permanent constant", "Only the enclosure colour changes"], "Ageing mechanisms depend on chemistry, temperature, voltage, and use and can reduce capacity and power capability.", "easy"),
        ],
        [
            ("In a hydrogen fuel cell, what is the overall role of hydrogen and oxygen?", "Their electrochemical reaction produces electricity, water, and heat", ["They create electricity without an energy source", "Oxygen is stored as a solid in the catalyst", "Hydrogen becomes nitrogen"], "A fuel cell converts chemical energy to electrical energy through electrochemical reactions with water and heat as products for a typical hydrogen-oxygen cell.", "easy"),
            ("Why is hydrogen storage and delivery part of a fuel-cell system assessment?", "Production, compression or liquefaction, transport, and leakage affect efficiency and safety", ["Hydrogen has no storage requirements", "The fuel cell creates hydrogen from nothing", "Delivery has no lifecycle impact"], "The full hydrogen pathway affects well-to-wheel efficiency, cost, emissions, and safety considerations.", "intermediate"),
        ],
        [
            ("What is latent-heat thermal storage based on?", "Energy absorbed or released during a material's phase change", ["Only sensible heating of air", "Electric charge in a wire", "Chemical fuel combustion only"], "Phase-change materials store energy as latent heat during melting and release it during solidification.", "easy"),
            ("Why is thermal conductivity important in a phase-change storage unit?", "It controls how quickly heat can enter or leave the storage material", ["It sets the material's molecular identity", "It determines the grid voltage", "It prevents phase change"], "Low conductivity can limit charge and discharge rates, motivating heat-transfer enhancement designs.", "intermediate"),
        ],
        [
            ("What is a role of a DC-DC converter in a renewable energy system?", "Adjust voltage and control power flow between DC components", ["Convert a battery into a turbine", "Measure wind speed mechanically", "Replace every protection device"], "DC-DC converters regulate voltage and power between sources, storage, and DC buses.", "easy"),
            ("Why use maximum-power-point tracking with a PV array?", "Adjust the electrical operating point to extract available power under changing conditions", ["Fix the array at short circuit", "Guarantee output despite zero sunlight", "Eliminate inverter losses"], "MPPT controls the operating voltage/current to follow the maximum-power point as irradiance and temperature change.", "easy"),
        ],
        [
            ("What is a microgrid?", "A local group of loads and distributed resources that can operate connected to or islanded from a wider grid", ["A single household appliance", "A transformer with no loads", "A type of fuel cell"], "Microgrids coordinate local resources and loads and may disconnect and reconnect under controlled conditions.", "easy"),
            ("Why is dispatch optimization needed in a microgrid?", "It balances demand, resource availability, storage, cost, and operational constraints", ["It makes demand constant", "It removes reserve requirements", "It guarantees zero emissions for every source"], "Dispatch schedules controllable sources and storage subject to reliability, power limits, and economic or environmental objectives.", "intermediate"),
        ],
    ],
    "ENERGY04": [
        [
            ("Why forecast energy demand by sector and time rather than only as an annual total?", "Peak timing and sector patterns affect capacity and network requirements", ["Annual totals determine the weather", "Demand is identical every hour", "It eliminates uncertainty"], "Hourly and sectoral patterns support resource adequacy, infrastructure planning, and demand-management decisions.", "easy"),
            ("What does an energy supply portfolio describe?", "The mix of sources and technologies meeting energy demand", ["Only the colour of transmission towers", "A list of consumer names", "The thermal conductivity of buildings"], "A supply portfolio summarizes contributions from fuels and technologies, often by energy or capacity share.", "easy"),
        ],
        [
            ("What is the difference between energy efficiency and energy conservation?", "Efficiency delivers the same service with less energy; conservation may reduce or avoid the service", ["They are identical terms in every context", "Efficiency increases energy input", "Conservation always reduces comfort to zero"], "Efficiency improves the energy-to-service ratio; conservation can change behaviour or service demand.", "intermediate"),
            ("Why compare measured energy use with a weather-adjusted baseline in building audits?", "Heating and cooling demand varies with outdoor conditions", ["Weather determines lighting colour", "A baseline removes all occupant effects", "Energy use is independent of temperature"], "Weather normalization improves comparisons when heating and cooling loads are climate-sensitive.", "easy"),
        ],
        [
            ("What does a lifecycle assessment boundary define?", "Which processes and stages are included in the impact evaluation", ["The project's physical fence only", "The equipment's warranty period only", "The colour scale of an emissions chart"], "System boundaries determine included inputs, outputs, and lifecycle stages and must be stated for fair comparisons.", "easy"),
            ("Why can two products with different functional units not be compared directly in an LCA?", "Their assessed services or quantities are not equivalent", ["LCA never uses quantities", "They must have the same material colour", "The database converts all services automatically"], "A functional unit defines comparable service; different units can make impact comparisons misleading.", "intermediate"),
        ],
        [
            ("Why distinguish direct operational emissions from lifecycle emissions?", "Upstream fuel and equipment processes can contribute outside the operating boundary", ["Direct emissions include every supply-chain stage", "Lifecycle accounting ignores manufacturing", "The categories are always numerically identical"], "Operational emissions arise during use, while lifecycle accounting can include extraction, production, transport, and end of life.", "easy"),
            ("What is one purpose of a carbon intensity metric?", "Compare emissions per unit of energy, output, or service", ["Measure voltage stability only", "Replace all pollutant limits", "Set the price of every fuel"], "Intensity normalizes emissions to an activity or output unit; the boundary and gases included should be specified.", "easy"),
        ],
        [
            ("How can a carbon price influence energy-system decisions?", "It changes the relative costs of higher- and lower-emissions options", ["It fixes the weather", "It removes technology constraints", "It guarantees a particular generation mix"], "Carbon pricing can affect dispatch and investment incentives, with outcomes depending on design and market context.", "intermediate"),
            ("Why evaluate energy affordability alongside decarbonization policy?", "Policy costs and benefits can affect households and industries unevenly", ["All consumers have identical budgets", "Emissions have no relation to energy access", "Affordability can be inferred from generation technology alone"], "Distributional impacts and access matter for an equitable, workable energy transition.", "easy"),
        ],
    ],
    "ENV02": [
        [
            ("What is a common objective of drinking-water treatment?", "Remove or inactivate contaminants to meet health and quality targets", ["Increase turbidity", "Add pathogens for stability", "Remove all dissolved oxygen"], "Treatment trains are designed for source-water risks and applicable water-quality targets.", "easy"),
            ("Why characterize source-water quality before choosing a treatment process?", "Contaminants and variability determine which barriers are needed", ["Every source has identical chemistry", "Treatment design depends only on plant colour", "Characterization prevents seasonal variation"], "Source-water properties and seasonal changes guide process selection and operational control.", "easy"),
        ],
        [
            ("What is the purpose of coagulation in conventional water treatment?", "Destabilize fine colloids so they can aggregate", ["Dissolve every suspended solid", "Disinfect only with ultraviolet light", "Remove dissolved salts by boiling"], "Coagulants reduce colloidal stability so particles can form flocs for subsequent separation.", "easy"),
            ("Why is flocculation performed after rapid mixing of coagulant?", "Gentle mixing promotes collisions and growth of settleable flocs", ["It breaks every floc into smaller particles", "It sterilizes the water", "It changes water into steam"], "Slow mixing encourages particle aggregation while avoiding shear that would break formed flocs.", "easy"),
        ],
        [
            ("How does granular filtration remove particles from water?", "Straining and attachment within a porous media bed", ["Only by changing water temperature", "By converting particles into gas", "By adding more suspended solids"], "Filtration removes particles through a combination of transport, attachment, and straining within the bed.", "easy"),
            ("Why is disinfection applied after physical clarification and filtration?", "Lower turbidity can improve disinfectant contact and reduce shielding", ["Clear water cannot contain microbes", "Filtration creates chlorine", "Disinfection removes all dissolved minerals"], "Particle removal improves disinfection effectiveness, although treatment barriers and contact conditions remain necessary.", "intermediate"),
        ],
        [
            ("What does activated sludge use to remove biodegradable organic matter?", "A suspended microbial community under controlled aeration", ["Only a sand filter", "An ion-exchange resin that digests solids", "A UV lamp that removes all carbon"], "Microorganisms oxidize organic matter in an aerated mixed liquor, followed by solids separation and recycle.", "easy"),
            ("Why is dissolved oxygen monitored in an aeration basin?", "Microbes need suitable oxygen for aerobic treatment and process performance", ["It directly measures sludge age", "It determines the pipe's diameter", "It replaces pH monitoring"], "Dissolved oxygen helps assess aeration and biological conditions but should be interpreted with loading and other process measures.", "easy"),
        ],
        [
            ("Why thicken wastewater sludge before dewatering?", "Reduce water volume and improve downstream handling efficiency", ["Increase the amount of liquid to transport", "Sterilize the sludge", "Convert all solids to gas"], "Thickening concentrates solids and can reduce pumping, storage, and dewatering loads.", "easy"),
            ("What should be evaluated before reusing treated sludge or biosolids?", "Pathogens, contaminants, treatment quality, and the intended use requirements", ["Only the material's colour", "The plant's electricity tariff alone", "A guarantee that treatment removes every chemical"], "Reuse decisions require risk-based quality, treatment, exposure, and regulatory evaluation.", "intermediate"),
        ],
    ],
    "ENV03": [
        [
            ("Why does atmospheric stability affect pollutant dispersion?", "It influences vertical mixing and dilution", ["It sets the fuel's octane number", "It removes all emissions", "It changes stack height automatically"], "Stable air suppresses vertical mixing, while unstable conditions often enhance turbulent dispersion.", "easy"),
            ("What is a primary source of ground-level ozone in urban air?", "Photochemical reactions involving nitrogen oxides and volatile organic compounds", ["Direct release of ozone from all car engines", "Pure water evaporation", "Combustion of oxygen alone"], "Tropospheric ozone forms through sunlight-driven chemistry of NOx and VOCs, rather than being emitted directly in large amounts by most sources.", "intermediate"),
        ],
        [
            ("What does PM2.5 refer to?", "Particles with aerodynamic diameter at or below about 2.5 micrometres", ["Particles containing exactly 2.5 grams of carbon", "A gas measured in parts per million", "Particles larger than every pollen grain"], "PM2.5 is a size-based particulate matter category defined using aerodynamic diameter.", "easy"),
            ("Why are air-quality indices useful to the public?", "They summarize pollutant concentrations into understandable health-related categories", ["They measure each person's exact inhaled dose", "They replace monitoring instruments", "They guarantee no health risk below the top category"], "An AQI communicates ambient conditions but does not represent individual exposure or a no-risk threshold.", "easy"),
        ],
        [
            ("How does a cyclone separator remove many coarse particles from a gas stream?", "Centrifugal motion drives particles toward the wall for collection", ["It dissolves particles chemically", "It uses a membrane with molecular pores", "It converts dust into water vapour"], "Cyclones use swirling flow and particle inertia to separate particles, with efficiency depending on size and operating conditions.", "easy"),
            ("Why can a fabric filter achieve high particulate removal efficiency?", "A dust cake and filter media capture particles from the gas", ["It neutralizes every pollutant gas", "It uses gravity alone", "It guarantees no pressure drop"], "Fabric filters collect particles on media and dust cake but require pressure-drop and cleaning management.", "intermediate"),
        ],
        [
            ("What is the role of an absorber in flue-gas desulfurization?", "Transfer sulfur dioxide from gas into a reactive liquid or slurry", ["Create nitrogen oxides", "Increase particulate emissions", "Remove carbon dioxide by freezing only"], "Wet scrubbing absorbs SO2 and may chemically react it with alkaline sorbents.", "easy"),
            ("Why is selective catalytic reduction used in some combustion exhaust systems?", "Convert nitrogen oxides to nitrogen and water using a reducing agent over a catalyst", ["Convert oxygen to ozone", "Remove all dust without a filter", "Increase NOx concentration"], "SCR uses a catalyst and reductant such as ammonia or urea-derived ammonia to reduce NOx under controlled conditions.", "intermediate"),
        ],
        [
            ("Why are ambient air samples collected using defined averaging periods?", "Pollutant concentrations vary over time and standards use specified time bases", ["Averaging removes all uncertainty", "Air composition never changes", "It determines the sampler's colour"], "Averaging periods support comparable interpretation against short- and long-term standards and health guidance.", "easy"),
            ("Why document calibration and detection limits for an air monitor?", "They affect confidence in measurements and interpretation near thresholds", ["They control atmospheric pressure", "They make results independent of interference", "They replace field siting criteria"], "Instrument performance, detection limits, calibration, and siting influence data quality and regulatory use.", "intermediate"),
        ],
    ],
    "ENV04": [
        [
            ("What does the waste hierarchy generally prioritize above disposal?", "Prevention, reduction, reuse, and recycling where feasible", ["Landfilling all materials first", "Mixing hazardous and nonhazardous waste", "Ignoring product design"], "The hierarchy gives preference to avoiding waste and recovering value before final disposal, subject to safety and lifecycle context.", "easy"),
            ("Why characterize a municipal solid-waste stream before designing a facility?", "Composition, moisture, and variability affect collection and treatment choices", ["Every city has identical waste", "It determines only the vehicle colour", "Characterization eliminates seasonal changes"], "Waste characterization informs capacity, separation, biological and thermal treatment, and landfill planning.", "easy"),
        ],
        [
            ("Why optimize collection routes and container placement?", "Reduce travel, missed pickups, fuel use, and service delays", ["Increase empty truck travel", "Prevent waste generation", "Change the waste's chemical formula"], "Route and container design can improve service efficiency and cost while considering access and public needs.", "easy"),
            ("What is a transfer station used for in a waste system?", "Consolidate loads before longer-distance transport", ["Compost all waste automatically", "Replace source separation", "Treat drinking water"], "Transfer stations can consolidate collection vehicles' loads into larger transport units for distant facilities.", "easy"),
        ],
        [
            ("What conditions support aerobic composting?", "Oxygen, suitable moisture, biodegradable feed, and managed temperature", ["Complete absence of oxygen", "Only inert metals", "Zero microbial activity"], "Aerobic microbes require oxygen and suitable moisture and temperature to stabilize biodegradable material.", "easy"),
            ("Why is the carbon-to-nitrogen ratio considered in compost feedstock blending?", "Microbes need balanced carbon for energy and nitrogen for growth", ["It sets the landfill liner thickness", "It measures particle hardness", "It controls only the finished colour"], "Feedstock C:N affects biological activity; moisture, porosity, and degradability also matter.", "intermediate"),
        ],
        [
            ("What is one purpose of energy recovery from waste?", "Recover useful heat or power from suitable residual waste", ["Eliminate the need for emissions controls", "Create unlimited renewable energy", "Replace recycling of every material"], "Waste-to-energy can recover energy from residual fractions, but emissions, ash, and material-recovery trade-offs must be managed.", "easy"),
            ("Why is combustion temperature and residence time monitored in a waste-to-energy unit?", "They influence destruction of organics and combustion completeness", ["They determine the city's population", "They make flue gas harmless without cleanup", "They control recycling rates"], "Combustion conditions affect destruction efficiency, while flue-gas treatment is still needed for pollutants.", "intermediate"),
        ],
        [
            ("What is leachate in a landfill?", "Liquid that has percolated through waste and accumulated dissolved or suspended constituents", ["A gas released by a turbine", "A dry soil cover", "A type of recycling container"], "Leachate forms as water contacts waste and can carry contaminants, requiring collection and treatment.", "easy"),
            ("Why is a composite liner used in many engineered landfills?", "Provide a low-permeability barrier to limit contaminant migration", ["Increase leachate leakage", "Allow direct contact with groundwater", "Replace leachate collection"], "Liner systems combine materials to reduce leakage risk, alongside leachate collection, monitoring, and operational controls.", "intermediate"),
        ],
    ],
    "FOODTECH01": [
        [
            ("Why include moisture and solids in a food-process material balance?", "They determine product yield and concentration changes", ["They measure packaging colour", "They replace the energy balance", "They make flow rates irrelevant"], "Component balances track water and solids through heating, concentration, drying, and other operations.", "easy"),
            ("What does water activity indicate in a food?", "The availability of water for microbial and chemical processes", ["The total water mass only", "The food's protein sequence", "The rate of conveyor motion"], "Water activity relates to water's thermodynamic availability and helps predict stability, though pH and other hurdles also matter.", "intermediate"),
        ],
        [
            ("What is the purpose of pasteurizing a liquid food?", "Achieve a specified pathogen reduction and shelf-life objective", ["Make all products shelf-stable without packaging", "Remove all nutrients", "Increase microbial load"], "Pasteurization uses defined thermal treatment and handling to meet safety and quality objectives; it is not commercial sterilization.", "easy"),
            ("Why is a cold spot considered when validating thermal processing of a packaged food?", "It may receive the least lethal heat treatment", ["It always has the highest temperature", "It determines package colour", "It removes the need for sensors"], "The cold spot governs process lethality because it heats more slowly than other locations in the container.", "intermediate"),
        ],
        [
            ("Why use an evaporator to concentrate a liquid food?", "Remove water as vapour to increase solids concentration", ["Add water without heating", "Separate dissolved minerals by magnetism", "Freeze the entire product"], "Evaporation removes solvent and concentrates nonvolatile components, with heat-sensitive products often requiring careful conditions.", "easy"),
            ("Why may vacuum evaporation benefit a heat-sensitive juice?", "Lower pressure reduces the boiling temperature", ["It increases the boiling temperature", "It prevents evaporation", "It sterilizes the product automatically"], "Reduced pressure allows evaporation at lower temperature and can limit thermal degradation.", "easy"),
        ],
        [
            ("What is the main objective of dehydration in food processing?", "Reduce moisture to improve stability and reduce mass or volume", ["Increase water activity", "Add oxygen to all products", "Eliminate all sensory changes"], "Drying reduces moisture and may improve shelf stability, while product quality and rehydration behaviour must be considered.", "easy"),
            ("Why does drying rate depend on both air conditions and food structure?", "Heat and mass transfer through the product govern moisture removal", ["Only package colour matters", "Food structure has no effect", "Air humidity is always irrelevant"], "Temperature, humidity, velocity, geometry, and internal moisture transport affect drying kinetics.", "intermediate"),
        ],
        [
            ("Why keep refrigerated foods within a controlled cold-chain temperature range?", "Slow microbial growth and quality deterioration", ["Increase pathogen growth", "Replace hygienic handling", "Make food sterile"], "Refrigeration slows but does not stop all microbial and chemical changes; continuous handling controls remain necessary.", "easy"),
            ("Why is temperature monitoring useful during transport of chilled food?", "It helps identify excursions that may compromise safety or shelf life", ["It measures packaging tensile strength", "It guarantees no contamination occurred", "It replaces product traceability"], "Temperature records support risk assessment and corrective action but cannot alone prove product safety.", "easy"),
        ],
    ],
    "FOODTECH02": [
        [
            ("Why can Salmonella be a concern in ready-to-eat foods?", "The food may receive no further kill step before consumption", ["It grows only in metal", "Cooking always happens after packaging", "It is a packaging polymer"], "Ready-to-eat products require controls that prevent contamination because consumers may not cook them.", "easy"),
            ("Why distinguish an indicator organism from a pathogen test?", "Indicators assess process hygiene but do not identify every pathogen", ["Indicators are always pathogens", "Pathogen tests measure only food colour", "The terms are interchangeable"], "Indicator organisms can reveal sanitation or process conditions but are not a substitute for pathogen-specific assessment.", "easy"),
        ],
        [
            ("How does reducing water activity help preserve food?", "It limits growth of many microorganisms and slows some reactions", ["It increases available water", "It guarantees destruction of spores", "It removes the need for packaging"], "Lower water activity inhibits many microbes but does not guarantee safety without considering organism limits and other hurdles.", "easy"),
            ("Why can refrigeration and acidity be combined as preservation hurdles?", "Multiple controls can inhibit growth through different mechanisms", ["They always sterilize food", "They increase microbial growth together", "They replace hazard analysis"], "Hurdle technology combines controls such as temperature and pH to improve stability, but needs product validation.", "intermediate"),
        ],
        [
            ("What is a purpose of sanitation after cleaning food-contact equipment?", "Reduce remaining microorganisms to an acceptable level", ["Remove all visible soil only", "Replace disassembly of inaccessible parts", "Guarantee sterile conditions permanently"], "Cleaning removes soil; sanitation reduces microorganisms on cleaned surfaces under specified conditions.", "easy"),
            ("Why must sanitizer concentration and contact time be monitored?", "They affect antimicrobial effectiveness and residue control", ["They set the food's nutritional label", "Sanitizer works identically at any concentration", "They replace pre-cleaning"], "Correct concentration and contact time are necessary for effective, safe sanitation and depend on the product and surface.", "easy"),
        ],
        [
            ("In HACCP, what is a critical control point?", "A step where control is essential to prevent, eliminate, or reduce a significant hazard", ["Any point where a worker takes a break", "A marketing approval step", "A storage location with no hazard analysis"], "CCPs are determined by hazard analysis and require measurable control limits and monitoring.", "easy"),
            ("Why establish a critical limit at a CCP?", "It separates acceptable from unacceptable process conditions", ["It guarantees every product is identical", "It removes the need for corrective actions", "It determines shelf price"], "A validated critical limit provides a measurable threshold to maintain hazard control.", "easy"),
        ],
        [
            ("What is the purpose of environmental monitoring in a food plant?", "Detect potential harborage or contamination patterns in the processing environment", ["Measure product sweetness only", "Replace supplier approval", "Prove that no pathogen can ever occur"], "Risk-based environmental sampling can identify sanitation gaps and verify control programs over time.", "easy"),
            ("Why investigate a recurring environmental positive even when finished-product tests are negative?", "Contamination niches can persist and product sampling may miss an intermittent hazard", ["Finished-product tests detect every unit", "A positive is never meaningful", "Environmental sites cannot affect product"], "A recurring trend may indicate a harborage requiring corrective action even if limited product samples are negative.", "intermediate"),
        ],
    ],
    "FOODTECH03": [
        [
            ("Why can lower water activity improve dry-food stability?", "It reduces water available for microbial growth and many chemical reactions", ["It adds free water", "It makes all foods sterile", "It removes all carbohydrates"], "Water activity is linked to microbial growth and reaction rates, but does not replace other safety controls.", "easy"),
            ("What is a glass transition in an amorphous food material?", "A temperature-dependent change between glassy and rubbery states", ["A crystalline melting point in every food", "A microbial growth phase", "The boiling point of all fats"], "Amorphous matrices can change mobility across a glass transition, affecting stickiness, collapse, and stability.", "intermediate"),
        ],
        [
            ("What are proteins made from?", "Amino-acid residues linked by peptide bonds", ["Fatty acids linked by ester bonds", "Glucose monomers only", "Mineral crystals"], "Proteins are polymers of amino acids joined through peptide bonds.", "easy"),
            ("Why can heat denature a food protein?", "It disrupts noncovalent interactions that stabilize higher-order structure", ["It changes every peptide bond into DNA", "It removes all amino acids", "It prevents molecular motion"], "Heat can unfold proteins and expose reactive groups, affecting solubility, gelation, and texture.", "easy"),
        ],
        [
            ("Why are unsaturated lipids often more susceptible to oxidation than saturated lipids?", "Double bonds provide sites prone to oxidative reactions", ["They contain no carbon", "They cannot contact oxygen", "They are always solid at room temperature"], "Unsaturated bonds can be more reactive toward lipid oxidation, producing rancid flavours and other products.", "easy"),
            ("What is the role of an antioxidant in a food formulation?", "Delay oxidation through mechanisms such as radical scavenging", ["Increase oxygen exposure", "Accelerate rancidity", "Replace all packaging barriers"], "Antioxidants can slow oxidative reactions but must be selected and used within formulation and regulatory constraints.", "easy"),
        ],
        [
            ("Why can pH affect the colour of anthocyanin pigments?", "Their molecular forms and absorption spectra vary with acidity", ["pH changes the pigment's atomic number", "Anthocyanins are insensitive to all conditions", "Colour depends only on package thickness"], "Anthocyanin structure and visible colour shift across pH due to changes in protonation and molecular form.", "intermediate"),
            ("Why are food additives used only within specified conditions and limits?", "Their safety and technological function depend on dose, food, and intended use", ["Any additive is safe at any dose", "Additives remove the need for good manufacturing practice", "Limits are set by colour preference alone"], "Regulations define permitted uses and maximum levels based on safety evaluation and technological need.", "easy"),
        ],
        [
            ("Why can Maillard browning occur during heating or storage?", "Reducing sugars react with amino groups through a complex sequence", ["Water reacts only with salt", "Lipids become minerals", "It requires no reactive food components"], "The Maillard reaction involves reducing carbonyl compounds and amino groups and can affect colour, flavour, and nutrition.", "easy"),
            ("Why monitor nutrient retention during thermal processing?", "Heat and process conditions can degrade sensitive vitamins", ["Nutrients are never affected by heat", "Only packaging colour changes", "It replaces microbial lethality validation"], "Processing can reduce or improve bioavailability of nutrients; nutrition and safety objectives both need evaluation.", "intermediate"),
        ],
    ],
    "FOODTECH04": [
        [
            ("Why use a trained sensory panel with controlled serving conditions?", "Reduce bias and make sensory comparisons more repeatable", ["Make every consumer response identical", "Eliminate the need for product formulation", "Measure microbial load directly"], "Panel training, blinding, randomization, and controlled serving conditions improve interpretability of sensory tests.", "easy"),
            ("What does a triangle sensory test ask a participant to do?", "Identify the odd sample among three, two of which are alike", ["Rank five samples by price", "Measure pH by taste", "Describe the packaging material"], "A triangle test is a discrimination method for detecting a perceptible difference.", "easy"),
        ],
        [
            ("Why calibrate an instrument used for colour measurement?", "Ensure its readings are traceable and comparable to reference standards", ["It changes the food's pigment", "It eliminates sample variability", "It measures flavour directly"], "Calibration checks instrument response against standards; sample preparation and measurement geometry also matter.", "easy"),
            ("What does a texture analyser measure in a compression test?", "Force-displacement response under a defined test setup", ["The product's microbial species", "Its exact consumer preference", "The package's oxygen permeability only"], "Texture analysis measures mechanical response under specified probe, speed, sample, and deformation conditions.", "easy"),
        ],
        [
            ("Why select packaging based on both barrier and mechanical properties?", "It must protect product quality and withstand handling and distribution", ["Only printing determines package performance", "Barrier properties never matter", "Mechanical strength changes the food's DNA"], "Packaging protects against moisture, oxygen, light, and physical damage according to product sensitivity and logistics.", "easy"),
            ("Why can multilayer packaging combine different polymers or materials?", "Each layer can contribute a distinct barrier, seal, or mechanical function", ["Layers always dissolve into food", "It guarantees recyclability in every system", "It removes the need for package testing"], "Multilayer structures can optimize performance but may complicate recycling and need migration evaluation.", "intermediate"),
        ],
        [
            ("What is modified-atmosphere packaging intended to change?", "The gas composition around the product to influence respiration or microbial growth", ["The food's genetic composition", "The package's weight only", "The storage temperature automatically"], "MAP adjusts headspace gases, with gas mix selected for the product, film, and temperature.", "easy"),
            ("Why can excessive carbon dioxide in a package be undesirable for some foods?", "It may cause package collapse, sensory defects, or tissue injury", ["It always improves all foods", "It eliminates all pathogens", "It prevents gas dissolution"], "High CO2 can dissolve into product or affect quality; target atmosphere is product-specific.", "intermediate"),
        ],
        [
            ("What does a shelf-life study establish?", "How long the product meets defined safety and quality criteria under stated conditions", ["A universal expiration date for every storage condition", "Only the package's colour stability", "The food's exact composition forever"], "Shelf life depends on product, package, storage, and acceptance limits; study design should represent intended conditions.", "easy"),
            ("Why retain lot codes and distribution records for traceability?", "Enable targeted investigation, withdrawal, or recall if a hazard or defect is found", ["Increase product temperature", "Replace sanitation records", "Guarantee no recall will be needed"], "Traceability supports identification of affected lots and efficient corrective action.", "easy"),
        ],
    ],
    "GEO01": [
        [
            ("Why must coordinates be interpreted with their coordinate reference system (CRS)?", "The same numeric coordinates can locate different places under different datums or projections", ["A CRS changes the measured feature's physical location", "Coordinates never require units", "Every map uses the same global grid"], "A CRS defines the datum, axes, units, and projection needed to interpret coordinates consistently.", "easy"),
            ("What is a key consequence of projecting the curved Earth onto a flat map?", "Some combination of area, shape, distance, or direction is distorted", ["All spatial distortion disappears", "Only attribute tables are affected", "The map scale becomes identical everywhere"], "No planar projection preserves every geometric property across the whole Earth; projection choice should suit the task.", "intermediate"),
        ],
        [
            ("Which GIS data model is generally best for representing a continuous elevation surface?", "Raster", ["A point-only event table", "A topology-free list of labels", "A relational key without geometry"], "A raster stores values in a regular grid, which is well suited to continuous fields such as elevation.", "easy"),
            ("What does topology help represent in vector GIS?", "Spatial relationships such as connectivity, adjacency, and containment", ["Only a feature's display colour", "The computer's screen resolution", "A raster cell's compression ratio"], "Topology encodes relationships between features and can support validation and network analysis.", "easy"),
        ],
        [
            ("In a polygon overlay, what does an intersection operation return?", "The shared area and attributes where the input polygons overlap", ["Only the outer boundary of both layers", "All features from one layer regardless of location", "A distance raster from the polygon centroid"], "Intersection retains the common spatial area and combines relevant attributes from the inputs.", "easy"),
            ("Why should layers be checked for compatible CRS before overlay analysis?", "Misaligned coordinates can produce incorrect or empty spatial relationships", ["CRS controls the spelling in attribute fields", "Overlay automatically repairs every coordinate error", "Different CRSs always mean the features are unrelated"], "Layers should be transformed to a suitable common CRS before precise overlay or measurement.", "intermediate"),
        ],
        [
            ("Which cartographic choice improves readability when many polygon categories share a map?", "Use a clear, perceptually distinct colour scheme with a legible legend", ["Use nearly identical colours for every class", "Remove the legend and all labels", "Choose symbol sizes unrelated to the mapped variable"], "Visual variables and legends should make categories easy to distinguish without implying false order or magnitude.", "easy"),
            ("What does a scale bar communicate on a map?", "The relationship between map distance and ground distance", ["The map's data licence", "The number of layers in the project", "The uncertainty of every attribute"], "A scale bar provides a visual distance reference that remains meaningful when the map is resized proportionally.", "easy"),
        ],
        [
            ("What does positional accuracy describe?", "How close a mapped position is to its true or accepted reference position", ["Whether a map uses attractive colours", "How many attribute columns are present", "Whether every feature has a unique name"], "Positional accuracy concerns location error and should be evaluated against an appropriate reference and tolerance.", "easy"),
            ("Why record data provenance and acquisition date in GIS metadata?", "Users can judge fitness for use, currency, and lineage", ["Metadata removes all measurement error", "It guarantees public redistribution rights", "It replaces the need to document a CRS"], "Lineage, date, CRS, and quality metadata help users assess whether a dataset is suitable for a decision.", "intermediate"),
        ],
    ],
    "GEO02": [
        [
            ("Why do passive optical sensors depend on illumination from the Sun?", "They measure reflected solar energy in relevant wavelength bands", ["They emit their own radio pulses", "They measure only underground temperature", "They record coordinates without sensing energy"], "Passive optical systems generally rely on reflected solar radiation, so illumination and acquisition time matter.", "easy"),
            ("What does a radar sensor use to form an observation?", "Microwave energy transmitted by the sensor and returned from the surface", ["Only visible sunlight reflected by clouds", "Sound waves from a ground microphone", "Aerial photographs scanned as text"], "Radar is an active microwave system and can acquire data independent of sunlight, though geometry and weather effects still matter.", "easy"),
        ],
        [
            ("What does spatial resolution describe in a raster image?", "The ground area represented by one pixel", ["The number of spectral bands", "How often the satellite revisits", "The number of bits used for one value"], "Spatial resolution is related to pixel footprint; spectral, temporal, and radiometric resolution describe different properties.", "easy"),
            ("A sensor records many narrow wavelength bands. Which resolution is especially high?", "Spectral resolution", ["Temporal resolution", "Map projection resolution", "Geodetic resolution"], "Spectral resolution describes the ability to distinguish narrow wavelength intervals or features.", "easy"),
        ],
        [
            ("Why apply a radiometric correction before comparing imagery from different dates?", "To reduce sensor or atmospheric effects that change measured pixel values", ["To make all land-cover classes identical", "To convert every pixel into a vector point", "To remove the need for ground validation"], "Radiometric normalization helps make observations more comparable, though correction assumptions and residual effects should be checked.", "intermediate"),
            ("What is a supervised image-classification model trained from?", "Representative labelled samples for the target classes", ["Only the image filename", "A random colour palette with no examples", "The map legend alone"], "Supervised classification learns class patterns from labelled samples and needs independent validation.", "easy"),
        ],
        [
            ("What is the central idea of post-classification change detection?", "Compare classified maps from different dates to identify class transitions", ["Compare only image file sizes", "Assume all pixel differences indicate real change", "Replace the older image with a blank raster"], "Post-classification comparison maps transitions but inherits errors from both date-specific classifications.", "easy"),
            ("Why should images be geometrically co-registered before pixel-wise change analysis?", "Corresponding pixels must represent the same ground locations", ["It guarantees identical spectral response", "It changes the land cover to match the map", "It removes seasonal variation automatically"], "Misregistration creates false change along boundaries because pixels no longer refer to the same locations.", "intermediate"),
        ],
        [
            ("Why is a confusion matrix useful for validating a land-cover classification?", "It compares predicted classes with independent reference labels", ["It measures satellite battery life", "It chooses a map projection automatically", "It proves all errors are impossible"], "A confusion matrix summarizes agreement and class-specific errors when based on appropriate reference data.", "easy"),
            ("Why should validation samples be independent of training samples?", "Using the same samples can give an overly optimistic accuracy estimate", ["Training labels cannot contain categories", "Independent samples force accuracy to equal 100%", "The model otherwise cannot make predictions"], "Independent validation estimates generalization more honestly than reusing the examples used for fitting.", "intermediate"),
        ],
    ],
    "GEO03": [
        [
            ("Why are redundant observations useful in a surveying control network adjustment?", "They allow residuals to be examined and precision to be estimated", ["They eliminate the need for a datum", "They guarantee all measurements are exact", "They make instrument calibration unnecessary"], "Redundancy provides checks and supports least-squares estimation and uncertainty assessment.", "intermediate"),
            ("What does a survey residual represent after an adjustment?", "The difference between an observation and its adjusted or predicted value", ["The instrument's serial number", "The map's nominal scale", "The horizontal datum itself"], "Residuals help identify inconsistencies and assess whether the observation model fits the data.", "easy"),
        ],
        [
            ("What is the main purpose of a GNSS receiver tracking signals from multiple satellites?", "Estimate position and time from satellite ranging observations", ["Measure soil salinity directly", "Create a topographic contour without observations", "Determine a satellite's colour"], "GNSS positioning uses satellite signals and receiver processing; geometry and corrections affect the solution.", "easy"),
            ("Why can a GNSS position degrade near tall buildings?", "Signal blockage and multipath can reduce measurement quality", ["Buildings change the satellite orbit", "The receiver's coordinate axes reverse", "GNSS requires clear weather to transmit"], "Obstructions and reflected signals can weaken or bias satellite range measurements.", "easy"),
        ],
        [
            ("Why backsight a known point when setting up a total station?", "Establish the instrument's orientation relative to the survey control", ["Measure atmospheric pressure", "Set the reflector's material", "Determine the prism's colour code"], "A backsight to known control provides the direction reference needed for subsequent angle and distance observations.", "easy"),
            ("What should be checked before relying on a total-station traverse?", "Instrument centring, levelling, target identification, and closure", ["Only the field notebook cover", "Whether the station names are alphabetical", "Whether all distances are rounded to whole kilometres"], "Careful setup and closure checks help reveal blunders and control traverse quality.", "intermediate"),
        ],
        [
            ("In photogrammetry, what does image overlap enable?", "Common features can be matched across images to reconstruct three-dimensional geometry", ["Each photograph becomes a GPS satellite", "It removes lens distortion automatically", "It prevents any occlusion"], "Forward and side overlap provide shared observations for stereo reconstruction and bundle adjustment.", "easy"),
            ("Why include ground control points in an aerial image block?", "Tie image measurements to known ground coordinates and the chosen reference frame", ["Increase the camera's focal length", "Replace all image matching", "Change the terrain elevation"], "Ground control helps georeference and constrain the photogrammetric solution.", "intermediate"),
        ],
        [
            ("What is a common purpose of closing a survey traverse on known control?", "Check accumulated angular and positional misclosure", ["Increase the size of the field book", "Remove the need for instrument checks", "Guarantee all measurements are error-free"], "Closure provides a practical quality check; acceptable tolerances depend on survey purpose and standards.", "easy"),
            ("Why preserve raw survey observations alongside adjusted coordinates?", "They support audit, reprocessing, and investigation of detected errors", ["Raw observations always have no uncertainty", "Adjusted coordinates cannot be stored digitally", "It makes a datum unnecessary"], "Retaining raw measurements and metadata supports reproducibility and later quality review.", "easy"),
        ],
    ],
    "GEO04": [
        [
            ("When would a raster suitability model commonly use map algebra?", "Combine aligned cell-by-cell criteria into a derived surface", ["Replace every vector point with a label", "Measure internet latency", "Sort map layers by filename only"], "Raster map algebra combines cell values, so consistent extent, resolution, and alignment are important.", "easy"),
            ("What does a spatial join typically do?", "Attach attributes based on a defined spatial relationship between features", ["Move all geometries to a new continent", "Compress a raster into a vector table", "Change feature geometry to text"], "Spatial joins transfer attributes using relationships such as within, intersects, or nearest, according to the chosen rule.", "easy"),
        ],
        [
            ("What does a digital elevation model support in hydrologic analysis?", "Derivation of terrain, flow direction, and drainage patterns", ["Direct measurement of water chemistry", "Automatic classification of every land parcel", "A guarantee that culverts are mapped"], "DEM-derived flow products depend on elevation quality, conditioning, and appropriate hydrologic assumptions.", "easy"),
            ("Why might sinks be inspected or conditioned before deriving flow paths from a DEM?", "Some sinks are data artifacts that interrupt modeled drainage", ["Every real depression must be removed", "Sinks determine the raster's colour table", "Conditioning changes the Earth's actual relief"], "DEM conditioning can correct artifacts, but real closed depressions should be preserved where they matter.", "intermediate"),
        ],
        [
            ("In a road network, what does a shortest-path algorithm usually minimize?", "A specified edge cost such as distance or travel time", ["The number of map colours", "The raster's number of rows", "The coordinate system's name"], "Network routing optimizes the cost assigned to edges; the cost definition determines what 'shortest' means.", "easy"),
            ("Why must a network dataset encode connectivity at intersections correctly?", "Routing depends on which edges are allowed to connect", ["Connectivity controls the map title", "It changes the road's legal ownership automatically", "It guarantees traffic conditions are constant"], "Incorrect connectivity can create impossible routes or break valid paths.", "intermediate"),
        ],
        [
            ("What does spatial autocorrelation describe?", "The degree to which nearby locations have similar or dissimilar values", ["The number of attributes in a GIS layer", "A map's print resolution", "A satellite's revisit interval"], "Spatial autocorrelation measures spatial patterning and should be interpreted with scale and neighborhood definitions.", "easy"),
            ("Why is spatial clustering not proof that one variable causes another?", "Spatial association alone does not establish a causal mechanism", ["Coordinates cannot be analyzed statistically", "Clusters are always random", "Causation is defined by map colour"], "Confounding, sampling, and spatial dependence can create associations without causal evidence.", "intermediate"),
        ],
        [
            ("What should a geospatial project plan define before analysis begins?", "Decision purpose, data, spatial scale, methods, and validation criteria", ["Only the map's background colour", "A result regardless of evidence", "A single software brand"], "Project design should connect the question to suitable data, analytical choices, quality checks, and users.", "easy"),
            ("Why consider privacy when publishing detailed location data?", "Locations can reveal sensitive information about identifiable people or places", ["Coordinates are always anonymous", "Maps cannot be copied", "A public dataset has no ethical obligations"], "Fine-grained location data may enable re-identification or expose sensitive sites; access and aggregation should be considered.", "intermediate"),
        ],
    ],
    "INDUSTRIAL01": [
        [
            ("In a linear-programming model, what do decision variables represent?", "The controllable quantities to be chosen", ["The optimal answer before solving", "Only measurement error", "The computer's processing speed"], "Decision variables encode choices such as production quantities and are linked to constraints and an objective.", "easy"),
            ("Why must units be consistent when formulating a linear constraint?", "Inconsistent units can make the constraint mathematically invalid", ["Units affect only the chart colour", "A solver automatically infers every unit", "Units are unnecessary in engineering models"], "Dimensional consistency helps ensure coefficients, variables, and right-hand sides represent compatible quantities.", "easy"),
        ],
        [
            ("What does the simplex method move between while solving a linear program?", "Feasible corner-point solutions of the constraint region", ["Random points outside every constraint", "Only the objective's units", "The rows of the input spreadsheet"], "Simplex pivots between basic feasible solutions and improves the objective until an optimality condition is met.", "intermediate"),
            ("What is a common interpretation of a dual variable in a resource constraint?", "The marginal change in the optimal objective for a small relaxation of that constraint", ["The count of decision variables", "The probability of infeasibility", "The variable's measurement unit only"], "A shadow price has a marginal interpretation under the model's assumptions and relevant sensitivity range.", "intermediate"),
        ],
        [
            ("In a balanced transportation model, what do row and column totals commonly represent?", "Supply at origins and demand at destinations", ["Unit shipping costs only", "Machine failure rates", "Project activity durations"], "The transportation tableau allocates shipments subject to supply, demand, and route-cost data.", "easy"),
            ("What distinguishes an assignment problem from a general transportation problem?", "It matches individual agents or resources to individual tasks, often one-to-one", ["It has no objective function", "It models only continuous fluid flow", "It forbids costs"], "Assignment is a structured special case with unit matching constraints.", "easy"),
        ],
        [
            ("What does the basic economic order quantity model balance?", "Ordering cost and inventory holding cost", ["Advertising cost and machine speed", "Queue waiting time and project slack", "Only purchase price and tax"], "EOQ balances replenishment and holding costs under simplifying assumptions such as steady demand.", "easy"),
            ("In a stable single-server queue, what happens as utilization approaches one?", "Expected waiting time tends to increase sharply", ["The queue disappears", "Service time becomes zero", "Arrival rate becomes negative"], "When arrivals nearly use all available service capacity, small variability can cause large delays.", "intermediate"),
        ],
        [
            ("In a project network, what does the critical path determine?", "The minimum project completion time given the modeled activity durations", ["The cheapest supplier", "The inventory reorder point", "The statistical process mean"], "The critical path is the longest-duration path through the precedence network and has zero total slack under the schedule.", "easy"),
            ("What is the effect of delaying an activity with zero total float?", "It delays the modeled project completion unless the schedule is changed", ["It increases unrelated inventory automatically", "It has no possible schedule effect", "It shortens every successor activity"], "A zero-float activity lies on the critical path in the current network schedule.", "easy"),
        ],
    ],
    "INDUSTRIAL02": [
        [
            ("Why use a time-series forecast baseline before adopting a complex demand model?", "It provides a transparent benchmark for judging added model value", ["It guarantees demand will not change", "It removes the need for historical data", "It proves causality"], "A simple baseline helps determine whether added complexity improves out-of-sample forecast performance.", "easy"),
            ("What is forecast bias?", "A persistent tendency for forecasts to overpredict or underpredict actual demand", ["Random variation around zero error only", "The average inventory level", "The supplier's delivery lead time"], "Bias describes systematic error, while accuracy metrics also reflect the magnitude of errors.", "easy"),
        ],
        [
            ("Which practice helps compare supplier bids fairly?", "Evaluate consistent specifications, total cost, quality, delivery, and risk criteria", ["Choose the lowest quoted unit price without context", "Ignore delivery performance", "Change criteria after reviewing each bid"], "Supplier selection should use transparent, relevant criteria, including total cost and operational risk.", "easy"),
            ("Why qualify a critical supplier before relying on it?", "To assess capability, quality controls, capacity, and continuity risks", ["To ensure it has no competitors", "To remove the need for incoming inspection", "To guarantee demand is constant"], "Qualification reduces risk but should be supported by monitoring and contingency planning.", "intermediate"),
        ],
        [
            ("What is the purpose of a reorder point in an inventory policy?", "Trigger replenishment early enough to cover lead-time demand and chosen protection", ["Set the product's selling price", "Calculate the supplier's carbon footprint only", "Determine a machine's cycle time"], "A reorder point commonly accounts for expected demand during lead time and may include safety stock.", "easy"),
            ("When is safety stock especially useful?", "When demand or replenishment lead time is uncertain and a service target is needed", ["When demand and lead time are guaranteed zero", "To eliminate all inventory records", "To increase stockouts intentionally"], "Safety stock buffers variability, with its amount tied to the service level and uncertainty assumptions.", "easy"),
        ],
        [
            ("What is a trade-off in distribution network design?", "Balancing facility and transport costs with service, inventory, and resilience", ["Choosing a colour for warehouses", "Eliminating all demand variation", "Maximizing distance regardless of cost"], "Network design balances fixed facility costs, flows, inventory, service times, and risk.", "easy"),
            ("Why might a firm use more than one distribution center?", "To improve proximity or resilience, while accepting additional facility and inventory costs", ["More centers always minimize total cost", "One center cannot store products", "It removes the need for forecasting"], "Additional centers can improve responsiveness but may increase fixed costs and duplicated stock.", "intermediate"),
        ],
        [
            ("What does supply-chain resilience emphasize?", "The ability to prepare for, absorb, and recover from disruptions", ["Keeping no information about suppliers", "Optimizing only for normal conditions", "Replacing all risk controls with extra inventory"], "Resilience combines visibility, mitigation, response, and recovery rather than relying on one measure.", "easy"),
            ("Why include environmental impacts in supply-chain decisions?", "Sourcing, transport, and packaging choices can shift lifecycle impacts", ["Environmental impacts are always zero after purchase", "It guarantees a lower unit price", "It replaces product safety requirements"], "Sustainability assessment should consider impacts across relevant lifecycle stages and trade-offs.", "intermediate"),
        ],
    ],
    "INDUSTRIAL03": [
        [
            ("What does a control chart help distinguish?", "Common-cause process variation from signals of special-cause change", ["Product cost from sales price", "A calibration standard from a sample label", "A process average from a customer identity"], "Control charts use limits and time order to detect evidence that a process may have changed.", "easy"),
            ("Why should control limits not be confused with specification limits?", "Control limits describe process behavior; specifications express requirements", ["Both are always set by the same formula", "Specifications measure the process mean only", "Control limits are customer tolerances"], "A stable process can still fail specifications, and a capable process should be assessed separately from statistical control.", "intermediate"),
        ],
        [
            ("What does a measurement-system study evaluate?", "Variation and bias introduced by the measurement process", ["Only the production schedule", "The product's selling price", "The machine's energy tariff"], "Measurement-system analysis checks whether measurement variation is acceptable for the intended decisions.", "easy"),
            ("Why calibrate a measuring instrument against traceable standards?", "To detect and quantify measurement error relative to a reference", ["To guarantee every future reading is exact", "To remove all operator influence automatically", "To increase the product specification width"], "Calibration establishes a documented relationship to standards and supports measurement traceability.", "easy"),
        ],
        [
            ("For a constant failure rate, what does the exponential reliability model describe?", "The probability a component operates without failure up to a given time", ["The component's purchase price", "The production takt time", "The probability of a supplier delay only"], "Under a constant hazard-rate assumption, reliability decreases exponentially with time.", "intermediate"),
            ("What is mean time between failures commonly used to summarize?", "Average operating time between failures for a repairable system under stated conditions", ["The time to manufacture one product", "The maximum possible system lifetime", "The period between calibration certificates"], "MTBF is a reliability summary for repairable items; it is not a guarantee for an individual unit.", "easy"),
        ],
        [
            ("In acceptance sampling, what decision is made from a sample?", "Accept or reject a lot according to a sampling plan", ["Set every unit's final selling price", "Estimate the process routing", "Choose a control-chart colour"], "Acceptance sampling makes a lot disposition decision with risks for both producer and consumer.", "easy"),
            ("What does an operating-characteristic curve show?", "The probability of lot acceptance at different quality levels", ["The machine's temperature profile", "The time to complete a project", "The distribution of supplier locations"], "The OC curve characterizes sampling-plan behavior and the protection it provides at specified defect levels.", "intermediate"),
        ],
        [
            ("Why use a fishbone diagram during root-cause investigation?", "Organize possible contributing causes for structured examination", ["Prove a suspected cause without evidence", "Replace measurement and experiments", "Calculate a product's tolerance automatically"], "Cause-and-effect diagrams support brainstorming and analysis but do not establish causality on their own.", "easy"),
            ("What is the purpose of a corrective-action effectiveness check?", "Confirm the action prevents recurrence without creating unacceptable side effects", ["Close the issue before implementation", "Avoid collecting follow-up evidence", "Assign blame to the operator"], "Follow-up evidence verifies that the action addressed the cause and remains effective.", "intermediate"),
        ],
    ],
    "INDUSTRIAL04": [
        [
            ("What is the purpose of method study in work systems?", "Develop a safer and more effective way to perform a task", ["Set a product's chemical composition", "Calculate a supplier's tax", "Replace all operator training"], "Method study records and critically examines work to improve flow, effort, and safety.", "easy"),
            ("Why map material and information flow before redesigning a work method?", "It can reveal unnecessary transport, delays, and handoffs", ["It makes demand constant", "It sets employee salaries", "It eliminates the need for observation"], "Process mapping makes the current method visible so improvement opportunities can be evaluated.", "easy"),
        ],
        [
            ("What should a time standard represent?", "The time a qualified worker needs at a defined performance level under specified conditions", ["The fastest time ever observed regardless of conditions", "The equipment's warranty period", "An unadjusted observation from one unusual cycle"], "A standard time accounts for a representative observed time, performance rating, and appropriate allowances.", "intermediate"),
            ("Why document the task and operating conditions when setting a time standard?", "The standard is meaningful only for the defined method and conditions", ["Time standards never change", "The task duration depends only on the calendar", "Documentation replaces ergonomic review"], "Method, equipment, product, and work conditions affect the validity and maintenance of a time standard.", "easy"),
        ],
        [
            ("What is an ergonomic risk factor in manual handling?", "High force, awkward posture, repetition, or sustained duration", ["A clear workstation label", "A calibrated torque tool", "A documented break schedule alone"], "Musculoskeletal risk depends on task demands and exposure; controls should address the relevant hazards.", "easy"),
            ("Why involve workers in ergonomic redesign?", "They can identify real task demands and evaluate whether controls work in practice", ["It removes the need for hazard assessment", "It guarantees no injuries can occur", "It makes workstation dimensions irrelevant"], "Worker participation provides useful task knowledge and helps assess the usability of proposed controls.", "easy"),
        ],
        [
            ("What is a common objective of facility-layout planning?", "Reduce unnecessary movement while meeting flow, safety, and space needs", ["Maximize travel distance", "Place every process at random", "Ignore material-handling routes"], "Layout decisions affect material flow, utilization, safety, and the ability to adapt to future changes.", "easy"),
            ("What is a key benefit of a cellular layout for product families?", "It can reduce travel and support smoother flow for similar products", ["It eliminates all setup time", "It forces every product through the same process", "It removes the need for capacity planning"], "Cells group resources around product families but require suitable volume, routing, and balance.", "intermediate"),
        ],
        [
            ("Why use leading safety indicators alongside injury counts?", "They can show whether preventive controls are being implemented before harm occurs", ["They guarantee zero incidents", "They replace incident investigation", "They count only production output"], "Leading indicators monitor preventive activity while outcome metrics capture harm; both need careful interpretation.", "intermediate"),
            ("Why interpret productivity measures with quality and safety measures?", "Output gains can be misleading if defects or risk increase", ["Quality and safety have no relation to operations", "Productivity is always independent of process conditions", "More output proves lower cost per good unit"], "Balanced measures reduce incentives to optimize one dimension at the expense of customer or worker outcomes.", "easy"),
        ],
    ],
    "INSTR01": [
        [
            ("What does measurement sensitivity describe?", "Change in instrument output per unit change in the measured input", ["The maximum operating temperature only", "The time between calibration certificates", "The instrument's physical mass"], "Sensitivity is the slope of the input-output relationship over a stated range.", "easy"),
            ("What is hysteresis in an instrument?", "Different output for the same input depending on the direction of approach", ["A constant output at every input", "A zero-length measurement range", "A perfectly linear calibration curve"], "Hysteresis is path-dependent response and can matter when inputs increase and decrease.", "intermediate"),
        ],
        [
            ("What does a differential-pressure flow meter infer from a measured pressure drop?", "Flow rate, using a calibrated relationship and fluid properties", ["Fluid colour only", "Pipe wall thickness without inspection", "The fluid's chemical formula"], "Differential-pressure devices relate pressure drop to flow; density, geometry, and installation affect the result.", "easy"),
            ("Why install a level instrument at a representative location in a tank?", "Local conditions such as turbulence or deposits can bias the reading", ["All locations give identical readings under all conditions", "Tank geometry has no effect on level measurement", "A sensor location sets liquid density"], "Sensor placement should account for tank geometry, flow disturbance, foam, and the measurement principle.", "intermediate"),
        ],
        [
            ("Which sensor is commonly used for contact temperature measurement over a broad industrial range?", "A thermocouple", ["A venturi meter", "A Bourdon pressure tube", "A magnetic flowmeter"], "Thermocouples use the Seebeck effect and are widely used for temperature measurement.", "easy"),
            ("Why use a thermowell with a temperature sensor in a pressurized process line?", "It provides a process barrier and allows sensor removal while limiting exposure", ["It converts temperature into flow", "It makes calibration unnecessary", "It guarantees zero response lag"], "Thermowells protect the sensor and process boundary but add thermal mass and response time.", "intermediate"),
        ],
        [
            ("What is measurement uncertainty intended to express?", "The range of values reasonably attributable to the measured quantity", ["A known error that can always be subtracted exactly", "The instrument's purchase price", "The number of readings collected"], "Uncertainty characterizes dispersion associated with a measurement result and its stated coverage.", "easy"),
            ("Why include repeatability and calibration contributions in an uncertainty budget?", "They are sources that can contribute to the result's combined uncertainty", ["They always cancel each other", "They replace the measured value", "They describe only the process setpoint"], "An uncertainty budget combines relevant components using a documented measurement model.", "intermediate"),
        ],
        [
            ("What is the purpose of a 4–20 mA industrial current loop's nonzero lower endpoint?", "It can distinguish a valid low reading from some fault conditions such as an open circuit", ["It makes current independent of the signal", "It encodes the sensor's serial number", "It prevents all electrical noise"], "The live zero supports fault detection, though exact fault interpretation depends on the device and standard.", "easy"),
            ("Why use shielded twisted-pair cable for a low-level instrumentation signal?", "It can reduce electromagnetic interference when installed and grounded appropriately", ["It increases the process pressure", "It removes the need for isolation in every design", "It converts analogue values to Ethernet"], "Twisting and shielding help control coupled noise; routing and grounding practices remain important.", "intermediate"),
        ],
    ],
    "INSTR02": [
        [
            ("What does a first-order process time constant indicate after a step input?", "The time to complete about 63% of the total response change", ["The time to reach an infinite output", "The controller's sampling frequency", "The steady-state gain by itself"], "For a first-order response, one time constant gives approximately 63.2% of the final change.", "easy"),
            ("Why does process dead time make feedback control more difficult?", "The controller acts on delayed information about the process response", ["It makes the process output instantaneous", "It removes measurement noise", "It guarantees stable control at any gain"], "Dead time adds phase lag and limits how aggressively feedback can be tuned.", "intermediate"),
        ],
        [
            ("In a negative-feedback loop, what happens when measured output is below setpoint?", "The controller responds according to its action and tuning to reduce the error", ["The controller must always close the valve", "The setpoint is deleted", "The sensor changes its calibration automatically"], "Negative feedback uses the error sign and controller action to drive the controlled variable toward setpoint.", "easy"),
            ("What is the role of a final control element in a feedback loop?", "Manipulate the process input, such as flow or heat, in response to the controller output", ["Store the operator password", "Measure the setpoint without a sensor", "Calculate the process model from scratch"], "Valves, drives, and dampers are common actuators that change a manipulated variable.", "easy"),
        ],
        [
            ("What can integral action help eliminate in a stable control loop?", "Persistent steady-state error to a constant load or setpoint change", ["All process dead time", "Every sensor fault", "The need for feedback"], "Integral action accumulates error and can remove offset, but excessive integral action may cause oscillation or windup.", "easy"),
            ("What is integral windup?", "Accumulation of integral error while the actuator is saturated", ["A sensor reading with the correct units", "A process with zero gain", "A proportional term changing sign each scan"], "Anti-windup methods limit or unwind the integrator when actuator saturation prevents the requested action.", "intermediate"),
        ],
        [
            ("In a step test, sustained growing oscillations after a tuning change indicate what concern?", "The closed-loop system may be unstable or insufficiently damped", ["The loop has no feedback path", "The process reached perfect steady state", "The measurement units are necessarily correct"], "Oscillation growth is evidence of poor stability; tuning should be evaluated against safety and performance limits.", "easy"),
            ("What does settling time measure?", "How long the response takes to remain within a specified band around its final value", ["The time to open a valve manually", "The steady-state process gain", "The controller's network address"], "Settling time depends on the response and the chosen tolerance band.", "easy"),
        ],
        [
            ("In a cascade-control structure, what is the inner loop usually designed to do?", "Correct a fast secondary variable that influences the primary controlled variable", ["Replace all sensors with one alarm", "Control a variable unrelated to the process", "Disable the primary controller"], "Cascade can reject disturbances at the secondary variable before they propagate to the primary variable.", "intermediate"),
            ("When is cascade control most useful?", "When a measurable secondary variable responds faster and reliably affects the primary variable", ["When the secondary variable cannot be measured", "When both loops use unrelated actuators", "Whenever a process has no disturbances"], "Cascade benefits depend on a suitable secondary measurement and a faster inner-loop response.", "intermediate"),
        ],
    ],
    "INSTR03": [
        [
            ("How does a strain gauge commonly convert deformation into an electrical signal?", "Its electrical resistance changes with strain", ["Its capacitance becomes a fluid pressure", "It emits light proportional to mass", "Its inductance measures pH directly"], "A bonded strain gauge changes resistance as its geometry and resistivity respond to deformation.", "easy"),
            ("Why place strain gauges in a Wheatstone bridge?", "The bridge can convert small resistance changes into a measurable differential voltage", ["It removes all temperature effects automatically", "It turns a DC sensor into a camera", "It calibrates the material's yield strength"], "Bridge circuits improve sensitivity to resistance changes; compensation and calibration are still required.", "intermediate"),
        ],
        [
            ("What physical property does an inductive proximity sensor detect well?", "Changes in an electromagnetic field caused by nearby conductive targets", ["Only transparent liquids", "Acoustic frequency in air", "The target's chemical pH"], "Inductive sensors detect conductive metal targets through a changing electromagnetic field.", "easy"),
            ("What does a Hall-effect sensor produce in response to?", "A voltage related to magnetic field when current flows through the sensing element", ["A pressure drop across an orifice", "A change in fluid viscosity only", "An optical image of the target"], "Hall sensors use the Hall voltage to detect magnetic fields, position, or speed.", "easy"),
        ],
        [
            ("Why use a thermistor in temperature sensing?", "Its resistance changes substantially with temperature", ["Its output is a direct pressure measurement", "It produces a flow rate without fluid", "Its resistance is fixed by definition"], "Thermistors have a temperature-dependent resistance and need suitable linearization and range consideration.", "easy"),
            ("What is a photodiode used to detect?", "Incident optical radiation", ["Mechanical torque without strain", "Liquid level by hydrostatic pressure", "Magnetic flux without a magnetic element"], "A photodiode converts incident light into electrical current, with response dependent on wavelength and circuit configuration.", "easy"),
        ],
        [
            ("What does a low-pass filter do to a sensor signal?", "Attenuates frequency components above its cutoff region", ["Amplifies every frequency equally", "Converts voltage to temperature units", "Removes all DC content by definition"], "A low-pass filter reduces higher-frequency content while retaining lower-frequency components, subject to its design.", "easy"),
            ("Why can an instrumentation amplifier help with a bridge sensor?", "It amplifies a small differential signal while rejecting common-mode voltage", ["It forces both input terminals to ground", "It turns analogue readings into mechanical motion", "It guarantees no noise can enter the circuit"], "Instrumentation amplifiers are designed for accurate differential measurements with high input impedance and common-mode rejection.", "intermediate"),
        ],
        [
            ("Why should a smart sensor retain calibration and configuration metadata?", "It helps interpret readings and maintain traceability across devices and time", ["It makes the sensing element never drift", "It replaces all maintenance records", "It reveals the user's account password"], "Metadata supports interpretation and lifecycle management but cannot eliminate drift or verification needs.", "easy"),
            ("What is a useful response when a smart sensor reports a diagnostic fault?", "Check the fault meaning, wiring, operating conditions, and device health before trusting the reading", ["Ignore the fault if the value looks familiar", "Delete the calibration history", "Assume every fault is a network delay"], "Diagnostics should be interpreted with the device documentation and process context.", "intermediate"),
        ],
    ],
    "INSTR04": [
        [
            ("What is a transfer function for a linear time-invariant system with zero initial conditions?", "The ratio of output transform to input transform", ["The ratio of sensor cost to actuator cost", "A list of sampled alarm names", "A plot of noise without an input"], "The transfer function represents input-output dynamics in the transform domain under stated assumptions.", "easy"),
            ("Why are poles of a transfer function important?", "They strongly determine natural response and stability", ["They determine the wiring colour", "They equal the input units", "They specify the sampling timestamp"], "Pole locations influence modes, damping, and stability for the modeled system.", "intermediate"),
        ],
        [
            ("What does percent overshoot describe in a step response?", "The peak amount above the final value relative to the response change", ["The steady-state error in sensor units only", "The system's number of inputs", "The time between two samples"], "Overshoot is a transient-response measure commonly used with rise time and settling time.", "easy"),
            ("For a stable system, what is steady-state error evaluated after?", "Transient effects have decayed under the specified input and conditions", ["Before the system receives an input", "Only while the actuator is disconnected", "When all model parameters are unknown"], "Steady-state error compares the long-term output with the desired reference for a defined input.", "easy"),
        ],
        [
            ("In root-locus analysis, what is varied to trace closed-loop pole locations?", "A feedback gain parameter", ["The plant's coordinate origin", "The sensor serial number", "The sampling clock's colour"], "Root locus shows how closed-loop poles move as a scalar loop gain varies.", "easy"),
            ("Why add a compensator in a root-locus design?", "Shape closed-loop pole locations to improve stability or response requirements", ["Make the plant's input physically disappear", "Guarantee zero uncertainty", "Replace the feedback sensor"], "Compensator poles and zeros can shape the locus, but model assumptions and implementation limits must be checked.", "intermediate"),
        ],
        [
            ("What does phase margin indicate in frequency-response analysis?", "A relative measure of stability robustness at the gain crossover", ["The process's final temperature", "The number of controller outputs", "The sensor's static accuracy"], "Phase margin is a frequency-domain stability measure; interpretation assumes the loop model and convention are appropriate.", "intermediate"),
            ("What does a Bode magnitude plot show?", "Gain magnitude as a function of frequency", ["Controller code length against memory", "Position against map scale", "Sampling date against sensor name"], "Bode plots show magnitude and phase versus logarithmic frequency.", "easy"),
        ],
        [
            ("What is the Nyquist sampling condition for a band-limited signal?", "Sampling frequency must exceed twice the highest signal frequency to avoid aliasing", ["Sampling frequency must equal zero", "Every signal must be sampled once per day", "Quantization removes the need for sampling"], "The Nyquist criterion assumes band-limited content and ideal conditions; practical systems also need anti-alias filtering.", "easy"),
            ("Why include an anti-alias filter before an ADC?", "Attenuate frequency content that would fold into the sampled band", ["Increase the ADC's number of bits", "Guarantee no quantization error", "Convert a digital output to an analogue input"], "An analogue anti-alias filter limits out-of-band energy before sampling.", "intermediate"),
        ],
    ],
    "MARINE01": [
        [
            ("What does the ideal Diesel-cycle model add heat at approximately constant?", "Pressure", ["Volume", "Entropy", "Density"], "In the air-standard Diesel cycle, heat addition is modeled as constant pressure.", "easy"),
            ("Why does a real marine diesel engine have lower efficiency than an ideal cycle model predicts?", "Combustion, heat transfer, friction, pumping, and finite-rate effects cause losses", ["The ideal model includes every loss", "Real fuel has no chemical energy", "Engine speed cannot affect operation"], "Ideal cycle analyses omit or simplify losses that matter in an actual engine.", "intermediate"),
        ],
        [
            ("What does propeller pitch represent geometrically?", "The theoretical axial advance per revolution in an idealized screw motion", ["The blade's paint thickness", "The ship's rudder angle", "The engine's compression ratio"], "Pitch describes the helix-like advance; slip and wake make actual advance differ from the ideal value.", "easy"),
            ("What is propeller cavitation?", "Formation and collapse of vapour cavities when local pressure falls sufficiently", ["Combustion inside the cylinder", "A change in seawater salinity", "A shaft alignment procedure"], "Cavitation can cause noise, vibration, erosion, and performance loss.", "easy"),
        ],
        [
            ("Why match an engine operating point to the propeller load curve?", "To ensure the combined system operates efficiently within safe engine limits", ["Propeller load is independent of engine speed", "It removes the need for a gearbox", "It guarantees constant thrust at all speeds"], "Engine-propeller matching affects fuel use, manoeuvring, and overload risk across operating conditions.", "intermediate"),
            ("What can an oversized fixed-pitch propeller do to an engine at high load?", "Cause the engine to overload or fail to reach its rated speed", ["Reduce propeller torque to zero", "Eliminate wake effects", "Make engine cooling unnecessary"], "Propeller load must be compatible with engine ratings and vessel operating profile.", "easy"),
        ],
        [
            ("Why is lubricating-oil analysis used in marine maintenance?", "It can reveal wear particles, contamination, or oil degradation", ["It directly measures vessel displacement", "It replaces all engine inspections", "It identifies the ship's route from colour alone"], "Oil condition monitoring supports maintenance decisions but should be combined with other evidence.", "easy"),
            ("What is the purpose of fuel filtration before injection equipment?", "Protect precision components from particles and contaminants", ["Increase fuel's water content", "Change the engine's compression ratio", "Remove the need for storage controls"], "Clean fuel helps protect pumps and injectors; filtration and water separation are selected for the system.", "easy"),
        ],
        [
            ("Why measure specific fuel oil consumption at a defined engine load?", "Fuel consumption depends on operating point and must be compared on a consistent basis", ["Fuel use is identical at every load", "It measures propeller diameter only", "It eliminates exhaust monitoring"], "Specific fuel consumption is load-dependent and comparisons need consistent measurement boundaries and conditions.", "intermediate"),
            ("Which change can reduce local air-pollutant emissions from a marine engine?", "Use compliant fuel or exhaust treatment appropriate to the pollutant and regulations", ["Disable engine monitoring", "Increase oil contamination", "Remove all maintenance intervals"], "Emission controls may include fuel choices and after-treatment, and must meet applicable rules and operating needs.", "easy"),
        ],
    ],
    "MARINE02": [
        [
            ("What is the purpose of a centrifugal pump's impeller?", "Transfer energy to the fluid and increase its velocity and pressure", ["Measure the liquid's salinity", "Remove the need for a suction line", "Control a boiler's flame directly"], "The rotating impeller imparts energy; the casing converts part of velocity head to pressure.", "easy"),
            ("Why can a pump lose prime?", "Air or vapour in the casing or suction line prevents effective liquid pumping", ["The discharge pressure is always too high", "The pump has too much lubrication", "The sea-water temperature is constant"], "Many centrifugal pumps require a liquid-filled casing; air ingress or vaporization can disrupt pumping.", "intermediate"),
        ],
        [
            ("What does a boiler safety valve protect against?", "Pressure exceeding the permitted limit", ["Low lighting in the engine room", "Excessive propeller pitch", "Salt concentration in cooling water"], "A correctly selected and maintained safety valve provides overpressure protection.", "easy"),
            ("Why maintain a heat exchanger's seawater-side surfaces?", "Fouling and corrosion can reduce heat transfer and damage the equipment", ["To increase the oil's viscosity", "To change the ship's trim", "To eliminate the need for flow control"], "Marine heat exchangers are exposed to fouling and corrosive conditions that affect performance.", "easy"),
        ],
        [
            ("What is the purpose of a refrigeration expansion valve?", "Meter refrigerant into the evaporator while reducing its pressure", ["Compress refrigerant vapour", "Remove heat from the condenser by combustion", "Measure the ship's draft"], "The expansion device throttles refrigerant, enabling low-pressure evaporation downstream.", "easy"),
            ("Why is ventilation important in a shipboard machinery space?", "It helps manage heat, contaminants, and safe working conditions", ["It increases bilge-water salinity", "It replaces fire detection", "It makes refrigerant leak response unnecessary"], "Ventilation supports thermal management and air quality but must be coordinated with fire and hazardous-area controls.", "intermediate"),
        ],
        [
            ("In a hydraulic steering system, what does the actuator do?", "Convert hydraulic pressure and flow into rudder movement", ["Generate electrical frequency", "Measure hull thickness", "Filter combustion exhaust"], "Hydraulic cylinders or rotary actuators apply force to move the steering gear.", "easy"),
            ("Why inspect hydraulic hoses and fittings periodically?", "Leaks, damage, or degradation can cause loss of control and environmental release", ["Hydraulic fluid never degrades", "Hose condition cannot affect operation", "Inspection changes the rudder's geometry"], "Condition monitoring and maintenance help prevent failures in a critical control system.", "easy"),
        ],
        [
            ("What is a useful first step when diagnosing an auxiliary-system fault?", "Confirm the symptom, operating state, alarms, and relevant measurements", ["Replace every component at once", "Disable the alarm without investigation", "Assume the fault is always electrical"], "Structured fault diagnosis starts with evidence and system conditions before testing likely causes.", "easy"),
            ("Why record maintenance actions and measured values in a fault report?", "They support trend analysis, handover, and verification of the repair", ["They guarantee the fault can never recur", "They replace safe isolation procedures", "They remove the need for manuals"], "Accurate maintenance records improve continuity and help determine whether a corrective action worked.", "easy"),
        ],
    ],
    "MARINE03": [
        [
            ("What is the moulded breadth of a ship?", "Its maximum transverse dimension measured to the specified moulded lines", ["Its forward speed at sea", "The propeller's pitch", "The vertical distance from keel to waterline only"], "Breadth is a principal hull dimension; exact definitions depend on the reference convention used.", "easy"),
            ("What does a ship's displacement represent?", "The weight of water displaced, equal to ship weight when floating in equilibrium", ["The engine's swept volume", "The cargo hold's length", "The ship's cruising distance"], "By Archimedes' principle, a floating vessel displaces a weight of water equal to its own weight.", "easy"),
        ],
        [
            ("What does the metacentric height GM indicate for small-angle stability?", "The initial tendency of a ship to return toward upright after a small heel", ["The vessel's maximum speed", "The water salinity", "The propeller's blade count"], "Positive initial GM generally indicates positive initial stability, though excessive values can produce uncomfortable motion.", "intermediate"),
            ("Why can free liquid in a partially filled tank reduce a ship's stability?", "The moving liquid's free-surface effect reduces effective metacentric height", ["The liquid raises the metacentre automatically", "It eliminates heel in all conditions", "It changes the hull's breadth"], "Free-surface correction accounts for fluid shift and can reduce effective stability.", "intermediate"),
        ],
        [
            ("What is a ship's block coefficient a measure of?", "Hull volume relative to a rectangular block based on length, breadth, and draft", ["Propeller efficiency alone", "The ratio of crew to passengers", "The ship's electrical load"], "The block coefficient indicates fullness of hull form and influences resistance and capacity.", "easy"),
            ("Why is the Froude number relevant to ship resistance?", "It relates speed to gravity-wave effects and helps characterize wave-making behavior", ["It measures fuel sulphur content", "It is the ratio of rudder angle to draft", "It replaces Reynolds number in every flow regime"], "Froude similarity is important for free-surface and wave-making effects in model testing.", "intermediate"),
        ],
        [
            ("Why design a ship's structure for wave-induced bending loads?", "The hull girder experiences changing longitudinal stresses in waves", ["Wave loads affect only paint colour", "Ships in waves have no structural loads", "Hull girder strength depends only on engine speed"], "Longitudinal wave bending can create hogging and sagging stresses that structural design must consider.", "easy"),
            ("What is a watertight bulkhead intended to do?", "Limit flooding spread and subdivide the hull", ["Increase propeller cavitation", "Control the radio frequency", "Replace all bilge systems"], "Subdivision improves damage containment, subject to the vessel's arrangement and safety requirements.", "easy"),
        ],
        [
            ("What does a ship's response amplitude operator (RAO) describe?", "Motion response per unit wave amplitude across frequency or heading conditions", ["Fuel use per crew member", "The number of cargo compartments", "A propeller's material hardness"], "RAOs characterize linearized motion response under specified conditions and assumptions.", "intermediate"),
            ("Why can resonance increase a vessel's motion response?", "Wave encounter frequency can approach a natural motion frequency", ["It makes wave amplitude zero", "It stops all damping", "It changes the ship's length automatically"], "Near resonance, response can grow depending on damping, forcing, and the system's natural frequency.", "easy"),
        ],
    ],
    "MARINE04": [
        [
            ("What is the purpose of an alternator in a shipboard generator set?", "Convert mechanical shaft power into electrical power", ["Convert seawater into cooling oil", "Control the rudder angle", "Measure fuel viscosity"], "The alternator generates electrical output from mechanical rotation through electromagnetic induction.", "easy"),
            ("Why synchronize an incoming generator before connecting it to a live bus?", "Match voltage, frequency, phase sequence, and phase angle within limits", ["Ensure its fuel tank is full", "Reverse the ship's shaft", "Disconnect all protective relays"], "Synchronizing prevents severe electrical and mechanical transients when paralleling sources.", "intermediate"),
        ],
        [
            ("What does an overcurrent protective device respond to?", "Current exceeding its defined time-current operating characteristic", ["A change in hull draft", "A low refrigerant level", "A radio call sign"], "Breakers and fuses interrupt overcurrent according to ratings and coordination design.", "easy"),
            ("Why coordinate protective devices in a shipboard distribution system?", "Isolate a fault as selectively as practical while maintaining protection", ["Make every breaker trip simultaneously", "Remove all short-circuit protection", "Change load frequency"], "Selectivity limits the portion of the system lost during a fault; it depends on device characteristics and fault levels.", "intermediate"),
        ],
        [
            ("What is one advantage of electric propulsion for a vessel?", "Flexible placement and control of propulsion power can suit the operating profile", ["It removes all conversion losses", "It never needs electrical protection", "It makes propeller loading irrelevant"], "Electric drives can offer flexible power management, but conversion losses, cooling, and system complexity remain.", "easy"),
            ("Why monitor motor temperature in an electric propulsion system?", "Overheating can indicate overload, cooling problems, or insulation risk", ["Temperature determines the ship's longitude", "Motors cannot be damaged by heat", "It replaces current protection"], "Temperature monitoring provides a condition signal but should complement electrical and mechanical protection.", "easy"),
        ],
        [
            ("What does a machinery alarm-and-monitoring system help operators do?", "Detect abnormal conditions and respond using prioritized indications", ["Automatically remove every failure cause", "Replace all local inspections", "Change machinery design without approval"], "Monitoring supports situational awareness; alarm limits, validation, and operator procedures are essential.", "easy"),
            ("Why should alarms be prioritized and rationalized?", "Reduce nuisance and low-value alarms so important conditions remain actionable", ["Increase the alarm count regardless of value", "Hide safety-critical indications", "Eliminate operator procedures"], "Alarm management aims to make each alarm meaningful, timely, and linked to an operator response.", "intermediate"),
        ],
        [
            ("Why use protective earthing and bonding in ship electrical installations?", "Provide fault-current paths and reduce hazardous touch-voltage differences", ["Increase fuel pressure", "Prevent all insulation failures", "Replace overcurrent protection"], "Earthing and bonding support fault protection and equipotentiality, subject to the vessel's electrical design.", "easy"),
            ("What should be done before electrical maintenance on an isolated circuit?", "Verify isolation and absence of voltage using approved safe-work procedures", ["Rely only on a panel label", "Assume the breaker is open without checking", "Bridge the protective earth"], "Safe electrical work requires appropriate isolation, verification, and controls for the system and task.", "easy"),
        ],
    ],
    "MECHATRONICS01": [
        [
            ("What does a microcontroller's program counter usually hold?", "The address of the next instruction to be fetched or executed", ["The analogue sensor voltage", "The system's supply current", "The stack's maximum size"], "The program counter tracks instruction flow, with exact update behavior defined by the architecture.", "easy"),
            ("Why consult a microcontroller datasheet before connecting a peripheral?", "Pin functions, voltage limits, timing, and electrical capabilities vary by device", ["All microcontrollers have identical pins", "Datasheets are only product advertisements", "A datasheet removes the need for testing"], "The device documentation defines electrical and timing constraints needed for safe integration.", "easy"),
        ],
        [
            ("Why should an interrupt service routine generally be short?", "Long handlers can delay other time-critical work and increase latency", ["Short handlers use more supply voltage", "Interrupts cannot change program flow", "It prevents the processor from returning"], "A short ISR captures essential state and defers heavier processing to the main loop or a task.", "easy"),
            ("What is a timer peripheral commonly used for in an embedded system?", "Generate periodic events or measure time intervals", ["Store source code permanently", "Measure chemical concentration without a sensor", "Replace every communication bus"], "Hardware timers support periodic scheduling, pulse measurement, and other time-based tasks.", "easy"),
        ],
        [
            ("What is SPI commonly used for?", "Synchronous serial communication between a controller and peripherals", ["Wireless routing without a radio", "Analogue power conversion", "A mechanical shaft connection"], "SPI uses clock and data signals with device selection and is common for short-distance board-level peripherals.", "easy"),
            ("Why can I2C support multiple devices on two signal wires?", "Devices share clock and data lines and are selected by address or protocol mechanism", ["Every device has a separate clock wire", "It transmits using hydraulic pressure", "It requires no pull-up behavior"], "I2C uses shared SDA/SCL lines with addressing and electrical requirements such as pull-ups.", "intermediate"),
        ],
        [
            ("In a fixed-priority preemptive scheduler, what happens when a higher-priority task becomes ready?", "It can preempt a lower-priority task", ["The processor shuts down", "The lower-priority task becomes a hardware interrupt", "Task priorities are ignored"], "Preemption allows a ready higher-priority task to run, subject to scheduler and critical-section rules.", "easy"),
            ("What is a deadline miss in a real-time system?", "A computation completes after its required completion time", ["A task uses less memory than expected", "A sensor returns a valid sample", "The scheduler selects the highest priority"], "Real-time correctness includes timing constraints, so a late result may be incorrect for the application.", "easy"),
        ],
        [
            ("What does a hardware watchdog do if software stops servicing it?", "Reset or otherwise recover the system according to its configuration", ["Increase CPU clock indefinitely", "Rewrite the application safely", "Calibrate every sensor"], "A watchdog detects lack of expected progress and can trigger a defined recovery action.", "easy"),
            ("Why use a logic analyzer when debugging a digital peripheral interface?", "Observe signal timing and protocol transitions on the wires", ["Measure polymer viscosity", "Replace the system clock", "Inspect a database schema"], "A logic analyzer helps compare bus activity with the expected protocol and timing.", "easy"),
        ],
    ],
    "MECHATRONICS02": [
        [
            ("What is calibration intended to establish for a sensor?", "A documented relationship between its indication and reference values", ["A guarantee that it can never drift", "A new physical quantity", "A way to remove all environmental effects"], "Calibration compares indications to reference standards; adjustment and uncertainty are separate considerations.", "easy"),
            ("Why choose a sensor range that covers expected peaks with margin?", "Avoid saturation while retaining adequate resolution for the operating range", ["Make every reading equal to full scale", "Increase noise deliberately", "Remove the need for overload protection"], "Range selection balances overload margin and useful resolution for the measurement task.", "intermediate"),
        ],
        [
            ("What does an incremental encoder commonly provide?", "Pulses that indicate relative motion and, with suitable channels, direction", ["Absolute temperature without electronics", "Fluid pressure directly", "The rotor's material composition"], "Incremental encoders produce counts as a shaft moves; homing may be needed to establish absolute position.", "easy"),
            ("What is a resolver used to measure?", "Angular position, often using sine and cosine signals", ["Liquid pH", "Airborne particle concentration", "Linear pressure drop"], "Resolvers provide robust angular position information and require signal excitation and decoding.", "easy"),
        ],
        [
            ("What does a pneumatic directional-control valve do?", "Route compressed air to control actuator motion", ["Measure motor winding resistance", "Set a camera's focal length", "Remove particles from a digital image"], "Directional valves control the path of compressed air to pneumatic actuators.", "easy"),
            ("Why include pressure regulation in a pneumatic actuator circuit?", "Maintain suitable operating pressure and force within system limits", ["Make air incompressible", "Eliminate the need for a valve", "Convert air pressure directly into data"], "Pressure regulation helps control actuator force and protect components, within the circuit design.", "easy"),
        ],
        [
            ("What does a variable-frequency drive control for an AC motor?", "The frequency and voltage supplied to influence speed and torque", ["The motor's bearing material", "The power-grid location", "The sensor's sampling language"], "A VFD adjusts electrical supply to control motor operation; the motor and load characteristics matter.", "easy"),
            ("Why consider motor-load inertia when tuning a motion axis?", "It affects acceleration, deceleration, and control response", ["It sets the sensor's colour", "It removes torque limits", "It guarantees zero overshoot"], "The combined inertia and drive limits influence achievable motion and stability.", "intermediate"),
        ],
        [
            ("Why add a low-pass filter to a noisy sensor channel?", "Reduce high-frequency noise that is not needed for the control task", ["Increase all noise components", "Change the sensor's physical range", "Make sampling theory irrelevant"], "Filtering can reduce noise but adds delay and should preserve relevant signal dynamics.", "easy"),
            ("What can happen if a sensor signal is sampled too slowly?", "Rapid signal changes may be missed or appear as a false lower-frequency pattern", ["The analogue signal becomes perfectly smooth", "The sensor creates new physical information", "Quantization disappears"], "Insufficient sampling can cause aliasing and poor representation of changing signals.", "intermediate"),
        ],
    ],
    "MECHATRONICS03": [
        [
            ("What should a system requirement state to be testable?", "A measurable behavior or constraint under defined conditions", ["A vague aspiration with no acceptance criterion", "Only the designer's preferred tool", "A result that cannot be observed"], "Testable requirements are specific enough to verify against acceptance criteria.", "easy"),
            ("Why use a block diagram during mechatronic design?", "Show subsystem functions and signal or energy interfaces", ["Replace all detailed calculations", "Choose the final paint colour", "Hide dependencies between components"], "Block diagrams help communicate system structure and interfaces early in design.", "easy"),
        ],
        [
            ("Why check mechanical stiffness when mounting a position sensor?", "Mounting flex can create measurement error or alter system dynamics", ["Stiffness controls the sensor's communication protocol", "Flexible mounting always improves accuracy", "It prevents all electrical noise"], "Sensor mounting is part of the measurement chain and can affect alignment and dynamic response.", "intermediate"),
            ("What is one benefit of co-designing mechanical and electrical subsystems?", "Interfaces, loads, packaging, and performance can be resolved together", ["It removes the need for system validation", "It guarantees every component is compatible", "It eliminates safety requirements"], "Integrated design helps uncover cross-domain constraints before they become costly interface failures.", "easy"),
        ],
        [
            ("Why implement closed-loop control on a microcontroller rather than rely only on a preset command?", "Feedback can adjust actuation based on measured error", ["It guarantees the sensor is perfect", "It eliminates actuator limits", "It makes timing irrelevant"], "Feedback uses measurements to correct deviations, subject to sampling, model, and actuator constraints.", "easy"),
            ("Why choose a control-loop sampling period based on system dynamics?", "Sampling that is too slow can degrade response or destabilize the loop", ["Sampling period changes the sensor material", "Any sampling rate is equally suitable", "A controller needs only one sample"], "Sampling and computation delay affect digital control performance and stability.", "intermediate"),
        ],
        [
            ("What is a safe response when a sensor value becomes implausible during operation?", "Detect the fault and move the system to a defined safe or degraded state", ["Continue maximum actuation without checks", "Delete the alarm and hide the value", "Assume the sensor is correct"], "Fault handling should define detection, safe response, and recovery for the system hazard analysis.", "easy"),
            ("Why consider fail-safe behavior during actuator selection?", "The system should respond predictably if power, signal, or control is lost", ["Actuators never fail", "Fail-safe position has no safety effect", "It replaces emergency procedures"], "Fail-safe state depends on the hazard and application and should be engineered and verified.", "intermediate"),
        ],
        [
            ("Why prototype a subsystem before committing to a full production design?", "Test key assumptions and interfaces while changes are relatively inexpensive", ["A prototype proves production reliability by itself", "It removes the need for specifications", "It guarantees users will prefer the design"], "Prototyping is an evidence-gathering step, not a substitute for qualification and validation.", "easy"),
            ("What is the purpose of a validation test against system requirements?", "Show that the integrated system meets its intended use and acceptance criteria", ["Measure only component purchase cost", "Replace design reviews", "Avoid recording test conditions"], "Validation checks the resulting system against requirements under documented conditions.", "easy"),
        ],
    ],
    "MECHATRONICS04": [
        [
            ("In PLC ladder logic, what does a normally-open contact instruction typically test?", "Whether its associated Boolean condition is true", ["Whether a motor has an open housing", "The line voltage's frequency", "A timer's physical enclosure"], "A normally-open ladder contact evaluates a logical condition; actual I/O wiring and instruction semantics should be checked.", "easy"),
            ("Why use a seal-in circuit or latch carefully in ladder logic?", "It maintains a state after a momentary command and needs a defined reset condition", ["It eliminates all interlocks", "It makes an input permanently true", "It removes the PLC scan cycle"], "Latching logic is useful but must have explicit stop, reset, and safety behavior.", "intermediate"),
        ],
        [
            ("Why debounce a mechanical switch input?", "Contact bounce can create multiple rapid transitions from one physical action", ["It increases sensor range", "It changes motor rotation", "It removes a PLC output"], "Debouncing filters short transitions caused by mechanical contacts.", "easy"),
            ("What should be verified before wiring an industrial sensor to a PLC input?", "Supply, signal type, input rating, polarity, and isolation requirements", ["Only its housing colour", "The network's DNS name", "A production forecast"], "Electrical compatibility and field wiring practices prevent damage and invalid signals.", "easy"),
        ],
        [
            ("What is SCADA commonly used to provide?", "Supervisory monitoring, alarms, and control across distributed equipment", ["A replacement for every local safety interlock", "A method for machining a valve seat", "An analogue sensor element"], "SCADA systems collect and present data and supervisory commands; local controls and safety layers remain important.", "easy"),
            ("Why control access to SCADA operator commands?", "Unauthorized or mistaken commands can affect physical processes", ["It improves image resolution", "It eliminates the need for backups", "It makes field sensors unnecessary"], "Industrial control actions can have operational consequences, so access and change controls matter.", "easy"),
        ],
        [
            ("What is a fieldbus or industrial Ethernet protocol used for?", "Exchange data between controllers, field devices, and supervisory systems", ["Increase hydraulic pressure", "Measure polymer crystallinity directly", "Replace all electrical protection"], "Industrial communication links control and instrumentation devices using defined protocols and timing properties.", "easy"),
            ("Why segment industrial control networks?", "Limit unintended traffic and reduce the impact of faults or security incidents", ["Make every device publicly reachable", "Remove the need for device identity", "Guarantee every packet arrives instantly"], "Segmentation supports security and operational resilience but requires sound routing, monitoring, and maintenance.", "intermediate"),
        ],
        [
            ("What should a safety interlock do when a required guard condition is false?", "Prevent or stop the hazardous operation according to the risk assessment", ["Ignore the guard to preserve throughput", "Disable every alarm", "Increase actuator force"], "Safety functions are designed to reduce defined risks and must be validated to the required performance level.", "easy"),
            ("Why perform commissioning checks on an automation system before handover?", "Verify I/O, sequences, interlocks, alarms, and operating documentation in the installed system", ["Assume simulation guarantees field wiring", "Skip tests if the PLC compiles", "Change safety limits without approval"], "Commissioning verifies installed behavior and records results against approved requirements.", "intermediate"),
        ],
    ],
    "MINING02": [
        [
            ("What is the purpose of a preliminary surface-mine pit optimization?", "Identify a set of economically attractive blocks subject to slope and mining constraints", ["Set the mine's office location", "Guarantee a fixed commodity price", "Remove the need for geotechnical data"], "Pit optimization evaluates block values and constraints; the result depends on assumptions and is not a final design by itself.", "intermediate"),
            ("Why update a surface-mine plan when geological estimates change?", "The mine sequence and economic limits may change with new information", ["Orebody boundaries never affect design", "Equipment capacity is unlimited", "A previous plan is always optimal"], "Planning is iterative because grade, costs, prices, and geotechnical constraints affect extraction decisions.", "easy"),
        ],
        [
            ("Why use a burden and spacing design in production blasting?", "Control energy distribution and fragmentation while managing vibration and safety", ["Set the truck's payload", "Determine the ore's chemical formula", "Avoid all ground monitoring"], "Blast geometry influences fragmentation, throw, vibration, and operational risk.", "intermediate"),
            ("Why establish an exclusion zone before a blast?", "Protect people and assets from flyrock, airblast, and other hazards", ["Increase the explosive charge after firing", "Improve ore grade", "Replace the blast plan"], "Blast clearance and exclusion procedures are critical controls defined by the approved blast plan.", "easy"),
        ],
        [
            ("What does a mine haulage cycle time include?", "Loading, travel, dumping, and return components as defined for the route", ["Only the truck's purchase time", "The mineral's geological age", "The shift supervisor's commute"], "Cycle-time estimates support fleet sizing and production planning and should reflect actual operating conditions.", "easy"),
            ("Why coordinate shovel capacity with truck fleet size?", "A mismatch can leave the loading unit or haulage fleet waiting", ["Truck and shovel rates are independent", "It changes the deposit's grade", "It eliminates road maintenance"], "Fleet matching balances loading and haulage capacities to reduce avoidable idle time.", "easy"),
        ],
        [
            ("Why use a factor of safety in slope-stability assessment?", "Represent uncertainty and provide a margin against failure for the defined model", ["It guarantees a slope can never fail", "It replaces groundwater analysis", "It is the same as the slope angle"], "A factor of safety compares resisting and driving effects under assumptions; uncertainty and consequences also matter.", "intermediate"),
            ("How can pore-water pressure affect a soil or rock slope?", "It can reduce effective stress and lower shear resistance", ["It always increases rock strength", "It changes only the surface colour", "It has no effect on stability"], "Elevated pore pressure can reduce effective normal stress and therefore decrease available shear strength.", "intermediate"),
        ],
        [
            ("Why plan progressive rehabilitation during mine operation?", "It can reduce long-term disturbance and make closure more manageable", ["It increases the need for uncontrolled runoff", "It replaces environmental monitoring", "It guarantees no post-closure obligations"], "Progressive rehabilitation can reduce exposure and test closure methods before the final mine closure.", "easy"),
            ("What should a mine-water management plan consider?", "Runoff, contact water, groundwater, treatment needs, and discharge requirements", ["Only the mine's office supply", "Ore grade but not water flow", "The colour of haul roads"], "Integrated water planning protects operations and receiving environments through the mine lifecycle.", "easy"),
        ],
    ],
    "MINING03": [
        [
            ("Why develop mine access before stoping production underground?", "Provide safe routes for people, equipment, ventilation, and ore movement", ["Set a surface pit limit", "Increase roof pressure", "Replace ground-support design"], "Development establishes access and services needed for safe, sequenced production.", "easy"),
            ("Why coordinate headings with ventilation and escape routes?", "Development can change air paths and emergency access", ["Ventilation is independent of mine layout", "It eliminates the need for monitoring", "Escape routes are used only for ore haulage"], "Underground development must maintain safe ventilation and egress as the mine expands.", "intermediate"),
        ],
        [
            ("What is a key design requirement for room-and-pillar mining?", "Pillars must support the overlying strata while allowing planned extraction", ["Remove every pillar immediately", "Ignore roof conditions", "Use only surface haulage"], "Pillar dimensions and extraction sequence depend on geology, stress, depth, and safety factors.", "easy"),
            ("Why might a pillar-recovery plan require additional geotechnical review?", "Removing support can alter load redistribution and ground-control risk", ["Pillars carry no load", "Recovery always improves stability", "It changes only the ventilation fan colour"], "Pillar recovery changes the support system and requires assessment of sequencing and consequences.", "intermediate"),
        ],
        [
            ("In longwall mining, what does the powered support system primarily do?", "Support the roof near the face and advance with the mining sequence", ["Pump crude oil to surface", "Measure ore grade by colour", "Replace conveyor controls"], "Hydraulic roof supports maintain a protected working area and advance as the face progresses.", "easy"),
            ("What is the purpose of a longwall shearer or cutting machine?", "Cut the coal or target seam along the production face", ["Support the mine roof", "Condition mine air", "Survey the surface lease boundary"], "The cutting machine extracts material at the face while supports and conveyors manage the production sequence.", "easy"),
        ],
        [
            ("Why install rock bolts as part of ground support?", "Reinforce and retain fractured rock near an excavation", ["Increase the ore's grade", "Measure ventilation quantity", "Replace all geological mapping"], "Rock bolts improve the stability of a rock mass by tying discontinuities or supporting the near-surface zone.", "easy"),
            ("What can convergence monitoring reveal in an underground opening?", "Deformation that may indicate changing ground conditions", ["The mineral's atomic number", "Truck fuel quality", "The mine's surface rainfall only"], "Convergence trends can support ground-control decisions but should be interpreted with other observations.", "easy"),
        ],
        [
            ("Why sequence underground production across mining panels?", "Balance access, equipment, ventilation, ground control, and output targets", ["Avoid all planning constraints", "Make every panel identical", "Replace reserve estimation"], "Production sequencing affects development lead time, recovery, safety, and available capacity.", "easy"),
            ("What is a benefit of tracking equipment availability and utilization separately?", "It distinguishes equipment readiness from how effectively available time is used", ["The terms always have identical meaning", "It removes the need for maintenance data", "It measures ore grade directly"], "Availability and utilization describe different parts of productive time and help diagnose losses.", "intermediate"),
        ],
    ],
    "MINING04": [
        [
            ("What drives natural ventilation pressure differences in a mine?", "Differences in air density caused by temperature and elevation", ["The ore's electrical resistance", "The number of haul trucks alone", "The colour of the shaft lining"], "Natural ventilation can arise from density differences, but mechanical fans usually control required mine airflow.", "easy"),
            ("Why measure airflow quantity at multiple points in a mine network?", "Confirm required distribution reaches working areas and identify imbalance", ["Air quantity is equal everywhere", "It measures rock strength", "It replaces gas monitoring"], "Airflow distribution, leakage, and resistance vary across branches of a ventilation network.", "easy"),
        ],
        [
            ("What is a fan duty point?", "The intersection of a fan's pressure-flow performance with the system resistance", ["A worker's shift assignment", "The mine's total ore reserve", "A gas detector calibration date"], "The operating point depends on the fan characteristic and connected system resistance.", "intermediate"),
            ("What can an air-door adjustment do in a mine ventilation network?", "Change branch resistance and redistribute airflow", ["Change the orebody's dip", "Increase gas concentration by definition", "Replace a main fan"], "Regulators and doors affect network resistance and should be adjusted under a controlled ventilation plan.", "easy"),
        ],
        [
            ("Why can high humidity increase heat stress underground?", "It limits evaporative cooling from the body", ["It always lowers air temperature", "It removes metabolic heat instantly", "It prevents sweating"], "High humidity can reduce sweat evaporation, worsening physiological heat stress.", "easy"),
            ("Why is contaminant dilution not a substitute for source control?", "Uncontrolled release can exceed ventilation capacity or expose workers locally", ["Ventilation always removes every contaminant", "Source control increases exposure", "Airflow cannot transport contaminants"], "Safe practice combines elimination or control at source with ventilation and exposure monitoring.", "intermediate"),
        ],
        [
            ("Why calibrate and function-test a mine gas detector before use?", "Confirm it responds accurately to the expected hazard and alarm conditions", ["Make methane harmless", "Replace ventilation planning", "Change the mine air composition"], "Calibration and bump tests verify detector response; use interval follows manufacturer and site procedures.", "easy"),
            ("What is a key control for preventing an underground mine fire from escalating?", "Early detection, safe isolation, and a practiced emergency response", ["Ignore smoke until production ends", "Disable communications", "Remove all escape signage"], "Fire prevention and response require layered controls, detection, communication, and evacuation planning.", "easy"),
        ],
        [
            ("What does a mine risk assessment prioritize?", "Hazards by likelihood and consequence so controls can be selected", ["Tasks by alphabetical order", "Only equipment purchase cost", "The oldest incident first regardless of exposure"], "Risk assessment structures hazard evaluation and control; site-specific methods and legal duties apply.", "easy"),
            ("Why conduct emergency drills in underground operations?", "Test communication, routes, equipment, and worker readiness under realistic conditions", ["Guarantee that emergencies will not occur", "Replace maintenance inspections", "Increase production rate automatically"], "Drills reveal gaps in plans and help workers practice response actions.", "easy"),
        ],
    ],
    "MME02": [
        [
            ("Why crush and grind ore before many concentration processes?", "Liberate valuable mineral grains from gangue", ["Change the mineral's atomic number", "Make all particles dissolve", "Remove the need for size control"], "Comminution exposes mineral surfaces, but excessive grinding can raise energy use and hinder separation.", "easy"),
            ("What does a flotation reagent such as a collector generally do?", "Promote attachment of selected mineral particles to air bubbles", ["Increase the ore's bulk density only", "Replace all water in the cell", "Measure particle size"], "Collectors alter surface properties to aid selective attachment; reagent selection depends on mineralogy and chemistry.", "intermediate"),
        ],
        [
            ("What is the purpose of smelting in many extractive routes?", "Use high-temperature reactions to separate or transform metal-bearing phases", ["Measure hardness without heating", "Remove all gangue by screening only", "Produce electricity without chemical change"], "Pyrometallurgical smelting uses heat and reactions to form products such as metal, matte, or slag.", "easy"),
            ("Why is flux added in some smelting operations?", "React with gangue or impurities to form a separable slag", ["Make the furnace colder by definition", "Increase the ore particle count", "Replace the reductant in every process"], "Flux chemistry helps form slag with suitable properties, depending on the feed and process.", "intermediate"),
        ],
        [
            ("What is leaching in hydrometallurgy?", "Dissolving selected metal values into an aqueous solution", ["Grinding without size reduction", "Solidifying a melt", "Measuring alloy grain size"], "Leaching transfers target species from solids into solution under selected chemical conditions.", "easy"),
            ("Why control pH during metal leaching?", "It influences dissolution, selectivity, and unwanted precipitation", ["It determines the crusher rotation", "It sets the electrode spacing", "It has no chemical effect"], "Solution chemistry strongly influences metal speciation and recovery.", "easy"),
        ],
        [
            ("What is electrowinning used for?", "Recover metal from solution by electrodeposition", ["Separate ore by particle size", "Measure heat capacity", "Produce a polymer film by extrusion"], "Electrowinning uses electrical current to deposit metal from a suitable electrolyte.", "easy"),
            ("Why monitor current efficiency in an electrowinning cell?", "Some current may drive side reactions rather than the desired metal deposition", ["All current always deposits metal", "It measures ore hardness", "It replaces electrolyte analysis"], "Current efficiency compares actual desired production with the Faradaic theoretical amount.", "intermediate"),
        ],
        [
            ("What is a purpose of refining after primary metal extraction?", "Remove remaining impurities to meet product specifications", ["Increase gangue content", "Avoid all chemical analysis", "Reduce the metal's atomic number"], "Refining routes improve purity through methods suited to the impurity and metal system.", "easy"),
            ("What should guide selection between pyrometallurgical and hydrometallurgical routes?", "Ore mineralogy, grade, impurity profile, energy, water, emissions, and economics", ["A single universal method for every ore", "The product label colour", "Only the plant's name"], "Process selection is an integrated technical, environmental, and economic decision.", "intermediate"),
        ],
    ],
    "MME03": [
        [
            ("In the iron-carbon diagram, what does the eutectoid transformation describe?", "Austenite transforming to ferrite and cementite at the eutectoid composition and temperature", ["Liquid transforming directly to copper", "Ferrite melting at room temperature", "A polymer becoming crystalline"], "The eutectoid reaction in steel produces a ferrite-cementite mixture, commonly pearlite under suitable conditions.", "intermediate"),
            ("Why is carbon content important when selecting a steel heat treatment?", "It affects phase transformations and the resulting microstructure and properties", ["It sets the furnace's electrical frequency", "It changes the steel's atomic number", "It has no effect on hardness"], "Carbon content influences transformation behavior, hardenability, and attainable properties.", "easy"),
        ],
        [
            ("Why austenitize steel before quenching in a typical hardening treatment?", "Dissolve carbon into austenite so rapid cooling can form a harder structure", ["Remove all carbon from the steel", "Convert the steel into liquid", "Eliminate the need for temperature control"], "Austenitizing establishes a suitable starting phase; temperature and time depend on steel composition and section.", "intermediate"),
            ("What is martensite in quenched steel?", "A hard, supersaturated transformation product formed by rapid cooling from austenite", ["A nonmetallic coating", "A stable liquid phase at room temperature", "A form of graphite"], "Martensite is hard and often brittle as-quenched, so treatment and composition must be controlled.", "easy"),
        ],
        [
            ("What is a common objective of annealing steel?", "Soften or homogenize the material and improve ductility or workability", ["Increase residual stress intentionally", "Create a ceramic coating", "Prevent all grain growth under any condition"], "Annealing schedules are selected to achieve a desired structure and property response.", "easy"),
            ("How does normalizing generally differ from full annealing for steel?", "It uses air cooling from the austenitizing range and often yields a finer structure", ["It uses no heating", "It always produces martensite", "It is performed only below freezing"], "Normalizing involves austenitizing followed by air cooling, with outcomes dependent on section and composition.", "intermediate"),
        ],
        [
            ("Why temper hardened steel after quenching?", "Reduce brittleness and adjust the strength-toughness balance", ["Make it fully liquid", "Remove every alloying element", "Increase quench severity"], "Tempering changes the as-quenched microstructure and properties; the schedule controls the balance.", "easy"),
            ("What is the main trade-off when selecting a tempering temperature?", "Higher tempering can reduce hardness while improving toughness and relieving stress", ["Temperature has no effect on properties", "It changes only the steel's colour", "It always increases hardness and brittleness together"], "Tempering response depends on composition and time-temperature conditions.", "intermediate"),
        ],
        [
            ("What does hardenability describe?", "How deeply a steel can harden under a specified cooling condition", ["The maximum hardness of a ceramic", "The steel's corrosion rate", "The furnace's maximum temperature"], "Hardenability concerns depth of hardening rather than maximum surface hardness alone.", "easy"),
            ("Why use case hardening for some components?", "Provide a hard wear-resistant surface while retaining a tougher core", ["Make the entire component brittle", "Remove the need for fatigue design", "Change the part's dimensions to zero"], "Surface-hardening routes target a property gradient suited to wear and load requirements.", "easy"),
        ],
    ],
    "MME04": [
        [
            ("Why polish and etch a metallographic specimen before optical microscopy?", "Reveal microstructural features and grain boundaries without obscuring them with preparation damage", ["Increase the specimen's chemical composition", "Change the microscope's wavelength", "Remove all phases from the sample"], "Preparation quality strongly affects what features can be interpreted in a micrograph.", "easy"),
            ("What does the ASTM grain-size number generally indicate?", "A standardized relative measure of grain population in a defined field", ["The alloy's atomic number", "The sample's density", "The microscope's magnification only"], "Grain size is quantified using standardized methods and appropriate sampling and image preparation.", "intermediate"),
        ],
        [
            ("What information does X-ray diffraction provide about a crystalline material?", "Diffraction peaks that can identify phases and lattice spacings", ["A direct video of atoms moving", "The sample's mass without a balance", "The material's service history"], "XRD analyzes diffraction from crystal planes and can support phase identification and structural analysis.", "easy"),
            ("Why can peak broadening in an XRD pattern require careful interpretation?", "It can arise from multiple effects such as small crystallites, strain, or instrument broadening", ["It always proves a new phase exists", "It measures only surface colour", "It eliminates the need for calibration"], "Peak width has several contributions and should not be attributed to one cause without analysis.", "intermediate"),
        ],
        [
            ("What does a scanning electron microscope commonly use to form an image?", "Signals generated by an electron beam interacting with the specimen", ["Audible echoes from the chamber", "Visible sunlight focused by a lens", "A pressure gauge output"], "SEM images are formed from electron-specimen interactions, with contrast depending on signal and setup.", "easy"),
            ("Why is conductive coating sometimes applied before SEM imaging of an insulating sample?", "Reduce charging that can distort image formation", ["Increase sample conductivity permanently", "Change the mineral phase", "Measure tensile strength"], "A suitable coating can mitigate charging, while coating choice may affect analytical measurements.", "intermediate"),
        ],
        [
            ("What does a tensile test produce as its primary measured relationship?", "Applied load or stress versus extension or strain", ["Electrical resistance versus salinity", "Diffraction angle versus wavelength only", "Magnetic field versus temperature only"], "Tensile testing records force and deformation and derives properties using specimen geometry.", "easy"),
            ("Why calibrate a hardness tester and control the test surface?", "Indentation results depend on load, indenter, dwell, surface, and machine condition", ["Hardness is independent of test setup", "Calibration changes the alloy composition", "Surface finish affects only colour"], "Valid hardness measurements require an appropriate method, calibrated equipment, and representative preparation.", "easy"),
        ],
        [
            ("What can fractography help determine after a component failure?", "The fracture mode and possible crack initiation or propagation features", ["The operator's identity", "The exact purchase date from the surface alone", "The alloy's future price"], "Fracture-surface features support failure analysis but should be combined with material, loading, and service evidence.", "easy"),
            ("Why preserve a failed component before destructive analysis?", "Avoid altering evidence needed to identify the failure mechanism", ["It guarantees the cause is already known", "It removes the need for photographs", "It changes the fracture surface into a reference standard"], "Documentation and careful evidence handling help maintain the reliability of a failure investigation.", "intermediate"),
        ],
    ],
    "PETRO02": [
        [
            ("What is the function of the hoisting system on a drilling rig?", "Raise and lower the drill string, casing, and related tubulars", ["Separate crude oil from water", "Measure reservoir porosity directly", "Control cement chemistry"], "The drawworks, drilling line, and blocks provide hoisting capability for rig operations.", "easy"),
            ("Why prepare a well plan before drilling?", "Coordinate trajectory, casing, fluids, equipment, hazards, and operating limits", ["Guarantee there will be no subsurface uncertainty", "Set the final crude-oil price", "Replace real-time monitoring"], "A well plan integrates subsurface objectives and operational design while allowing for uncertainty and contingencies.", "easy"),
        ],
        [
            ("What is one key function of drilling fluid?", "Transport cuttings while supporting well control and borehole stability", ["Make formation pressure irrelevant", "Increase drill-bit wear", "Replace casing permanently"], "Drilling fluids serve several functions; properties must be maintained for the current hole section.", "easy"),
            ("Why monitor equivalent circulating density (ECD)?", "Circulating pressure can affect the bottom-hole pressure window", ["It measures cement compressive strength", "It describes the pipe's outside colour", "It replaces mud-weight measurement"], "ECD includes circulating pressure effects and can approach fracture or loss limits.", "intermediate"),
        ],
        [
            ("Why consider drill-string torque and drag during well design?", "Friction and mechanical loads can limit reach, transfer of weight, or safe operation", ["They determine the formation's age", "They eliminate buckling", "They affect only the mud colour"], "Torque-and-drag analysis helps plan trajectory, tubulars, and operating envelopes.", "easy"),
            ("What can drill-string buckling threaten?", "String integrity and effective transfer of axial load", ["The satellite clock", "The cement's curing chemistry only", "The well's geographic datum"], "Buckling risk depends on compression, clearance, trajectory, and support conditions.", "intermediate"),
        ],
        [
            ("Why run casing in a well?", "Isolate formations and provide structural support for the wellbore", ["Increase formation permeability", "Replace all wellhead equipment", "Measure the drilling rate"], "Casing supports well integrity, zonal isolation, and later completion operations.", "easy"),
            ("What is the purpose of primary cementing behind casing?", "Provide zonal isolation and support the casing", ["Create a larger open hole", "Increase drilling-fluid viscosity", "Measure reservoir temperature"], "Cement placement quality is important for isolation and well integrity and must be evaluated.", "easy"),
        ],
        [
            ("What is the purpose of a blowout preventer (BOP)?", "Close or control the wellbore during specified well-control situations", ["Increase the reservoir's pressure", "Separate gas by distillation", "Replace the drill bit"], "BOP equipment is a barrier in well-control systems and requires appropriate testing and procedures.", "easy"),
            ("Why recognize a kick early?", "Early detection allows well-control actions before influx escalates", ["A kick improves cement quality", "It removes the need for barriers", "It is simply a change in bit wear"], "Early kick indicators and prompt response are central to preventing loss of well control.", "intermediate"),
        ],
    ],
    "PETRO03": [
        [
            ("What does porosity quantify in a reservoir rock?", "The fraction of bulk rock volume occupied by pore space", ["The fraction of oil that is refined", "The well's inclination", "The number of fractures per field"], "Porosity describes pore volume relative to bulk volume; effective and total porosity are distinct concepts.", "easy"),
            ("What does permeability describe?", "The ability of connected pore space to transmit fluid", ["The rock's mineral colour", "The fraction of reservoir volume occupied by oil only", "The fluid's boiling point"], "Permeability characterizes flow capacity and depends on pore connectivity and fluid-rock conditions.", "easy"),
        ],
        [
            ("Why use a phase envelope for a reservoir fluid?", "Show pressure-temperature conditions for phase behavior such as bubble or dew points", ["Set the well's geographic coordinates", "Measure rock grain size directly", "Calculate rig crew count"], "A phase envelope helps interpret fluid phase behavior across pressure and temperature conditions.", "intermediate"),
            ("What is formation volume factor used to relate?", "A fluid volume at reservoir conditions to its volume at specified surface conditions", ["Reservoir depth to drilling-rig height", "Core diameter to grain count", "Pressure to electrical resistance"], "Formation volume factors account for expansion or shrinkage between reservoir and surface conditions.", "easy"),
        ],
        [
            ("In a simple reservoir material balance, what does production primarily do to reservoir inventory?", "Withdraw fluid or mass from the reservoir system", ["Create pore volume from nothing", "Eliminate pressure support requirements", "Change fluid density without affecting mass"], "Material balance accounts for production, influx, expansion, and changes in reservoir storage.", "easy"),
            ("Why can pressure decline during production if there is insufficient pressure support?", "Fluid withdrawal exceeds the expansion or influx replacing reservoir volume", ["Production always raises pressure", "Rock compressibility is infinite", "A pressure gauge creates the decline"], "Pressure response depends on fluid and rock expansion, aquifer support, injection, and production history.", "intermediate"),
        ],
        [
            ("What does Darcy's law relate in a porous medium?", "Fluid flow rate to pressure gradient, permeability, viscosity, and geometry", ["The number of wells to the oil price", "Rock colour to seismic frequency", "Casing weight to mud pH"], "Darcy flow assumes a continuum and applies under specified flow conditions.", "easy"),
            ("What does a well's productivity index commonly relate?", "Production rate to pressure drawdown under stated conditions", ["Oil density to drilling depth only", "The number of completion tools to water cut", "Reservoir area to pipeline colour"], "Productivity index summarizes well inflow response and may vary with operating regime and multiphase flow.", "easy"),
        ],
        [
            ("Why can water injection support reservoir pressure?", "Injected water can replace produced voidage and displace hydrocarbons", ["Water creates new hydrocarbons", "It removes all heterogeneity", "It guarantees uniform sweep"], "Waterflood performance depends on pattern, mobility, heterogeneity, and operating controls.", "easy"),
            ("What is a common challenge in enhanced oil recovery?", "Maintaining effective sweep and acceptable economics under reservoir constraints", ["All methods work identically in every reservoir", "It eliminates the need for formation data", "It always reduces water handling"], "EOR selection depends on fluid, rock, temperature, facilities, environmental factors, and economics.", "intermediate"),
        ],
    ],
    "PETRO04": [
        [
            ("What does a well completion provide?", "A controlled connection between the reservoir and production or injection facilities", ["A new geological formation", "A guarantee of constant production", "A replacement for the reservoir model"], "Completion design supports flow, isolation, monitoring, and intervention according to the well objectives.", "easy"),
            ("Why may a completion include a packer?", "To isolate annular intervals and direct flow through the intended path", ["Increase porosity in the formation", "Measure crude-oil colour", "Replace the wellhead pressure barrier"], "Packers provide downhole isolation subject to design, setting, and integrity conditions.", "easy"),
        ],
        [
            ("What is nodal analysis used to evaluate?", "Compatibility between reservoir inflow and wellbore or surface outflow", ["The drilling rig's electrical grounding", "The rock's grain shape only", "A pipeline's legal ownership"], "Nodal analysis identifies operating points by combining inflow and outflow performance relationships.", "intermediate"),
            ("Why can increasing tubing size affect production performance?", "It changes frictional pressure loss and the outflow relationship", ["It changes the reservoir's porosity", "It sets the fluid's chemical formula", "It removes multiphase effects"], "Tubing diameter influences velocity and pressure drop; the net effect depends on flow regime and conditions.", "easy"),
        ],
        [
            ("What is the purpose of artificial lift?", "Provide additional energy or pressure reduction to produce fluids when natural drive is insufficient", ["Increase reservoir rock age", "Eliminate all water production", "Replace surface separation"], "Artificial-lift methods support production through different mechanisms and operating envelopes.", "easy"),
            ("What is a key factor when choosing an artificial-lift method?", "Well depth, rate, fluid properties, pressure, reliability, and available facilities", ["Only the operator's preferred colour", "A universal method independent of well conditions", "The casing's manufacturing date only"], "Lift selection is a system-level decision including operating conditions and lifecycle costs.", "intermediate"),
        ],
        [
            ("Why perform a production test with documented separator conditions?", "Rates depend on measurement conditions and must be reported consistently", ["Separator conditions never affect rates", "It proves the reservoir is homogeneous", "It replaces metering calibration"], "Test data are meaningful only with measured conditions, calibration, stabilization, and allocation basis.", "easy"),
            ("What does production allocation attempt to determine?", "Assign measured production to wells or sources under a defined method", ["Set the field's drilling direction", "Measure rock hardness", "Eliminate the need for accounting records"], "Allocation uses metering and agreed procedures to distribute commingled production among sources.", "easy"),
        ],
        [
            ("What is hydrate risk in a gas-production system?", "Formation of solid water-gas crystals that can restrict or block flow", ["A type of reservoir porosity", "A corrosion inhibitor concentration", "A method of well logging"], "Hydrates can form under suitable low-temperature, high-pressure, water-containing conditions.", "easy"),
            ("Why include pressure relief and separation in surface-facility design?", "Manage abnormal pressure and separate produced phases within safe operating limits", ["Make all process upsets impossible", "Remove the need for inspection", "Increase wellbore permeability"], "Facilities use layered safeguards and process equipment to handle normal and abnormal conditions.", "intermediate"),
        ],
    ],
    "POLYMER01": [
        [
            ("What is degree of polymerization?", "The number of repeat units in a polymer chain", ["The number of mould cavities", "The polymer's melting-point instrument", "The mass of one test specimen"], "Degree of polymerization relates chain length to the number of repeat units.", "easy"),
            ("Why can molecular-weight distribution affect polymer processing?", "Chain lengths influence viscosity, flow, and mechanical response", ["It changes the element symbols", "It makes all chains identical", "It determines the extruder's location"], "Polymer molecular-weight distribution affects entanglement, rheology, and properties.", "intermediate"),
        ],
        [
            ("In free-radical polymerization, what does an initiator commonly do?", "Generate reactive species that start chain growth", ["Stop all chain reactions permanently", "Measure polymer density", "Remove every monomer from the mixture"], "Initiators create radicals or other active centers that initiate polymerization.", "easy"),
            ("What distinguishes step-growth polymerization from chain-growth polymerization?", "Molecules of many sizes can react through functional groups as conversion proceeds", ["Only a single active chain end adds monomer", "It cannot form high-molecular-weight material", "It requires no reactive functionality"], "Step-growth processes build molecular size through reactions among functional species and generally require high conversion for high molecular weight.", "intermediate"),
        ],
        [
            ("What is the glass-transition temperature (Tg) associated with?", "A change in segmental mobility of amorphous polymer regions", ["A universal boiling point for every polymer", "The temperature at which all polymer becomes metal", "The onset of crosslinking in every material"], "Tg marks a transition in amorphous-chain mobility and is distinct from crystalline melting.", "easy"),
            ("Why can crystallinity increase polymer stiffness but reduce clarity?", "Ordered regions can increase modulus and scatter light at crystalline boundaries", ["Crystals always make the polymer transparent", "Crystallinity removes all density variation", "Light scattering depends only on sample labels"], "Crystalline morphology can affect mechanical properties and optical scattering, depending on size and refractive contrast.", "intermediate"),
        ],
        [
            ("What does viscoelasticity mean in a polymer?", "It exhibits both time-dependent elastic and viscous response", ["It has no deformation under load", "Its response is independent of time and temperature", "It behaves only as a perfect liquid"], "Polymers often combine recoverable deformation and time-dependent flow.", "easy"),
            ("Why does polymer melt viscosity generally change with shear rate?", "Entangled chains can orient and disentangle under flow", ["Shear rate changes the polymer's atomic number", "Viscosity is fixed for every processing condition", "Melt flow has no molecular effects"], "Many polymer melts are shear-thinning because molecular structure responds to deformation rate.", "intermediate"),
        ],
        [
            ("Why can adding a plasticizer lower a polymer's glass-transition temperature?", "It increases chain mobility by reducing intermolecular constraints", ["It increases crosslink density in every case", "It removes all amorphous regions", "It changes the polymer into a metal"], "Plasticizers can increase segmental mobility, with effect depending on compatibility and concentration.", "easy"),
            ("Why can two polymers with similar chemistry have different mechanical properties?", "Molecular weight, morphology, orientation, additives, and processing history can differ", ["Polymer structure never affects properties", "Only colour determines strength", "All processing produces identical morphology"], "Properties reflect structure across multiple scales and the processing path.", "intermediate"),
        ],
    ],
    "POLYMER02": [
        [
            ("What does the screw in a single-screw extruder commonly do?", "Convey, melt, mix, and pressurize polymer feed", ["Measure the final part's impact strength", "Cool the polymer without a barrel", "Set the polymer's molecular formula"], "Extruder zones and screw geometry support solids conveying, melting, and melt pumping.", "easy"),
            ("Why can excessive melt temperature during extrusion be harmful?", "It can cause thermal degradation and unstable product properties", ["It always improves strength", "It eliminates all die swell", "It makes screw speed irrelevant"], "Thermal history and residence time can degrade polymers, so processing windows matter.", "easy"),
        ],
        [
            ("What is the purpose of a holding-pressure stage in injection moulding?", "Compensate for shrinkage as the part cools before the gate freezes", ["Increase the mould's cavity count", "Remove the polymer from the screw", "Measure tensile modulus in the mould"], "Packing or holding pressure feeds material to offset shrinkage until the gate seals.", "intermediate"),
            ("What can an inadequately packed injection-moulded part exhibit?", "Sink marks or voids from shrinkage", ["Higher fibre length by definition", "A guaranteed uniform density", "No dimensional change during cooling"], "Insufficient packing may leave shrinkage defects, depending on geometry, material, and process settings.", "easy"),
        ],
        [
            ("In blow moulding, what does the parison become?", "The hollow polymer preform expanded against a mould", ["The extruder motor", "A solid metal insert", "The cooling-water circuit"], "A parison or preform is expanded to form the hollow article in blow moulding.", "easy"),
            ("Why control sheet temperature during thermoforming?", "The sheet must be soft enough to form without excessive sag or degradation", ["Temperature has no effect on forming", "It sets the finished product's legal status", "It replaces vacuum or pressure"], "Thermoforming relies on a suitable temperature window and forming conditions to achieve uniform geometry.", "intermediate"),
        ],
        [
            ("What is a common purpose of compression moulding?", "Form a charge under heat and pressure in a closed mould", ["Measure polymer molecular weight", "Coat a pipe with gas", "Create a woven reinforcement"], "Compression moulding shapes a material charge in a heated cavity under pressure.", "easy"),
            ("Why can transfer moulding be useful for some thermoset parts?", "A metered charge is transferred into cavities and can fill complex geometry", ["It requires the polymer to melt repeatedly", "It eliminates cure time", "It produces only flat films"], "Transfer moulding feeds material from a pot through channels into the mould, with cure behavior controlling the cycle.", "intermediate"),
        ],
        [
            ("What is a likely cause of short shots in moulding?", "Insufficient material or inadequate flow to fill the cavity", ["Excessive product labelling", "A fully vented cavity filling correctly", "The test specimen being too large"], "Short shots can result from shot size, pressure, temperature, venting, or flow restrictions.", "easy"),
            ("Why investigate a recurring weld line in an injection-moulded part?", "It may indicate flow fronts meeting with reduced strength or appearance", ["It proves the polymer is unprocessed", "It is always a harmless colour mark", "It increases the part's molecular weight"], "Weld-line quality depends on flow, temperature, pressure, and design; the location may be structurally important.", "intermediate"),
        ],
    ],
    "POLYMER03": [
        [
            ("What happens when a thermoplastic is reheated sufficiently under suitable conditions?", "It softens or melts and can generally be reshaped", ["It forms an irreversible covalent network by definition", "It becomes a thermoset automatically", "It loses all molecular chains"], "Thermoplastics can usually be processed repeatedly, although degradation can limit recycling cycles.", "easy"),
            ("Why can a thermoset not be remelted like a thermoplastic?", "Its crosslinked network prevents chains from flowing as a melt", ["It has no chemical bonds", "It contains no polymer chains", "Its glass-transition temperature is always below room temperature"], "Thermoset crosslinks form a network that decomposes rather than flowing on reheating.", "easy"),
        ],
        [
            ("What property is characteristic of an elastomer above its glass transition?", "Large recoverable deformation under appropriate loading", ["Zero strain under all loads", "Perfectly brittle fracture at small strain", "Permanent liquid flow without recovery"], "Elastomers combine flexible chains and network structure to provide large elastic strain.", "easy"),
            ("Why add a compatibilizer to an immiscible polymer blend?", "Improve interfacial adhesion and dispersion between phases", ["Make all phases chemically identical", "Remove the need for mixing", "Guarantee transparency"], "Compatibilizers can stabilize morphology and improve stress transfer, with effectiveness depending on the blend.", "intermediate"),
        ],
        [
            ("Why condition polymer specimens before mechanical testing?", "Moisture and temperature can affect the measured properties", ["It changes the test standard's title", "It ensures every result is identical", "It replaces specimen dimensional checks"], "Controlled conditioning improves repeatability and makes results comparable to specified test conditions.", "easy"),
            ("What does a differential scanning calorimeter (DSC) measure?", "Heat flow to or from a sample during a controlled temperature program", ["Only tensile force", "Fluid flow through a die", "Surface roughness directly"], "DSC detects thermal transitions and events such as glass transition, crystallization, and melting.", "easy"),
        ],
        [
            ("Why add an antioxidant to some polymers?", "Slow oxidative degradation during processing or service", ["Increase oxidation deliberately", "Remove every UV wavelength", "Replace the polymer matrix"], "Antioxidants interrupt or delay oxidation pathways; additive choice depends on material and application.", "easy"),
            ("What can ultraviolet stabilizers help reduce?", "Photo-oxidative degradation under UV exposure", ["Thermal expansion at all temperatures", "Every mechanical load", "Moisture absorption in all polymers"], "UV absorbers and stabilizers reduce damage mechanisms but do not make a polymer immune to weathering.", "easy"),
        ],
        [
            ("Why separate polymer waste by resin type before mechanical recycling?", "Different polymers may be incompatible and process at different temperatures", ["All polymers have identical melt behavior", "Sorting changes the polymer's atomic number", "Mixed waste always improves properties"], "Sorting improves feed consistency and helps avoid incompatible phases or degradation during reprocessing.", "easy"),
            ("What is an important circular-design consideration for a polymer product?", "Material choice, separability, durability, and realistic end-of-life routes", ["Use the most layers possible regardless of recovery", "Assume every region has the same recycling system", "Ignore product lifetime"], "Circularity depends on design and the infrastructure and markets that can actually recover the material.", "intermediate"),
        ],
    ],
    "POLYMER04": [
        [
            ("Why align fibres with principal load directions in a composite laminate?", "Fibres carry load most effectively along their length", ["Fibre orientation has no effect", "It changes the matrix into ceramic", "It removes all interlaminar stress"], "Composite stiffness and strength are anisotropic and depend strongly on reinforcement orientation.", "easy"),
            ("What is the role of a matrix in a fibre-reinforced composite?", "Bind fibres, transfer load, and protect reinforcement", ["Replace fibre strength in every direction", "Make fibres electrically isolated in every design", "Determine only the product's colour"], "The matrix supports load transfer, environmental protection, and composite shape.", "easy"),
        ],
        [
            ("What does classical laminate theory estimate for a layered composite?", "In-plane stiffness and response from the stacking sequence and ply properties", ["The exact impact history of a part", "A metal's grain size", "The cost of the mould only"], "Laminate theory combines oriented ply properties and stacking sequence under stated assumptions.", "intermediate"),
            ("Why can a symmetric laminate stacking sequence be desirable?", "It can reduce coupling between in-plane extension and bending", ["It guarantees no delamination", "It makes every ply isotropic", "It removes residual stress from manufacturing"], "Laminate symmetry reduces certain coupling terms but does not eliminate every deformation or failure mode.", "intermediate"),
        ],
        [
            ("What is resin transfer moulding (RTM)?", "Inject resin into a closed mould containing a dry fibre preform", ["Extrude a thermoplastic through an open die only", "Weave fibres after curing", "Machine a solid metal billet"], "RTM impregnates a preplaced reinforcement preform with resin inside a mould.", "easy"),
            ("Why control fibre wet-out during composite manufacturing?", "Poor impregnation can leave voids and reduce load transfer", ["It determines the resin's colour only", "Voids improve fatigue strength", "Wet-out is irrelevant to composite quality"], "Fibre wet-out and void control are important quality variables for many composite routes.", "easy"),
        ],
        [
            ("What is delamination in a laminate composite?", "Separation between adjacent plies", ["Uniform melting of the matrix", "A measurement calibration method", "A change in fibre orientation without damage"], "Delamination is an interlaminar separation that can reduce stiffness and residual strength.", "easy"),
            ("Why inspect a composite fracture surface after failure?", "Identify failure modes such as fibre breakage, pull-out, matrix cracking, or delamination", ["Determine the product's marketing category", "Guarantee the exact load history without context", "Replace nondestructive inspection records"], "Fractography supports diagnosis but should be interpreted with loading and manufacturing evidence.", "intermediate"),
        ],
        [
            ("Why use nondestructive inspection for composite structures?", "Detect internal or surface defects without consuming the component", ["Measure every material property directly", "Eliminate acceptance criteria", "Guarantee no defect exists"], "Methods such as ultrasonic or thermographic inspection can reveal selected defect types within their limitations.", "easy"),
            ("What should guide selection of a composite for a structural application?", "Loads, environment, manufacturing route, repairability, and lifecycle requirements", ["Only the material's colour", "A universal strongest material independent of design", "The supplier's logo"], "Material and layup selection is application-specific and should be validated for expected service conditions.", "easy"),
        ],
    ],
    "PROD02": [
        [
            ("What is the purpose of a process route sheet?", "Specify the planned sequence of operations for a part", ["List only supplier phone numbers", "Measure customer satisfaction directly", "Replace the engineering drawing"], "Routing documents the ordered operations and resources used to manufacture a product.", "easy"),
            ("Why include setup and inspection steps in process planning?", "They affect capacity, quality, and total production time", ["They do not use resources", "They change the product's material grade", "They replace operation sequencing"], "A realistic route includes supporting steps and checks needed to produce conforming output.", "easy"),
        ],
        [
            ("What is a benefit of a product-oriented line layout for high-volume production?", "Sequential flow can reduce backtracking and material handling", ["Every product must follow a different route", "It removes the need for balancing", "It guarantees zero downtime"], "Product layouts support repetitive flow but can be less flexible and sensitive to disruptions.", "easy"),
            ("What is a potential drawback of a functional layout?", "Jobs may travel longer distances and wait between departments", ["It cannot process varied products", "It has no machines", "It eliminates scheduling complexity"], "Functional layouts offer flexibility but may increase routing and work-in-process complexity.", "intermediate"),
        ],
        [
            ("What is the objective of group technology?", "Identify similar parts and processes to support families and efficient routing", ["Make every part unique", "Eliminate classification", "Set the factory's power factor"], "Group technology exploits similarities in design and manufacture to improve planning and flow.", "easy"),
            ("What does a manufacturing cell commonly group together?", "Different machines needed to process a family of similar parts", ["Only unrelated office functions", "All equipment regardless of process", "Products with no shared operations"], "Cellular manufacturing organizes resources around product families and their typical routes.", "easy"),
        ],
        [
            ("What is a flexible manufacturing system designed to provide?", "Automated production of a range of parts with coordinated material handling", ["One manual operation with no changeover", "A system without control software", "A fixed product with no routing flexibility"], "FMS integrates machines and handling to support flexibility, with investment and control complexity.", "easy"),
            ("Why is tool and fixture management important in an FMS?", "Automated changeovers depend on correct, available, and identifiable resources", ["Tools cannot affect machining", "It replaces machine monitoring", "Fixture identity is always obvious to a robot"], "Reliable automated production depends on tool condition, identification, offsets, and fixture availability.", "intermediate"),
        ],
        [
            ("In lean production, what is a bottleneck?", "A constrained step that limits the system's throughput", ["The fastest workstation", "A warehouse label", "A product with the lowest defect rate"], "System output is constrained by the limiting resource, so improvement should consider flow and demand.", "easy"),
            ("Why use a value-stream map?", "Visualize material and information flow to identify delays and waste", ["Set employee names alphabetically", "Replace all production measurements", "Guarantee every process is lean"], "A value-stream map helps teams see current-state flow and plan targeted improvements.", "easy"),
        ],
    ],
    "PROD03": [
        [
            ("What is the purpose of a quality management system?", "Provide coordinated processes to meet requirements and improve outcomes", ["Guarantee that defects are impossible", "Replace customer requirements", "Control only the product's colour"], "A QMS structures responsibilities, processes, evidence, and improvement but cannot guarantee perfection.", "easy"),
            ("What does cost of poor quality include?", "Costs from defects, rework, scrap, returns, and failure-related activities", ["Only employee training cost", "Only conforming production cost", "The product's list price"], "Poor-quality costs include internal and external failures and may include appraisal and prevention categories depending on the model.", "easy"),
        ],
        [
            ("When is an X-bar chart commonly used?", "Monitor the process mean using rational subgroups of measurements", ["Count nonconforming units only", "Track supplier delivery routes", "Measure project completion time"], "X-bar charts monitor subgroup averages; companion charts may monitor within-subgroup variation.", "intermediate"),
            ("Why investigate a control-chart signal before adjusting a process?", "An unnecessary adjustment can increase variation when the process is stable", ["Every signal is caused by the operator", "Stable processes require constant changes", "Control limits are product specifications"], "Control-chart signals indicate evidence to investigate; tampering with common-cause variation may worsen performance.", "intermediate"),
        ],
        [
            ("What does Cpk account for compared with Cp?", "Process centering relative to the specification limits", ["Only the sample size", "The supplier's geographic region", "The measurement instrument's colour"], "Cp compares spread with tolerance width; Cpk also reflects how centered the process is.", "easy"),
            ("Why should capability be evaluated only after checking process stability?", "Capability estimates assume a sufficiently predictable process", ["A stable process has no variation", "Specifications cannot be measured", "Capability changes the process mean"], "Capability indices can mislead when the process distribution is unstable or assumptions are violated.", "intermediate"),
        ],
        [
            ("What is the consumer's risk in acceptance sampling?", "Accepting a lot whose quality is worse than the agreed quality level", ["Rejecting a high-quality lot", "Measuring a sample twice", "A supplier's transport cost"], "Sampling plans balance producer and consumer risks across quality levels.", "easy"),
            ("Why does increasing sample size generally change a sampling plan's discrimination?", "It can improve the ability to distinguish quality levels, usually at higher inspection effort", ["It eliminates all sampling risk", "It makes lot quality irrelevant", "It guarantees every defect is found"], "Larger samples often improve discrimination but do not remove uncertainty or inspection cost.", "intermediate"),
        ],
        [
            ("What is the purpose of a failure mode and effects analysis (FMEA)?", "Identify potential failure modes, effects, and actions to reduce risk", ["Prove a product can never fail", "Set the product's retail price", "Replace process validation"], "FMEA is a structured prospective risk analysis, not proof that all hazards have been found.", "easy"),
            ("Why verify improvement with follow-up data after a corrective action?", "Confirm the change produced a sustained benefit without unwanted effects", ["Avoid checking whether the action worked", "Guarantee other processes are identical", "Remove the need for documentation"], "Improvement should be verified against defined measures and monitored for unintended consequences.", "easy"),
        ],
    ],
    "PROD04": [
        [
            ("What is metrological traceability?", "An unbroken documented calibration chain to a stated reference, each link contributing uncertainty", ["A list of instrument serial numbers only", "A guarantee of zero measurement error", "A method for setting production targets"], "Traceability links measurement results to references through documented calibrations and associated uncertainty.", "intermediate"),
            ("Why distinguish precision from accuracy?", "Repeatability and closeness to a reference describe different measurement qualities", ["They are synonyms in every standard", "Precision describes the product's cost", "Accuracy is the number of decimal places"], "A measurement can be precise but biased, or accurate on average but imprecise.", "easy"),
        ],
        [
            ("What does a fit between a hole and shaft specify?", "Permitted dimensional relationship and resulting clearance or interference", ["The material's chemical composition", "The machine's cycle time", "The measurement uncertainty alone"], "Limits and fits define allowable sizes and functional assembly relationships.", "easy"),
            ("Why apply geometric tolerances to a drawing?", "Control form, orientation, location, or runout relative to functional datums", ["Set the colour of a component", "Replace every size dimension", "Guarantee zero manufacturing variation"], "GD&T communicates geometric requirements and datum references for function and inspection.", "intermediate"),
        ],
        [
            ("What is a go/no-go gauge intended to determine?", "Whether a feature falls within specified size limits", ["The exact value of every dimension", "The material's grain size", "The component's fatigue life"], "Limit gauges support rapid conformance checks but do not provide a full measured value.", "easy"),
            ("How does a dial comparator typically help inspection?", "Compare a dimension with a reference or setting standard", ["Measure chemical purity directly", "Set a machine's spindle speed", "Remove surface roughness"], "Comparators indicate deviation from a reference and require suitable setup and calibration.", "easy"),
        ],
        [
            ("What does a coordinate measuring machine (CMM) use to inspect a part?", "Probe coordinates of selected points relative to a defined reference frame", ["A chemical titration", "A process alarm trend", "A machining toolpath as the measured result"], "A CMM captures spatial coordinates and evaluates geometry against a measurement strategy.", "easy"),
            ("Why is a CMM measurement strategy important?", "Point selection, alignment, fixturing, and probing affect the reported geometry", ["A CMM always measures every surface perfectly", "Only software colour affects the result", "The strategy changes the part's design"], "Measurement results depend on datum alignment, sampling, probe configuration, and uncertainty.", "intermediate"),
        ],
        [
            ("Why consider measurement uncertainty when deciding product conformance?", "A result near a tolerance limit may require a decision rule that accounts for uncertainty", ["Uncertainty is always exactly zero", "The nominal dimension replaces measurement", "Uncertainty affects only the drawing font"], "Decision rules define how uncertainty and risk are considered when declaring conformity.", "intermediate"),
            ("What should an inspection plan link together?", "Product characteristics, methods, sampling, acceptance criteria, and records", ["Only the inspector's shift", "A guarantee of perfect parts", "Unrelated supplier advertisements"], "A usable inspection plan ties requirements to measurement and decision evidence.", "easy"),
        ],
    ],
    "ROBOTICS01": [
        [
            ("What does a homogeneous transformation matrix combine?", "Rotation and translation between coordinate frames", ["Torque and temperature only", "A robot's software license and serial number", "The actuator's maximum current only"], "Homogeneous transforms represent rigid-body pose changes with rotation and translation.", "easy"),
            ("Why use consistent frame conventions in a robot model?", "Frame-direction errors can produce incorrect pose and motion calculations", ["Frames change the physical link lengths", "Conventions affect only display colour", "A transformation has no direction"], "Transform composition depends on clear source and destination frame definitions.", "intermediate"),
        ],
        [
            ("What does forward kinematics calculate?", "End-effector pose from the robot's joint variables", ["Joint friction from a camera image", "The motor's purchase cost", "A trajectory without joint values"], "Forward kinematics maps joint configuration through link geometry to end-effector pose.", "easy"),
            ("Why can small joint errors affect end-effector position differently across the workspace?", "The Jacobian and robot geometry vary with configuration", ["Joint errors always cancel", "Link dimensions change during every move", "Workspace position is independent of joints"], "The local mapping from joint to Cartesian motion depends on configuration.", "intermediate"),
        ],
        [
            ("Why can inverse kinematics have multiple solutions?", "Different joint configurations can produce the same end-effector pose", ["A robot has only one joint", "The target pose has no coordinates", "All configurations are singular"], "Manipulator geometry can admit elbow-up/down, wrist, or other alternative solutions.", "easy"),
            ("What should an inverse-kinematics solver check beyond pose error?", "Joint limits, collision constraints, and solution continuity", ["Only the target's display colour", "Whether a joint name is alphabetically first", "Ignore actuator limits"], "A numerically accurate pose may still be infeasible or unsafe if limits and collisions are ignored.", "intermediate"),
        ],
        [
            ("What does the manipulator Jacobian map locally?", "Joint velocities to end-effector linear and angular velocity", ["Motor temperature to link length", "Camera pixels to product cost", "Robot time to network bandwidth"], "The Jacobian describes local differential motion relationships at a configuration.", "easy"),
            ("Why can the Jacobian be useful for Cartesian velocity control?", "It relates desired end-effector velocity to joint rates", ["It directly prevents every collision", "It replaces inverse kinematics globally", "It measures a link's elastic modulus"], "Jacobian-based control uses local mappings and must handle singularities and joint-rate limits.", "intermediate"),
        ],
        [
            ("What occurs at a kinematic singularity?", "The robot loses one or more instantaneous motion directions or requires extreme joint rates", ["Every joint becomes physically locked", "The robot gains unlimited force", "The end effector leaves its coordinate frame"], "Singularities reduce Jacobian rank and can make some Cartesian motions unattainable or poorly conditioned.", "easy"),
            ("Why avoid planning a path too close to a singularity?", "Small Cartesian commands can demand large or unstable joint motions", ["The robot's mass becomes zero", "A singularity increases every joint limit", "It guarantees better precision"], "Near-singular configurations can amplify velocity and noise demands, so planning should consider margins.", "intermediate"),
        ],
    ],
    "ROBOTICS02": [
        [
            ("What does a rigid-body pose specify?", "Position and orientation of a body relative to a reference frame", ["Only its material density", "The controller's software version", "Its motor current without configuration"], "Pose includes translational and rotational state, represented according to a chosen convention.", "easy"),
            ("Why distinguish body-frame from world-frame velocity?", "The same physical motion has different components when expressed in different frames", ["Velocity has no direction", "Frames affect only mass", "A coordinate transform changes the actual speed"], "Vector components depend on the frame, even though the physical motion is unchanged.", "intermediate"),
        ],
        [
            ("What does a manipulator dynamics model relate?", "Joint motion and acceleration to forces or torques and robot parameters", ["Camera exposure to map projection", "A part's colour to its price", "Only the robot's network address"], "Dynamics models use inertia, gravity, and other terms to predict or control motion.", "easy"),
            ("Why account for gravity in robot joint torque calculations?", "Links and payload create configuration-dependent gravitational loads", ["Gravity acts only on sensors", "Joint torque is always zero at rest", "It changes the robot's link count"], "Gravity compensation can be important for accurate and safe motion control.", "easy"),
        ],
        [
            ("Why limit acceleration and jerk in a robot trajectory?", "Reduce abrupt motion that can excite vibration, loads, or actuator limits", ["Increase collision risk by design", "Change the target's coordinate frame", "Eliminate the need for interpolation"], "Smooth trajectories can reduce mechanical stress and improve tracking, subject to task requirements.", "easy"),
            ("What is the purpose of trajectory time parameterization?", "Assign timing to a geometric path while respecting motion constraints", ["Change the robot's kinematic structure", "Set the sensor's calibration", "Convert a joint into a link"], "Time parameterization maps path progress to time under velocity and acceleration bounds.", "intermediate"),
        ],
        [
            ("What is a common role of a PID controller at a robot joint?", "Use position or velocity error to adjust actuator command", ["Estimate the robot's colour", "Replace encoder feedback in every case", "Create a new kinematic link"], "PID feedback can regulate joint behavior but requires suitable sampling, tuning, and actuator limits.", "easy"),
            ("Why use gravity compensation in joint control?", "Reduce steady effort needed to hold or move the robot against gravity", ["Remove every friction effect", "Guarantee zero tracking error under all loads", "Increase payload mass"], "Model-based gravity compensation reduces a known load component but model error and disturbances remain.", "intermediate"),
        ],
        [
            ("What does Lyapunov stability analysis seek to establish?", "That system trajectories remain near or converge toward an equilibrium under stated conditions", ["The robot's paint colour", "A path's shortest Euclidean length", "The sensor's manufacturing date"], "Lyapunov methods use an energy-like function to analyze stability without necessarily solving trajectories.", "intermediate"),
            ("Why use force control for some robot tasks?", "The task depends on controlled contact force rather than position alone", ["It removes the need for a force sensor or model", "It guarantees safe contact at any speed", "It is required for all free-space motion"], "Force control is useful in contact tasks, with safety and sensor limitations carefully handled.", "easy"),
        ],
    ],
    "ROBOTICS03": [
        [
            ("What does camera intrinsic calibration estimate?", "Internal imaging parameters such as focal length and principal point", ["The robot's joint torque constants", "The object's material strength", "The camera's Wi-Fi password"], "Intrinsics describe the camera projection model and may include lens distortion.", "easy"),
            ("Why calibrate a camera to a robot coordinate frame?", "Relate image observations to robot motion or workspace coordinates", ["Change the camera sensor size", "Make image pixels equal metres automatically", "Eliminate every depth ambiguity"], "Extrinsic calibration estimates the transform between coordinate frames for tasks such as hand-eye coordination.", "intermediate"),
        ],
        [
            ("What does a feature detector identify in an image?", "Repeatable local structures such as corners or blobs", ["A robot's joint acceleration directly", "The object's hidden chemical composition", "The camera's network route"], "Feature detectors locate image patterns that can be described and matched across views.", "easy"),
            ("Why use geometric verification after matching image features?", "Reject correspondences inconsistent with a plausible scene transformation", ["Make every match correct by definition", "Remove the need for camera calibration", "Change the original image resolution"], "Geometric verification filters false matches using constraints such as epipolar or projective geometry.", "intermediate"),
        ],
        [
            ("What does a LiDAR point cloud represent?", "Spatial samples derived from laser range measurements", ["A time-series of motor current only", "A list of image colours without positions", "A robot's source code"], "LiDAR measurements are transformed into points using range, angle, and sensor pose.", "easy"),
            ("Why can reflective or transparent surfaces challenge range sensing?", "They may produce weak, missing, or misleading returns", ["They increase sensor range in every case", "They change the sensor's coordinate system", "They guarantee perfect depth"], "Surface properties can affect return quality and bias or invalidate range measurements.", "easy"),
        ],
        [
            ("What is localization in robotics?", "Estimate the robot's pose within a map or reference frame", ["Build a motor without encoders", "Detect a component's colour only", "Choose a network password"], "Localization estimates pose from sensor observations and a map or motion model.", "easy"),
            ("What is a common difficulty in simultaneous localization and mapping (SLAM)?", "The robot must estimate pose and map while their errors are coupled", ["A map cannot contain landmarks", "Sensors always provide exact global position", "SLAM is independent of motion estimates"], "SLAM jointly estimates trajectory and map, and uncertainty in one affects the other.", "intermediate"),
        ],
        [
            ("What is the purpose of sensor fusion?", "Combine complementary observations to improve state estimation", ["Ensure every sensor has identical errors", "Replace all calibration", "Average readings without regard to units"], "Fusion uses models and uncertainty to combine data; poorly calibrated sensors can make the estimate worse.", "easy"),
            ("Why represent uncertainty in a perception estimate?", "Downstream decisions can account for confidence and sensor limitations", ["Uncertainty proves the estimate is wrong", "It removes the need for validation", "Every estimate has exact certainty"], "Uncertainty helps planners and operators make risk-aware decisions rather than treating estimates as exact.", "easy"),
        ],
    ],
    "ROBOTICS04": [
        [
            ("What is the nonholonomic constraint for a typical wheeled robot?", "It cannot move instantaneously sideways without changing orientation", ["It cannot move forward", "It has no wheel rotation", "It can move in every direction independently"], "Rolling constraints restrict instantaneous velocity, as in a standard differential-drive robot.", "intermediate"),
            ("What does wheel odometry estimate?", "Motion from measured wheel rotations and a kinematic model", ["Absolute global position without drift", "Obstacle material composition", "The battery's chemical age"], "Odometry integrates wheel motion and accumulates error from slip, calibration, and model mismatch.", "easy"),
        ],
        [
            ("What is a map used for in mobile-robot localization?", "Provide spatial structure against which sensor observations can be matched", ["Set the robot's motor voltage only", "Replace every range sensor", "Guarantee obstacle-free travel"], "Maps support pose estimation but can be outdated or incomplete.", "easy"),
            ("Why can a robot become lost in a repetitive corridor?", "Similar observations may not distinguish one location from another", ["The corridor changes gravity", "Localization needs no sensor data", "A map always contains unique visual features"], "Perceptual aliasing can make multiple places look alike and increase localization uncertainty.", "intermediate"),
        ],
        [
            ("What does a global path planner usually compute?", "A route through a map from start to goal", ["The motor winding resistance", "A sensor's calibration certificate", "A guaranteed collision-free physical execution regardless of uncertainty"], "A path planner reasons over a map or configuration space; execution still needs obstacle checks and control.", "easy"),
            ("Why include robot footprint when planning a path?", "A path for the robot's center may collide if its body has nonzero size", ["The footprint changes the map resolution automatically", "Robots are dimensionless", "Footprints affect only display icons"], "Configuration-space planning accounts for the robot geometry and obstacle clearance.", "intermediate"),
        ],
        [
            ("What is a reactive obstacle-avoidance controller intended to do?", "Adjust motion using nearby obstacle observations", ["Create the robot's global map by itself", "Replace emergency stops", "Guarantee optimality for every route"], "Reactive avoidance handles local interactions but can require a global planner to avoid dead ends.", "easy"),
            ("Why should an obstacle-avoidance system consider sensor latency?", "The obstacle may move before the robot's delayed response takes effect", ["Latency makes obstacles stationary", "It changes the robot's wheel radius", "Fast motion requires no sensing"], "Perception and actuation delays matter for stopping distance and safe navigation.", "intermediate"),
        ],
        [
            ("Why evaluate a mobile robot on varied routes and conditions?", "Performance can change with lighting, surfaces, clutter, speed, and sensor coverage", ["One route proves universal reliability", "Testing removes every environmental uncertainty", "Navigation depends only on the robot's colour"], "Evaluation should represent the operating domain and include failure and recovery behavior.", "easy"),
            ("What is a useful navigation safety metric alongside task completion time?", "Collision or near-miss rate and minimum clearance", ["The map file's name", "The number of screen icons", "The robot's software line count"], "Time alone can reward risky motion; safety and robustness measures provide necessary context.", "easy"),
        ],
    ],
    "TEXTILE02": [
        [
            ("What is the main purpose of opening and cleaning in spinning preparation?", "Separate fibre tufts and remove a portion of foreign matter", ["Twist the final yarn", "Set the fabric weave", "Apply a durable water repellent finish"], "Opening and cleaning prepare fibre for downstream blending and carding; excessive action can damage fibres.", "easy"),
            ("Why control cleaning intensity for staple fibres?", "Aggressive cleaning can break fibres and create neps or waste", ["More intensity always improves yarn quality", "Fibre strength is unaffected by processing", "Cleaning determines the loom speed"], "Opening and cleaning must balance removal of trash with preservation of fibre length and quality.", "intermediate"),
        ],
        [
            ("What does a draw frame do to slivers?", "Combine and draft them to improve evenness and alignment", ["Weave them into fabric", "Dye them uniformly", "Measure fabric abrasion resistance"], "Drawing blends slivers and improves fibre parallelization and linear density uniformity.", "easy"),
            ("Why may combing be used for finer yarns?", "Remove short fibres and improve fibre alignment and yarn uniformity", ["Increase trash content", "Replace drafting", "Create a knitted loop structure"], "Combing can improve fibre preparation and yarn quality, with additional cost and waste.", "easy"),
        ],
        [
            ("In ring spinning, what does the traveller help provide?", "Twist insertion and winding of yarn onto the bobbin", ["Carding of raw fibres", "Warp shedding at the loom", "Chemical fixation of dye"], "The ring and traveller system inserts twist while winding yarn onto the package.", "easy"),
            ("Why does spindle speed affect ring-spinning performance?", "It influences production rate, yarn tension, and end-break risk", ["It changes the fibre species", "It removes all yarn imperfections", "It determines the fabric weave directly"], "Higher spindle speeds can increase output but also affect tension, heat, and breakage.", "intermediate"),
        ],
        [
            ("How does rotor spinning form yarn?", "Fibres collect in a rotor groove and are continuously twisted into yarn", ["A shuttle interlaces warp and weft", "Fibres are bonded only by a resin bath", "A ring traveller winds staple without twist"], "Rotor spinning uses fibre separation, collection, and twist insertion in a rotor system.", "easy"),
            ("What can influence yarn quality in air-jet spinning?", "Fibre properties, nozzle airflow, drafting, and process settings", ["Only the package label", "The loom reed count alone", "The colour of the machine enclosure"], "Air-jet spinning performance depends on fibre control and aerodynamic wrapping under suitable settings.", "intermediate"),
        ],
        [
            ("What does yarn count express?", "A relationship between yarn fineness and mass or length under a defined system", ["The number of loom operators", "The fabric's colour fastness", "The fibre's chemical formula"], "Yarn numbering systems may be direct or indirect, so the convention and units must be stated.", "easy"),
            ("Why measure yarn evenness and imperfections?", "Irregularities can affect appearance, strength, and downstream processing", ["They determine the fibre's atomic number", "They remove the need for tensile testing", "Evenness has no effect on fabric"], "Evenness tests characterize mass variation and imperfections relevant to yarn quality and end use.", "easy"),
        ],
    ],
    "TEXTILE03": [
        [
            ("What does warp crimp describe in a woven fabric?", "The waviness of warp yarns as they pass over and under weft yarns", ["The yarn's chemical composition", "The loom's motor power", "The fabric's dye concentration"], "Crimp reflects yarn interlacement geometry and affects cover, extension, and fabric properties.", "easy"),
            ("Why does yarn diameter influence fabric cover?", "It affects how much projected area yarns occupy in the structure", ["Diameter affects only the fabric colour", "Cover is independent of yarn spacing", "It changes the fibre's melting point"], "Cover depends on yarn size, spacing, and interlacement geometry.", "easy"),
        ],
        [
            ("In plain weave, how do warp and weft yarns interlace?", "Each yarn alternates over and under successive perpendicular yarns", ["They never cross", "Only the warp forms loops", "Yarns are bonded without interlacement"], "Plain weave has a one-up, one-down interlacement pattern, producing a balanced simple structure.", "easy"),
            ("What does a weave draft communicate?", "The interlacement pattern between warp and weft", ["A yarn's chemical recipe", "The loom's electrical wiring", "A dye bath's pH"], "Weave plans use conventions such as design, draft, and lifting plan to describe structure.", "easy"),
        ],
        [
            ("What is the function of a loom reed?", "Space warp ends and beat the inserted weft into the fabric fell", ["Spin fibres into yarn", "Measure yarn tensile strength", "Apply finishing chemicals"], "The reed controls warp spacing and contributes to beat-up during weaving.", "easy"),
            ("Why coordinate shed formation with weft insertion timing?", "The shed must be open when the weft passes through", ["It determines fibre fineness", "It changes yarn polymerization", "Timing has no effect on loom operation"], "Correct timing supports reliable insertion and reduces stoppages or fabric defects.", "easy"),
        ],
        [
            ("How does a knitted structure differ from a woven structure?", "Knitting forms interconnected loops, while weaving interlaces warp and weft systems", ["Knitting uses no yarn", "Weaving is formed only by chemical bonding", "Both structures have identical geometry"], "Loop geometry gives knitted fabrics distinct stretch and structure compared with woven interlacements.", "easy"),
            ("What characterizes a nonwoven fabric?", "Fibres or filaments are bonded into a web without conventional yarn weaving or knitting", ["Every fibre must be woven on a loom", "It contains no fibres", "It is always a knitted fabric"], "Nonwovens are formed by web creation and bonding methods such as mechanical, thermal, or chemical routes.", "easy"),
        ],
        [
            ("What is a common cause of a warp stripe defect?", "Variation in warp yarn properties, tension, or end arrangement", ["A change in the package barcode", "A difference in weft colour only", "The fabric's storage location"], "Warpwise visual defects can arise from yarn, tension, preparation, or loom conditions.", "easy"),
            ("Why test fabric tensile properties in both warp and weft directions?", "The structure and yarn system can make strength direction-dependent", ["Woven fabrics are always isotropic", "Test direction changes the material's chemistry", "Only one direction can carry load"], "Fabric properties often differ by direction because yarn count, crimp, and structure differ.", "intermediate"),
        ],
    ],
    "TEXTILE04": [
        [
            ("Why desize a woven fabric before some wet-processing steps?", "Remove sizing materials that can obstruct uniform treatment", ["Increase the loom's warp count", "Add twist to the yarn", "Create a mechanical seam"], "Desizing removes applied warp size to improve access for subsequent preparation and dyeing.", "easy"),
            ("What is scouring intended to remove from textile material?", "Natural and processing impurities such as oils, waxes, and dirt", ["The cellulose backbone", "The fabric's warp yarns", "Every colourant from a finished print"], "Scouring cleans fibres or fabrics to improve absorbency and consistency in later processes.", "easy"),
        ],
        [
            ("Why does dye-fibre affinity matter in dyeing?", "It affects uptake, fixation, and the conditions needed for level shade", ["It sets the loom's electrical frequency", "It makes every dye work on every fibre", "It determines the fabric's yarn count"], "Different dye classes interact with fibres through different mechanisms and operating conditions.", "easy"),
            ("What is one role of a mordant in some dye systems?", "Help form or strengthen association between a dye and fibre", ["Remove all fibre moisture", "Increase yarn twist", "Replace colour measurement"], "Mordants can aid fixation for certain dye-fibre combinations, though environmental and safety considerations apply.", "intermediate"),
        ],
        [
            ("What does colour fastness to washing evaluate?", "Resistance of colour to change or transfer during a defined laundering test", ["Fabric tensile strength only", "The dye bath's flow rate", "The yarn count"], "Fastness tests use specified conditions and grading methods; results depend on the tested construction and procedure.", "easy"),
            ("Why control dye-bath pH and temperature?", "They influence dye uptake, reaction rate, levelness, and fixation", ["They set the fabric width automatically", "They remove the need for recipe control", "They only affect package shape"], "Dyeing conditions must suit the dye class and fibre to achieve consistent shade and performance.", "intermediate"),
        ],
        [
            ("What is textile printing designed to do?", "Apply colour in a localized pattern rather than uniformly across the whole material", ["Measure yarn twist", "Set loom shedding timing", "Remove all preparation chemicals"], "Printing places colourant selectively to create a design, followed by suitable fixation and afterwashing.", "easy"),
            ("Why cure or steam a printed textile after application, when required by the print system?", "Fix the colourant to achieve the intended durability", ["Increase the fabric's yarn count", "Set the machine's spindle speed", "Replace all colour measurement"], "Fixation conditions depend on the chemistry and substrate and influence fastness.", "easy"),
        ],
        [
            ("Why characterize textile effluent before selecting treatment?", "Its flow, colour, organic load, salts, and chemicals affect treatment needs", ["All textile effluent has identical composition", "Treatment depends only on fabric width", "Characterization changes the dye class"], "Effluent varies by process and recipe; treatment should be designed around measured loads and discharge limits.", "easy"),
            ("Why use chemical handling controls in textile wet processing?", "Dyes and auxiliaries can present exposure, reaction, or environmental hazards", ["All process chemicals are harmless", "PPE replaces storage compatibility", "Chemical identity is irrelevant"], "Safe chemical management includes identification, compatibility, handling, training, and spill response.", "easy"),
        ],
    ],
    "VLSI01": [
        [
            ("In a CMOS inverter, what happens when the input is high enough to turn the NMOS on and PMOS off?", "The output is pulled toward ground", ["The output is pulled to the supply", "Both transistors must be open", "The input becomes a clock"], "For a valid high input, the NMOS pull-down conducts and the PMOS pull-up is off.", "easy"),
            ("Why is the CMOS inverter switching threshold important?", "It affects noise margins and the interpretation of logic levels", ["It sets the chip package colour", "It is the same as clock frequency", "It determines the metal layer count"], "The voltage-transfer characteristic defines switching behavior and static noise margins.", "intermediate"),
        ],
        [
            ("What is the threshold voltage of a MOS transistor?", "The gate-related condition at which a conducting channel forms under a defined convention", ["The maximum supply current", "The transistor's physical width", "The clock period"], "Threshold voltage is a device parameter whose definition and value depend on operating conditions and process.", "easy"),
            ("Why can short-channel effects alter MOSFET behavior as channel length shrinks?", "The gate has less electrostatic control over the channel", ["The device becomes a mechanical switch", "Shorter devices have no parasitic capacitance", "The threshold voltage becomes universally constant"], "Short-channel effects include threshold roll-off and drain-induced barrier lowering, among others.", "intermediate"),
        ],
        [
            ("Why use De Morgan's laws during combinational logic design?", "Transform logic expressions while preserving Boolean equivalence", ["Change a synchronous circuit into analogue", "Set transistor width automatically", "Remove all logic gates"], "De Morgan's laws relate complements of products and sums and support equivalent logic implementations.", "easy"),
            ("What is a hazard in combinational logic?", "A temporary unwanted output transition caused by unequal path delays", ["A permanent memory element", "A clock that cannot toggle", "A transistor material defect only"], "Logic hazards are transient glitches that may matter if captured or propagated.", "intermediate"),
        ],
        [
            ("What does a setup-time constraint require for a flip-flop?", "Input data be stable for a specified interval before the active clock edge", ["Data change only after reset", "The clock stop permanently", "The output be tied to ground"], "Setup time is a sequential timing requirement for reliable state capture.", "easy"),
            ("What can violate a hold-time requirement?", "Data changes too soon after the active clock edge", ["Data is stable long before the edge", "The clock has a valid period", "The logic has no combinational path"], "Hold checks ensure data remains stable for the required interval after capture.", "easy"),
        ],
        [
            ("Why is dynamic power in CMOS logic related to switching activity and capacitance?", "Charging and discharging capacitances consumes energy as signals toggle", ["Static power is the only power component", "Power is independent of supply voltage", "A clock consumes no energy"], "Dynamic power is commonly approximated as proportional to activity, capacitance, voltage squared, and frequency.", "intermediate"),
            ("What does a PPA trade-off compare in digital design?", "Power, performance, and area objectives", ["Pins, ports, and attributes", "Pressure, process, and atmosphere", "Packets, paths, and addresses"], "PPA summarizes competing implementation goals; optimizing one can worsen another.", "easy"),
        ],
    ],
    "VLSI02": [
        [
            ("What does a Verilog module declaration define?", "A hardware block interface and its implementation scope", ["A transistor's measured threshold voltage", "A PCB's physical dimensions", "A software package manager"], "Modules define ports and internal logic and can be instantiated hierarchically.", "easy"),
            ("Why declare signal widths explicitly in RTL?", "Width affects arithmetic, truncation, and hardware interpretation", ["Width changes only comments", "All signals are infinitely wide", "It prevents synthesis"], "Explicit widths reduce unintended sizing and signedness issues.", "easy"),
        ],
        [
            ("What does a combinational always block need to model?", "Outputs determined by current inputs without unintended storage", ["State retained from an earlier event in every branch", "Only a clock divider", "A physical transistor layout"], "Complete assignments and appropriate sensitivity semantics avoid unintended latches in combinational logic.", "intermediate"),
            ("What is a common RTL cause of an inferred latch?", "A combinational output is not assigned on every control path", ["Every branch assigns an output", "A module has a port", "The testbench has a clock"], "Incomplete combinational assignments imply that the output must retain its previous value.", "easy"),
        ],
        [
            ("For edge-triggered sequential RTL, what usually controls when a register updates?", "A specified clock edge", ["Any change in a comment", "A synthesis report", "The output wire's name"], "Clocked procedural logic models state updates at defined clock edges.", "easy"),
            ("Why assign a reset value consistently in sequential logic?", "Define the known initial state and avoid ambiguous or unsafe startup behavior", ["Increase combinational fan-in", "Guarantee timing closure", "Remove the need for a clock"], "Reset behavior establishes intended state, with synchronous/asynchronous semantics chosen to suit the design.", "easy"),
        ],
        [
            ("What is a testbench in RTL verification?", "A simulation environment that drives inputs and checks expected behavior", ["A fabricated silicon package", "A timing constraint file only", "A transistor doping recipe"], "Testbenches exercise the design model and may use assertions, scoreboards, and coverage.", "easy"),
            ("Why include assertions in a testbench?", "Check properties or protocol expectations during simulation", ["Generate the final chip masks", "Replace all test cases", "Guarantee the silicon cannot fail"], "Assertions make expected behavior explicit and can detect violations in simulation or formal flows.", "easy"),
        ],
        [
            ("Why avoid unintended delays and simulation-only constructs in synthesizable RTL?", "Synthesis may not map them into the intended hardware", ["They always improve timing", "They replace logic operators", "They guarantee portable implementation"], "RTL should use constructs supported by the target synthesis flow for predictable hardware inference.", "easy"),
            ("What is a useful way to make RTL arithmetic synthesis-aware?", "Specify widths, signedness, and overflow behavior deliberately", ["Rely on implicit widths everywhere", "Assume simulation sizing always matches intent", "Remove all type declarations"], "Explicit arithmetic sizing improves correctness and reduces tool-dependent interpretation.", "intermediate"),
        ],
    ],
    "VLSI03": [
        [
            ("Why define clock and interface assumptions before RTL implementation?", "They shape architecture, latency, timing, and integration requirements", ["They determine the chip's logo", "They are irrelevant until after tapeout", "They replace functional specification"], "A clear specification constrains the architecture and verification approach.", "easy"),
            ("What is a microarchitecture specification expected to describe?", "How the architecture's functions are implemented as blocks and state", ["Only the package's outer dimensions", "The fab's cafeteria schedule", "A final test result before design"], "Microarchitecture translates functional requirements into internal datapaths, control, and interfaces.", "easy"),
        ],
        [
            ("What does logic synthesis map RTL into?", "A technology-dependent network of library cells", ["A board-level cable harness", "A list of user accounts", "A package's thermal resistance only"], "Synthesis optimizes and maps a logic representation to available standard cells under constraints.", "easy"),
            ("Why do synthesis constraints matter?", "They guide optimization toward required clocks, interfaces, and design limits", ["They change the RTL source code automatically in every tool", "Constraints cannot affect mapping", "They replace functional verification"], "Timing and design constraints influence mapping and must reflect realistic design requirements.", "intermediate"),
        ],
        [
            ("What does static timing analysis evaluate?", "Timing paths against constraints without applying input test vectors", ["Only transistor colour", "The chip's end-user satisfaction", "The analogue noise in every package"], "STA propagates timing information through paths and checks setup, hold, and other timing requirements.", "easy"),
            ("What is a setup timing violation?", "A data path arrives too late for capture at the required clock edge", ["The input arrives too early after the edge", "A net has no name", "A floorplan is symmetric"], "Setup checks ensure data reaches and stabilizes before the capture edge, considering clock relationships.", "easy"),
        ],
        [
            ("What is the purpose of floorplanning?", "Allocate major blocks, interfaces, and resources within the die area", ["Choose a source-code font", "Set the transistor's chemical symbol", "Verify every functional output"], "Floorplanning establishes placement regions, I/O, power, and macro arrangement early in physical design.", "easy"),
            ("Why consider congestion during placement?", "High routing demand can make implementation difficult and degrade timing", ["Congestion improves every clock path", "Routing resources are unlimited", "It affects only the chip package colour"], "Placement congestion affects routability, buffering, and timing and may require architectural or floorplan changes.", "intermediate"),
        ],
        [
            ("Why run design-rule checks after routing?", "Verify layout geometry follows manufacturing constraints", ["Measure software code coverage", "Confirm every requirement by inspection alone", "Set the chip's logic function"], "DRC identifies physical layout violations relative to a process design rule deck.", "easy"),
            ("What is layout-versus-schematic (LVS) checking intended to verify?", "The extracted layout connectivity matches the intended schematic or netlist", ["The design meets every timing constraint", "The RTL has no syntax errors", "The chip passes its final customer test"], "LVS checks connectivity correspondence; timing, reliability, and functional verification require other checks.", "easy"),
        ],
    ],
    "VLSI04": [
        [
            ("What does a MOS capacitor's C-V curve help characterize?", "Capacitance behavior across accumulation, depletion, and inversion conditions", ["A chip's routing congestion", "The processor's software throughput", "An antenna's radiation pattern"], "MOS capacitor C-V behavior provides information about device electrostatics and interface properties.", "intermediate"),
            ("What is threshold voltage associated with in a MOSFET?", "The gate bias condition for forming a conducting inversion channel under a defined criterion", ["The maximum drain current for every device", "The circuit's clock frequency", "The metal layer thickness"], "Threshold voltage depends on structure, doping, work function, bias, and short-channel effects.", "easy"),
        ],
        [
            ("What is drain-induced barrier lowering (DIBL)?", "A short-channel effect where drain bias lowers the source-channel energy barrier", ["A layout rule for metal spacing", "A method to reduce package size", "A type of clock tree"], "DIBL weakens gate control as drain voltage influences the channel barrier, increasing off-state leakage.", "intermediate"),
            ("Why can subthreshold leakage increase as transistor dimensions scale?", "Short-channel electrostatics and threshold-voltage behavior become harder to control", ["Smaller devices have no gate", "Leakage is independent of device structure", "Scaling removes all off-state current"], "Scaling can worsen leakage through effects including DIBL and threshold variation, depending on technology.", "easy"),
        ],
        [
            ("What is one benefit of CMOS scaling?", "Higher integration density and potentially improved switching performance", ["Elimination of all leakage", "No need for interconnect design", "Unlimited supply voltage"], "Scaling can improve density and performance but introduces power, variability, and interconnect challenges.", "easy"),
            ("Why can interconnect delay become more significant in scaled VLSI?", "Wire resistance and capacitance do not scale like transistor gate delay", ["Wires have zero capacitance", "Transistors stop switching", "Chip dimensions become infinite"], "As devices shrink, interconnect RC can dominate some paths and motivates routing-aware design.", "intermediate"),
        ],
        [
            ("What is process variation?", "Unavoidable differences in device or interconnect parameters across fabrication", ["A change in the RTL variable name", "A deliberate software update", "A fixed clock period"], "Manufacturing variation affects device characteristics and circuit behavior across dies and locations.", "easy"),
            ("Why use statistical corner or Monte Carlo analysis?", "Assess performance and yield sensitivity to parameter variation", ["Prove every device is identical", "Replace all process models", "Set the package's barcode"], "Variation-aware analysis estimates distributions and risk rather than relying only on a single nominal case.", "intermediate"),
        ],
        [
            ("What is electromigration in an interconnect?", "Metal atom transport driven by current density and temperature over time", ["A transistor's logic inversion", "A clock-domain crossing", "A lithography alignment mark"], "Electromigration can cause voids or hillocks and is a reliability concern under current stress.", "easy"),
            ("Why is bias-temperature instability considered in device reliability?", "Long-term electrical and thermal stress can shift transistor parameters", ["It changes only the package label", "It guarantees faster switching", "It affects no circuit behavior"], "BTI mechanisms can shift threshold voltage over time and affect timing or leakage margins.", "intermediate"),
        ],
    ],
}


def main() -> None:
    with BANK.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("Question bank is empty.")
    fields = list(rows[0])
    topics = {}
    titles = {}
    for row in csv.DictReader((DATA_DIR / "topics.csv").open("r", encoding="utf-8-sig", newline="")):
        topics.setdefault(row["course_code"], []).append(row["topic_name"])
    curriculum_rows = csv.DictReader((DATA_DIR / "branch_curriculum.csv").open("r", encoding="utf-8-sig", newline=""))
    for row in curriculum_rows:
        topics.setdefault(row["course_code"], [name.strip() for name in row["topics"].split("|") if name.strip()])
    for row in rows:
        titles.setdefault(row["course_id"], row["quiz_title"])

    additions = []
    keys = set()
    for course_id, topic_sets in PACKS.items():
        if course_id not in titles or len(topics.get(course_id, [])) != 5 or len(topic_sets) != 5:
            raise ValueError(f"Expected an existing five-topic quiz and outline for {course_id}.")
        for topic_index, questions in enumerate(topic_sets):
            if len(questions) < 2:
                raise ValueError(f"Expected at least two drafted questions for {course_id} topic {topic_index + 1}.")
            for prompt, correct, distractors, explanation, difficulty in questions:
                key = (course_id, prompt.casefold())
                if key in keys:
                    raise ValueError(f"Duplicate authored question: {course_id}: {prompt}")
                keys.add(key)
                options = [correct, *distractors]
                answer_index = (len(additions) + 1) % 4
                options[0], options[answer_index] = options[answer_index], options[0]
                additions.append({
                    "course_id": course_id,
                    "quiz_title": titles[course_id],
                    "quiz_topic": "Course-wide practice",
                    "question_topic": topics[course_id][topic_index],
                    "prompt": prompt,
                    "options_json": json.dumps(options, ensure_ascii=False),
                    "answer_index": str(answer_index),
                    "explanation": explanation,
                    "difficulty": difficulty,
                    "review_status": "pending",
                    "reviewer_name": "",
                    "reviewer_role": "",
                    "source_url": "",
                    "review_notes": "Original Nebula draft guided by public topic outlines; instructor review required.",
                    "review_date": "",
                })

    # Make the content build repeatable without replacing any admin-authored data.
    rows = [row for row in rows if (row["course_id"], row["prompt"].casefold()) not in keys]
    existing = {(row["course_id"], row["prompt"].casefold()) for row in rows}
    if any((row["course_id"], row["prompt"].casefold()) in existing for row in additions):
        raise ValueError("Authored question already exists in the bank outside this managed pack.")
    rows.extend(additions)
    with BANK.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Added {len(additions)} original MCQs across {len(PACKS)} computing and engineering courses; all remain pending instructor review.")


if __name__ == "__main__":
    main()
