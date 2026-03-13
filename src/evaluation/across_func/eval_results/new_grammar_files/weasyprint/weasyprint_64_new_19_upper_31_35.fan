import tracemalloc
import time
import weasyprint
from fandango.language.symbols import NonTerminal
from fandango.language.tree import DerivationTree
from across_func.eval_subjects.weasyprint import user_systems
import inspect

<start> ::= <html_tag>
<html_tag> ::= <_l_> 'html' <_r_> <head_tag> <body_tag> <_cl_> 'html' <_r_>
<head_tag> ::= <_l_> 'head' <_r_> <title_tag> <_cl_> 'head' <_r_>
<title_tag> ::= <_l_> 'title' <_r_> <title_content> <_cl_> 'title' <_r_>
<title_content> ::= <title_text>
<title_text> ::= ('Title of the pdf' | 'My Awesome Webpage' | 'Welcome to my website')
<body_tag> ::= <_l_> 'body' <_r_> <body_content> <_cl_> 'body' <_r_>
<body_content> ::= <header_tag> <paragraph_tag> <link_tag> <para_text>* <img_tag> {31,35}
<header_tag> ::= <_l_> 'h1' <_r_> <header_content> <_cl_> 'h1' <_r_> ',' <_l_> 'h2' <_r_> <header_content> <_cl_> 'h2' <_r_> ',' <_l_> 'h3' <_r_> <header_content> <_cl_> 'h3' <_r_>
<header_content> ::= <header_text>
<header_text> ::= ('Welcome' | 'About Us' | 'Contact')
<paragraph_tag> ::= <_l_> 'p' <_r_> <paragraph_content> <_cl_> 'p' <_r_>
<paragraph_content> ::= <para_text>
<para_text> ::= ('hello world Lorem Ipsum is simply dummy text of the printing and typesetting industry.' | "goodbye world Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book." | 'This is a paragraph. It is a long established fact that a reader will be distracted by the readable content of a page when looking at its layout. ' | 'Lorem ipsum dolor sit amet.')
<link_tag> ::= <_l_> 'a href=' <_link_url_> <link_content> <_cl_> 'a' <_r_>
<_link_url_> ::= ('https://google.com' | 'https://github.com' | 'https://stackoverflow.com')
<link_content> ::= <link_text>
<link_text> ::= ('Click here' | 'Learn more' | 'Visit our website')
<img_tag> ::= <_l_> 'img src=' <_img_path_> <_r_>
<_img_path_> ::= ('home.jpg' | 'flower.jpg' | 'coffee.jpg' | 'workstation.jpg')
<_l_> ::= '<'
<_r_> ::= '>'
<_cl_> ::= '</'
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
            print('[ERROR] weasyprint failed:', e)
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
        results.append(time_and_memory['weasyprint_64']['memory_peak'] >= 2543101 or time_and_memory['weasyprint_64']['memory_peak'] <= 2683148 or time_and_memory['weasyprint_63_1']['memory_peak'] >= 2543101 or (time_and_memory['weasyprint_63_1']['memory_peak'] <= 2683148))
    return all(results)

def count_para_text(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal('<para_text>')

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count
    return _count(tree)

def count_img_tag(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal('<img_tag>')

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count
    return _count(tree)
where constraints(<start>)
