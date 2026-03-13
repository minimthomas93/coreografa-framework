from .logger import get_logger
logger = get_logger(__name__)
from .analyzer_library import InfoStorage, FunctionRunSummary, FunctionInputInfo, Metric, Feature
from .coreografa_requests import CoreoRequest, CoreoBasicConstraint

import sys
import random
import os

# imports for plots
import matplotlib.pyplot as plt
import numpy as np
import big_o
import statsmodels.api as sm
import scipy.integrate as si
import scipy.stats as ss
import math
import pandas as pd


class Analyzer:
    def __init__(self, names = [], summaries = {}) -> None:
        self.names = names
        self.summaries = summaries
        self.metrics = []
        self.features = []
        self.requests = []
        self.function_names = {}
        self.storage = None

    def read_csvs(self, 
                  file_names = [], 
                  metrics = ["runtime_ns", "memory_peak"], 
                  categoricals = [], 
                  input_features = ["length","sortedness"], 
                  ignore = ["memory_after"], 
                  prop_filters = [],
                  metric_filters = [],
                  grab_every = 1, 
                  input_dir = None):
        # filters is a list of tuples, where each tuple is (feature_name, value); do not add an entry if the feature_name has the value
        if len(categoricals) == 0:
            self.names = file_names
        else:
            self.names = []
        self.summaries = dict()
        self.metrics = metrics

        for file_name in file_names:
            # to deal with categoricals, we might update the summary_file_names with each category
            # e.g., if we have a category "C" with values "a" and "b" with file name "n", we might have summary_file_names = ["n-C/a", "n-C/b"]
            summary_file_names = []

            try:
                with open(file_name, 'r') as file:
                    summaries = []
                    input_feature_names = []
                    first_line = True
                    data_mapping = {
                        "function_name": -1,
                        "input_id": -1,
                    }
                    index = 0
                    for line in file:
                        # trim newline
                        line = line.strip()
                        # handle header
                        if first_line:
                            # split by commas
                            header_contents = line.split(',')
                            if "function_name" in header_contents:
                                data_mapping["function_name"] = header_contents.index("function_name")
                            if "input_id" in header_contents:
                                data_mapping["input_id"] = header_contents.index("input_id")

                            for metric in metrics:
                                if metric in header_contents:
                                    data_mapping[metric] = header_contents.index(metric)
                                else:
                                    logger.warning(f"[WARNING] Metric '{metric}' not found in '{file_name}'.")
                                    logger.warning(f"[WARNING] Specify metrics when you begin analysis.")
                                    sys.exit(1)
                            
                            for categorical in categoricals:
                                if categorical in header_contents:
                                    data_mapping[categorical] = header_contents.index(categorical)
                                else:
                                    logger.warning(f"[WARNING] Categorical '{categorical}' not found in '{file_name}'.")
                                    logger.warning(f"[WARNING] Specify categoricals when you begin analysis.")
                                    sys.exit(1)

                            # for all unaccounted for columns, assume they are input features
                            for i in range(len(header_contents)):
                                if header_contents[i] in ignore:
                                    continue
                                if i not in data_mapping.values():
                                    input_feature_names.append(header_contents[i])
                                    data_mapping[header_contents[i]] = i

                            first_line = False
                            continue

                        index += 1
                        if index % grab_every != 0:
                            continue

                        # split by commas
                        data = line.split(',')
                        # create a new summary
                        # first, collect function info, if any
                        function_name = "function"
                        input_id = "-1"
                        if data_mapping["function_name"] != -1:
                            function_name = data[data_mapping["function_name"]]
                        if data_mapping["input_id"] != -1:
                            input_id = data[data_mapping["input_id"]]
                        fn_input_info = FunctionInputInfo(function_name, input_id)

                        # then, collect metrics
                        metrics_list = []
                        skip_line = False
                        for metric in metrics:
                            for (mn, fn) in metric_filters:
                                if mn == metric and fn(float(data[data_mapping[metric]])):
                                    logger.warning(f"[WARNING] Skipping line with {metric} = {data[data_mapping[metric]]}.")
                                    skip_line = True
                            metrics_list.append(Metric(metric, data[data_mapping[metric]]))
                        # then, collect input features
                        features_list = []
                        for feature_name in input_feature_names:
                            for (ff, fn) in prop_filters:
                                if ff == feature_name and fn(float(data[data_mapping[feature_name]])):
                                    logger.warning(f"[WARNING] Skipping line with {feature_name} = {data[data_mapping[feature_name]]}.")
                                    skip_line = True
                            features_list.append(Feature(feature_name, data[data_mapping[feature_name]]))
                        if skip_line:
                            continue
                        # then, collect categoricals
                        # if there are categoricals...
                        if len(categoricals) > 0:
                            for categorical in categoricals:
                                the_name = f"{file_name}-{categorical}/{data[data_mapping[categorical]]}"
                                summary_file_names.append(the_name)
                                if the_name not in self.names:
                                    self.names.append(the_name)
                        else:
                            summary_file_names.append(file_name)
                        # create the summary
                        summary = FunctionRunSummary(fn_input_info, metrics_list, features_list)
                        # append to summaries
                        summaries.append(summary)
                        for name in summary_file_names:
                            if name not in self.function_names:
                                self.function_names[name] = set()
                            self.function_names[name].add(function_name)
                    
                    # add the summaries to the appropriate place
                    for i in range(len(summaries)):
                        if summary_file_names[i] not in self.summaries:
                            self.summaries[summary_file_names[i]] = []
                        self.summaries[summary_file_names[i]].append(summaries[i])
                    
                    self.features = input_feature_names
            except FileNotFoundError:
                logger.error(f"[ERROR] File '{file_name}' not found.")
                exit(1)
        self.storage = InfoStorage(metrics, input_feature_names, self.names, input_dir)
        logger.info(f"self.storage {self.storage}")
        logger.info("DEBUG storage attributes: %s", dir(self.storage))
        self.storage.build_storage(self)
        logger.info("function name in read csvs func: %s", self.function_names)
        logger.info(f"Total summaries loaded: {sum(len(v) for v in self.summaries.values())}")

    def generate_edge_request(self, name, metric, prop, write_json = False, request_directory = None, request_type = "edge request"):
        try:
            #how can we add multiple functions here
            function = list(self.function_names[name])[0]
            logger.info(f"function name is {function}")
            metric_ordered_by = self.storage.get_metric_ordered_by_feature(name, metric, prop)
            input_files = self.storage.get_inputs_ordered_by_metric_and_feature(name, metric, prop)
            logger.info(f"Length of input files: {len(input_files)}")
            #print(f"input files: {input_files}")

            # get top and bottom 10% of inputs w.r.t. metric values
            # get the top 10% of inputs
            ten_percent = int(len(metric_ordered_by) * 0.1)

            # get metric and property ranges for these
            top_10_percent_metric = [pmp[0] for pmp in metric_ordered_by[9*ten_percent:]]
            bottom_10_percent_metric = [pmp[0] for pmp in metric_ordered_by[:ten_percent]]
            top_10_percent_prop = [pmp[1] for pmp in metric_ordered_by[9*ten_percent:]]
            bottom_10_percent_prop = [pmp[1] for pmp in metric_ordered_by[:ten_percent]]

            # get the min and max of the top 10% and bottom 10%
            top_10_percent_metric_min = min(top_10_percent_metric)
            top_10_percent_metric_max = max(top_10_percent_metric)
            bottom_10_percent_metric_min = min(bottom_10_percent_metric)
            bottom_10_percent_metric_max = max(bottom_10_percent_metric)
            top_10_percent_prop_min = min(top_10_percent_prop)
            top_10_percent_prop_max = max(top_10_percent_prop)
            bottom_10_percent_prop_min = min(bottom_10_percent_prop)
            bottom_10_percent_prop_max = max(bottom_10_percent_prop)

            # ok now generate two requests: 
            # one for the top 10% and one for the bottom 10%
            constraints = []
            constraints.append(CoreoBasicConstraint("metric", metric, ">=", top_10_percent_metric_min))
            constraints.append(CoreoBasicConstraint("metric", metric, "<=", top_10_percent_metric_max))
            constraints.append(CoreoBasicConstraint("prop", prop, ">=", top_10_percent_prop_min))
            #constraints.append(CoreoBasicConstraint("prop", prop, "<=", top_10_percent_prop_max))
            initial_pop_files = [v[0] for v in input_files[9*ten_percent:]]
            self.generate_request(name,function, constraints, [], [], initial_pop_files, write_json, request_directory, request_type)
            constraints = []
            constraints.append(CoreoBasicConstraint("metric", metric, ">=", bottom_10_percent_metric_min))
            constraints.append(CoreoBasicConstraint("metric", metric, "<=", bottom_10_percent_metric_max))
            constraints.append(CoreoBasicConstraint("prop", prop, ">=", bottom_10_percent_prop_min))
            #constraints.append(CoreoBasicConstraint("prop", prop, "<=", bottom_10_percent_prop_max))
            initial_pop_files = [v[0] for v in input_files[:ten_percent]]
            self.generate_request(name,function, constraints, [], [], initial_pop_files, write_json, request_directory, request_type)  
            logger.info(f'Request Type is {request_type}')
        except Exception as e:
            logger.error(f"[ERROR] Edge request generation failed: {e}")
            self.generate_random_requests(name, function if 'function' in locals() else "unknown_function", request_directory)

    def generate_upper_edge_request(self, name, metric, prop, write_json = False, request_directory = None, request_type = "upper edge request"):
        try:
            function = list(self.function_names[name])[0] 
            metric_ordered_by = self.storage.get_metric_ordered_by_feature(name, metric, prop)
            input_files = self.storage.get_inputs_ordered_by_metric_and_feature(name, metric, prop)
            logger.info(f"Length of input files: {len(input_files)}")
            #print(f"input files: {input_files}")

            # get the top 10% of inputs
            ten_percent = int(len(metric_ordered_by) * 0.1)

            # get metric and property ranges for these
            top_10_percent_metric = [pmp[0] for pmp in metric_ordered_by[9*ten_percent:]]
            top_10_percent_prop = [pmp[1] for pmp in metric_ordered_by[9*ten_percent:]]

            # get the min and max of the top 10%
            top_10_percent_metric_min = min(top_10_percent_metric)
            top_10_percent_metric_max = max(top_10_percent_metric)
            top_10_percent_prop_min = min(top_10_percent_prop)
            top_10_percent_prop_max = max(top_10_percent_prop)

            constraints = []
            constraints.append(CoreoBasicConstraint("metric", metric, ">=", top_10_percent_metric_min))
            constraints.append(CoreoBasicConstraint("metric", metric, "<=", top_10_percent_metric_max))
            constraints.append(CoreoBasicConstraint("prop", prop, ">=", top_10_percent_prop_min))
            #constraints.append(CoreoBasicConstraint("prop", prop, "<=", top_10_percent_prop_max))
            initial_pop_files = [v[0] for v in input_files[9*ten_percent:]]
            self.generate_request(name,function, constraints, [], [], initial_pop_files, write_json, request_directory, request_type)  
        except Exception as e:
            logger.error(f"[ERROR] Upper edge request generation failed: {e}")
            self.generate_random_requests(name, function if 'function' in locals() else "unknown_function", request_directory)

    def generate_lower_edge_request(self, name, metric, prop, write_json = False, request_directory = None, request_type = "lower edge request"):
        try:
            function = list(self.function_names[name])[0] 
            metric_ordered_by = self.storage.get_metric_ordered_by_feature(name, metric, prop)
            input_files = self.storage.get_inputs_ordered_by_metric_and_feature(name, metric, prop)
            logger.info(f"Length of input files: {len(input_files)}")
            #print(f"input files: {input_files}")

            # get the bottom 10% of inputs
            ten_percent = int(len(metric_ordered_by) * 0.1)

            # get metric and property ranges for these
            bottom_10_percent_metric = [pmp[0] for pmp in metric_ordered_by[:ten_percent]]
            bottom_10_percent_prop = [pmp[1] for pmp in metric_ordered_by[:ten_percent]]

            if not bottom_10_percent_metric or not bottom_10_percent_prop:
                logger.warning(
                    f"Bottom 10 percent empty (n={len(metric_ordered_by)}, ten_percent={ten_percent}). "
                    f"Skipping lower edge request."
                )
                return

            # get the min and max of the bottom 10%
            bottom_10_percent_metric_min = min(bottom_10_percent_metric)
            bottom_10_percent_metric_max = max(bottom_10_percent_metric)
            bottom_10_percent_prop_min = min(bottom_10_percent_prop)
            bottom_10_percent_prop_max = max(bottom_10_percent_prop)

            constraints = []
            constraints.append(CoreoBasicConstraint("metric", metric, ">=", bottom_10_percent_metric_min))
            constraints.append(CoreoBasicConstraint("metric", metric, "<=", bottom_10_percent_metric_max))
            constraints.append(CoreoBasicConstraint("prop", prop, ">=", bottom_10_percent_prop_min))
            #constraints.append(CoreoBasicConstraint("prop", prop, "<=", bottom_10_percent_prop_max))
            initial_pop_files = [v[0] for v in input_files[:ten_percent]]
            self.generate_request(name,function, constraints, [], [], initial_pop_files, write_json, request_directory, request_type)  
        except Exception as e:
            logger.error(f"[ERROR] Lower edge request generation failed: {e}")
            self.generate_random_requests(name, function if 'function' in locals() else "unknown_function", request_directory)
    
    def generate_frequency_based_requests(self, name, metric, prop, write_json = False,request_directory=None, request_type = "frequency request"):
        try:
            function = list(self.function_names[name])[0]
            #print("function name: ", function)
            # divide metrics in 10 groups
            #metric_vals = self.storage.get_metric(name, metric).copy() #remove this property-added to check default request
            #input_files = self.storage.inputs.copy()
            rows = self.storage.get_inputs_ordered_by_metric_and_feature(name, metric, prop)
            if not rows:
                logger.warning(f"No data available for '{name}' with metric '{metric}' and property '{prop}'. Skipping frequency-based request generation.")
                return
            metric_vals = [row[1] for row in rows]
            min_val = min(metric_vals)
            max_val = max(metric_vals)
            if min_val == max_val:
                logger.warning(f"[WARNING] Metric '{metric}' is constant. Falling back to random request.")
                return self.generate_random_requests(name, metric, prop, request_directory=request_directory, request_type=request_type)

            step = (max_val - min_val) / 10
            groups = []
            for i in range(10):
                groups.append((min_val + i * step, min_val + (i + 1) * step))
            # divide the metrics into groups
            groupings = {}
            for i, g in enumerate(groups):
                lo, hi = g
                if i == len(groups) - 1:
                    groupings[g] = [row for row in rows if lo <= row[1] <= hi]
                else:
                    groupings[g] = [row for row in rows if lo <= row[1] < hi]

            non_empty = {g: rs for g, rs in groupings.items() if rs}
            smallest_three = sorted(non_empty, key=lambda g: len(non_empty[g]))[:3]
            # generate requests for the smallest three groups
            #smallest_three = sorted(groupings, key = lambda x: len(groupings[x]))[:3]
            for g in smallest_three:
                rs = non_empty[g]
                m_lo, m_hi = g

                prop_vals = [r[2] for r in rs]
                p_lo, p_hi = min(prop_vals), max(prop_vals)

                constraints = []
                constraints.append(CoreoBasicConstraint("metric", metric, ">=", m_lo))
                constraints.append(CoreoBasicConstraint("metric", metric, "<=", m_hi))
                constraints.append(CoreoBasicConstraint("prop",   prop,   ">=", p_lo))
                constraints.append(CoreoBasicConstraint("prop",   prop,   "<=", p_hi))

                initial_pop_files = [os.path.normpath(r[0]) for r in rs]

                self.generate_request(name, function,constraints, [], [], initial_pop_files, write_json,request_directory, request_type)
        except Exception as e:
            logger.error(f"[ERROR] Frequency-based request generation failed: {e}")
            self.generate_random_requests(name, metric, prop, request_directory=request_directory, request_type=request_type)

        '''
    def generate_frequency_based_requests(self, name, metric, write_json = False,request_directory=None, request_type = "frequency request"):
        try:
            function = list(self.function_names[name])[0] 
            #print("function name: ", function)
            # divide metrics in 10 groups
            metric_vals = self.storage.get_metric(name, metric).copy() #remove this property-added to check default request
            input_files = self.storage.inputs.copy()
            #print(f"input files: {input_files}")
            #input_files = (self.storage.inputs * (len(metric_vals) // len(self.storage.inputs))) -- this is needed for weasyprint
            logger.info(f"Length of metric values: {len(metric_vals)}")
            logger.info(f"Length of input files: {len(input_files)}")
            min_val = min(metric_vals)
            max_val = max(metric_vals)
            step = (max_val - min_val) / 10
            groups = []
            for i in range(10):
                groups.append((min_val + i * step, min_val + (i + 1) * step))
            # divide the metrics into groups
            groupings = dict()
            #for group in groups:
            #    groupings[group] = [(metric_vals[i], input_files[i]) for i in range(len(metric_vals)) if group[0] <= metric_vals[i] < group[1]]
            for i in range(len(groups)):
                group = groups[i]
                if i == len(groups) - 1:
                    groupings[group] = [
                        (metric_vals[j], input_files[j]) for j in range(len(metric_vals)) if group[0] <= metric_vals[j] <= group[1]
                    ]
                else:
                    groupings[group] =[(metric_vals[j], input_files[j]) for j in range(len(metric_vals)) if group[0] <= metric_vals[j] < group[1]]
            
                #print(f"Group {group} -> entries: {groupings[group]}")
            non_empty_groups = {k: v for k, v in groupings.items() if len(v) > 0}
            smallest_three = sorted(non_empty_groups, key = lambda x: len(non_empty_groups[x]))[:3]
            # generate requests for the smallest three groups
            #smallest_three = sorted(groupings, key = lambda x: len(groupings[x]))[:3]
            for group in smallest_three:
                #print(f"Request for '{name}' and '{metric}' in range {group}:")
                constraints = []
                constraints.append(CoreoBasicConstraint("metric", metric, ">=", group[0]))
                constraints.append(CoreoBasicConstraint("metric", metric, "<=", group[1]))
                initial_pop_files = [os.path.normpath(x[1]) for x in non_empty_groups[group]]
                #print("Initial pop files:", initial_pop_files)
                #initial_pop_files = [x[1] for x in groupings[group]]
                self.generate_request(name, function,constraints, [], [], initial_pop_files, write_json,request_directory, request_type)
        except Exception as e:
            logger.error(f"[ERROR] Frequency-based request generation failed: {e}")
            self.generate_random_requests(name, function if 'function' in locals() else "unknown_function", request_directory, request_type)    
        '''


    def generate_uniform_negation_requests(self,name,metric,prop,write_json=False,request_directory=None, request_type = "negation request"):
        function = list(self.function_names[name])[0] 
        try:
            metric_values = self.storage.get_metric(name,metric).copy()
            logger.info(f"metric values{metric_values}")
            column_values = self.storage.get_feature(name,prop).copy()
            logger.info(f"column values{column_values}")

            if not column_values: 
                raise ValueError(f"No values found for property '{prop}'.")
            
            if all(val == column_values[0] for val in column_values):
                common_val = column_values[0]
                logger.info(f"All values for '{prop}' are the same: {common_val}")
                logger.info(f"Prop '{prop}' values: {column_values}")
                constraints = []
                #constraints.append(CoreoBasicConstraint("metric", metric, "!=", common_val))
                constraints.append(CoreoBasicConstraint("prop", prop, "!=", common_val))
                #constraints = CoreoBasicConstraint("prop", prop, "!=", common_val)
                logger.info(f"constraints: {constraints}")
                input_files = self.storage.inputs.copy()
                initial_pop_files = [os.path.normpath(x) for x in input_files]

                self.generate_request(name,function, constraints, [], [], initial_pop_files, write_json,request_directory, request_type)

                #self.generate_request(name,constraints, [], [],initial_pop=initial_pop_files,write_json=write_json,request_directory=request_directory)
                logger.info(f"Request generated to negate uniform value {common_val} in '{prop}'")
            else:
                logger.info(f"Values for '{prop}' are already diverse — no request needed.")
        except Exception as e:
            # Fallback: create a default request to keep workflow running
            logger.error(f"[ERROR] Negation request generation failed: {e}")
            self.generate_random_requests(name, function, request_directory, reason=str(e),request_type=request_type)

    def generate_random_requests(self, name, metric,prop,sample_size=5,write_json = False,request_directory=None,request_type = "random request"):
        function = list(self.function_names[name])[0]
        logger.info(f"Generating random request for '{name}' with metric '{metric}' and property '{prop}'.")
        #input_files = self.storage.inputs.copy()
        #metric_ordered_by = self.storage.get_metric_ordered_by_feature(name, metric, prop)

        # get the (path, metric_value, prop_value) tuples ordered by the requested metric
        input_files = self.storage.get_inputs_ordered_by_metric_and_feature(name, metric, prop)
        #print(f"metric ordered by {metric_ordered_by}")
        logger.info(f"Input files : {input_files}")

        # choose an actual sample size (can't be larger than available)
        k = min(sample_size,len(input_files))
        sampled = random.sample(input_files,k)

        # sampled elements are like: (path, metric_val, prop_val)
        metric_vals = [t[1] for t in sampled]
        prop_vals   = [t[2] for t in sampled]
        initial_pop_files = [os.path.normpath(t[0]) for t in sampled]

         # compute min/max and guard against degenerate cases
        min_metric, max_metric = min(metric_vals), max(metric_vals)
        min_prop,   max_prop   = min(prop_vals),   max(prop_vals)

        # if min == max, expand a bit (optional; prevents zero-width ranges)
        if min_metric == max_metric:
            delta = max(1, abs(min_metric) * 0.1)
            min_metric = min_metric - delta
            max_metric = max_metric + delta

        if min_prop == max_prop:
            delta = 1 if isinstance(min_prop, (int, float)) else 0
            min_prop = max(0, min_prop - delta)
            max_prop = max_prop + delta

        constraints = [
            CoreoBasicConstraint("metric", metric, ">=", min_metric),
            CoreoBasicConstraint("metric", metric, "<=", max_metric),
            CoreoBasicConstraint("prop",   prop,   ">=", min_prop),
            CoreoBasicConstraint("prop",   prop,   "<=", max_prop),
        ]

        # create the request: initial_pop_files are file paths for initial population
        request_id = self.generate_request(name, function, constraints, [], [], initial_pop_files, write_json, request_directory,request_type)
        logger.info(f"[INFO] Random request generated (id={request_id}) for metric '{metric}', prop '{prop}' using {k} sampled files.")
        return request_id

    def generate_request(self, name,function, metric_constraints, prop_constraints, initial_pop = [], initial_pop_files = [], write_json = False,request_directory=None, request_type = None):
        logger.info(f"Request type is {request_type}")
        function_names = []
        for file_path in initial_pop_files:
            with open(file_path, "r") as f:
                inputs = f.read()
                #print(inputs)
                initial_pop.append(inputs)
        request = CoreoRequest(name, function, metric_constraints + prop_constraints, initial_pop, initial_pop_files, request_type=request_type)

        self.requests.append(request)
        if write_json:
            request_id = random.randint(0,10000)
            jsonfile_path = os.path.join(request_directory,f"request_{request_id}.json")
            request.write_json(jsonfile_path)
            return request_id

    ###
    #
    # Plotting Methods
    #
    ###

        # Create a scatterplot of the metric vs. the feature for each function/summary.
    # Coreografa note: This can be the basis for the first set of scatterplots in the poster.
    
    def plot_metric_vs_feature(self, metric, feature, remove_outliers = False,output_dir=None):
        os.makedirs(output_dir, exist_ok=True)
        for name in self.names:
            short_name = os.path.splitext(os.path.basename(name))[0]
            label_name = short_name.replace("_summary", "")
            logger.info(f"Plotting '{metric}' vs '{feature}' for '{name}':")
            s = self.storage.get_metric_ordered_by_feature(name, metric, feature, remove_outliers)
            x_s = [x[1] for x in s]
            y_s = [x[0] for x in s]
            plt.figure()
            plt.scatter(x_s, y_s, label = short_name)
            plt.xlabel(feature)
            plt.ylabel(metric)
            plt.legend()
            filename=f"{metric}_vs_{feature}_{label_name}.png".replace(" ", "_")
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath)
            logger.info(f"Saved plot to {filepath}")
            plt.close()
            #plt.show()
    
    # 
    '''
    def plot_metric_vs_feature(self, metric, feature, remove_outliers=False, output_dir=None):

        rows = []
        for name in self.summaries:
            for summary in self.summaries[name]:
                row = {
                    "function_name": summary.fn_input_info.function_name,
                    "input_id": summary.fn_input_info.input_id
                    
                }
                # add metrics
                for m in summary.metrics:
                    row[m.name] = float(m.value)
                # add features
                for f in summary.features:
                    row[f.name] = float(f.value)
                rows.append(row)

        df = pd.DataFrame(rows)
        #df = self.df.copy()

        # Remove outliers if requested
        if remove_outliers:
            df = self.remove_outliers(df, metric)

        plt.figure(figsize=(8, 6))

        # Group by function_name
        if "function_name" not in df.columns:
            raise ValueError("Column 'function_name' not found in summary CSV.")

        groups = df.groupby("function_name")

        # Plot each function separately
        for func, grp in groups:
            plt.scatter(
                grp[feature],
                grp[metric],
                label=func,
                alpha=0.7,
                s=25
            )

        plt.xlabel(feature)
        plt.ylabel(metric)
        plt.title(f"{metric} vs {feature} grouped by function_name")
        plt.legend(title="Function")

        # Save figure if directory is given
        if output_dir is not None:
            os.makedirs(output_dir, exist_ok=True)
            fname = f"{metric}_vs_{feature}.png"
            plt.savefig(os.path.join(output_dir, fname), dpi=300, bbox_inches='tight')

        plt.close()
    '''

    def fit_model_for_metric_and_feature(self, metric, feature, remove_outliers = False,output_dir=None):
        os.makedirs(output_dir, exist_ok=True)
        for name in self.names:
            short_name = os.path.splitext(os.path.basename(name))[0]
            label_name = short_name.replace("_summary", "")
            data = self.storage.get_metric_ordered_by_feature(name, metric, feature, remove_outliers)
            
            feature_vals = [x[1] for x in data]
            metric_vals = [x[0] for x in data]

            # are there any NaNs?
            if any([math.isnan(x) for x in metric_vals]):
                logger.info(f"NaNs found in '{name}' for feature '{feature}' and metric '{metric}'.")
                continue
            # any negative values?
            if any([x < 0 for x in metric_vals]):
                logger.info(f"Negative values found in '{name}' for feature '{feature}' and metric '{metric}'.")
                continue
            # any zeroes in the metrics?
            if any([x == 0 for x in metric_vals]):
                logger.info(f"Zeroes found in '{name}' for feature '{feature}' and metric '{metric}'.")
                continue
            # any zeroes in the feature?
            if any([x == 0 for x in feature_vals]):
                logger.info(f"Zeroes found in '{name}' for feature '{feature}' and metric '{metric}'.")
                # remove them, and corresponding metrics
                metric_vals = [metric_vals[i] for i in range(len(metric_vals)) if feature_vals[i] != 0]
                feature_vals = [x for x in feature_vals if x != 0]
            try:
                best, others = big_o.infer_big_o_class(feature_vals, metric_vals)
                logger.info(f"For '{name}', feature '{feature}' and metric '{metric}' the best fit is:")
                logger.info(big_o.reports.big_o_report(best, others))

                # ... and plot it
                plt.figure()
                plt.scatter(feature_vals, metric_vals, label = short_name)
                plt.plot(feature_vals, best.compute(np.asanyarray(feature_vals)), label = f"{name} fit")
                plt.title(f"'{metric}' vs '{feature}', incl. lines of best fit")
                plt.xlabel(feature)
                plt.ylabel(metric)
                plt.legend()
                filename=f"fitmodel_{metric}_vs_{feature}_{label_name}.png".replace(" ", "_")
                filepath = os.path.join(output_dir, filename)
                plt.savefig(filepath)
                logger.info(f"Saved fit model plot to {filepath}")
                plt.close()
                #plt.show()
            except Exception as e:
                logger.error(f"[ERROR] Could not fit model for '{name}': {e}")
                continue
        
    # subset is a list of indices to focus on, if any
    def fit_model_for_metric_and_features(self, metric, features, interaction = False, remove_outliers = False,output_dir=None):
        os.makedirs(output_dir, exist_ok=True)
        complexity_classes = [
            "Linear",
            "Quadratic",
            "Cubic",
            "Logarithmic",
            "Exponential",
            "LogLinear"
            # There's more, but these are probably the most common
            # "Constant"
            # "Polynomial"
        ]  

        def build_fun_for_complexity_class(complexity_class):
            if complexity_class == "Linear":
                return lambda x: x
            elif complexity_class == "Quadratic":
                return lambda x: x ** 2
            elif complexity_class == "Cubic":
                return lambda x: x ** 3
            elif complexity_class == "Logarithmic":
                return lambda x: math.log(x)
            elif complexity_class == "Exponential":
                return lambda x: math.exp(x)
            elif complexity_class == "LogLinear":
                return lambda x: x * math.log(x)
            else:
                return lambda x: x
        '''
        def build_complete_fun_for_complexity_classes(complexity_classes, coefficients):
            # The complexity classes is a tuple of three complexity classes.
            constant = coefficients[0]
            fn_ft1 = build_fun_for_complexity_class(complexity_classes[0])
            fn_ft2 = build_fun_for_complexity_class(complexity_classes[1])
            # fn_int = build_fun_for_complexity_class(complexity_classes[2])

            return lambda x, y : constant + coefficients[1]*fn_ft1(x) + coefficients[2]*fn_ft2(y) 
        #+ coefficients[3]*fn_ft1(x)*fn_ft2(y)
        '''
        def build_complete_fun_for_complexity_classes(complexity_classes, coefficients):
            constant = coefficients[0]

            # Always build f1
            fn_ft1 = build_fun_for_complexity_class(complexity_classes[0])

            # CASE 1: Only 1 feature → produce 1-variable model
            if len(complexity_classes) == 1 or len(coefficients) == 2:
                return lambda x, y=None: constant + coefficients[1] * fn_ft1(x)

            # CASE 2: Two features → standard model
            fn_ft2 = build_fun_for_complexity_class(complexity_classes[1])
            return lambda x, y: constant + coefficients[1] * fn_ft1(x) + coefficients[2] * fn_ft2(y)

        def transform_feature_vals(feature_vals, complexity_class):
            fn_for_class = build_fun_for_complexity_class(complexity_class)
            return np.array([fn_for_class(x) for x in feature_vals])

        # If there are interaction terms...
        interaction_terms = []
        if interaction:
            for i in range(len(features)):
                for j in range(i + 1, len(features)):
                    interaction_terms.append((features[i], features[j]))

        model_fit_results = dict()
        # Idea: we are going to try the various complexity classes _for each feature_.
        # We will then compare the R^2 values and the coefficients.
        for name in self.names:
            model_fit_results[name] = dict()
            # Make all combinations of complexity classes of each feature.
            # There will be |complexity_classes|^|features| combinations.
            # They shall be tuples (complexity_class, ..., complexity_class) 
            # and the length of the tuple will be the number of features.
            # We will then fit the model for each combination.
            # 
            # (1) Make |complexity_classes|^|features| combinations.
            complexity_combos = []
            for i in range(len(complexity_classes) ** (len(features) + len(interaction_terms))):
                # This is total witchcraft.
                complexity_combos.append(tuple([complexity_classes[i // (len(complexity_classes) ** j) % len(complexity_classes)] for j in range(len(features) + len(interaction_terms))]))

            for combo in complexity_combos:
                model_fit_results[name][combo] = dict()

        aucs = dict()
        best_complexity_combos = dict()

        # extract the data and model
        for name in self.names:
            short_name = os.path.splitext(os.path.basename(name))[0]
            label_name = short_name.replace("_summary", "")
            # This is going to run once per name, i.e., once per summary file.
            # We should extract the data for the metric and the features.
            metric_vals = self.storage.get_metric(name, metric)
            feature_vals = []
            for feature in features:
                these_features = self.storage.get_feature(name, feature)
                feature_vals.append(these_features)
            #to avoid crashing if metrics and features are None
            if len(metric_vals) == 0 or any(len(f) == 0 for f in feature_vals):
                logger.warning(f"[WARNING] Skipping '{name}' — empty metric or feature values.")
                return
            
            # --- CONSTANT METRIC CHECK ---
            if all(v == metric_vals[0] for v in metric_vals):
                logger.warning(f"[WARNING] Metric '{metric}' for '{label_name}' is constant ({metric_vals[0]}).")
                logger.warning("[WARNING] Skipping model fitting, AUC, and plots for this metric.")
                aucs[name] = None 
                continue

            #Skip multi-feature fitting when only one feature is present
            if len(feature_vals) < 2:
                logger.info(f"[INFO] Only one feature available for '{label_name}' — skipping multi-feature model fitting.")
                # We already produced a plot in fit_model_for_metric_and_feature()
                return
            
            if remove_outliers:
                z_scores = ss.zscore(metric_vals)

            # Sanitize the data.
            indices_to_remove = []
            for i in range(len(metric_vals)):
                #print("Loop 1")
                metric_nan = math.isnan(metric_vals[i])
                features_nan = any([math.isnan(x[i]) for x in feature_vals])
                metric_zero = metric_vals[i] == 0
                features_zero = any([x[i] == 0 for x in feature_vals])
                metric_neg = metric_vals[i] < 0
                features_neg = any([x[i] < 0 for x in feature_vals])
                if remove_outliers and abs(z_scores[i]) > 3:
                    indices_to_remove.append(i)
                elif metric_nan or features_nan or metric_zero or features_zero or metric_neg or features_neg:
                    indices_to_remove.append(i)

            # Remove the indices.
            metric_vals = [metric_vals[i] for i in range(len(metric_vals)) if i not in indices_to_remove]
            for i in range(len(feature_vals)):
                #print("Loop 2")
                feature_vals[i] = [x for j, x in enumerate(feature_vals[i]) if j not in indices_to_remove]

            # We're trying to use statsmodels OLS, so the feature_vals array should be transposed.
            feature_vals = np.array(feature_vals).T

            # Let's also assume independence of the feature vals for now, and other assumptions.

            # Now, we want, for each combination of complexity classes, to fit the model.
            this_model_fit_results = model_fit_results[name]
            complexity_combos = list(this_model_fit_results.keys())
            for combo in complexity_combos:
                #print("Loop 3")
                # Based on the complexity class combination, we need to 
                # transform the feature_vals.
                # Make a copy of the feature_vals.
                feature_vals_this_combo = np.copy(feature_vals)
                try:
                    for i in range(len(features)):
                        the_combo = combo[i]
                        feature_vals_this_combo[:, i] = transform_feature_vals(feature_vals_this_combo[:, i], the_combo)
                except OverflowError:
                    logger.error(f"[ERROR] Overflow error for '{name}' and combo '{combo}'.")
                    this_model_fit_results[combo] = (-1, None)
                    continue

                # If there are interaction terms, we will compute them here.
                for interaction_term in interaction_terms:
                    #print("Loop 4")
                    feature_1 = features.index(interaction_term[0])
                    feature_2 = features.index(interaction_term[1])
                    interaction_vals = feature_vals_this_combo[:, feature_1] * feature_vals_this_combo[:, feature_2]
                    feature_vals_this_combo = np.column_stack((feature_vals_this_combo, interaction_vals))

                # Let's fit the model.
                # They suggest adding a constant to the feature_vals.
                feature_vals_this_combo = sm.add_constant(feature_vals_this_combo)
                model = sm.OLS(metric_vals, feature_vals_this_combo).fit()
                #print("DEBUG: metric vals before loop", metric_vals)
                #print("DEBUG: feature vals before loop", feature_vals_this_combo)
                
                # Collect R^2 and coefficients.
                r_squared = model.rsquared
                #print("DEBUG: rsquared before loop", r_squared)
                coefficients = model.params

                this_model_fit_results[combo] = (r_squared, coefficients)

            # can't reload b/c we removed some stuff above.
            # metric_vals = self.storage.get_metric(name, metric)
            
            logger.info(f"Model fit results for '{name}':")
            best_r_squared = -1
            best_combo = None
            best_coeffs = None
            for combo in complexity_combos:
                #print("Loop 5")
                r_squared, coefficients = model_fit_results[name][combo]
                #print("DEBUGGING..r squared ",r_squared)
                #print("DEBUGGING..coefficients ", coefficients)
                #to avoid crashing the function if there are no coefficients
                if coefficients is None:
                    continue
                if r_squared > best_r_squared:
                    best_r_squared = r_squared
                    best_combo = combo
                    best_coeffs = coefficients
            #to avoid crashing the function if there are no best_coeffs
            if best_coeffs is None:
                logger.warning(f"[WARNING] Could not find a valid model fit for '{name}'.Skipping.")
                continue

            logger.info(f"Best fit for '{name}':")
            logger.info(f"R^2: {best_r_squared}")
            logger.info(f"Intercept: {best_coeffs[0]}")
            for i in range(len(features)):
                #print("Loop 6")
                #wrap with if and else
                if (i+1) < len(best_coeffs):
                    logger.info(f"Feature '{features[i]}' has complexity class '{best_combo[i]}'.")
                    logger.info(f"The coefficient for this feature is {best_coeffs[i + 1]}.")
                else:
                    logger.warning(f"[WARNING] Missing coefficient for feature '{features[i]}'. Only {len(best_coeffs)} coefficients found.")
            if interaction:
                for i in range(len(interaction_terms)):
                    logger.info(f"Interaction term '{interaction_terms[i][0]} * {interaction_terms[i][1]}' has complexity class '{best_combo[len(features) + i]}'.")
                    logger.info(f"The coefficient for this interaction term is {best_coeffs[len(features) + i + 1]}")

            best_complexity_combos[name] = best_combo

            # Compute the area under curve for the best fit.
            # Assume two features and interaction.
            fn_for_model = build_complete_fun_for_complexity_classes(best_combo, best_coeffs)

            # Compute the area under the curve for fn_for_model.
            # (Using scipy.integrate.dblquad since we are assuming two features.)
            # We will assume the range of the first feature is [0, 200] 
            # and the range of the second feature is [0, 1].
            # Also, added a max(0, ...) to avoid negative values, since they don't make sense here I don't think.
            area_under_curve = si.dblquad(lambda x, y : max(fn_for_model(y, x), 0), 0, 200, lambda x : 0, lambda x : 1)

            # Print the area under the curve.
            logger.info(f"Area under curve for '{name}': {area_under_curve}")

            aucs[name] = area_under_curve

            # We will plot the best fit.
            # z : metric value and also the predicted metric value
            # x : feature 1
            # y : feature 2

            # Compute best fit.
            fitted_metric_vals = []
            constant = best_coeffs[0]
            feature_values_1 = feature_vals[:, 0]
            feature_values_2 = feature_vals[:, 1] 

            transformed_feature_values_1 = transform_feature_vals(feature_values_1, best_combo[0])
            transformed_feature_values_2 = transform_feature_vals(feature_values_2, best_combo[1])
            for i in range(len(metric_vals)):
                fitted_metric_vals.append(constant + best_coeffs[1] * transformed_feature_values_1[i] + best_coeffs[2] * transformed_feature_values_2[i])

            if interaction:
                # Assuming again only two features.
                interaction_vals = transformed_feature_values_1 * transformed_feature_values_2
                for i in range(len(metric_vals)):
                    # Also not right, depends on the complexity class of the interaction term.
                    fitted_metric_vals[i] += best_coeffs[3] * interaction_vals[i]

            fig = plt.figure()
            ax = fig.add_subplot(111, projection='3d')
            ax.scatter(feature_values_1, feature_values_2, metric_vals, label = "actual")
            ax.scatter(feature_values_1, feature_values_2, fitted_metric_vals, label = "fitted")
            # can we get the fitted values as ameshgrid?
            # X, Y = np.meshgrid(feature_values_1, feature_values_2)
            # Z = # ???
            # ax.plot_surface(X, Y, Z, alpha = 0.5)
            ax.set_xlabel(features[0])
            ax.set_ylabel(features[1])
            ax.set_zlabel(metric)
            # title
            ax.set_title(f"Best fit for '{short_name}'")
            # dump it
            # only_basename_no_ext = os.path.splitext(name)[0]
            # pickle.dump(ax, open(f"{only_basename_no_ext}_{metric}_{features[0]}_{features[1]}_3d_model.p", "wb"))
            plt.legend()
            filename=f"3d_{metric}_vs_{feature}_{label_name}.png".replace(" ", "_")
            filepath = os.path.join(output_dir, filename)
            plt.savefig(filepath)
            logger.info(f"Saved 3d fit model plot to {filepath}")
            plt.close()

        lowest_auc = -1
        lowest_auc_name = "default"
        for name in self.names:
            if aucs.get(name) is None:
                continue
            if aucs[name][0] < lowest_auc or lowest_auc == -1:
                lowest_auc = aucs[name][0]
                lowest_auc_name = name

        logger.info("----------------------------------------------------------------------")
        logger.info(f"Lowest AUC for {metric}: {lowest_auc} for '{lowest_auc_name}'.")
        logger.info("======================================================================")
    
    def plot_3d_interactive(self, metric, propx, propy, output_dir=None):
        import plotly.graph_objects as go
        os.makedirs(output_dir, exist_ok=True)

        fig = go.Figure()

        for name in self.names:
            metric_vals, propx_vals = self.storage.get_metric_and_feature(name, metric, propx)
            _, propy_vals = self.storage.get_metric_and_feature(name, metric, propy)

            short_name = os.path.splitext(os.path.basename(name))[0]

            fig.add_trace(go.Scatter3d(
                x=propx_vals,
                y=propy_vals,
                z=metric_vals,
                mode="markers",
                name=short_name,
                marker=dict(size=3)
            ))

        fig.update_layout(
            scene=dict(
                xaxis_title=propx,
                yaxis_title=propy,
                zaxis_title=metric,
            ),
            margin=dict(l=0, r=0, b=0, t=30),
            title=f"{metric} vs {propx} and {propy}"
        )

        filename = f"3dplot_{metric}_vs_{propx}_and_{propy}.html".replace(" ", "_")
        fig.write_html(os.path.join(output_dir, filename))

