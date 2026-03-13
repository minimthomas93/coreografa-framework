import tracemalloc
import time
from fandango.language.symbols import NonTerminal
from fandango.language.tree import DerivationTree
from across_func.eval_subjects.sort import user_systems
import inspect

<start> ::= <simple_value><more_value>{21,30}
<simple_value> ::= <number>
<more_value> ::= "," <number> 
<number> ::= "-"? <digits>
<digits> ::= <digit>{1,5}
<digit> ::= "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"

def get_user_system_funcs():
    user_funcs = inspect.getmembers(user_systems, inspect.isfunction)
    user_system_funcs = []
    for func_tuple in user_funcs:
        func_name = func_tuple[0]
        func_obj = func_tuple[1]
        if func_obj.__module__ == "user_systems":
            user_system_funcs.append(func_name)
    return user_system_funcs

def convert_to_list(tree):
    sequence_as_str = str(tree)
    sequence_as_list = []
    for x in sequence_as_str.split(","):
        try:
            sequence_as_list.append(int(x.strip()))
        except ValueError:
            continue
    return sequence_as_list

def constraints(tree):
    time_and_memory = {}
    results = []
    user_system_funcs = get_user_system_funcs()
    for func_name in user_system_funcs:
        time_and_memory[func_name] = elapsed(tree,func_name)
        results.append(time_and_memory[func_name]['runtime_ns'] >= 0 and time_and_memory[func_name]['memory_peak'] >= 0 )
    return all(results)

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = [x for x in arr[1:] if x < pivot]
        right = [x for x in arr[1:] if x >= pivot]
        return quicksort(left) + [pivot] + quicksort(right)

def elapsed(tree,func_name):
    sort_pattern = str(tree)
    func = getattr(user_systems, func_name, None)
    if callable(func):
        tracemalloc.start()                 # starts tracing memory
        start_time = time.perf_counter_ns()
        try:
            func(sort_pattern)
        except Exception as e:
            print("[ERROR] sorting failed:", e)
        end_time = time.perf_counter_ns()
        elapsed_time = end_time - start_time
        memory_consumed = tracemalloc.get_traced_memory()        # access memory
        tracemalloc.stop()                  # stops tracing memory
        return {"runtime_ns": elapsed_time, "memory_peak": memory_consumed[1]}

#where len(convert_to_list(<start>)) >= 5
where constraints(<start>)
