from .logger import get_logger
logger = get_logger(__name__)
from fandango.evolution.algorithm import Fandango
#import fandango
from fandango.language.parse.parse import parse
import os
import ast
import re
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class FanRepresentation:

    def __init__(self, path_to_file,functions_to_execute):
        self.path_to_file = path_to_file
        self.fns = functions_to_execute

    def retrieve_fanfile(self, fanfile_path):
        self.importfunctions= ""
        self.grammar = ""
        self.functions = []
        self.constraints = []
        current_function  = []
        inside_function = False         #flag to track if we are currently inside a function definition block
        try:
            with open(fanfile_path,"r") as file:
                lines = file.readlines()
        except FileNotFoundError:
            logger.error(f"[ERROR] FAN file not found: {fanfile_path}")
            return
        except Exception as e:
            logger.error(f"[ERROR] Unexpected error reading FAN file: {e}")
            return
        with open(fanfile_path,"r") as file:
            grammar,constraints = parse(file, use_stdlib= False)
        self.grammar = grammar
        self.constraints = constraints

        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("import") or stripped_line.startswith("from"):
                self.importfunctions +=line
            #elif stripped_line.startswith("<"):
                #self.grammar += line
            elif stripped_line.startswith("def"):
                inside_function = True
                current_function = [line]
            elif inside_function:
                if line.startswith(" ") or line.startswith("\t"):
                    current_function.append(line)
                else:
                    self.functions.append("".join(current_function))
                    inside_function = False
                    if stripped_line.startswith("def"): #trigger if next function is not seperated by a line break
                        inside_function = True
                        current_function = [line]
            #elif stripped_line.startswith("where"):
                #self.constraints.append(stripped_line)
        if inside_function and current_function:
            self.functions.append("".join(current_function))
    
    def retrieve_json(self, jsonfile_path):
        import json
        from pprint import pprint
        try:
            with open(jsonfile_path) as fd:
                json_data = json.load(fd)
                #pprint(json_data)
        except FileNotFoundError:
            logger.error(f"[ERROR] JSON file not found: {jsonfile_path}")
            return
        except json.JSONDecodeError:
            logger.error(f"[ERROR] Invalid JSON format in {jsonfile_path}")
            return

        self.metrics = json_data["metric_constraints"]
        self.properties = json_data["prop_constraints"] #retrieve property constraints from json
        self.input_data = json_data["initial_pop"]
        self.request_type = json_data["request_type"]
        self.cleaned_inputs = []
        for input in self.input_data:
            input = input.strip()
            input = ','.join([x.strip() for x in input.split(',')])
            self.cleaned_inputs.append(input)

    '''
    #template redirection - working function - commenting out for check upper edge grammar generation

    def template_redirection(self,new_grammar_filepath, custom_properties=[],user_def_path=None):
        names = []
        #template for metric constraints
        if self.metrics:
            for metric in self.metrics:
                name = metric["name"]
                if isinstance(name, list):
                    names.extend(name)  
                else:
                    names.append(name)   
            #print("names", names)
        if "runtime_ns" in names or "memory_peak" in names:
            self.update_constraint_function()
            self.generate_newfan(new_grammar_filepath,user_def_path)
        #else:
        #template for property constraints
        if self.properties:
            for prop in self.properties:
                name = prop["name"]
                if isinstance(name, list):
                    names.extend(name)  
                else:
                    names.append(name)  
            #print("names", names)
            self.update_constraints_general(custom_properties=custom_properties)
            self.generate_newfan_general(new_grammar_filepath,user_def_path)
        #print("Final constraints before write:", self.constraints)
        '''
    
    def template_redirection(self, new_grammar_filepath, custom_properties=[], user_def_path=None):
        """
        Redirect grammar construction based on request type:
        - metric constraints -> constraint function
        - lower edge property constraints -> where clause
        - upper edge property constraints -> structural grammar bounds
        """

        names = []

        # --------------------------------------------------
        # STEP 1: Collect metric names
        # --------------------------------------------------
        if self.metrics:
            for metric in self.metrics:
                name = metric["name"]
                if isinstance(name, list):
                    names.extend(name)
                else:
                    names.append(name)

        # --------------------------------------------------
        # STEP 2: Apply metric constraints (unchanged)
        # --------------------------------------------------
        if "runtime_ns" in names or "memory_peak" in names:
            self.update_constraint_function()
            self.generate_newfan(new_grammar_filepath, user_def_path)

        # --------------------------------------------------
        # STEP 3: Property constraints handling
        # --------------------------------------------------
        if not self.properties:
            return [new_grammar_filepath]

        generated_grammars = []

        for prop in self.properties:
            prop_name = prop["name"]
            operator = prop["op"]
            value = int(prop["value"])

            # --------------------------------------------------
            # Detect upper edge request
            # (Analyzer already split this logically)
            # --------------------------------------------------
            request_type = self.request_type
            logger.info(f"Processing property '{prop_name}' as '{request_type}'")

            if request_type == "upper edge request":
                # ----------------------------------------------
                # CASE 1: STRUCTURAL (count_*) → grammar change
                # ----------------------------------------------

                if prop_name.startswith("count_"):
                    nonterminal = f"<{prop_name.replace('count_', '')}>"

                    self.generate_newfan(new_grammar_filepath, user_def_path)
                    
                    generated_grammars = self.generate_upper_edge_grammars(
                        base_fan_file=new_grammar_filepath,
                        output_dir=os.path.dirname(new_grammar_filepath),
                        nonterminal=nonterminal,
                        threshold=value
                    )
                    return generated_grammars
                else:
                    self.update_constraints_general(custom_properties=custom_properties)
                    self.generate_newfan_general(new_grammar_filepath, user_def_path)
                    return [new_grammar_filepath]

            else:
                # ----------------------------------------------
                # LOWER EDGE (existing behavior)
                # ----------------------------------------------
                self.update_constraints_general(custom_properties=custom_properties)
                self.generate_newfan_general(new_grammar_filepath, user_def_path)
                return [new_grammar_filepath]

#Template for update runtime and memory constraints
    def update_constraint_function(self):
        self.updated_constraints=[]
        #constraint_function = '''
#def constraints(tree):
    #time_and_memory= elapsed(tree)
    #return {constraints}'''
        constraint_function = '''
def constraints(tree):
    time_and_memory = {{}}
    results = []
    user_system_funcs = get_user_system_funcs()
    for func_name in user_system_funcs:
        time_and_memory[func_name] = elapsed(tree,func_name)
        results.append({constraints})
    return all(results)'''
        
        if not self.metrics:
            logger.warning("[WARNING] No metric constraints provided.")
            return
        
        for fn in self.fns:
            for metric in self.metrics:
                names = metric["name"]
                operator = metric["op"]
                values = metric["value"]
                if isinstance(names,list):
                    for name in names:
                        try:
                            value = int(values)
                        except (ValueError,TypeError):
                            value = values
                        self.updated_constraints.append(f'time_and_memory["{fn.__name__}"]["{name}"] {operator} {value}')
                else:
                    try:
                        value = int(values)
                    except ValueError:
                        value = values
                    self.updated_constraints.append(f'time_and_memory["{fn.__name__}"]["{names}"] {operator} {value}')
        combine_constraint = " or ".join(self.updated_constraints)
        self.final_constraint_function = constraint_function.format(constraints = combine_constraint)
        self.final_constraint = "constraints(<start>)"
        constraint_value = "constraints(NonTerminal('<start>'))"
        existing_string_constraints = [ c for c in self.constraints if isinstance(c, str)]
        #if constraint_value not in str(self.constraints):
        if self.final_constraint not in existing_string_constraints:
            self.constraints.append(self.final_constraint)
        else:
            return self.constraints
    
    def extract_user_functions(self,user_def_path):
        if not os.path.exists(user_def_path):
            return []

        with open(user_def_path, "r") as f:
            source = f.read()

        module = ast.parse(source)
        functions = []

        for node in module.body:
            if isinstance(node, ast.FunctionDef):
                # get source of function (including nested defs)
                func_code = ast.unparse(node)
                functions.append(func_code)

        return functions

    def generate_newfan(self, new_grammar_file,user_def_path=None):
        #new_grammar_file = f"sorting_newtest.fan"
        self.functions = [fn for fn in self.functions if not fn.strip().startswith("def constraints(")]
        self.functions.append(self.final_constraint_function)
        full_code = "\n".join(self.functions)
        try:
            parsed_code = ast.parse(full_code)
            self.formatted_code = ast.unparse(parsed_code)
            #print(f"formattedcode: {self.formatted_code}")
        except SyntaxError as e:
            logger.error(f"[ERROR] Syntax error in function block: {e}")
            return
        if not user_def_path or not os.path.exists(user_def_path):
            raise FileNotFoundError(f"user_def_functions.py not found at {user_def_path}")
        self.user_functions = self.extract_user_functions(user_def_path)
        self.user_formatted_code = "\n\n".join(self.user_functions)
        '''
        with open(user_def_path,"r") as file:
        #with open("user_def_functions.py","r") as file:
            lines = file.readlines()
        u_inside_function = False
        u_current_function = []
        self.user_functions = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("def"):
                u_inside_function = True
                u_current_function = [line]
            elif u_inside_function:
                #added stripped == ""
                if line.startswith(" ") or line.startswith("\t") or stripped == "":
                    u_current_function.append(line)
                else:
                    self.user_functions.append("".join(u_current_function))
                    u_inside_function = False
                    u_current_function = []
                    if stripped.startswith("def"):
                        u_inside_function = True
                        u_current_function = [line]
        if u_inside_function and u_current_function:
            self.user_functions.append("".join(u_current_function))
        user_def_code = "\n".join(self.user_functions)
        #print(f"user def code: {user_def_code}")
        u_parsed_code = ast.parse(user_def_code)
        self.user_formatted_code = ast.unparse(u_parsed_code)
        #print(f"user_formatted_code: {self.user_formatted_code}")
        '''

        with open(new_grammar_file,"w") as file:
            #print("new grammar file:",new_grammar_file)
            file.write(self.importfunctions + "\n")
            file.write(str(self.grammar) + "\n")
            file.write(self.formatted_code + "\n")
            existing_content = ""
            if os.path.exists(new_grammar_file):
                with open(new_grammar_file,"r") as f:
                    existing_content = f.read()
            #print(f"existing_content: {existing_content}")
            user_code_exists = self.user_formatted_code.strip() in self.formatted_code
            #print(f"user code : {user_code_exists}")
            if not user_code_exists:
                file.write("\n" + self.user_formatted_code + "\n")
            for constraint in self.constraints:
                if isinstance(constraint, str):
                    file.write("where " + constraint + "\n")

    def update_constraints_general(self,custom_properties = []):
        self.updated_constraints=[]
        #default_ids = ["length","int","str","count"]
        for prop in self.properties:
            names = prop["name"]        #here i took header names- but its wrong as any header names can be use.
            #if isinstance(names,list):
                #names = names[0]
            operators = prop["op"]
            values = prop["value"]
            if names in custom_properties:
                self.updated_constraint = f"where {names}(<start>) {operators} {values}"
                self.updated_constraints.append(self.updated_constraint) 
            else:
                logger.warning(f"[WARNING] unknown custom property: {names}") 

    def generate_newfan_general(self,new_grammar_file,user_def_path=None):
        if os.path.exists(new_grammar_file) and len(self.metrics) != 0:
            with open(new_grammar_file, "a") as file:
                file.write("\n".join(self.updated_constraints) + "\n")
        else:
            #new_grammar_file = f"sorting_newtest.fan"
            with open(new_grammar_file, "w") as file:
                file.write(self.importfunctions + "\n")
                file.write(str(self.grammar) + "\n")
                file.write(self.user_formatted_code + "\n")
                file.write("\n".join(self.updated_constraints) + "\n")                

    def extract_quantitative_constraints(self, fan_file):
        QUANT_CONSTRAINT_RE = re.compile(
        r'(?P<prop>\w+)\s*'
        r'\(\s*(?P<nt><[^>]+>)\s*\)\s*'
        r'(?P<op>>=|<=|==|>|<)\s*'
        r'(?P<value>\d+)'
    )
        constraints = []

        with open(fan_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Skip comments and grammar rules
                if not line or line.startswith("#") or "::=" in line:
                    continue

                match = QUANT_CONSTRAINT_RE.search(line)
                if match:
                    constraints.append({
                        "property": match.group("prop"),
                        "nonterminal": match.group("nt"),
                        "operator": match.group("op"),
                        "value": int(match.group("value")),
                        "original_line": line
                    })

        return constraints

    def generate_upper_edge_grammars(self, base_fan_file: str, output_dir: str,nonterminal: str,threshold: int,ranges=None):
        """
        Generate multiple FAN grammars by structurally constraining
        a non-terminal using repetition bounds.

        Example:
            <img_tag> {41,45}
            <img_tag> {46,50}
        """

        if ranges is None:
            ranges = [
                (threshold, threshold + 4)
                #(threshold + 5, threshold + 9)
            ]

        with open(base_fan_file, "r", encoding="utf-8") as f:
            original_text = f.read()

        generated_files = []

        for i, (low, high) in enumerate(ranges):
            modified_text = original_text

            # Replace first occurrence of the non-terminal repetition
            pattern = re.compile(
                rf"({re.escape(nonterminal)})(\s*\{{[^}}]*\}}|\*)?"
            )

            def replacer(match):
                return f"{nonterminal} {{{low},{high}}}"

            modified_text = pattern.sub(replacer, modified_text, count=1)

            out_file = os.path.join(
                output_dir,
                f"{os.path.splitext(os.path.basename(base_fan_file))[0]}_upper_{low}_{high}.fan"
            )

            with open(out_file, "w", encoding="utf-8") as f:
                f.write(modified_text)

            generated_files.append(out_file)

        return generated_files
