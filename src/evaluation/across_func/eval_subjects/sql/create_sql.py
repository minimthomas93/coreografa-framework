import sqlite3
import random
import string
from datetime import datetime, timedelta

def random_name(length=8):
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def random_date(start_year=2000, end_year=2023):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

def create_company_db(db_path='company.db', n_rows=5000):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Speed up bulk inserts
    cur.execute("PRAGMA synchronous = OFF;")
    cur.execute("PRAGMA journal_mode = MEMORY;")

    # Drop tables if they exist
    tables = [
        "departments","employees","projects","tasks","clients",
        "meetings","salaries","benefits","locations","assets","trainings"
    ]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table};")

    # ------------------------
    # Create tables
    # ------------------------

    cur.execute("""
    CREATE TABLE departments (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        location TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        age INTEGER,
        department_id INTEGER,
        hire_date TEXT,
        FOREIGN KEY(department_id) REFERENCES departments(id)
    );
    """)

    cur.execute("""
    CREATE TABLE projects (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department_id INTEGER,
        start_date TEXT,
        end_date TEXT,
        FOREIGN KEY(department_id) REFERENCES departments(id)
    );
    """)

    cur.execute("""
    CREATE TABLE tasks (
        id INTEGER PRIMARY KEY,
        project_id INTEGER,
        employee_id INTEGER,
        description TEXT,
        status TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    );
    """)

    cur.execute("""
    CREATE TABLE clients (
        id INTEGER PRIMARY KEY,
        name TEXT,
        industry TEXT,
        contact_email TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE meetings (
        id INTEGER PRIMARY KEY,
        project_id INTEGER,
        client_id INTEGER,
        meeting_date TEXT,
        location TEXT,
        FOREIGN KEY(project_id) REFERENCES projects(id),
        FOREIGN KEY(client_id) REFERENCES clients(id)
    );
    """)

    cur.execute("""
    CREATE TABLE salaries (
        employee_id INTEGER PRIMARY KEY,
        base_salary REAL,
        bonus REAL,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    );
    """)

    cur.execute("""
    CREATE TABLE benefits (
        employee_id INTEGER PRIMARY KEY,
        health_insurance TEXT,
        retirement_plan TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    );
    """)

    cur.execute("""
    CREATE TABLE locations (
        id INTEGER PRIMARY KEY,
        city TEXT,
        country TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE assets (
        id INTEGER PRIMARY KEY,
        asset_name TEXT,
        asset_type TEXT,
        assigned_to_employee INTEGER,
        FOREIGN KEY(assigned_to_employee) REFERENCES employees(id)
    );
    """)

    cur.execute("""
    CREATE TABLE trainings (
        id INTEGER PRIMARY KEY,
        employee_id INTEGER,
        training_name TEXT,
        completion_date TEXT,
        FOREIGN KEY(employee_id) REFERENCES employees(id)
    );
    """)

    # ------------------------
    # Insert sample data
    # ------------------------

    # Locations
    cities = ["Berlin","Munich","Frankfurt","Hamburg","Stuttgart","Dusseldorf","Cologne","Leipzig"]
    for city in cities:
        cur.execute("INSERT INTO locations(city,country) VALUES (?,?)", (city, "Germany"))

    # Departments
    dept_names = ["Engineering","HR","Sales","Marketing","Operations","Finance","Support","R&D"]
    for name, city in zip(dept_names, cities):
        cur.execute("INSERT INTO departments(name,location) VALUES (?,?)", (name, city))

    dept_ids = [row[0] for row in cur.execute("SELECT id FROM departments").fetchall()]

    # Employees
    for i in range(1, n_rows + 1):
        first_name = random_name(6)
        last_name = random_name(8)
        age = random.randint(20, 65)
        dept_id = random.choice(dept_ids)
        hire_date = random_date(2000,2023)
        cur.execute("""
        INSERT INTO employees(id,first_name,last_name,age,department_id,hire_date)
        VALUES (?,?,?,?,?,?)""", (i, first_name, last_name, age, dept_id, hire_date))

        # Salaries and benefits
        base_salary = round(random.uniform(30000,120000),2)
        bonus = round(random.uniform(0,20000),2)
        health = random.choice(["Standard","Premium","Basic"])
        retirement = random.choice(["Plan A","Plan B","Plan C"])
        cur.execute("INSERT INTO salaries(employee_id,base_salary,bonus) VALUES (?,?,?)",(i,base_salary,bonus))
        cur.execute("INSERT INTO benefits(employee_id,health_insurance,retirement_plan) VALUES (?,?,?)",(i,health,retirement))

    emp_ids = [row[0] for row in cur.execute("SELECT id FROM employees").fetchall()]

    # Projects
    for i in range(1, 21):
        name = f"Project_{i}"
        dept_id = random.choice(dept_ids)
        start_date = random_date(2018,2022)
        end_date = random_date(2023,2025)
        cur.execute("INSERT INTO projects(id,name,department_id,start_date,end_date) VALUES (?,?,?,?,?)",(i,name,dept_id,start_date,end_date))

    proj_ids = [row[0] for row in cur.execute("SELECT id FROM projects").fetchall()]

    # Tasks
    statuses = ["Todo","In Progress","Done"]
    for i in range(1, 101):
        project_id = random.choice(proj_ids)
        employee_id = random.choice(emp_ids)
        description = f"Task {i} for project {project_id}"
        status = random.choice(statuses)
        cur.execute("INSERT INTO tasks(id,project_id,employee_id,description,status) VALUES (?,?,?,?,?)",(i,project_id,employee_id,description,status))

    # Clients
    industries = ["Tech","Finance","Retail","Healthcare","Education"]
    for i in range(1, 21):
        name = f"Client_{i}"
        industry = random.choice(industries)
        email = f"{name.lower()}@example.com"
        cur.execute("INSERT INTO clients(id,name,industry,contact_email) VALUES (?,?,?,?)",(i,name,industry,email))

    client_ids = [row[0] for row in cur.execute("SELECT id FROM clients").fetchall()]

    # Meetings
    for i in range(1, 51):
        project_id = random.choice(proj_ids)
        client_id = random.choice(client_ids)
        date = random_date(2020,2025)
        location = random.choice(cities)
        cur.execute("INSERT INTO meetings(id,project_id,client_id,meeting_date,location) VALUES (?,?,?,?,?)",(i,project_id,client_id,date,location))

    # Assets
    asset_types = ["Laptop","Monitor","Phone","Desk","Chair"]
    for i in range(1, 101):
        asset_name = f"Asset_{i}"
        asset_type = random.choice(asset_types)
        assigned = random.choice(emp_ids)
        cur.execute("INSERT INTO assets(id,asset_name,asset_type,assigned_to_employee) VALUES (?,?,?,?)",(i,asset_name,asset_type,assigned))

    # Trainings
    training_names = ["Python","Excel","SQL","Leadership","Communication"]
    for i in range(1, 51):
        emp_id = random.choice(emp_ids)
        training_name = random.choice(training_names)
        completion = random_date(2019,2025)
        cur.execute("INSERT INTO trainings(id,employee_id,training_name,completion_date) VALUES (?,?,?,?)",(i,emp_id,training_name,completion))

    conn.commit()
    conn.close()
    print(f"Database '{db_path}' created successfully with multiple tables!")

if __name__ == "__main__":
    create_company_db()
