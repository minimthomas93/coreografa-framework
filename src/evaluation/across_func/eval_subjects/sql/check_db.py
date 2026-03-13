import sqlite3

def check_db(db_path="company.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # List all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print(f"Tables ({len(tables)}): {[t[0] for t in tables]}")

    # Show row counts for each table
    for table in tables:
        table_name = table[0]
        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cur.fetchone()[0]
        print(f"Table {table_name}: {count} rows")

    # Show first 5 rows of employees
    cur.execute("SELECT * FROM employees LIMIT 5;")
    print("\nSample employees:")
    for row in cur.fetchall():
        print(row)

    # Sample from projects
    cur.execute("SELECT * FROM projects LIMIT 5;")
    print("\nSample projects:")
    for row in cur.fetchall():
        print(row)

    conn.close()

if __name__ == "__main__":
    check_db()
