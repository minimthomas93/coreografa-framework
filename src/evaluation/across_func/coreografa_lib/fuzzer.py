from .logger import get_logger
logger = get_logger(__name__)
from .fuzzer_library import FanRepresentation 
from fandango.evolution.algorithm import Fandango
#import fandango
from fandango.language.parse.parse import parse
print(parse)
#from fandango.language.grammar import DerivationTree
import tracemalloc
import time
import csv
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from across_func.eval_subjects.xml import user_def_functions
from across_func.eval_subjects.regex_redos import user_def_functions
#import user_def_functions
from fandango.language.symbols import NonTerminal
import re
import importlib.util
import inspect

def evolve_fandango(grammar, constraints):
    fandango = Fandango(grammar, constraints, population_size=20, desired_solutions=20, initial_population=None, best_effort=True)
    return fandango.evolve()

import time
import tracemalloc
import multiprocessing as mp

def _run_fn_with_tracemalloc(fn, inp, q):
    """
    Runs fn(inp) and returns metrics via a multiprocessing Queue.
    Must be top-level for Windows pickling.
    """
    tracemalloc.start()
    start = time.perf_counter_ns()
    try:
        fn(inp)
        ok = True
        err = None
    except Exception as e:
        ok = False
        err = repr(e)
    end = time.perf_counter_ns()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    q.put({
        "ok": ok,
        "error": err,
        "runtime_ns": end - start,
        "memory_after": current,
        "memory_peak": peak
    })

class Coreografa:

    def __init__(self, functions_to_execute, custom_properties,non_terminals,converter_func):
        self.fan_rep = None
        self.fns = functions_to_execute
        self.collected_metrics = []
        self.custom_properties = custom_properties
        self.non_terminals = non_terminals
        self.converter_func = converter_func
    
    def converter_fan_output(self, solution):
        return self.converter_func(solution)

    '''
    def converter_fan_output(self, solution):
        #algorithm = self.fns.__name__
        #if algorithm == "weasyprint_fn" or "xml":
        if any("weasyprint_fn" in fn.__name__ or "xml" in fn.__name__ or "re" in fn.__name__ for fn in self.fns):
            input_str = str(solution)
            return input_str,solution
        else:
            input_str = str(solution).strip()
            clean_inp = []
            for x in input_str.split(","):
                try:
                    clean_inp.append(str(int(x)))
                except (ValueError,TypeError):
                    print(f"skipping invalid value {x}")
            if clean_inp:
                return ",".join(clean_inp),[int(x) for x in clean_inp]
            else:
                return "",[]
    '''

    def read_fan_file(self, path_to_file):
        # read a normal .fan file, convert it to the FanRepresentation, and save/store it
        fan = FanRepresentation(path_to_file,self.fns)
        fan.retrieve_fanfile(path_to_file)
        self.fan_rep = fan
    
    def check_star_in_grammar(self, original_fan_file):
        star_pattern = re.compile(r"<[^>]+>\s*\*")
        try:
            with open(original_fan_file,"r") as f:
                for line in f:
                    if star_pattern.search(line):
                        print(str(line))
                        return True
        except FileNotFoundError:
            print(f"[WARN] Grammar file not found: {original_fan_file}")
            return False
        return False
    
    def generate_star_grammars(self, original_fan_file, grammars_output_dir):
        logger.info(f"Generating grammars with quantified ranges from {original_fan_file}")
        ranges = [(1,10),(11,20),(21,30),(31,40)]
        #ranges = [(1,10)]
        with open(original_fan_file, "r") as f:
            original_grammar = f.read()
        generated_grammars = []
        for (start,end) in ranges:
            updated_grammar = original_grammar.replace("*", f"{{{start},{end}}}")
            new_name = os.path.splitext(os.path.basename(original_fan_file))[0]
            updated_grammar_fname = os.path.join(grammars_output_dir, f"{new_name}_{start}_{end}.fan")
            with open(updated_grammar_fname,"w") as nf:
                nf.write(updated_grammar)
            generated_grammars.append(updated_grammar_fname)
    
        return generated_grammars

    def generate_inputs(self,grammar_filepath = None,initial_population = None,request_id = None,input_directory=None):
        # use fandango to generate them based on the fan file we read
        if grammar_filepath is None:
            logger.error("[ERROR] No grammar file path provided to generate_inputs()")
            return []
        logger.info(f"Generating inputs from grammar file: {grammar_filepath}")
        os.makedirs(input_directory, exist_ok=True)
        inputs =[]

        try:
            with open(grammar_filepath, "r") as file:
                grammar, constraints = parse(file, use_stdlib=False)
            
        except FileNotFoundError as e:
            logger.error(f"[ERROR] File Not Found: {e}")
            return []
        except Exception as e:
            logger.error(f"[ERROR] Unexpected issue while parsing grammar: {e}")
            return []
        fandango = Fandango(grammar,constraints,population_size=50,initial_population=None) 
        logger.info("Generating inputs using Fandango...")
        fan_output = fandango.evolve(desired_solutions=50,max_generations=50)
        logger.info("Fandango evolve completed.")

        if not fan_output:
            logger.warning("Fandango did not generate any valid inputs.")
            return []
        
        for i,solution in enumerate(fan_output,start=1):
            input_id = f"{request_id}_{i}" if request_id else str(i)
            file_content,eval_input  = self.converter_fan_output(solution)
            if not file_content:
                logger.warning(f"[WARNING] Empty content for {input_id}, skipping.")
                continue

            filename=os.path.join(input_directory, f"input_{input_id}.txt")
            with open(filename, "w",encoding="utf-8") as f:
                f.write(file_content + "\n")
            inputs.append((input_id,solution,eval_input))
        logger.info(f"Generated {len(inputs)} inputs for grammar {grammar_filepath}. Saved to {input_directory}")
        return inputs
    
    #this is function that we run and succeeded.commenting just to check redos with timeout

    # def collect_metrics(self, input,fn):
    #     input_str = str(input)
    #     tracemalloc.start()
    #     start_time = time.perf_counter_ns()
    #     try:
    #         fn(input)
    #     except Exception as e:
    #         logger.error(f"Error running function on input {input}: {e}")
    #         return {"runtime_ns": 0, "memory_after": 0, "memory_peak": 0}
    #     end_time = time.perf_counter_ns()
    #     elapsed_time = end_time - start_time
    #     memory_consumed =tracemalloc.get_traced_memory()        #access memory
    #     tracemalloc.stop()                                      #stops tracing memory
    #     result = {"runtime_ns": elapsed_time,"memory_after" : memory_consumed[0], "memory_peak": memory_consumed[1],"function": fn}
    #     logger.info(f"Metrics collected: {result}")
    #     return result

    def collect_metrics(self, input, fn, timeout_seconds=None):
    # Normal path (no timeout): keep your existing behavior
        if not timeout_seconds:
            input_str = str(input)
            tracemalloc.start()
            start_time = time.perf_counter_ns()
            try:
                fn(input)
            except Exception as e:
                logger.error(f"Error running function on input {input}: {e}")
                tracemalloc.stop()
                return {"runtime_ns": 0, "memory_after": 0, "memory_peak": 0, "timeout": 0}
            end_time = time.perf_counter_ns()
            elapsed_time = end_time - start_time
            memory_consumed = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            return {
                "runtime_ns": elapsed_time,
                "memory_after": memory_consumed[0],
                "memory_peak": memory_consumed[1],
                "timeout": 0
            }

        # Timeout path (Windows-safe): run in a child process
        ctx = mp.get_context("spawn")
        q = ctx.Queue()
        p = ctx.Process(target=_run_fn_with_tracemalloc, args=(fn, input, q))
        p.start()
        p.join(timeout_seconds)

        if p.is_alive():
            p.terminate()
            p.join()
            # timeout result
            return {"runtime_ns": int(timeout_seconds * 1e9), "memory_after": 0, "memory_peak": 0, "timeout": 1}

        # finished within time
        if not q.empty():
            res = q.get()
            if not res["ok"]:
                logger.error(f"Error running function on input {input}: {res['error']}")
                return {"runtime_ns": 0, "memory_after": 0, "memory_peak": 0, "timeout": 0}

            return {
                "runtime_ns": res["runtime_ns"],
                "memory_after": res["memory_after"],
                "memory_peak": res["memory_peak"],
                "timeout": 0
            }

        # edge case: process ended but no result
        return {"runtime_ns": 0, "memory_after": 0, "memory_peak": 0, "timeout": 0}


    def collect_properties(self,input,solution,custom_properties,non_terminals=None,user_def_path=None):
        props = {}
        if not user_def_path or not os.path.exists(user_def_path):
            raise FileNotFoundError(f"user_def_functions.py not found at {user_def_path}")

        spec = importlib.util.spec_from_file_location("user_def_functions", user_def_path)
        user_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(user_module)

        for fn in self.fns:
            for prop_name in custom_properties:
                func = getattr(user_module, prop_name, None)
                if callable(func):
                        count = func(input)
                        props[prop_name] = count
                else:
                    raise ValueError (f"Function {prop_name} is not found in {user_def_path}") 
            logger.info(f"Properties collected: {props}")
            return props 

    def read_request(self, request_file,new_grammar_filepath, custom_properties=[],user_def_path=None):
        self.fan_rep.retrieve_json(request_file)
        return self.fan_rep.template_redirection(new_grammar_filepath,custom_properties=custom_properties,user_def_path=user_def_path)                #generate new fan file

    def fuzz(self,grammar_filepath,initial_population=None,request_id = None,non_terminals=None,input_directory=None,user_def_path=None):
        logger.info(f"file in fuzz {grammar_filepath}")
        inputs_to_run = self.generate_inputs(grammar_filepath,initial_population, request_id = request_id,input_directory=input_directory)
        logger.info('Input generation completed. Starting execution and metric/property collection...')
        self.collected_metrics = []
        self.collected_props = []
        for input_id,solution,input in inputs_to_run:
            for fn in self.fns:
                try:
                    metric_start = time.perf_counter_ns()
                    logger.info(f"starting Metrics {metric_start} for the input {input_id} and function {fn.__name__}")
                    #metrics = self.collect_metrics(input,fn)

                    if fn.__name__ == "redos_match" or fn.__name__ == "not_redos_match":
                        metrics = self.collect_metrics(input, fn, timeout_seconds=10)
                    else:
                        metrics = self.collect_metrics(input, fn)

                    logger.info("Metrics collection completed")
                except Exception as e:
                    logger.error(f"[ERROR] Failed to collect metrics for input {input_id}: {e}")
                    continue
                try:
                    props = self.collect_properties(solution,input,self.custom_properties,non_terminals,user_def_path)
                    #print("user_def_files",user_def_path)
                    #print("props in fuzz:",props)
                    prop_end = time.perf_counter_ns()
                    logger.info(f"Properties collection completed- {prop_end}")
                    time_diff = prop_end - metric_start
                    time_diff_sec = time_diff / 1000000000
                    logger.info(f"Time difference is {time_diff_sec}")
                except Exception as e:
                    logger.error(f"[ERROR] Failed to collect properties for input {input_id}: {e}")
                    continue
                metrics["input_id"] = input_id
                metrics["function_name"] = fn.__name__
                self.collected_metrics.append(metrics)
                self.collected_props.append(props)
        
    def write_summary(self, summary_path,headernames =None):
        with open(summary_path, "w", newline= '') as file:
            writer = csv.writer(file)
            base_headers = ["function_name", "input_id","runtime_ns", "memory_after", "memory_peak"]
            if headernames:
                fields = base_headers + headernames
            else:
                fields = base_headers
            writer.writerow(fields)
            for metric,props in zip(self.collected_metrics, self.collected_props):
                if not isinstance(metric,dict) or not isinstance(props,dict):
                    logger.warning(f"Skipping non-dict metric/prop: {metric}, {props})")
                    continue
                row = [metric.get("function_name", ""), metric.get("input_id", ""),metric.get("runtime_ns", ""),metric.get("memory_after", ""),metric.get("memory_peak", "")]
                for name in headernames:
                    # Try from metric first, then props
                    row.append(props.get(name, 0))
                writer.writerow(row)

    def split_summary_by_function(self, main_summary_path,output_dir):
        os.makedirs(output_dir, exist_ok=True)
        with open(main_summary_path, "r") as infile:
            reader = csv.reader(infile)
            header = next(reader)  

            function_groups = {}

            for row in reader:
                if not row:
                    continue
                function_name = row[0]  # first column is function_name
                if function_name not in function_groups:
                    function_groups[function_name] = []
                function_groups[function_name].append(row)

        # Write each function's rows to its own file
        for function_name, rows in function_groups.items():
            output_file = os.path.join(output_dir, f"{function_name}_summary.csv")
            with open(output_file, "w", newline="") as outfile:
                writer = csv.writer(outfile)
                writer.writerow(header)  # write header
                writer.writerows(rows)   # write all rows
            logger.info(f"Wrote {len(rows)} rows for {function_name} → {output_file}")

    def write_final_summary(self,summary_files,final_summary_file,headernames =None):
        base_headers = ["function_name", "input_id","runtime_ns", "memory_after", "memory_peak"]
        if headernames:
            fields = base_headers + [h for h in headernames if h not in base_headers]
        else:
            fields = base_headers

        #writer.writerow(fields)
        with open(final_summary_file, "w", newline= '') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(fields)
            for file in summary_files:
                with open(file, "r") as infile:
                    csvreader = csv.DictReader(infile)
                    for row in csvreader:
                        rowvalues =[]
                        for field in fields:
                            rowvalues.append(row.get(field,""))
                        writer.writerow(rowvalues)

    def extract_nonterminals(original_fan_filepath):
        nonterminal_pattern = re.compile(r'<[^<> ]+>')
        non_terminals = set()
        try:
            with open(original_fan_filepath, "r", encoding= "utf-8") as file:
                for line in file:
                    matches = nonterminal_pattern.findall(line)
                    non_terminals.update(matches)
        except FileNotFoundError:
            logger.error(f"[ERROR] File not found: {original_fan_filepath}")
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error while reading {original_fan_filepath}: {e}")
        return sorted(non_terminals)

    def generate_softconstraint_grammar(self, original_fan_file):
        constraints = self.fan_rep.extract_quantitative_constraints(original_fan_file)
        with open(original_fan_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        new_grammar_lines = []

        for line in lines:
            stripped_line = line.strip()
            if any(c["original_line"] in stripped_line for c in constraints):
                new_grammar_lines.append(f"# Soft constraint applied: {stripped_line}\n")
                continue
            new_grammar_lines.append(line)
        if constraints:
            new_grammar_lines.insert(0, "import math\n")
            for c in constraints:
                new_grammar_lines.append(f"minimizing math.abs({c['value']} - "
                                         f"{c['property']}({c['nonterminal']}))\n"
                                         )
        with open(original_fan_file, "w" , encoding="utf-8") as f:
            f.writelines(new_grammar_lines)
        return [original_fan_file]

