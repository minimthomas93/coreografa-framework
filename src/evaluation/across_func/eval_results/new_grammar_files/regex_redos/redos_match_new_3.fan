import tracemalloc
import time
from fandango.language.symbols import NonTerminal
from fandango.language.tree import DerivationTree
from across_func.eval_subjects.regex_redos import user_systems
import inspect
import re
import regex

<start> ::= <a>* 'b'
<a> ::= 'a'
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
    reg_pattern = str(tree)
    func = getattr(user_systems, func_name, None)
    if callable(func):
        tracemalloc.start()
        start_time = time.perf_counter_ns()
        try:
            func(reg_pattern)
        except Exception as e:
            print('[ERROR] Regex failed:', e)
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
        results.append(time_and_memory['redos_match']['runtime_ns'] >= 609860 or time_and_memory['redos_match']['runtime_ns'] <= 631480 or time_and_memory['not_redos_match']['runtime_ns'] >= 609860 or (time_and_memory['not_redos_match']['runtime_ns'] <= 631480))
    return all(results)

def count_a(s: str) -> int:
    return s.count('a')
where constraints(<start>)
