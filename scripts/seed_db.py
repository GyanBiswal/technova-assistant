import sqlite3

from create_db import DB_PATH
from create_db import main as create_database

# (id, name, email, department, role, manager_id, hire_date, location)
EMPLOYEES = [
    (1, "Aarav Mehta", "aarav.mehta@technova.example", "Executive", "CEO", None, "2019-04-01", "Bengaluru"),
    (2, "Priya Nair", "priya.nair@technova.example", "Engineering", "VP Engineering", 1, "2020-02-15", "Bengaluru"),
    (3, "Rohan Iyer", "rohan.iyer@technova.example", "Engineering", "Engineering Manager", 2, "2021-06-01", "Bengaluru"),
    (4, "Sneha Kulkarni", "sneha.kulkarni@technova.example", "Engineering", "Senior Software Engineer", 3, "2021-09-13", "Bengaluru"),
    (5, "Karthik Reddy", "karthik.reddy@technova.example", "Engineering", "Software Engineer", 3, "2023-01-09", "Bengaluru"),
    (6, "Ananya Das", "ananya.das@technova.example", "Engineering", "Software Engineer", 3, "2024-07-01", "Bengaluru"),
    (7, "Vikram Singh", "vikram.singh@technova.example", "Engineering", "QA Engineer", 3, "2025-03-17", "Bengaluru"),
    (8, "Meera Joshi", "meera.joshi@technova.example", "Sales", "Head of Sales", 1, "2020-08-03", "Mumbai"),
    (9, "Arjun Kapoor", "arjun.kapoor@technova.example", "Sales", "Account Executive", 8, "2022-04-11", "Delhi"),
    (10, "Divya Menon", "divya.menon@technova.example", "Sales", "Account Executive", 8, "2023-10-02", "Chennai"),
    (11, "Nikhil Rao", "nikhil.rao@technova.example", "Product", "Product Manager", 1, "2022-01-17", "Bengaluru"),
    (12, "Farah Khan", "farah.khan@technova.example", "HR", "HR Manager", 1, "2021-03-08", "Bengaluru"),
    (13, "Sanjay Gupta", "sanjay.gupta@technova.example", "Finance", "Finance Manager", 1, "2021-11-22", "Bengaluru"),
    (14, "Tara Bose", "tara.bose@technova.example", "Engineering", "Software Engineer", 3, "2026-09-01", "Bengaluru"),
    (15, "Rahul Verma", "rahul.verma@technova.example", "Customer Support", "Support Lead", 1, "2022-05-09", "Bengaluru"),
]


# (id, name, product, status, lead_id, start_date, end_date)
PROJECTS = [
    (1, "Project Atlas", "NovaDesk", "In Progress", 3, "2026-05-04", None),
    (2, "Project Beacon", "NovaInsight", "In Progress", 4, "2026-06-01", None),
    (3, "Project Compass", "NovaDesk", "Completed", 3, "2026-01-12", "2026-06-30"),
    (4, "Project Delta", "NovaInsight", "On Hold", 11, "2026-03-02", None),
    (5, "Project Echo", "NovaDesk", "Planning", 2, "2026-11-15", None),
]


# (id, project_id, title, assignee_id, status, priority, due_date)
TASKS = [
    (1, 1, "Design ticket routing rules", 5, "Done", "High", "2026-08-15"),
    (2, 1, "Build chat integration API", 6, "In Progress", "High", "2026-11-20"),
    (3, 1, "Fix ticket assignment bug", 5, "In Progress", "High", "2026-10-20"),
    (4, 1, "Write API test cases", 7, "To Do", "Medium", "2026-11-25"),
    (5, 1, "Update canned replies UI", 14, "In Progress", "Low", "2026-11-12"),
    (6, 2, "Create dashboard export feature", 4, "In Progress", "High", "2026-11-18"),
    (7, 2, "Add email alert thresholds", 5, "To Do", "Medium", "2026-12-05"),
    (8, 2, "Optimize report query speed", 6, "In Progress", "High", "2026-10-28"),
    (9, 2, "Review scheduled report design", 4, "Done", "Low", "2026-09-30"),
    (10, 3, "Launch satisfaction survey", 5, "Done", "High", "2026-05-20"),
    (11, 3, "Migrate old tickets", 6, "Done", "Medium", "2026-06-10"),
    (12, 3, "Final QA sign-off", 7, "Done", "High", "2026-06-25"),
    (13, 4, "Evaluate spreadsheet connector options", 11, "To Do", "Medium", "2026-10-10"),
    (14, 4, "Prototype data connector", 6, "In Progress", "Low", "2026-09-15"),
    (15, 5, "Draft project requirements", 2, "To Do", "High", "2026-11-30"),
    (16, 5, "Estimate team and timeline", 4, "To Do", "Medium", "2026-12-10"),
]


# (id, sale_date, region, product, customer, amount_rs)
SALES = [
    (1, "2026-07-08", "North", "NovaDesk", "Himalaya Retail Pvt Ltd", 1800000),
    (2, "2026-09-14", "North", "NovaDesk", "Punjab Agro Services", 1200000),
    (3, "2026-07-22", "North", "NovaInsight", "Delhi Logistics Co", 1500000),
    (4, "2026-08-30", "North", "NovaInsight", "Jaipur Textiles Ltd", 1000000),
    (5, "2026-07-05", "South", "NovaDesk", "Kaveri Telecom", 2500000),
    (6, "2026-08-18", "South", "NovaDesk", "Malabar Foods", 2000000),
    (7, "2026-07-29", "South", "NovaInsight", "Deccan Healthcare", 2200000),
    (8, "2026-09-09", "South", "NovaInsight", "Chennai Auto Parts", 1800000),
    (9, "2026-08-04", "East", "NovaDesk", "Ganga Finance Ltd", 900000),
    (10, "2026-09-21", "East", "NovaDesk", "Kolkata Media House", 600000),
    (11, "2026-08-12", "East", "NovaInsight", "Odisha Steel Works", 600000),
    (12, "2026-09-26", "East", "NovaInsight", "Assam Tea Traders", 400000),
    (13, "2026-07-15", "West", "NovaDesk", "Konkan Shipping", 2000000),
    (14, "2026-08-25", "West", "NovaDesk", "Pune Education Trust", 1500000),
    (15, "2026-07-31", "West", "NovaInsight", "Mumbai Retail Group", 1700000),
    (16, "2026-09-18", "West", "NovaInsight", "Gujarat Chemicals Ltd", 1300000),
]


def seed_employees(conn):
    conn.executemany(
        "INSERT INTO employees "
        "(id, name, email, department, role, manager_id, hire_date, location) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        EMPLOYEES,
    )


def seed_projects(conn):
    conn.executemany(
        "INSERT INTO projects "
        "(id, name, product, status, lead_id, start_date, end_date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        PROJECTS,
    )

def seed_tasks(conn):
    conn.executemany(
        "INSERT INTO tasks "
        "(id, project_id, title, assignee_id, status, priority, due_date) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        TASKS,
    )    

def seed_sales(conn):
    conn.executemany(
        "INSERT INTO sales "
        "(id, sale_date, region, product, customer, amount_rs) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        SALES,
    )

def main():
    create_database()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    seed_employees(conn)
    seed_projects(conn) 
    seed_tasks(conn)
    seed_sales(conn)
    conn.commit()
    conn.close()
    print(f"Seeded {len(EMPLOYEES)} employees")
    print(f"Seeded {len(PROJECTS)} projects")
    print(f"Seeded {len(TASKS)} tasks")
    print(f"Seeded {len(SALES)} sales")


if __name__ == "__main__":
    main()