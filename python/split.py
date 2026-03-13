import os
import pandas as pd
from datetime import time
FILE_1 = "D:\\uid03859\\Desktop\\python\\bias_log_2026_02_27_17_55_50.txt"
# FILE_2 = "D:\\uid03859\\Desktop\\python\\bias_log_2026_02_25_13_06_52.txt"

OUT_1 = "doc3_timestamp_to_hmsms.txt"
#OUT_2 = "doc2_timestamp_to_hmsms.txt"

# 你想按哪个时区显示（一般图上看起来像本地时间就用 Asia/Shanghai；否则用 UTC）
TZ = "UTC"   # 或 "Asia/Shanghai"

def convert_timestamp_col(in_path: str, out_path: str):
    df = pd.read_csv(in_path)
    df["timestamp"] = df["timestamp"].astype("int64")

    dt = pd.to_datetime(df["timestamp"], unit="ns", utc=True).dt.tz_convert(TZ)
    # HH:MM:SS.mmm（毫秒）
    df["timestamp"] = dt.dt.strftime("%H:%M:%S.%f").str.slice(0, 12)

    # 保持原列顺序/格式
    df = df[["timestamp", "distances", "validty", "bias"]]
    df.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[OK] {in_path} -> {out_path}, 行数: {len(df)}")

convert_timestamp_col(FILE_1, OUT_1)
#convert_timestamp_col(FILE_2, OUT_2)