import os
import pandas as pd
from datetime import time

FILE_1 = "D:\\uid03859\\Desktop\\python\\doc3_timestamp_to_hmsms.txt"

# 输出文件放到一个目录里（可改）
OUT_DIR = r"D:\uid03859\Desktop\python\split_ranges"
os.makedirs(OUT_DIR, exist_ok=True)

# 7 个绝对时间段（HH:MM:SS）
RANGES = [
    ("03_17_25_to_03_21_21", time(3, 17, 25, 0), time(3, 21, 21, 0)),
    ("03_21_47_to_03_22_30", time(3, 21, 47, 0), time(3, 22, 30, 0)),
    ("03_22_30_to_03_23_17", time(3, 22, 30, 0), time(3, 23, 17, 0)),
    ("03_25_12_to_03_25_56", time(3, 25, 12, 0), time(3, 25, 56, 0)),
    ("03_26_00_to_03_29_55", time(3, 26, 0, 0),  time(3, 29, 55, 0)),
    ("03_32_35_to_03_35_21", time(3, 32, 35, 0), time(3, 35, 21, 0)),
    ("03_35_50_to_03_36_10", time(3, 35, 50, 0), time(3, 36, 10, 0)),
]

def filter_time_range(df: pd.DataFrame, start_t: time, end_t: time) -> pd.DataFrame:
    # timestamp 是字符串：HH:MM:SS.mmm
    dt = pd.to_datetime(df["timestamp"], format="%H:%M:%S.%f", errors="coerce")
    t = dt.dt.time
    mask = (t >= start_t) & (t <= end_t)
    return df.loc[mask, ["timestamp", "distances", "validty", "bias"]].copy()

def main():
    df = pd.read_csv(FILE_1)

    for tag, start_t, end_t in RANGES:
        out_path = os.path.join(OUT_DIR, f"table_{tag}.txt")
        out_df = filter_time_range(df, start_t, end_t)
        out_df.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"[OK] {tag} -> {out_path}, 行数: {len(out_df)}")

if __name__ == "__main__":
    main()