import csv
import random
import uuid
from datetime import datetime, timedelta

# ---------------- Define Issues & Reasons ---------------- #
ISSUES = {
    "SQL server db connection": [
        "The server is low on resources like memory, cpu, io serving etc.",
        "Too many sessions blocking on server.",
        "Listener switch-over happened, DB inaccessible for some time.",
        "SQL service not online due to failure.",
        "Target DB not online due to recovery or crash."
    ],
    "SQL server high CPU": [
        "A bad or inefficient query running too long.",
        "Index/table scan causing server overhead.",
        "More connections than expected hitting the server.",
        "Queries returning too many rows causing overload."
    ],
    "SQL server deadlocks": [
        "Poor transaction isolation levels.",
        "Missing indexes causing lock contention.",
        "Application logic causing circular locking.",
        "Batch queries holding locks too long."
    ],
    "SQL server memory pressure": [
        "Buffer pool exhaustion due to heavy queries.",
        "High concurrent query execution.",
        "Query execution plans consuming excessive memory.",
        "In-Memory OLTP pressure."
    ],
    "SQL server disk I/O bottleneck": [
        "Underlying storage subsystem is slow.",
        "Excessive tempdb usage under workload.",
        "Missing indexes leading to full scans.",
        "Transaction log growth issue filling disk."
    ],
    "SQL server availability group failover": [
        "Cluster node heartbeat lost.",
        "Automatic failover triggered.",
        "Cluster service instability.",
        "Log send queue high delaying synchronization."
    ]
}

# ---------------- Log Generator ---------------- #
def generate_log_entries(issue, reason, start_time):
    actions = [
        "DBA acknowledged the incident.",
        "Investigated system performance counters.",
        "Checked SQL server error logs.",
        "Identified root cause: " + reason,
        "Applied mitigation step.",
        "Service returned to healthy state."
    ]
    logs = []
    current_time = start_time
    for action in actions:
        logs.append(f"[{current_time.strftime('%Y-%m-%d %H:%M')}] {action}")
        current_time += timedelta(minutes=random.randint(5, 20))
    return " || ".join(logs)

# ---------------- Record Generator ---------------- #
def generate_records(n=1000):
    records = []
    for _ in range(n):
        ticket_id = str(uuid.uuid4())[:8]
        issue = random.choice(list(ISSUES.keys()))
        reason = random.choice(ISSUES[issue])
        title = issue
        description = f"{issue} observed. Possible reason: {reason}"
        start_time = datetime.now() - timedelta(days=random.randint(1, 30))
        log_entries = generate_log_entries(issue, reason, start_time)
        records.append({
            "ticket_id": ticket_id,
            "title": title,
            "description": description,
            "log_entries": log_entries
        })
    return records

# ---------------- Write CSV ---------------- #
def write_csv(filename="sqlserver_incidents.csv", n=500):
    records = generate_records(n)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "title", "description", "log_entries"])
        writer.writeheader()
        writer.writerows(records)
    return filename

if __name__ == "__main__":
    write_csv("sqlserver_incidents.csv", 1000)
    print("Generated sqlserver_incidents.csv with 1000 records")
