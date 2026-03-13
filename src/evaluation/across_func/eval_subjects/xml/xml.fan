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
<xml_tree> ::= <xml_open_tag><inner_xml_tree><xml_close_tag>
<inner_xml_tree> ::= <xml_tree> | <text>
<xml_open_tag> ::= "<" <id> " " <xml_attribute> ">" | "<" <id> ">"
<xml_close_tag> ::= "</" <id> ">"
#<xml_attributes> ::= <xml_attribute> | <xml_attribute> " " <xml_attributes>
<xml_attribute> ::= <id> '=\"' <text> '\"' ' '
<id> ::= <id_start_char> <id_chars> | <id_start_char>
<id_start_char> ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" | "_"
<id_chars> ::= <id_char> <id_chars> | <id_char>
<id_char> ::= <id_start_char> | "-" | "." | "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"
<text> ::= <text_char> <text> | <text_char>
<text_char> ::= "a" | "b" | "c" | "d" | "e" | "f" | "g" | "h" | "i" | "j" | "k" | "l" | "m" | "n" | "o" | "p" | "q" | "r" | "s" | "t" | "u" | "v" | "w" | "x" | "y" | "z" | "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "I" | "J" | "K" | "L" | "M" | "N" | "O" | "P" | "Q" | "R" | "S" | "T" | "U" | "V" | "W" | "X" | "Y" | "Z" | "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "&quot;" | "&#x27;" | "." | " " | "\t" | "/" | "?" | "-" | "," | "=" | ":" | "+"
forall <tree> in <xml_tree>:
    <tree>.<xml_open_tag>.<id> == <tree>.<xml_close_tag>.<id>
;
forall <open_tag> in <xml_tree>.<xml_open_tag>:
    forall <xml_attribute_1> in <open_tag>..<xml_attribute>:
        forall <xml_attribute_2> in <open_tag>..<xml_attribute>:
            (not(<xml_attribute_1> != <xml_attribute_2>) or (str(<xml_attribute_1>.<id>) != str(<xml_attribute_2>.<id>)))
;

def get_user_system_funcs():
    user_funcs = inspect.getmembers(user_systems, inspect.isfunction)
    user_system_funcs = []
    for func_tuple in user_funcs:
        func_name = func_tuple[0]
        func_obj = func_tuple[1]
        if func_obj.__module__ == "user_systems":
            user_system_funcs.append(func_name)
    return user_system_funcs

def xml_v02(tree):
    try:
        xml_str = str(tree)
        root = safe_fromstring(xml_str)
        return bf.data(root)   # JSON dict
    except ParseError:
        return None  # failed

def xml_v04(tree):
    try:
        xml_str = str(tree)
        root = safe_fromstring(xml_str)
        return xml_element_to_dict(root)  # JSON dict
    except ParseError:
        return None

def constraints(tree):
    time_and_memory = {}
    results = []
    user_system_funcs = get_user_system_funcs()
    for func_name in user_system_funcs:
        time_and_memory[func_name] = elapsed(tree,func_name)
        results.append(time_and_memory[func_name]['runtime_ns'] >= 0 and time_and_memory[func_name]['memory_peak'] >= 0 )
    return all(results)

def elapsed(tree,func_name):
    xml_string = str(tree)
    func = getattr(user_systems, func_name, None)
    if callable(func):
        tracemalloc.start()                 # starts tracing memory
        start_time = time.perf_counter_ns()
        try:
            func(xml_string)
        except Exception as e:
            print("[ERROR] XML failed:", e)
        end_time = time.perf_counter_ns()
        elapsed_time = end_time - start_time
        memory_consumed = tracemalloc.get_traced_memory()        # access memory
        tracemalloc.stop()                  # stops tracing memory
        return {"runtime_ns": elapsed_time, "memory_peak": memory_consumed[1]}

where constraints(<start>)