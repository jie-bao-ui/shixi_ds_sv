import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

FILE_A = "D:\\uid03859\\Desktop\\python\\table_1_15_03_17_25_to_03_21_21.txt"
FILE_B = "D:\\uid03859\\Desktop\\python\\table_1_16_03_17_25_to_03_21_21.txt"

OUT_DIR = "./plots_overlay_datetime"
os.makedirs(OUT_DIR, exist_ok=True)

TZ = "UTC"
DISTANCES = [0, 10, 20, 30, 40]

def parse_pipe_list(s: str, cast=float):
    s = str(s).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    if s == "":
        return []
    return [cast(x) for x in s.split("|")]

def load_long_df_hms(file_path: str, source_name: str) -> pd.DataFrame:
    """
    适配 timestamp 已经是 'HH:MM:SS.mmm' 的文件（例如 03:17:25.095）
    输出 long 表：dt(datetime), distance(int), bias(float), source(str)
    同一 dt+distance 重复时保留第一个。
    """
    df = pd.read_csv(file_path)

    # 解析时间字符串 -> datetime（默认日期会是 1900-01-01，不影响画相对时间轴）
    df["dt"] = pd.to_datetime(df["timestamp"], format="%H:%M:%S.%f", errors="coerce")
    df = df.dropna(subset=["dt"]).reset_index(drop=True)

    # distances/validty/bias 还是 pipe list 的话走展开；
    # 如果你的 table_doc*.txt 已经是一行一个点（distance/bias单值），那告诉我我再改成单值版。
    def parse_pipe_list(s: str, cast=float):
        s = str(s).strip()
        if s.startswith("[") and s.endswith("]"):
            s = s[1:-1]
        if s == "":
            return []
        return [cast(x) for x in s.split("|")]

    df["dist_list"]  = df["distances"].apply(lambda x: parse_pipe_list(x, int))
    df["valid_list"] = df["validty"].apply(lambda x: parse_pipe_list(x, int))
    df["bias_list"]  = df["bias"].apply(lambda x: parse_pipe_list(x, float))

    records = []
    for row_no, (dt, dists, valids, biases) in enumerate(
        zip(df["dt"], df["dist_list"], df["valid_list"], df["bias_list"])
    ):
        for d, v, b in zip(dists, valids, biases):
            if v == 1:
                records.append({
                    "row_no": row_no,
                    "dt": dt,
                    "distance": int(d),
                    "bias": float(b),
                    "source": source_name,
                })

    long_df = pd.DataFrame(records)
    if long_df.empty:
        return long_df

    # 去重：同一 dt + distance 保留第一个
    long_df = (long_df
               .sort_values(["dt", "row_no"])
               .drop_duplicates(subset=["dt", "distance"], keep="first")
               .reset_index(drop=True))
    return long_df

A = load_long_df_hms(FILE_A, "1_15")
B = load_long_df_hms(FILE_B, "1_16")
if A.empty and B.empty:
    raise ValueError("两个文件过滤 valid==1 后都没有数据。")

for d in DISTANCES:
    a = A[A["distance"] == d].sort_values(["dt", "row_no"])
    b = B[B["distance"] == d].sort_values(["dt", "row_no"])

    plt.figure(figsize=(12, 4))

    if not a.empty:
        plt.plot(a["dt"], a["bias"], linestyle="-", label="1_15")
    if not b.empty:
        plt.plot(b["dt"], b["bias"], linestyle="-", label="1_16")

    plt.title(f"Bias vs Timestamp (distance={d})")
    plt.xlabel("time (MM:SS)")   # <-- 改这里：横轴名字
    plt.ylabel("bias")
    plt.grid(True)
    plt.legend()

    # ====== 横轴格式：分秒（MM:SS）======
    ax = plt.gca()

    # 只显示 分:秒（如果你想显示到毫秒，用 "%M:%S.%f" 并切片不方便，建议直接用 "%M:%S"）
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%M:%S"))

    # 刻度密度：优先按“秒”排（自动会根据范围调整），你也可以改成 MinuteLocator
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))

    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    # ===================================

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, f"overlay_bias_distance_{d}.png")
    plt.savefig(out_path, dpi=150)
    plt.close()

print(f"Done. Saved 5 overlay datetime plots to: {os.path.abspath(OUT_DIR)}")