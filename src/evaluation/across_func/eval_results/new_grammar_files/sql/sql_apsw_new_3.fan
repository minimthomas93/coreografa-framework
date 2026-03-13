import tracemalloc
import time
import weasyprint
from fandango.language.symbols import NonTerminal
from fandango.language.tree import DerivationTree
from across_func.eval_subjects.sql import user_systems
import inspect
import sqlite3
import apsw
import re

<start> ::= <select_stmt>
<select_stmt> ::= 'SELECT ' <select_list> ' FROM ' <table> <opt_where> <opt_order> ';'
<select_list> ::= (' * ' | <column_list>*)
<column_list> ::= (<column_name> | <column_name> ',' <column_list>)
<column_name> ::= (' id ' | ' name ' | ' location ' | ' first_name ' | ' last_name ' | ' age ' | ' department_id ' | ' hire_date ' | ' start_date ' | ' end_date ' | ' project_id ' | ' employee_id ' | ' description ' | ' status ' | ' industry ' | ' contact_email ' | ' meeting_date ' | ' base_salary ' | ' bonus ' | ' health_insurance ' | ' retirement_plan ' | ' city ' | ' country ' | ' asset_name ' | ' asset_type ' | ' assigned_to_employee ' | ' training_name ' | ' completion_date ')
<table> ::= (<single_table> | <single_table> ' JOIN ' <table> ' ON ' <join_condition>)
<single_table> ::= ('departments' | 'employees' | 'projects' | 'tasks' | 'clients' | 'meetings' | 'salaries' | 'benefits' | 'locations' | 'assets' | 'trainings')
<join_condition> ::= ('employees.department_id = departments.id' | 'projects.department_id = departments.id' | 'tasks.project_id = projects.id' | 'tasks.employee_id = employees.id' | 'meetings.project_id = projects.id' | 'meetings.client_id = clients.id' | 'salaries.employee_id = employees.id' | 'benefits.employee_id = employees.id' | 'assets.assigned_to_employee = employees.id' | 'trainings.employee_id = employees.id')
<opt_where> ::= ('' | ' WHERE ' <condition>)
<condition> ::= (<column_name> <operator> <value> | <condition> ' AND ' <condition> | <condition> ' OR ' <condition>)
<operator> ::= ('=' | '>' | '<' | '>=' | '<=' | '!=' | ' LIKE ')
<value> ::= (<int_val> | <float_val> | <string_val>)
<int_val> ::= (' 18 ' | ' 25 ' | ' 30 ' | ' 40 ' | ' 50 ' | ' 60 ' | ' 1 ' | ' 2 ' | ' 3 ' | ' 4 ')
<float_val> ::= (' 30000.0 ' | ' 50000.5 ' | ' 75000.99 ' | ' 120000.0 ')
<string_val> ::= ('Engineering' | 'HR' | 'Sales' | 'Marketing' | 'Operations' | 'Finance' | 'Support' | 'R&D' | 'Berlin' | 'Munich' | 'Frankfurt' | 'Hamburg' | 'Stuttgart' | 'Dusseldorf' | 'Cologne' | 'Leipzig' | 'Todo' | 'In Progress' | 'Done' | 'Tech' | 'Finance' | 'Retail' | 'Healthcare' | 'Education' | 'Python' | 'Excel' | 'SQL' | 'Leadership' | 'Communication')
<opt_order> ::= ('' | ' ORDER BY ' <column_name> <order_dir>)
<order_dir> ::= (' ASC ' | ' DESC ')
def get_user_system_funcs():
    user_funcs = inspect.getmembers(user_systems, inspect.isfunction)
    user_system_funcs = []
    for func_tuple in user_funcs:
        func_name = func_tuple[0]
        func_obj = func_tuple[1]
        if func_obj.__module__ == 'user_systems':
            user_system_funcs.append(func_name)
    return user_system_funcs

def elapsed(tree, func_name):
    sql_pattern = str(tree)
    func = getattr(user_systems, func_name, None)
    if callable(func):
        tracemalloc.start()
        start_time = time.perf_counter_ns()
        try:
            func(sql_pattern)
        except Exception as e:
            print('[ERROR] failed:', e)
        end_time = time.perf_counter_ns()
        elapsed_time = end_time - start_time
        memory_consumed = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {'runtime_ns': elapsed_time, 'memory_peak': memory_consumed[1]}

def constraints(tree):
    time_and_memory = {}
    results = []
    user_system_funcs = get_user_system_funcs()
    for func_name in user_system_funcs:
        time_and_memory[func_name] = elapsed(tree, func_name)
        results.append(time_and_memory['sql_apsw']['runtime_ns'] >= 1023700 or time_and_memory['sql_apsw']['runtime_ns'] <= 16131810 or time_and_memory['sql_sqlite']['runtime_ns'] >= 1023700 or (time_and_memory['sql_sqlite']['runtime_ns'] <= 16131810))
    return all(results)

def count_tables(tree: DerivationTree) -> int:
    sql_str = str(tree).lower()
    tables = re.findall('\\b(?:from|join)\\s+([a-zA-Z_][\\w]*)', sql_str)
    return len(tables)

def count_column_name(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal('<column_name>')

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count
    return _count(tree)
where constraints(<start>)
where count_tables(<start>) >= 1.0
where count_tables(<start>) <= 10.0
