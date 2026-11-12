"""Idempotently publish the original Nebula pilot lesson pack to MongoDB."""
from __future__ import annotations

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

LESSON_PACK = [
    {
        "course_id": "DSA", "topic_id": "DSA_T1", "title": "Choose a structure for the job",
        "summary": "Compare arrays, linked lists, stacks, queues, and hash tables by the operation you need.",
        "content": "A data structure is a way to arrange values so particular operations are convenient. There is no single structure that is best for every task.\n\nAn array stores items in indexed positions. Reading item i is fast, but inserting near the beginning can require shifting later items. A linked list connects nodes; inserting after a known node is simple, while finding the i-th item requires walking from the head.\n\nA stack follows last-in, first-out order. It is useful for undo history, nested brackets, and depth-first traversal. A queue follows first-in, first-out order and suits print jobs or breadth-first traversal. A hash table maps keys to values and is usually a good choice for quick lookup by key.\n\nWorked choice: to check whether a username is already present, use a set or hash table. To process support tickets in arrival order, use a queue. To undo the most recent edit first, use a stack.\n\nTry it: pick a structure for (1) reading a score at a known index, (2) serving people in line, and (3) looking up a student by ID. Explain which operation matters most in each case.\n\nRemember: begin with the operations and constraints, then choose the structure. Big-O describes how work grows; it does not replace measuring real workloads.",
        "position": 1,
    },
    {
        "course_id": "DSA", "topic_id": "DSA_T2", "title": "Read a simple Big-O comparison",
        "summary": "Use input size n to describe how an algorithm's work grows.",
        "content": "Big-O gives an upper-growth description of an algorithm as input size n becomes large. It helps compare designs, but it does not state an exact number of seconds.\n\nO(1) work stays bounded as n grows, such as reading an array element by index. O(log n) grows slowly when each step removes a fixed fraction of the remaining candidates, as in binary search on sorted data. O(n) examines each item once. O(n log n) commonly appears in efficient comparison sorting. O(n²) can arise from comparing every pair in a nested loop.\n\nWorked example: a loop over n values does about n checks, so its growth is O(n). Two nested loops over the same n values do about n × n checks, so their growth is O(n²). If the inner loop only halves the remaining range, the total may instead be O(n log n).\n\nWhen simplifying, keep the fastest-growing term and ignore constant multipliers: 3n² + 4n + 8 is O(n²). This is a growth class, not a precise runtime promise.\n\nTry it: estimate the growth of one loop that scans a list, then a pair of full nested loops. State the operation being counted and what n represents.\n\nCheck assumptions: binary search requires sorted input and efficient access to its middle element. Always include such prerequisites in your analysis.",
        "position": 2,
    },
    {
        "course_id": "PY", "topic_id": "PY_T1", "title": "Python values, names, and decisions",
        "summary": "Follow how Python names values and chooses a branch with if/elif/else.",
        "content": "A variable name refers to an object. Assignment binds a name to a value: attempts = 4. Python infers the value's type at runtime; names can later refer to values of another type, though keeping a clear meaning makes code easier to maintain.\n\nUse descriptive names such as quiz_score rather than x when the value has a clear role. Strings hold text, integers whole numbers, floats decimal values, and booleans True or False.\n\nA conditional runs a branch based on a boolean expression:\n\nscore = 72\nif score >= 80:\n    band = \"strong\"\nelif score >= 50:\n    band = \"building\"\nelse:\n    band = \"start here\"\n\nPython checks the conditions from top to bottom and executes the first matching branch. Indentation marks which statements belong to a branch.\n\nTry it: set minutes to 30. Write conditions that label less than 15 as \"short\", 15 through 45 as \"focused\", and more than 45 as \"long\". Test boundary values 14, 15, 45, and 46.\n\nA useful habit is to test boundaries and unexpected inputs. If a score might be missing, handle that case before comparing it with a number.",
        "position": 1,
    },
    {
        "course_id": "PY", "topic_id": "PY_T2", "title": "Work with lists and dictionaries",
        "summary": "Choose a list for ordered items and a dictionary for values addressed by key.",
        "content": "A list keeps items in order and supports access by position: scores = [65, 80, 72]. Indexing starts at zero, so scores[0] is 65. Use a list when sequence and iteration matter.\n\nA dictionary maps keys to values: learner = {\"name\": \"Asha\", \"score\": 72}. Retrieve a value with learner[\"score\"]. If a key may be absent, learner.get(\"streak\", 0) returns a default instead of raising KeyError.\n\nTo visit each score, use for score in scores:. To visit key/value pairs, use for key, value in learner.items():. Keep indentation consistent because it defines the loop body.\n\nWorked example: build a dictionary of topic scores, then select topics below 50 with a loop. The loop should examine every key and compare its value with 50.\n\nTry it: create a list with three quiz scores, compute its average, then create a dictionary with a student's name and average. Check what happens if a requested dictionary key is missing.\n\nLists are mutable, so appending changes the list. A dictionary key must be hashable; strings are common keys. Pick the collection based on how you need to find and use the data.",
        "position": 2,
    },
    {
        "course_id": "DBMS", "topic_id": "DBMS_T1", "title": "Rows, columns, and keys",
        "summary": "Model a small relational table and identify a reliable primary key.",
        "content": "A relational database organizes related records into tables. A table has columns (attributes) and rows (records). For example, Student(student_id, name, level) stores one student's details per row.\n\nA primary key uniquely identifies each row. student_id is safer than name because two students can share a name and names can change. A foreign key stores a reference to a key in another table. An Enrollment(student_id, course_id) table can connect students and courses without repeating all course details for every student.\n\nThis separation reduces repeated data. If a course title changes, update it in the Course table rather than correcting many copied enrollment rows. Constraints help keep references valid.\n\nWorked design: Student has student_id as its primary key; Course has course_id; Enrollment uses the pair (student_id, course_id) as a composite key and references both parent tables.\n\nTry it: sketch Course, Student, and Enrollment tables for a learning app. Mark primary keys and foreign keys. Decide how to prevent the same student from enrolling in the same course twice.\n\nA schema is a design, not the data itself. Choose constraints that match the real rules and validate them in the database.",
        "position": 1,
    },
    {
        "course_id": "DBMS", "topic_id": "DBMS_T2", "title": "Read and filter a SELECT query",
        "summary": "Use SELECT, FROM, WHERE, and ORDER BY to request a focused result set.",
        "content": "SQL describes the rows and columns you want from a database. A basic query is:\n\nSELECT name, level\nFROM Student\nWHERE level = 'Year 1'\nORDER BY name;\n\nSELECT lists output columns. FROM names the table. WHERE keeps rows that match a condition. ORDER BY sorts the result; add DESC for descending order. A query returns a result set and does not change stored rows.\n\nUse single quotes for text values in common SQL dialects. For multiple conditions, AND requires both conditions to be true, while OR accepts either. Be careful with NULL: use IS NULL rather than = NULL.\n\nWorked task: to show courses with at least 10 hours, select the course name and estimated hours from Course where estimated_hours >= 10.\n\nTry it: write a query to list each student's name and level for Year 2, sorted by name. Then change the filter to include Year 1 OR Year 2.\n\nAvoid SELECT * in code that only needs a few fields. Naming columns makes the intent clear and reduces unnecessary data transfer.",
        "position": 2,
    },
    {
        "course_id": "CN", "topic_id": "CN_T1", "title": "Follow a packet across a network",
        "summary": "Separate application data, transport, IP routing, and local link delivery.",
        "content": "When an application sends data, network layers add information needed for delivery. A useful simplified view is: application message → transport segment → IP packet → link frame. Each layer serves a different job.\n\nThe transport layer uses ports to deliver data to an application endpoint. IP addresses help route packets between networks. On one local link, a frame uses link-layer addressing to reach the next device. A router removes the incoming link frame and sends the IP packet onward inside a new frame for the next link.\n\nA common mistake is to assume the link-layer address is used end-to-end across the whole internet. It normally identifies delivery on the current local link; routers handle forwarding between links.\n\nWorked path: your laptop sends a request to a server. It frames the packet for the local Wi-Fi gateway. The router forwards the packet toward the server, using a new link frame for each next hop. The server's response follows a routed path back.\n\nTry it: explain which information identifies (1) the receiving application, (2) the destination host across networks, and (3) the next device on the local link.\n\nThis model is simplified: real stacks include additional protocols and security layers. Keep the responsibilities distinct when debugging connectivity.",
        "position": 1,
    },
    {
        "course_id": "CN", "topic_id": "CN_T2", "title": "Choose TCP or UDP for a task",
        "summary": "Compare transport services and choose based on reliability, ordering, and latency needs.",
        "content": "TCP provides a reliable, ordered byte stream between endpoints. It detects loss and retransmits data as needed. The application sees bytes rather than separate message boundaries. This suits many web pages, file transfers, and remote terminal sessions.\n\nUDP sends datagrams without TCP's built-in delivery and ordering guarantees. It has lower protocol overhead and lets an application decide how to handle loss, timing, or recovery. Real-time voice, games, and some DNS exchanges commonly use UDP, but the application may add its own reliability or congestion handling.\n\nNeither protocol is universally faster or better. Reliability and latency depend on the network, application behavior, and what a delayed packet means. A late voice packet may be less useful than a small gap; a missing file block must be recovered.\n\nWorked choice: a large file download generally needs complete, ordered data, so TCP is a natural fit. A live game update may prioritize fresh state over retransmitting an outdated position, so UDP can fit when the application handles its needs.\n\nTry it: choose a transport for a chat message, a live audio stream, and a file download. State what matters most in each choice.\n\nModern protocols can use other transports too. Learn the problem requirements before selecting a protocol.",
        "position": 2,
    },
    {
        "course_id": "OS", "topic_id": "OS_T1", "title": "Process, program, and thread",
        "summary": "Distinguish a program on disk from a running process and its threads.",
        "content": "A program is a set of instructions stored for execution. A process is a running instance with its own execution state and resources, such as an address space and open handles. Starting the same program twice can create two processes.\n\nA thread is an execution path within a process. Threads in one process share much of that process's memory, while each thread has its own stack and execution state. Shared memory makes communication convenient, but concurrent writes need coordination to avoid race conditions.\n\nWorked example: a browser may use multiple processes for isolation and multiple threads within a process to handle work concurrently. The exact design depends on the operating system and application.\n\nTry it: describe what two workers in one process share and one kind of state that remains private to each thread. Explain why updating the same shared counter without coordination can lose updates.\n\nMore threads do not always make work faster. CPU-bound tasks, I/O waits, scheduling, and synchronization costs all matter. Treat process/thread as operating-system abstractions and verify details for the platform you use.",
        "position": 1,
    },
    {
        "course_id": "OS", "topic_id": "OS_T2", "title": "How a scheduler shares the CPU",
        "summary": "Understand ready queues, preemption, and trade-offs in CPU scheduling.",
        "content": "A scheduler chooses which ready task gets CPU time. A task may be ready to run, running on a CPU, or blocked while waiting for something such as disk or network input. When the wait ends, it can return to the ready queue.\n\nIn non-preemptive scheduling, a running task keeps the CPU until it finishes or blocks. In preemptive scheduling, the operating system can interrupt it and choose another task. Preemption helps share the CPU, but switching tasks has overhead.\n\nScheduling policies balance goals such as response time, throughput, fairness, and deadline behavior. First-come, first-served is simple but a long job can make short jobs wait. Round robin gives each ready task a time slice; very short slices increase switching, while long slices feel less responsive.\n\nWorked example: for an interactive editor and a background export, a policy that lets interactive work respond promptly may improve user experience, while the export still needs fair CPU time to complete.\n\nTry it: draw a ready queue with three tasks and a time slice. Show which task runs next after one slice, then explain how blocking for I/O changes the queue.\n\nThere is no single best policy for all systems. Consider the workload and measure the chosen policy against the goal.",
        "position": 2,
    },
]


def seed_lessons(db):
    lessons = db.lessons
    lessons.create_index("seed_key", unique=True, sparse=True)
    inserted = 0
    existing = 0
    now = datetime.now(timezone.utc)
    for lesson in LESSON_PACK:
        seed_key = f"nebula-pilot-v1:{lesson['topic_id']}"
        document = {
            **lesson, "seed_key": seed_key, "source": "Nebula original pilot content",
            "video_url": "", "published": True, "created_at": now,
        }
        result = lessons.update_one({"seed_key": seed_key}, {"$setOnInsert": document}, upsert=True)
        inserted += int(result.upserted_id is not None)
        existing += int(result.upserted_id is None)
    return inserted, existing


def main():
    uri = os.getenv("MONGODB_URI")
    database = os.getenv("MONGODB_DB", "nebula")
    if not uri:
        raise SystemExit("MONGODB_URI is missing; no changes were made.")
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    try:
        client.admin.command("ping")
        inserted, existing = seed_lessons(client[database])
        print(f"Pilot lessons published: {inserted} new, {existing} already seeded, {len(LESSON_PACK)} total.")
    finally:
        client.close()


if __name__ == "__main__":
    main()
