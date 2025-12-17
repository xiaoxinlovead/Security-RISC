#!/usr/bin/env python3
import pandas as pd
import numpy as np
import os

DEFAULT_THRESHOLD = 23

def convert_log_to_csv(logfile="key_leak.log"):
    csvfile = logfile + ".csv"
    if not os.path.exists(logfile):
        raise FileNotFoundError(f"{logfile} not found")
    with open(logfile, "r") as f_in, open(csvfile, "w") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 3:
                continue
            f_out.write(",".join(parts[:3]) + "\n")
    return csvfile


def evaluate_threshold(df, threshold):
    df_aggr = pd.DataFrame()
    df_aggr["cycle-min"] = df.groupby("idx")["cycle"].min()
    df_aggr["cycle-median"] = df.groupby("idx")["cycle"].median()
    df_aggr["cycle-mean"] = df.groupby("idx")["cycle"].mean()
    df_aggr["realbit"] = df.groupby("idx")["realbit"].min()
    df_aggr["prediction"] = np.where(df_aggr["cycle-min"] < threshold, 1, 0)
  #  df_aggr["prediction"] = np.where(df_aggr["cycle-mean"] < threshold, 1, 0)
 #   df_aggr["prediction"] = np.where(df_aggr["cycle-median"] < threshold, 1, 0)
    return np.sum(df_aggr["realbit"] == df_aggr["prediction"])



def scan_threshold_range(csvfile):
    df = pd.read_csv(csvfile, names=["idx", "realbit", "cycle"])

    df["cycle"] = pd.to_numeric(df["cycle"], errors="coerce")
    df["realbit"] = pd.to_numeric(df["realbit"], errors="coerce")
    df["idx"] = pd.to_numeric(df["idx"], errors="coerce")

    LOW = 1
    HIGH = 30000

    best_t = None
    best_correct = -1

    for t in range(LOW, HIGH + 1):
        corr = evaluate_threshold(df, t)
        if corr > best_correct:
            best_correct = corr
            best_t = t

    print("\n========== AUTO THRESHOLD SEARCH ==========")
    print(f"Search range: {LOW} → {HIGH}")
    print(f"Best threshold: {best_t}")
    print(f"Max correct leaked bits: {best_correct}")
    print("===========================================\n")

    return best_t, best_correct


# -------------------------------------------------------------------
# 原有分析函数（未修改）
# -------------------------------------------------------------------
def analyze_csv(csvfile, threshold=DEFAULT_THRESHOLD):
    df = pd.read_csv(csvfile, names=["idx", "realbit", "cycle"])

    df["cycle"] = pd.to_numeric(df["cycle"], errors="coerce")
    df["realbit"] = pd.to_numeric(df["realbit"], errors="coerce")
    df["idx"] = pd.to_numeric(df["idx"], errors="coerce")

    df_aggr = pd.DataFrame()
    df_aggr["cycle-min"] = df.groupby("idx")["cycle"].min()
    df_aggr["cycle-median"] = df.groupby("idx")["cycle"].median()
    df_aggr["cycle-mean"] = df.groupby("idx")["cycle"].mean()
    df_aggr["prediction"] = np.where(df_aggr["cycle-min"] < threshold, 1, 0)
 #   df_aggr["prediction"] = np.where(df_aggr["cycle-mean"] < threshold, 1, 0)
#    df_aggr["prediction"] = np.where(df_aggr["cycle-median"] < threshold, 1, 0)

    df_aggr["realbit"] = df.groupby("idx")["realbit"].min()

    all_cycles_series = df.groupby("idx")["cycle"].apply(list)
    df_aggr["all_cycles"] = all_cycles_series

    result_table = df_aggr.reset_index()[[
        "idx", "realbit", "prediction", "all_cycles", "cycle-min"
    ]]

    print("\n=== Detailed Result with all cycles per idx ===")
    print(result_table.to_string(index=False))
    print("=================================================\n")

    correct_bits = np.sum(df_aggr["realbit"] == df_aggr["prediction"])
    print("Median cycle (realbit=1):", df_aggr.loc[df_aggr["realbit"]==1,"cycle-mean"].median())
    print("Median cycle (realbit=0):", df_aggr.loc[df_aggr["realbit"]==0,"cycle-mean"].median())
    print("Correct leaked bits:", correct_bits)
    print("Threshold used:", threshold)

    return correct_bits


# -------------------------------------------------------------------
# 主入口
# -------------------------------------------------------------------
def main():
    logfile = "key_leak.log"
    csvfile = convert_log_to_csv(logfile)
    print(f"[OK] Converted log to CSV: {csvfile}")

    analyze_csv(csvfile)


    scan_threshold_range(csvfile)


if __name__ == "__main__":
    main()

