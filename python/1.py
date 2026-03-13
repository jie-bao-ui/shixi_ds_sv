import os
import pandas as pd
import matplotlib.pyplot as plt

FILE_PATH = "D:\\uid03859\\Desktop\\python\\bias_log_2026_02_25_15_44_53.txt"
# FILE_PATH = "/mnt/data/f902278c-f2ff-463e-a089-351ea4ad16c2.txt"

OUT_DIR = "./plots"
os.makedirs(OUT_DIR, exist_ok=True)

USE_DATETIME_X = True  # True: 把纳秒时间戳转为datetime；False: 原始timestamp

def parse_pipe_list(s: str, cast=float):
    s = str(s).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    if s == "":
        return []
    return [cast(x) for x in s.split("|")]

# 读入（逗号分隔，首行表头：timestamp, distances, validty, bias）
df = pd.read_csv(FILE_PATH)

df["dist_list"]  = df["distances"].apply(lambda x: parse_pipe_list(x, int))
df["valid_list"] = df["validty"].apply(lambda x: parse_pipe_list(x, int))
df["bias_list"]  = df["bias"].apply(lambda x: parse_pipe_list(x, float))

# 拉平成 long 表：每个 timestamp 拆成 5 条（按距离）
records = []
for row_no, (ts, dists, valids, biases) in enumerate(
    zip(df["timestamp"], df["dist_list"], df["valid_list"], df["bias_list"])
):
    for d, v, b in zip(dists, valids, biases):
        if v == 1:  # 只保留有效数据
            records.append({
                "row_no": row_no,         # 用于“保留第一个”
                "timestamp": int(ts),
                "distance": int(d),
                "bias": float(b),
            })

long_df = pd.DataFrame(records)
if long_df.empty:
    raise ValueError("过滤 validty==1 后没有数据，请检查文件内容。")

# 关键：去重（同一 timestamp + 同一 distance 出现多次，保留第一个）
# 先按 timestamp、row_no 排序，确保“第一个”是文件中最先出现的那条
long_df = (long_df
           .sort_values(["timestamp", "row_no"])
           .drop_duplicates(subset=["timestamp", "distance"], keep="first"))

# x轴可选转 datetime（你的 timestamp 看起来是 epoch 纳秒）
if USE_DATETIME_X:
    long_df["time"] = pd.to_datetime(long_df["timestamp"], unit="ns")

# 分距离画图
for d in sorted(long_df["distance"].unique()):
    sub = long_df[long_df["distance"] == d].sort_values(["timestamp", "row_no"])

    plt.figure(figsize=(10, 4))
    if USE_DATETIME_X:
        plt.plot(sub["time"], sub["bias"])
        plt.xlabel("timestamp (datetime)")
    else:
        plt.plot(sub["timestamp"], sub["bias"])
        plt.xlabel("timestamp")

    plt.ylabel("bias")
    plt.title(f"Bias vs Timestamp (distance={d})")
    plt.grid(True)

    out_path = os.path.join(OUT_DIR, f"bias_distance_{d}.png")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()

print(f"Done. Saved plots to: {os.path.abspath(OUT_DIR)}")