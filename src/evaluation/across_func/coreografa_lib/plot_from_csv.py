
# def plot_from_csv(csv_file, figure_dir):
#     summary_file = csv_file
#     split_summary_dir = os.path.join(figure_dir, "split_summaries")
#     os.makedirs(split_summary_dir, exist_ok=True)

#     coreografa = Coreografa(functions_to_execute=[], custom_properties=[],non_terminals=[],converter_func=None)

#     for old in glob.glob(os.path.join(split_summary_dir, "*_summary.csv")):
#         os.remove(old)
#     coreografa.split_summary_by_function(summary_file,split_summary_dir)
#     final_split_files = glob.glob(os.path.join(split_summary_dir, "*_summary.csv"))

#     analyzer = Analyzer()

#     analyzer.read_csvs(
#         final_split_files,
#         metrics=["runtime_ns", "memory_peak"],
#         # input_features=[
#         #     "count_tables",
#         #     "count_column_name"
#         # ],
#         ignore=["memory_after"]
#     )

#     for metric in analyzer.metrics:
#         for propx, propy in combinations(analyzer.features, 2):
#             analyzer.plot_3d(
#                 metric,
#                 propx,
#                 propy,
#                 output_dir=figure_dir
#             )

# if __name__ == "__main__":
#     csv_path = sys.argv[1]
#     output_dir = sys.argv[2]

#     os.makedirs(output_dir, exist_ok=True)
#     plot_from_csv(csv_path, output_dir)


from .analyzer import Analyzer
from itertools import combinations
import sys
import os
import glob
from .fuzzer import Coreografa

def plot_from_csv(csv_file, figure_dir):
    summary_file = csv_file
    split_summary_dir = os.path.join(figure_dir, "split_summaries")
    os.makedirs(split_summary_dir, exist_ok=True)

    coreografa = Coreografa(functions_to_execute=[], custom_properties=[], non_terminals=[], converter_func=None)

    # Clean old split summaries
    for old in glob.glob(os.path.join(split_summary_dir, "*_summary.csv")):
        os.remove(old)

    # Split per function
    coreografa.split_summary_by_function(summary_file, split_summary_dir)
    final_split_files = glob.glob(os.path.join(split_summary_dir, "*_summary.csv"))

    analyzer = Analyzer()
    analyzer.read_csvs(
        final_split_files,
        metrics=["runtime_ns", "memory_peak"],
        ignore=["memory_after"]
    )

    # Make interactive plots
    for metric in analyzer.metrics:
        for propx, propy in combinations(analyzer.features, 2):
            analyzer.plot_3d_interactive(metric, propx, propy, output_dir=figure_dir)

if __name__ == "__main__":
    csv_path = sys.argv[1]
    output_dir = sys.argv[2]

    os.makedirs(output_dir, exist_ok=True)
    plot_from_csv(csv_path, output_dir)
    