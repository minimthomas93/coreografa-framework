import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_metric_vs_property(summary_csv, metric, property_name, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(summary_csv)

    plt.figure(figsize=(7,5))

    for func_name, group in df.groupby("function_name"):
        x = group[property_name]
        y = group[metric]

        plt.scatter(
            x,
            y,
            label=func_name,
            alpha=0.7,
            s=25
        )

    plt.xlabel(property_name)
    plt.ylabel(metric)
    plt.title(f"{metric} vs {property_name}")
    plt.legend()
    plt.yscale("log")  # Log scale for better visibility of differences

    filename = f"{metric}_vs_{property_name}.png"
    plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches="tight")
    plt.close()


def generate_plots(summary_csv, property_name, output_dir):

    plot_metric_vs_property(
        summary_csv,
        "runtime_ns",
        property_name,
        output_dir
    )

    plot_metric_vs_property(
        summary_csv,
        "memory_peak",
        property_name,
        output_dir
    )


if __name__ == "__main__":
    summary_csv = "evaluation/across_func/coreografa_lib/main_redos_summary.csv"
    property_name = "count_a"
    output_dir = "evaluation/across_func/eval_results/summary_figures/regex_redos"

    generate_plots(summary_csv, property_name, output_dir)