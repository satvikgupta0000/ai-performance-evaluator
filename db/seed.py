import os
import random
import bcrypt
from datetime import date, timedelta
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT", 5432),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
cur = conn.cursor()

def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(12)).decode()

DEPARTMENTS = ["Engineering", "Product", "Design", "QA", "Operations"]

cur.execute("DELETE FROM evaluations")
cur.execute("DELETE FROM daily_tasks")
cur.execute("DELETE FROM users")
cur.execute("DELETE FROM departments")
cur.execute("DELETE FROM roles")

execute_values(cur,
    "INSERT INTO roles (name) VALUES %s ON CONFLICT DO NOTHING",
    [("employee",), ("manager",), ("hr",)]
)

execute_values(cur,
    "INSERT INTO departments (name) VALUES %s ON CONFLICT DO NOTHING RETURNING id, name",
    [(d,) for d in DEPARTMENTS]
)

cur.execute("SELECT id, name FROM roles")
role_map = {name: rid for rid, name in cur.fetchall()}

cur.execute("SELECT id, name FROM departments")
dept_map = {name: did for did, name in cur.fetchall()}

DEFAULT_PW = hash_pw("Password@123")

hr_users = [
    ("Priya Sharma",  "priya.sharma@company.com"),
    ("Rahul Verma",   "rahul.verma@company.com"),
]

manager_data = [
    ("Arun Kumar",    "arun.kumar@company.com",    "Engineering"),
    ("Sneha Patel",   "sneha.patel@company.com",   "Product"),
    ("Vikram Singh",  "vikram.singh@company.com",  "Design"),
    ("Ananya Gupta",  "ananya.gupta@company.com",  "QA"),
    ("Rohit Mehta",   "rohit.mehta@company.com",   "Operations"),
]

employee_data = [
    ("Arjun Nair",       "arjun.nair@company.com",       "Engineering"),
    ("Kavya Reddy",      "kavya.reddy@company.com",      "Engineering"),
    ("Siddharth Joshi",  "siddharth.joshi@company.com",  "Engineering"),
    ("Meera Krishnan",   "meera.krishnan@company.com",   "Engineering"),
    ("Deepak Yadav",     "deepak.yadav@company.com",     "Product"),
    ("Pooja Iyer",       "pooja.iyer@company.com",       "Product"),
    ("Karan Malhotra",   "karan.malhotra@company.com",   "Product"),
    ("Riya Choudhary",   "riya.choudhary@company.com",   "Product"),
    ("Amit Tiwari",      "amit.tiwari@company.com",      "Design"),
    ("Neha Saxena",      "neha.saxena@company.com",      "Design"),
    ("Varun Chopra",     "varun.chopra@company.com",     "Design"),
    ("Priyanka Bose",    "priyanka.bose@company.com",    "Design"),
    ("Rajesh Pillai",    "rajesh.pillai@company.com",    "QA"),
    ("Anjali Mishra",    "anjali.mishra@company.com",    "QA"),
    ("Nikhil Sharma",    "nikhil.sharma@company.com",    "QA"),
    ("Swati Agarwal",    "swati.agarwal@company.com",    "QA"),
    ("Gaurav Pandey",    "gaurav.pandey@company.com",    "Operations"),
    ("Divya Menon",      "divya.menon@company.com",      "Operations"),
    ("Harsh Srivastava", "harsh.srivastava@company.com", "Operations"),
    ("Tanya Kapoor",     "tanya.kapoor@company.com",     "Operations"),
]

for name, email in hr_users:
    cur.execute(
        "INSERT INTO users (name, email, password_hash, role_id) VALUES (%s,%s,%s,%s)",
        (name, email, DEFAULT_PW, role_map["hr"])
    )

manager_ids = {}
for name, email, dept in manager_data:
    cur.execute(
        "INSERT INTO users (name, email, password_hash, role_id, department_id) VALUES (%s,%s,%s,%s,%s) RETURNING id",
        (name, email, DEFAULT_PW, role_map["manager"], dept_map[dept])
    )
    manager_ids[dept] = cur.fetchone()[0]

employee_ids = []
for name, email, dept in employee_data:
    cur.execute(
        "INSERT INTO users (name, email, password_hash, role_id, department_id, manager_id) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id",
        (name, email, DEFAULT_PW, role_map["employee"], dept_map[dept], manager_ids[dept])
    )
    employee_ids.append(cur.fetchone()[0])

TASKS_BY_DEPT = {
    "Engineering": [
        "Code review for PR", "Bug fix: auth module", "API endpoint implementation",
        "Unit test coverage", "Database query optimization", "CI pipeline fix",
        "Docker image update", "Feature branch development", "Security patch",
        "Performance profiling"
    ],
    "Product": [
        "Sprint planning", "User story writing", "Stakeholder meeting notes",
        "Roadmap update", "Feature prioritization", "Customer feedback analysis",
        "A/B test review", "Release planning", "OKR tracking", "Backlog grooming"
    ],
    "Design": [
        "Wireframe for dashboard", "Icon set creation", "UI review session",
        "Prototype update", "Design system tokens", "Figma component library",
        "User flow mapping", "Accessibility audit", "Brand guideline review",
        "Mobile screen design"
    ],
    "QA": [
        "Test case writing", "Regression testing", "Bug report filing",
        "Smoke test run", "Load test execution", "Test plan review",
        "Automation script update", "Defect triage", "Release sign-off",
        "Cross-browser testing"
    ],
    "Operations": [
        "Server monitoring", "Incident response", "Documentation update",
        "Infra cost review", "Backup verification", "Alert tuning",
        "Runbook update", "Capacity planning", "Vendor coordination",
        "SLA compliance check"
    ],
}

STATUSES = ["not_started", "in_progress", "completed", "completed", "completed", "blocked"]

task_rows = []
end_date = date.today()
start_date = end_date - timedelta(days=29)

for emp_id, (_, _, dept) in zip(employee_ids, employee_data):
    task_pool = TASKS_BY_DEPT[dept]
    performance_bias = random.uniform(0.5, 1.0)

    for day_offset in range(30):
        current_date = start_date + timedelta(days=day_offset)
        if current_date.weekday() >= 5:
            continue

        num_tasks = random.randint(1, 3)
        for _ in range(num_tasks):
            task_name = random.choice(task_pool) + f" #{random.randint(100, 999)}"
            priority = random.randint(1, 5)
            status = random.choice(STATUSES)

            base_completion = int(performance_bias * 100)
            completion_pct = min(100, max(0, base_completion + random.randint(-20, 20)))
            if status == "completed":
                completion_pct = 100
            elif status == "not_started":
                completion_pct = 0

            quality_score = min(10, max(1, int(performance_bias * 10) + random.randint(-2, 2)))
            deadline = current_date + timedelta(days=random.randint(1, 7))

            task_rows.append((
                emp_id, current_date, task_name, priority,
                status, completion_pct, quality_score, deadline, None
            ))

execute_values(cur, """
    INSERT INTO daily_tasks
        (employee_id, task_date, task_name, priority, status, completion_pct, quality_score, deadline, notes)
    VALUES %s
""", task_rows)

conn.commit()
cur.close()
conn.close()

print(f"Seeded: 2 HR, 5 managers, 20 employees, {len(task_rows)} task rows")
print("Default password for all users: Password@123")
