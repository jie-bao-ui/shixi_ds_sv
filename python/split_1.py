import os
import pandas as pd
from datetime import time
FILE_1 = "D:\\uid03859\\Desktop\\python\\doc3_timestamp_to_hmsms.txt"
FILE_2 = "D:\\uid03859\\Desktop\\python\\doc2_timestamp_to_hmsms.txt"

OUT_1 = "table_1_15_03_17_25_to_03_21_21.txt"
OUT_2 = "table_1_16_03_17_25_to_03_21_21.txt"

# 绝对时间范围：03:17:25.000 ~ 03:21:21.000
START_T = time(3, 17, 25, 0)
END_T   = time(3, 21, 21, 0)

def filter_time_range(in_path: str, out_path: str):
    df = pd.read_csv(in_path)

    # timestamp 是字符串：HH:MM:SS.mmm
    # 解析为 datetime.time 便于比较
    dt = pd.to_datetime(df["timestamp"], format="%H:%M:%S.%f", errors="coerce")
    t = dt.dt.time

    mask = (t >= START_T) & (t <= END_T)
    out = df.loc[mask, ["timestamp", "distances", "validty", "bias"]].copy()

    out.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[OK] {in_path} -> {out_path}, 行数: {len(out)}")

filter_time_range(FILE_1, OUT_1)
filter_time_range(FILE_2, OUT_2)