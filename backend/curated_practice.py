"""Curated focused practice sets for Nebula's five pilot subjects.

These are short learning checks, not comprehensive exam question banks. Every
item carries a topic mapping and an explanation that is shown after submission.
"""
from datetime import datetime, timezone

TOPIC_AREAS = (
    "Fundamentals & Core Concepts",
    "Architecture & Principles",
    "Primary Protocols & Operations",
    "Data Structures & Types",
    "Algorithms & Control Logic",
    "Implementation & Syntax",
    "Optimization & Performance",
    "Error Handling & Debugging",
)


def _q(area, prompt, options, answer, explanation):
    return {"topic_index": area, "prompt": prompt, "options": options,
            "answer_index": answer, "explanation": explanation}


SETS = [
    ("DSA", "Data Structures & Algorithms", [
        _q(0, "A service must undo the most recent operation first. Which structure matches that order?", ["Queue", "Stack", "Sorted array", "Graph"], 1, "A stack is last-in, first-out, so the newest operation is removed first."),
        _q(1, "You need frequent reads by numeric index and few insertions near the front. Which choice is usually simplest?", ["Array", "Singly linked list", "Queue", "Binary tree"], 0, "Arrays support constant-time indexed access; inserting at the front can be costly, but that is rare here."),
        _q(2, "A breadth-first graph traversal needs to visit the earliest discovered frontier node next. Which structure should hold that frontier?", ["Stack", "Queue", "Heap", "Hash map"], 1, "FIFO queue order processes vertices by discovery distance, which is the basis of BFS."),
        _q(3, "A dictionary-like lookup is needed for student IDs, with no requirement to keep keys sorted. Which structure is a natural fit?", ["Hash table", "Stack", "Linked list", "Queue"], 0, "A hash table provides expected fast lookup by key; ordering is not its primary guarantee."),
        _q(4, "Binary search is applied to an array of n sorted values. What is its worst-case comparison growth?", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 1, "Each comparison discards about half the remaining range, giving logarithmic growth."),
        _q(5, "An algorithm scans a list once, doing constant work per element. What is its time complexity?", ["O(1)", "O(log n)", "O(n)", "O(n log n)"], 2, "The number of operations grows proportionally to the number of list elements."),
        _q(6, "A hash table lookup is expected to be constant time on average. Which condition can make it slower?", ["Many keys collide into the same bucket", "The table stores strings", "The keys are unique", "The table has a hash function"], 0, "Collisions require extra comparisons or probing; worst-case lookup can approach linear time."),
        _q(7, "Why must binary search not be used directly on an unsorted array?", ["Its half-range elimination relies on sorted order", "It only works with linked lists", "It requires duplicate values", "It always uses O(n²) memory"], 0, "The algorithm chooses a half based on ordering; without sorted order, the target may be discarded incorrectly."),
    ]),
    ("PY", "Python for Data Science", [
        _q(0, "What does `items = [2, 4]; items.append(6)` leave in `items`?", ["[2, 4]", "[2, 4, 6]", "[6, 2, 4]", "None"], 1, "`append` mutates the list by placing the new item at the end."),
        _q(1, "A function should return a new list while leaving its input unchanged. Which approach best expresses that intent?", ["Mutate the input with append", "Build and return a separate list", "Use a global list", "Delete the input first"], 1, "A separate result avoids changing caller-owned state; the function can construct and return it."),
        _q(2, "What does `scores.get('midterm', 0)` return when `midterm` is absent?", ["KeyError", "0", "None always", "False always"], 1, "`dict.get` returns the supplied default when the key is missing."),
        _q(3, "Which collection is designed to store unique hashable values?", ["list", "tuple", "set", "str"], 2, "A set keeps distinct hashable elements and is useful for membership checks."),
        _q(4, "A loop visits each of n records once and performs constant work per record. What is its time growth?", ["O(1)", "O(log n)", "O(n)", "O(n²)"], 2, "One constant-work iteration per record gives linear time."),
        _q(5, "What does `enumerate(names)` provide in a loop?", ["Each item and its index", "Only sorted names", "A dictionary of counts", "A copy of every object"], 0, "`enumerate` yields index-item pairs, optionally starting from a chosen index."),
        _q(6, "Why can repeated `result = result + [item]` be inefficient while building a long list?", ["It may allocate and copy a new list repeatedly", "It sorts the list each time", "It converts values to strings", "It deletes prior elements"], 0, "List concatenation creates a new list; repeated copying can produce quadratic total work. `append` is usually better."),
        _q(7, "A function receives a possibly missing numeric value. What should robust code do before arithmetic?", ["Assume it is always an integer", "Validate or handle the missing case", "Convert it to a set", "Catch every exception and ignore it"], 1, "Explicit input validation or a defined missing-value path prevents accidental type errors and hidden failures."),
    ]),
    ("DBMS", "Database Management Systems", [
        _q(0, "What property should a primary key have for each row?", ["It may be duplicated", "It uniquely identifies the row", "It must contain a password", "It must be a date"], 1, "A primary key provides a unique, non-null identifier for each row."),
        _q(1, "Why split repeated customer details into a Customers table and reference it from Orders?", ["To reduce duplication and update anomalies", "To remove all relationships", "To prevent filtering", "To store every value as text"], 0, "Normalization can keep one authoritative customer record and avoid inconsistent repeated copies."),
        _q(2, "Which SQL clause filters individual rows before grouping?", ["HAVING", "WHERE", "ORDER BY", "LIMIT"], 1, "`WHERE` filters input rows; `HAVING` filters groups after aggregation."),
        _q(3, "What does a foreign key typically enforce?", ["Referential integrity to a referenced key", "Sorted results", "Automatic encryption", "A unique value in every non-key column"], 0, "A foreign-key constraint checks that a reference points to an allowed parent key, subject to the schema rules."),
        _q(4, "A query groups orders by customer and keeps only customers with more than five orders. Which clause filters that count?", ["WHERE COUNT(*) > 5", "HAVING COUNT(*) > 5", "ORDER BY COUNT(*) > 5", "FROM COUNT(*) > 5"], 1, "Aggregate conditions are applied to groups with `HAVING`."),
        _q(5, "What does a transaction provide when two related updates must succeed together or not at all?", ["Atomicity", "Indexing", "Sorting", "Sharding"], 0, "Atomicity makes the transaction all-or-nothing, avoiding a partial update."),
        _q(6, "Why can an index speed up a selective lookup but slow down writes?", ["The index must also be maintained when rows change", "Indexes disable query planning", "Every lookup scans the full table", "Indexes remove the base data"], 0, "An index can reduce search work, but inserts, deletes, and updates may need index maintenance."),
        _q(7, "An application builds SQL by concatenating untrusted input into a query. What is the safer common approach?", ["Parameterized queries", "More string concatenation", "Client-side hiding", "Disabling all constraints"], 0, "Parameters keep user input as data instead of executable SQL syntax, reducing injection risk."),
    ]),
    ("CN", "Computer Networks", [
        _q(0, "Which IP-layer device function chooses a next hop between different networks?", ["Routing", "DNS caching", "File compression", "HTML parsing"], 0, "Routers use network-layer addressing and routing information to select a next hop."),
        _q(1, "Why is the Internet organized as layers of protocols?", ["Each layer offers services while hiding many lower-level details", "Every layer uses the same address", "It guarantees zero packet loss", "It eliminates the need for standards"], 0, "Layering separates responsibilities and allows implementations to interoperate through defined interfaces."),
        _q(2, "Which transport protocol provides ordered delivery and retransmission as part of its core service?", ["UDP", "TCP", "ARP", "IP"], 1, "TCP provides a reliable ordered byte stream using acknowledgements and retransmission."),
        _q(3, "Which address is normally used by an Ethernet switch to forward a frame on a local link?", ["Destination MAC address", "HTTP path", "TCP port only", "DNS name"], 0, "A layer-2 switch learns MAC addresses and forwards frames within the LAN."),
        _q(4, "A router decrements a packet's TTL at each hop. What is the purpose?", ["Prevent a packet from circulating forever", "Encrypt the payload", "Guarantee delivery", "Choose the application port"], 0, "TTL limits a packet's lifetime; routers discard it when the value reaches zero."),
        _q(5, "What does DNS commonly resolve for a client starting a connection to a website?", ["A domain name to an IP address", "A MAC address to a password", "A URL path to a TCP sequence number", "An Ethernet frame to HTML"], 0, "DNS returns records such as IP addresses associated with a domain name."),
        _q(6, "Why might a real-time voice app choose UDP and add its own loss handling?", ["Fresh audio can matter more than retransmitting delayed packets", "UDP guarantees every packet arrives", "UDP automatically orders all messages", "TCP cannot carry audio"], 0, "For interactive media, late retransmissions may be less useful than timely current data; the app must handle trade-offs."),
        _q(7, "Two hosts on the same LAN can exchange IP packets but cannot reach an external network. Which device function is a likely place to inspect?", ["Default gateway/router", "CSS stylesheet", "Local keyboard driver", "Domain registrar only"], 0, "The default gateway routes traffic off the local subnet, so its address and route are key checks."),
    ]),
    ("OS", "Operating Systems", [
        _q(0, "What is a process?", ["A program in execution with state and resources", "A source file that has never run", "A CPU cache line", "A network protocol"], 0, "A process is a running program instance with execution state and allocated resources."),
        _q(1, "What is a common distinction between two threads in one process and two separate processes?", ["Threads share much of the address space; processes usually have separate address spaces", "Threads always run on different machines", "Processes cannot have files open", "Threads have no execution state"], 0, "Threads share process resources such as memory while retaining their own stack and execution context."),
        _q(2, "What does a context switch do?", ["Saves one task's execution state and restores another's", "Deletes the ready queue", "Formats virtual memory", "Changes source code into a process"], 0, "The OS saves/restores state so the CPU can run a different process or thread."),
        _q(3, "What does virtual memory primarily provide to each process?", ["An address-space abstraction mapped to physical memory and backing storage", "Unlimited physical RAM", "A replacement for every CPU register", "Guaranteed constant-time disk access"], 0, "Virtual memory gives a process a logical address space that the system maps to physical pages and, when needed, backing storage."),
        _q(4, "Which is one of the classic necessary conditions associated with deadlock?", ["Circular wait", "Infinite memory", "Single-threaded execution", "Sorted process IDs"], 0, "Circular wait is one of the Coffman conditions; deadlock requires all four conditions together."),
        _q(5, "In round-robin scheduling, what happens when a runnable task's time slice expires?", ["It is preempted and typically returns to the ready queue", "It is always terminated", "It permanently owns the CPU", "It is moved to disk"], 0, "Round robin gives each ready task a bounded slice, then schedules another runnable task."),
        _q(6, "Why can an extremely short time slice hurt throughput?", ["More CPU time is spent switching tasks", "It removes all waiting", "It makes every task run in parallel", "It guarantees cache hits"], 0, "Context-switch overhead can consume a larger share of CPU time as slices become very short."),
        _q(7, "Two threads increment the same shared counter without synchronization. What risk exists?", ["A race condition can cause a lost update", "The counter becomes immutable", "The process automatically forks", "The OS guarantees both increments are atomic"], 0, "Interleaved read-modify-write operations can overwrite each other unless protected or made atomic."),
    ]),
]


def curated_practice_quizzes():
    now = datetime.now(timezone.utc)
    quizzes = []
    for course_id, course_name, questions in SETS:
        built = []
        for item in questions:
            question = {key: value for key, value in item.items() if key != "topic_index"}
            question["topic"] = f"{course_name} - {TOPIC_AREAS[item['topic_index']]}"
            built.append(question)
        quizzes.append({
            "seed_key": f"nebula-practice-v1:{course_id}",
            "title": f"{course_name} focused practice",
            "course_id": course_id,
            "topic": f"{course_name} - Fundamentals & Core Concepts",
            "difficulty": "mixed",
            "assessment_type": "topic_practice",
            "description": "An 8-question practice set with explanations. Use it to check understanding, then review the linked lessons; it is not a complete exam syllabus.",
            "source": "Nebula curated practice v1",
            "published": True,
            "created_at": now,
            "questions": built,
        })
    return quizzes
