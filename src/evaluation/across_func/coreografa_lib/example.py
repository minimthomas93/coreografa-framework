import time

from .logger import get_logger
logger = get_logger(__name__)
import os
import glob
import csv
import sys
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from .fuzzer import Coreografa
from .analyzer import Analyzer
from .fuzzer_library import FanRepresentation
from fandango.language.symbols import NonTerminal
import inspect
import re
import xml.etree.ElementTree as ET
from fandango.language.tree import DerivationTree
import across_func.eval_subjects.xml.hypothetical_xml_consumer_v02.xmltojson as XML01
import across_func.eval_subjects.xml.hypothetical_xml_consumer_v04.xml2json as XML02
from xmljson import badgerfish as bf
from xml.etree.ElementTree import fromstring, ParseError
from defusedxml.cElementTree import fromstring, ParseError
from eval_subjects.xml.hypothetical_xml_consumer_v04.xml2json import xml_element_to_dict
import re
import regex
import importlib.util
from importlib import import_module
import sqlite3
import apsw
from itertools import combinations

# Get the directory containing `coreografa_lib`
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EVAL_SUBJECTS = os.path.join(BASE_DIR, "eval_subjects")
EVAL_RESULTS = os.path.join(BASE_DIR, "eval_results")

def sql_sqlite(tree: DerivationTree) -> bool:
    sql_query = str(tree)
    try:
        conn = sqlite3.connect("test.db")  # pre-created db
        cur = conn.cursor()
        cur.execute(sql_query)  
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

def sql_apsw(tree: DerivationTree) -> bool:
    sql_query = str(tree)
    try:
        conn = apsw.Connection("test.db")
        cur = conn.cursor()
        cur.execute(sql_query)
        conn.close()
        return True
    except Exception as e:
        return False

def re_match(tree):
    text = "ab"
    try:
        pattern = str(tree)
        return bool(re.match(pattern, text))
    except re.error:
        return False

def regex_match(tree):
    try:
        text = "ab"
        pattern = str(tree)
        return bool(regex.match(pattern, text))
    except regex.error:
        return False

def xml_v02(tree: DerivationTree):
    try:
        xml_str = str(tree)
        bf.data(fromstring(xml_str))  
        return True
    except ParseError:
        return False

def xml_v04(tree: DerivationTree):
    try:
        xml_str = str(tree)
        root = fromstring(xml_str)
        xml_element_to_dict(root)
        return True
    except ParseError:
        return False

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        left = [x for x in arr[1:] if x < pivot]
        right = [x for x in arr[1:] if x >= pivot]
        return quicksort(left) + [pivot] + quicksort(right)
    
def insertionSort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

def bubble_sort(arr):
    for n in range(len(arr) - 1, 0, -1):
        swapped = False  
        for i in range(n):
            if arr[i] > arr[i + 1]:
                arr[i], arr[i + 1] = arr[i + 1], arr[i] 
                swapped = True
        if not swapped:
            break

def redos_match(tree):
    try:
        text = str(tree)
        return bool(re.match(r"^(a|aa)+$", text))
    except re.error:
        return False

def not_redos_match(tree):
    try:
        text = str(tree)
        return bool(re.match(r"^a+$", text))
    except re.error:
        return False


def load_weasy(version):
    """
    Load a specific WeasyPrint version from a local folder.
    Import happens only once.
    """
    if version == 65:
        version_path = os.path.abspath("weasy_v65")
    elif version == 66:
        version_path = os.path.abspath("weasy_v66")
    elif version == 63.1:
        version_path = os.path.abspath("weasy_v63_1")
    elif version == 64:
        version_path = os.path.abspath("weasy_v64")
    else:
        raise ValueError("Unsupported version")

    if version_path not in sys.path:
        sys.path.insert(0, version_path)

    return import_module("weasyprint")

# Import once at module load
weasy63 = load_weasy(63.1)
weasy64 = load_weasy(64)

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
IMAGES_DIR = os.path.join(BASE, "eval_subjects", "weasyprint")

def weasyprint_63_1(output):
    """
    Render HTML using WeasyPrint v63.1.
    No PDF file is generated (fast).
    """
    html = weasy63.HTML(string=str(output), base_url=IMAGES_DIR)
    html.render()   # Layout engine only, no PDF write

def weasyprint_64(output):
    """
    Render HTML using WeasyPrint v63.1.
    No PDF file is generated (fast).
    """
    html = weasy64.HTML(string=str(output), base_url=IMAGES_DIR)
    html.render()   # Layout engine only, no PDF write

def extract_nonterminals(original_fan_filepath):
    nonterminal_pattern = re.compile(r'<[^<> ]+>')
    non_terminals = set()
    try:
        with open(original_fan_filepath, "r", encoding= "utf-8") as file:
            for line in file:
                matches = nonterminal_pattern.findall(line)
                non_terminals.update(matches)
    except FileNotFoundError:
        print(f"File not found: {original_fan_filepath}")
    except Exception as e:
        print(f"[ERROR] Unexpected error while reading {original_fan_filepath}: {e}")
    return sorted(non_terminals)

def delete_files_afteruse(mydir):
    for f in os.listdir(mydir):
        try:
            os.remove(os.path.join(mydir, f)) #joins the directory path with the filename to form the full file path and removes the file at the path.
        except Exception as e:
            print(f"Error deleting {f}:{e}")

#Coreografa auto-generated properties
def generate_default_property(nonterminal: str) -> str:
    name = nonterminal.strip("<>")
    return f'''
def count_{name}(tree):
    from fandango.language.symbols import NonTerminal
    from fandango.language.tree import DerivationTree
    target = NonTerminal("{nonterminal}")

    def _count(t):
        count = 1 if t.symbol == target else 0
        for c in t.children:
            count += _count(c)
        return count

    return _count(tree)
'''

def add_default_property(user_def_path: str, nonterminal: str):
    fn_name = f"count_{nonterminal.strip('<>')}"

    if os.path.exists(user_def_path):
        with open(user_def_path, "r") as f:
            content = f.read()
            if f"def {fn_name}" in content:
                return  # already exists

    with open(user_def_path, "a") as f:
        f.write(generate_default_property(nonterminal))

    if not os.path.exists(user_def_path):
        with open(user_def_path, "w") as f:
            f.write(generate_default_property(nonterminal))

def workflow(functions: list,config:dict):
    logger.info(f"Running workflow with functions: {functions}")

    original_fan_filepath = config["fan_file"]
    summary_file = config["summary_file"]
    main_summary = config["main_summary_dir"]
    split_summary_dir = config["split_summary_dir"]
    request_directory = config["request_dir"]
    individual_summary_dir = config["individual_summary_dir"]
    input_directory = config["input_dir"]
    new_grammar_dir = config["new_grammar_dir"]
    star_grammar_dir = config["star_grammar_dir"]
    figure_dir = config["figure_dir"]
    user_def_path = config["user_def_functions"]
    headernames = config["summary_headers"]
    converter_func = config["converter"]
    count_nonterminals = config["non-terminal"]

    for d in [main_summary,request_directory,individual_summary_dir,input_directory,new_grammar_dir,figure_dir,split_summary_dir,star_grammar_dir]:
        os.makedirs(d,exist_ok=True)
        delete_files_afteruse(d)

    #checking default properties in config and adding them to user defined functions if not already present
    if "non-terminal" in config:
        nts = config["non-terminal"]
        if isinstance(nts, str):
            nts = [nts]
        for nt in nts:
            add_default_property(user_def_path,nt)
    
    #user_defined_funcs = inspect.getmembers(user_def_functions, inspect.isfunction)
    spec = importlib.util.spec_from_file_location("user_def_functions", user_def_path)
    user_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(user_module)
    user_defined_funcs = inspect.getmembers(user_module, inspect.isfunction)
    custom_properties = [name for name, _ in user_defined_funcs]
    logger.info(f"Custom properties: {custom_properties}")
    
    non_terminals = extract_nonterminals(original_fan_filepath)
    logger.info(f"Non-terminals in grammar: {non_terminals}")
    
    coreografa = Coreografa(functions,custom_properties=custom_properties,non_terminals=non_terminals,converter_func=converter_func)
    coreo_analyzer = Analyzer()
    print("fanfile:", original_fan_filepath)
    coreografa.read_fan_file(original_fan_filepath)
    star_exist = coreografa.check_star_in_grammar(original_fan_filepath)
    if star_exist:
        fan_files = coreografa.generate_star_grammars(original_fan_filepath,new_grammar_dir)
    else:
        fan_files =[original_fan_filepath]

    all_summaries = []
    
    for index, f in enumerate(fan_files):
        logger.info(f"Running Coreografa for grammar: {f}")
        request_id = f"initial_{index}"  # unique per fan file
        coreografa.fuzz(f,non_terminals=non_terminals,request_id=request_id,input_directory=input_directory,user_def_path=user_def_path)
        name = os.path.splitext(os.path.basename(original_fan_filepath))[0]
        individual_summary = os.path.join(individual_summary_dir, f"firstsummary_{name}_{index}.csv")
        coreografa.write_summary(individual_summary,headernames)
        all_summaries.append(individual_summary)
    coreografa.write_final_summary(all_summaries,summary_file,headernames)
    logger.info("Initial summary completed. Starting request generation and second round of fuzzing.")

    for i in range(5):
        logger.info(f"Iteration {i}")
        # Split summary into per-function files BEFORE request generation
        coreografa.split_summary_by_function(summary_file,split_summary_dir)
        split_files = glob.glob(os.path.join(split_summary_dir, "*_summary.csv"))
        if not split_files:
            raise RuntimeError("No split summaries created! Ensure main summary is not empty.")
    
        summary_files = []
        delete_files_afteruse(request_directory)
        for split_file in split_files:
            logger.info(f"Analyzing summary for {split_file}")
            coreo_analyzer.read_csvs([split_file], metrics = ["runtime_ns", "memory_peak"],input_features=headernames, ignore = ["memory_after"],input_dir =input_directory)
            delete_files_afteruse(request_directory)
            logger.info(f"Generating Frequency based requests for {split_file}")
            #for name in coreo_analyzer.metrics:
                #coreo_analyzer.generate_frequency_based_requests(split_file, metric=name,prop=prop_value, write_json = True,request_directory=request_directory,request_type= "frequency request")

            for name in coreo_analyzer.metrics:
                for prop_value in coreo_analyzer.features:
                    coreo_analyzer.generate_frequency_based_requests(split_file, metric=name,prop=prop_value, write_json = True,request_directory=request_directory,request_type= "frequency request")
                    #coreo_analyzer.generate_edge_request(name =split_file,metric=name,prop=prop_value,write_json=True,request_directory=request_directory, request_type= "edge request")
                    logger.info(f"Generating edge requests for metric: {name} and feature: {prop_value}")
                    coreo_analyzer.generate_lower_edge_request(name=split_file,metric=name,prop=prop_value,write_json=True,request_directory=request_directory, request_type= "lower edge request")
                    coreo_analyzer.generate_upper_edge_request(name=split_file,metric=name,prop=prop_value,write_json=True,request_directory=request_directory, request_type= "upper edge request")
                    logger.info(f"Generating uniform negation requests for metric: {name} and feature: {prop_value}")
                    coreo_analyzer.generate_uniform_negation_requests(name=split_file,metric=name,prop =prop_value,write_json=True,request_directory=request_directory, request_type= "negation request")
            
            list_of_files = glob.glob(os.path.join(request_directory, "request_*.json"))
            if not list_of_files:
                raise FileNotFoundError(f"No request_*.json files found")
            logger.info(f"Total requests generated: {len(list_of_files)}")

            for index, json_file in enumerate(list_of_files):
                print("json file:", json_file)
                #grammar_id = os.path.basename(split_file).split("xml_")[1].split("_summary")[0]
                file_base = os.path.basename(split_file).replace(".csv", "")
                grammar_id = file_base.split("_summary")[0]
                #new_grammar_file = os.path.join(new_grammar_dir, f"xml_new_{grammar_id}_{index}.fan")
                new_grammar_file = os.path.join(new_grammar_dir, f"{grammar_id}_new_{index}.fan")
                logger.info(f"Generated new grammar file: {new_grammar_file} from request: {json_file}")
                logger.info(f"Processing request {json_file} for grammar {grammar_id}")
                generated_grammars = coreografa.read_request(json_file,new_grammar_file,custom_properties=custom_properties,user_def_path=user_def_path)
        
                fan = FanRepresentation(json_file,functions)
                fan.retrieve_json(json_file)
                request_id = json_file.split("request_")[1].split(".json")[0]
                for grammar in generated_grammars:
                    coreografa.fuzz(grammar,initial_population=fan.cleaned_inputs,request_id=request_id,non_terminals=None,input_directory=input_directory,user_def_path=user_def_path)
  
                individual_summary_f = os.path.join(individual_summary_dir, f"summary_{grammar_id}_{index}.csv")
                coreografa.write_summary(individual_summary_f,headernames)
                summary_files.append(individual_summary_f)
                logger.info(f"Completed fuzzing for request {json_file}. Summary written to {individual_summary_f}")
        
        coreografa.write_final_summary(summary_files,summary_file,headernames)
        logger.info(f"Final summary for iteration {i} written to {summary_file}")

    #new code for plotting for different functions
    coreografa.split_summary_by_function(summary_file,split_summary_dir)
    final_split_files = glob.glob(os.path.join(split_summary_dir, "*_summary.csv"))
    coreo_analyzer.read_csvs(final_split_files, metrics = ["runtime_ns", "memory_peak"],input_features=headernames, ignore = ["memory_after"],input_dir =input_directory)
    for metric in coreo_analyzer.metrics:
        for propx, propy in combinations(coreo_analyzer.features, 2):
            logger.info(f"Plotting interaction between features: {propx} and {propy} for metric: {metric} and summary: {split_file}")
            coreo_analyzer.plot_3d_interactive(metric, propx, propy, output_dir=figure_dir)

    for split_file in final_split_files:
        coreo_analyzer.read_csvs([split_file], metrics = ["runtime_ns", "memory_peak"],input_features=headernames, ignore = ["memory_after"],input_dir =input_directory)
        for metric in coreo_analyzer.metrics:
            for prop_value in coreo_analyzer.features:
                logger.info(f"Plotting metric: {metric} vs feature: {prop_value} for summary: {split_file}")
                coreo_analyzer.plot_metric_vs_feature(metric, prop_value, remove_outliers = False,output_dir=figure_dir)
                coreo_analyzer.fit_model_for_metric_and_feature(metric, prop_value, remove_outliers = False,output_dir=figure_dir)
            coreo_analyzer.fit_model_for_metric_and_features(metric,features=coreo_analyzer.features,interaction = False, remove_outliers = False,output_dir=figure_dir)

if __name__ == "__main__":   
    #if fan output is a strings or characters
    def convert_string(tree):
        input_str = str(tree)
        return input_str,tree  
    
    #if fan output is a list of numbers
    def convert_numbers(tree):
        input_str = str(tree).strip()
        clean_inp = []
        for x in input_str.split(","):
            try:
                clean_inp.append(str(int(x)))
            except (ValueError, TypeError):
                print(f"Skipping invalid value [{x}]")
                print(f"Input string was: {input_str}")
        if clean_inp:
            return ",".join(clean_inp), [int(x) for x in clean_inp]
        else:
            return "", []
    
    configs = {
    "xml": {
        "fan_file": os.path.join(EVAL_SUBJECTS, "xml", "xml.fan"),
        "main_summary_dir": os.path.join(EVAL_RESULTS, "main_summary", "xml"),
        "summary_file": os.path.join(EVAL_RESULTS, "main_summary", "xml", "main_summary.csv"),
        "split_summary_dir": os.path.join(EVAL_RESULTS, "split_summary", "xml"),
        "request_dir": os.path.join(EVAL_RESULTS, "requests", "xml"),
        "individual_summary_dir": os.path.join(EVAL_RESULTS, "individual_summary", "xml"),
        "input_dir": os.path.join(EVAL_RESULTS, "inputs", "xml"),
        "new_grammar_dir": os.path.join(EVAL_RESULTS, "new_grammar_files", "xml"),
        "star_grammar_dir": os.path.join(EVAL_RESULTS, "star_grammar_files", "xml"),
        "figure_dir": os.path.join(EVAL_RESULTS, "plots", "xml"),
        "user_def_functions": os.path.join(EVAL_SUBJECTS, "xml", "user_def_functions.py"),
        "user_systems_file": os.path.join(EVAL_SUBJECTS, "xml", "user_systems.py"),
        "summary_headers": ["avg_attributes", "depth","count_xml_attribute", "count_text"],
        "converter":convert_string,
        "non-terminal": ["<xml_attribute>","<text>"]
    },
    "regex": {
        "fan_file": os.path.join(EVAL_SUBJECTS, "regex", "regex.fan"),
        "main_summary_dir": os.path.join(EVAL_RESULTS, "main_summary", "regex"),
        "summary_file": os.path.join(EVAL_RESULTS, "main_summary", "regex", "main_summary.csv"),
        "split_summary_dir": os.path.join(EVAL_RESULTS, "split_summary", "regex"),
        "request_dir": os.path.join(EVAL_RESULTS, "requests", "regex"),
        "individual_summary_dir": os.path.join(EVAL_RESULTS, "individual_summary", "regex"),
        "input_dir": os.path.join(EVAL_RESULTS, "inputs", "regex"),
        "new_grammar_dir": os.path.join(EVAL_RESULTS, "new_grammar_files", "regex"),
        "star_grammar_dir": os.path.join(EVAL_RESULTS, "star_grammar_files", "regex"),
        "figure_dir": os.path.join(EVAL_RESULTS, "plots", "regex"),
        "user_def_functions": os.path.join(EVAL_SUBJECTS, "regex", "user_def_functions.py"),
        "user_systems_file": os.path.join(EVAL_SUBJECTS, "regex", "user_systems.py"),
        "summary_headers" : ["count_pattern_tokens", "count_term"],
        "converter":convert_string,
        "non-terminal": ["<term>"]
    },
    "sort": {
        "fan_file": os.path.join(EVAL_SUBJECTS, "sort", "sorting.fan"),
        "main_summary_dir": os.path.join(EVAL_RESULTS, "main_summary", "sort"),
        "summary_file": os.path.join(EVAL_RESULTS, "main_summary", "sort", "main_summary.csv"),
        "split_summary_dir": os.path.join(EVAL_RESULTS, "split_summary", "sort"),
        "request_dir": os.path.join(EVAL_RESULTS, "requests", "sort"),
        "individual_summary_dir": os.path.join(EVAL_RESULTS, "individual_summary", "sort"),
        "input_dir": os.path.join(EVAL_RESULTS, "inputs", "sort"),
        "new_grammar_dir": os.path.join(EVAL_RESULTS, "new_grammar_files", "sort"),
        "star_grammar_dir": os.path.join(EVAL_RESULTS, "star_grammar_files", "sort"),
        "figure_dir": os.path.join(EVAL_RESULTS, "plots", "sort"),
        "user_def_functions": os.path.join(EVAL_SUBJECTS, "sort", "user_def_functions.py"),
        "user_systems_file": os.path.join(EVAL_SUBJECTS, "sort", "user_systems.py"),
        "summary_headers" : ["sortedness","length"],
        "converter":convert_numbers,
        "non-terminal": []
    },
    "weasyprint": {
        "fan_file": os.path.join(EVAL_SUBJECTS, "weasyprint", "weasyprint.fan"),
        "main_summary_dir": os.path.join(EVAL_RESULTS, "main_summary", "weasyprint"),
        "summary_file": os.path.join(EVAL_RESULTS, "main_summary", "weasyprint", "main_summary.csv"),
        "split_summary_dir": os.path.join(EVAL_RESULTS, "split_summary", "weasyprint"),
        "request_dir": os.path.join(EVAL_RESULTS, "requests", "weasyprint"),
        "individual_summary_dir": os.path.join(EVAL_RESULTS, "individual_summary", "weasyprint"),
        "input_dir": os.path.join(EVAL_RESULTS, "inputs", "weasyprint"),
        "new_grammar_dir": os.path.join(EVAL_RESULTS, "new_grammar_files", "weasyprint"),
        "star_grammar_dir": os.path.join(EVAL_RESULTS, "star_grammar_files", "weasyprint"),
        "figure_dir": os.path.join(EVAL_RESULTS, "plots", "weasyprint"),
        "user_def_functions": os.path.join(EVAL_SUBJECTS, "weasyprint", "user_def_functions.py"),
        "user_systems_file": os.path.join(EVAL_SUBJECTS, "weasyprint", "user_systems.py"),
        "pdf_folder": os.path.join(EVAL_RESULTS, "pdf", "weasyprint"),
        "summary_headers" : ["count_para_text","count_img_tag"],
        "converter":convert_string,
        "non-terminal": ["<para_text>", "<img_tag>"]
    },
    "sql": {
        "fan_file": os.path.join(EVAL_SUBJECTS, "sql", "sql.fan"),
        "main_summary_dir": os.path.join(EVAL_RESULTS, "main_summary", "sql"),
        "summary_file": os.path.join(EVAL_RESULTS, "main_summary", "sql", "main_summary.csv"),
        "split_summary_dir": os.path.join(EVAL_RESULTS, "split_summary", "sql"),
        "request_dir": os.path.join(EVAL_RESULTS, "requests", "sql"),
        "individual_summary_dir": os.path.join(EVAL_RESULTS, "individual_summary", "sql"),
        "input_dir": os.path.join(EVAL_RESULTS, "inputs", "sql"),
        "new_grammar_dir": os.path.join(EVAL_RESULTS, "new_grammar_files", "sql"),
        "star_grammar_dir": os.path.join(EVAL_RESULTS, "star_grammar_files", "sql"),
        "figure_dir": os.path.join(EVAL_RESULTS, "plots", "sql"),
        "user_def_functions": os.path.join(EVAL_SUBJECTS, "sql", "user_def_functions.py"),
        "user_systems_file": os.path.join(EVAL_SUBJECTS, "sql", "user_systems.py"),
        "summary_headers" : ["count_tables","count_column_name"],
        "converter":convert_string,
        "non-terminal": ["<column_name>"]
    },
    "regex_redos": {
        "fan_file": os.path.join(EVAL_SUBJECTS, "regex_redos", "regexredos.fan"),
        "main_summary_dir": os.path.join(EVAL_RESULTS, "main_summary", "regex_redos"),
        "summary_file": os.path.join(EVAL_RESULTS, "main_summary", "regex_redos", "main_summary.csv"),
        "split_summary_dir": os.path.join(EVAL_RESULTS, "split_summary", "regex_redos"),
        "request_dir": os.path.join(EVAL_RESULTS, "requests", "regex_redos"),
        "individual_summary_dir": os.path.join(EVAL_RESULTS, "individual_summary", "regex_redos"),
        "input_dir": os.path.join(EVAL_RESULTS, "inputs", "regex_redos"),
        "new_grammar_dir": os.path.join(EVAL_RESULTS, "new_grammar_files", "regex_redos"),
        "star_grammar_dir": os.path.join(EVAL_RESULTS, "star_grammar_files", "regex_redos"),
        "figure_dir": os.path.join(EVAL_RESULTS, "plots", "regex_redos"),
        "user_def_functions": os.path.join(EVAL_SUBJECTS, "regex_redos", "user_def_functions.py"),
        "user_systems_file": os.path.join(EVAL_SUBJECTS, "regex_redos", "user_systems.py"),
        "summary_headers" : ["count_a"],
        "converter":convert_string,
        "non-terminal": []
    },
    }

    start = time.time()
    workflow([xml_v02,xml_v04],configs["xml"])
    end = time.time()
    logger.info(f"XML workflow time: {(end - start)/60:.2f} minutes")
    # start = time.time()
    # workflow([regex_match,re_match],configs["regex"])
    # end = time.time()
    # logger.info(f"Regex workflow time: {(end - start)/60:.2f} minutes")
    # #workflow([redos_match,not_redos_match],configs["regex_redos"])
    # start = time.time()
    # workflow([sql_apsw,sql_sqlite],configs["sql"])
    # end = time.time()
    # logger.info(f"SQL workflow time: {(end - start)/60:.2f} minutes")
    # start = time.time()
    # workflow([quicksort,bubble_sort,insertionSort],configs["sort"])
    # end = time.time()
    # logger.info(f"Sorting workflow time: {(end - start)/60:.2f} minutes")
    # start = time.time()
    # workflow([weasyprint_64,weasyprint_63_1],configs["weasyprint"])
    # end = time.time()
    # logger.info(f"WeasyPrint workflow time: {(end - start)/60:.2f} minutes")
    