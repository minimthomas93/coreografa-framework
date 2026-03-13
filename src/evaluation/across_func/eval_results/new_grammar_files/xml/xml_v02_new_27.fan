import tracemalloc
import time
from fandango.language.symbols import NonTerminal
import xml.etree.ElementTree as ET
from fandango.language.tree import DerivationTree
from xmljson import badgerfish as bf
from defusedxml.cElementTree import fromstring as safe_fromstring, ParseError
from across_func.eval_subjects.xml.hypothetical_xml_consumer_v04.xml2json import xml_element_to_dict
from across_func.eval_subjects.xml import user_systems
import inspect

<start> ::= <xml_tree>
<xml_tree> ::= <xml_open_tag> <inner_xml_tree> <xml_close_tag>
<inner_xml_tree> ::= (<xml_tree> | <text>)
<xml_open_tag> ::= ('<' <id> ' ' <xml_attribute> '>' | '<' <id> '>')
<xml_close_tag> ::= '</' <id> '>'
<xml_attribute> ::= <id> '="' <text> '"' ' '
<id> ::= (<id_start_char> <id_chars> | <id_start_char>)
<id_start_char> ::= ('a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i' | 'j' | 'k' | 'l' | 'm' | 'n' | 'o' | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v' | 'w' | 'x' | 'y' | 'z' | 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J' | 'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q' | 'R' | 'S' | 'T' | 'U' | 'V' | 'W' | 'X' | 'Y' | 'Z' | '_')
<id_chars> ::= (<id_char> <id_chars> | <id_char>)
<id_char> ::= (<id_start_char> | '-' | '.' | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9')
<text> ::= (<text_char> <text> | <text_char>)
<text_char> ::= ('a' | 'b' | 'c' | 'd' | 'e' | 'f' | 'g' | 'h' | 'i' | 'j' | 'k' | 'l' | 'm' | 'n' | 'o' | 'p' | 'q' | 'r' | 's' | 't' | 'u' | 'v' | 'w' | 'x' | 'y' | 'z' | 'A' | 'B' | 'C' | 'D' | 'E' | 'F' | 'G' | 'H' | 'I' | 'J' | 'K' | 'L' | 'M' | 'N' | 'O' | 'P' | 'Q' | 'R' | 'S' | 'T' | 'U' | 'V' | 'W' | 'X' | 'Y' | 'Z' | '0' | '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9' | '&quot;' | '&#x27;' | '.' | ' ' | '\t' | '/' | '?' | '-' | ',' | '=' | ':' | '+')
def get_user_system_funcs():
    user_funcs = inspect.getmembers(user_systems, inspect.isfunction)
    user_system_funcs = []
    for func_tuple in user_funcs:
        func_name = func_tuple[0]
        func_obj = func_tuple[1]
        if func_obj.__module__ == 'user_systems':
            user_system_funcs.append(func_name)
    return user_system_funcs

def xml_v02(tree):
    try:
        xml_str = str(tree)
        root = safe_fromstring(xml_str)
        return bf.data(root)
    except ParseError:
        return None

def xml_v04(tree):
    try:
        xml_str = str(tree)
        root = safe_fromstring(xml_str)
        return xml_element_to_dict(root)
    except ParseError:
        return None

def elapsed(tree, func_name):
    xml_string = str(tree)
    func = getattr(user_systems, func_name, None)
    if callable(func):
        tracemalloc.start()
        start_time = time.perf_counter_ns()
        try:
            func(xml_string)
        except Exception as e:
            print('[ERROR] XML failed:', e)
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
        results.append(time_and_memory['xml_v02']['memory_peak'] >= 23704 or time_and_memory['xml_v02']['memory_peak'] <= 24286 or time_and_memory['xml_v04']['memory_peak'] >= 23704 or (time_and_memory['xml_v04']['memory_peak'] <= 24286))
    return all(results)

def count_xml_attribute(tree: DerivationTree) -> int:
    target = NonTerminal('<xml_attribute>')
    count = 0
    if tree.symbol == target:
        count += 1
    for child in tree.children:
        count += count_xml_attribute(child)
    return count

def helper_count_attributes(node: DerivationTree):
    target_open_tag = NonTerminal('<xml_open_tag>')
    total_attrs = 0
    total_tags = 0
    if node.symbol == target_open_tag:
        tag_attrs = sum((count_xml_attribute(child) for child in node.children))
        if tag_attrs > 0:
            total_attrs += tag_attrs
            total_tags += 1
    for child in node.children:
        a, t = helper_count_attributes(child)
        total_attrs += a
        total_tags += t
    return (total_attrs, total_tags)

def avg_attributes(tree: DerivationTree) -> float:
    total_attrs, total_tags = helper_count_attributes(tree)
    if total_tags == 0:
        return 0.0
    return total_attrs / total_tags

def depth(tree: DerivationTree) -> int:
    if not tree.children:
        return 1
    return 1 + max((depth(child) for child in tree.children))

def count_text(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal('<text>')

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count
    return _count(tree)
where constraints(<start>)
where count_text(<start>) >= 5.0
where count_text(<start>) <= 13.0
