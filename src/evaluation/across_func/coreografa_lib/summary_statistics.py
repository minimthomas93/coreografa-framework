import os
import sys
import pandas as pd


def summarize(csv_path, out_dir):
    df = pd.read_csv(csv_path)
    os.makedirs(out_dir, exist_ok=True)

    # -------------------------------
    # 1) Compact performance table
    # -------------------------------
    results = []

    for fn, g in df.groupby("function_name"):
        runtime_ms = pd.to_numeric(g["runtime_ns"], errors="coerce") / 1_000_000  # ns → ms
        memory = pd.to_numeric(g["memory_peak"], errors="coerce")

        row = {
            "System": fn,
            "Inputs": int(runtime_ms.dropna().shape[0]),

            "Mean Runtime (ms)": runtime_ms.mean(),
            "Median Runtime (ms)": runtime_ms.median(),
            "Std Dev Runtime (ms)": runtime_ms.std(),
            "P95 Runtime (ms)": runtime_ms.quantile(0.95),

            "Mean Memory": memory.mean(),
            "Median Memory": memory.median(),
            "P95 Memory": memory.quantile(0.95)
        }
        results.append(row)

    perf_table = pd.DataFrame(results)

    # round numbers for readability
    perf_table = perf_table.round({
        "Mean Runtime (ms)": 3,
        "Median Runtime (ms)": 3,
        "Std Dev Runtime (ms)": 3,
        "P95 Runtime (ms)": 3,
        "Mean Memory": 1,
        "Median Memory": 1,
        "P95 Memory": 1
    })

    perf_out = os.path.join(out_dir, "performance_summary.csv")
    perf_table.to_csv(perf_out, index=False)

    print("Saved:", perf_out)
    print("\nPreview (performance_summary.csv):\n")
    print(perf_table)

    # -------------------------------
    # 2) Min/Max table (runtime, memory, XML properties)
    # -------------------------------
    # Map your desired labels to CSV column names + min/max operation.
    # NOTE: Update column names below to match YOUR summary CSV headers.
    minmax_specs = [
        ("Min. Run time", "runtime_ns", "min"),
        ("Max. Run time", "runtime_ns", "max"),
        ("Min. Memory peak", "memory_peak", "min"),
        ("Max. Memory peak", "memory_peak", "max"),
        ("Min. Paragraph text count", "count_para_text", "min"),
        ("Max. Paragraph text count", "count_para_text", "max"),
        ("Min. Image tag count", "count_img_tag", "min"),
        ("Max. Image tag count", "count_img_tag", "max"),
    ]

    systems = list(df["function_name"].dropna().unique())
    rows = []

    for label, col, op in minmax_specs:
        row = {"Metric": label}

        for sys_name in systems:
            g = df[df["function_name"] == sys_name]

            if col not in g.columns:
                # Keep empty if the property doesn't exist in this subject's CSV
                row[sys_name] = ""
                continue

            series = pd.to_numeric(g[col], errors="coerce").dropna()
            if series.empty:
                row[sys_name] = ""
            else:
                row[sys_name] = series.min() if op == "min" else series.max()

        rows.append(row)

    minmax_table = pd.DataFrame(rows)

    minmax_out = os.path.join(out_dir, "minmax_summary.csv")
    minmax_table.to_csv(minmax_out, index=False)

    print("\nSaved:", minmax_out)
    print("\nPreview (minmax_summary.csv):\n")
    print(minmax_table)


if __name__ == "__main__":
    csv_path = sys.argv[1]
    out_dir = sys.argv[2]
    summarize(csv_path, out_dir)