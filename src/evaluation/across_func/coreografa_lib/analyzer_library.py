from .logger import get_logger
logger = get_logger(__name__)
import os
import scipy.stats as ss
import re

class InfoStorage:
    def __init__(self, metric_names, feature_names, summary_names, inputs_dir = None) -> None:
        self.metric_names = metric_names
        self.feature_names = feature_names
        self.summary_names = summary_names

        self.metrics = dict()
        self.features = dict()

        if inputs_dir is not None:
            # pick only original input files like input_1, input_2, etc.
            self.inputs = [
                os.path.join(root, file)
                for root, dirs, files in os.walk(inputs_dir)
                for file in files
                #if re.match(r'^input_\d+(\.txt)?$', file)
                if re.match(r'^input_[A-Za-z0-9_]+(\.txt)?$', file)
                #if file.startswith("input_")
            ]

        # initialize metrics and features
        for summary_name in summary_names:
            self.metrics[summary_name] = {m: [] for m in metric_names}
            self.features[summary_name] = {f: [] for f in feature_names}

    '''
        if inputs_dir is not None:
            # get all the file names in input_dir and save them
            self.inputs = []
            for root, dirs, files in os.walk(inputs_dir):
                for file in files:
                    self.inputs.append(os.path.join(root, file))

        for summary_name in summary_names:
            self.metrics[summary_name] = dict()
            self.features[summary_name] = dict()
            for metric_name in metric_names:
                self.metrics[summary_name][metric_name] = []
            for feature_name in feature_names:
                self.features[summary_name][feature_name] = []
        '''


    def build_storage(self, pma):
        for summary_name in self.summary_names:
            for summary in pma.summaries[summary_name]:
                for metric_name in self.metric_names:
                    self.metrics[summary_name][metric_name].append(summary.get_metric(metric_name).value)
                for feature_name in self.feature_names:
                    self.features[summary_name][feature_name].append(summary.get_feature(feature_name).value)

    def print_metrics(self):
        for summary_name in self.summary_names:
            logger.info(f"Metrics for '{summary_name}':")
            for metric_name in self.metric_names:
                logger.info(f"{metric_name}: {self.metrics[summary_name][metric_name]}")

    def print_features(self):
        for summary_name in self.summary_names:
            logger.info(f"Features for '{summary_name}':")
            for feature_name in self.feature_names:
                logger.info(f"{feature_name}: {self.features[summary_name][feature_name]}")

    def get_metric_and_feature(self, summary_name, metric_name, feature_name):
        m_vals = self.metrics[summary_name][metric_name]
        f_vals = self.features[summary_name][feature_name]
        return m_vals, f_vals

    def get_metric(self, summary_name, metric_name):
        return self.metrics[summary_name][metric_name]
    
    def get_feature(self, summary_name, feature_name):
        return self.features[summary_name][feature_name]

    def get_metric_ordered_by_feature(self, summary_name, metric_name, feature_name, remove_outliers = False):
        m_vals = self.metrics[summary_name][metric_name]
        f_vals = self.features[summary_name][feature_name]
        res = sorted(zip(m_vals, f_vals), key = lambda x: x[1])
        if remove_outliers:
            z_scores = ss.zscore([x[0] for x in res])
            res = [x for i, x in enumerate(res) if abs(z_scores[i]) < 3]
        return res
    
    def get_inputs_ordered_by_metric_and_feature(self, summary_name, metric_name, feature_name, remove_outliers = False):
        m_vals = self.metrics[summary_name][metric_name]
        f_vals = self.features[summary_name][feature_name]
        inputs = self.inputs.copy()
        res = sorted(zip(self.inputs, m_vals, f_vals), key = lambda x: x[2])
        if remove_outliers:
            z_scores = ss.zscore([x[1] for x in res])
            res = [x for i, x in enumerate(res) if abs(z_scores[i]) < 3]
        return res
    
    def normalize_feature_wrt(self, target):
        remove_these = []
        for summary_name in self.summary_names:
            for feature_name in self.feature_names:
                if not feature_name == target:
                    for i in range(0, len(self.features[summary_name][feature_name])):
                        target_val = self.features[summary_name][target][i]
                        if target_val == 0:
                            remove_these.append(i)
                            continue
                        self.features[summary_name][feature_name][i] = self.features[summary_name][feature_name][i] / target_val
                        if self.features[summary_name][feature_name][i] > 1:
                            logger.warning("[WARNING]: feature value is greater than 1.")
        # remove all the ones that are zero
        for summary_name in self.summary_names:
            for feature_name in self.feature_names:
                self.features[summary_name][feature_name] = [x for i, x in enumerate(self.features[summary_name][feature_name]) if i not in remove_these]
            for metric_name in self.metric_names:
                self.metrics[summary_name][metric_name] = [x for i, x in enumerate(self.metrics[summary_name][metric_name]) if i not in remove_these]

class FunctionInputInfo:
    def __init__(self, function_name, input_id = -1):
        self.function_name = function_name
        #self.input_id = int(input_id)
        self.input_id = input_id

    def __str__(self):
        return "FunctionInputInfo{ function_name: " + self.function_name + ", input_id: " + str(self.input_id) + "}"

class Metric:
    def __init__(self, name, value):
        self.name = name
        self.value = float(value)

    def __str__(self):
        return "Metric{ name: " + self.name + ", values: " + str(self.value) + "}"

class Feature:
    def __init__(self, name, value):
        self.name = name
        self.value = float(value)

    def __str__(self):
        return "Feature{ name: " + self.name + ", value: " + str(self.value) + "}"

class FunctionRunSummary:
    def __init__(self, functionInputInfo, metrics = [], features = []):
        self.functionInputInfo = functionInputInfo
        self.metrics = metrics
        self.features = features
        
    # default print
    def __str__(self):
        metric_strs = ", ".join([str(metric) for metric in self.metrics])
        feature_strs = ", ".join([str(feature) for feature in self.features])
        return "FunctionRunSummary{ functionInputInfo: " + str(self.functionInputInfo) + ", metrics: " + metric_strs + ", features: " + feature_strs + "}"
    
    def get_metric(self, name):
        for metric in self.metrics:
            if metric.name == name:
                return metric
        return None
    
    def get_feature(self, name):
        for feature in self.features:
            if feature.name == name:
                return feature
        return None

    # take in input features
    def set_features(self, features):
        self.features = features