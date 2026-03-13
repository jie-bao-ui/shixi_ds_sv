import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ====== 改成你的两个文件路径（你上传的两个 txt）======
FILE_A = "D:\\uid03859\\Desktop\\python\\bias_log_2026_02_25_11_17_30.txt"
FILE_B = "D:\\uid03859\\Desktop\\python\\bias_log_2026_02_25_13_06_52.txt"
# ======================================================

OUT_DIR = "./plots_overlay_datetime"
os.makedirs(OUT_DIR, exist_ok=True)

# 时区：UTC / Asia/Shanghai 等（截图样式一般是本地时间，你按需要改）
TZ = "UTC"

DISTANCES = [0, 10, 20, 30, 40]

def parse_pipe_list(s: str, cast=float):
    """把形如 '[0|10|20|30|40]' 解析为 list"""
    s = str(s).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    if s == "":
        return []
    return [cast(x) for x in s.split("|")]

def load_long_df(file_path: str, source_name: str) -> pd.DataFrame:
    """
    输出 long 表：
    timestamp_ns(int), dt(datetime tz-aware), distance(int), bias(float), source(str), row_no(int)
    只保留 valid==1；同一 timestamp+distance 重复保留第一个。
    """
    df = pd.read_csv(file_path)

    df["dist_list"]  = df["distances"].apply(lambda x: parse_pipe_list(x, int))
    df["valid_list"] = df["validty"].apply(lambda x: parse_pipe_list(x, int))
    df["bias_list"]  = df["bias"].apply(lambda x: parse_pipe_list(x, float))

    records = []
    for row_no, (ts, dists, valids, biases) in enumerate(
        zip(df["timestamp"], df["dist_list"], df["valid_list"], df["bias_list"])
    ):
        for d, v, b in zip(dists, valids, biases):
            if v == 1:
                records.append({
                    "row_no": row_no,
                    "timestamp_ns": int(ts),
                    "distance": int(d),
                    "bias": float(b),
                    "source": source_name,
                })

    long_df = pd.DataFrame(records)
    if long_df.empty:
        return long_df

    # 去重：同一 timestamp + distance 出现多条时保留第一个
    long_df = (long_df
               .sort_values(["timestamp_ns", "row_no"])
               .drop_duplicates(subset=["timestamp_ns", "distance"], keep="first")
               .reset_index(drop=True))

    # ns -> datetime（先按 UTC，再转到目标 TZ）
    long_df["dt"] = pd.to_datetime(long_df["timestamp_ns"], unit="ns", utc=True).dt.tz_convert(TZ)

    return long_df

A = load_long_df(FILE_A, "docA")
B = load_long_df(FILE_B, "docB")
if A.empty and B.empty:
    raise ValueError("两个文件过滤 valid==1 后都没有数据。")

for d in DISTANCES:
    a = A[A["distance"] == d].sort_values(["timestamp_ns", "row_no"])
    b = B[B["distance"] == d].sort_values(["timestamp_ns", "row_no"])

    plt.figure(figsize=(12, 4))

    # 两条曲线叠加（不同颜色由 matplotlib 自动分配）
    if not a.empty:
        plt.plot(a["dt"], a["bias"], linestyle="-", label="docA")
    if not b.empty:
        plt.plot(b["dt"], b["bias"], linestyle="-", label="docB")

    plt.title(f"Bias vs Timestamp (distance={d})")
    plt.xlabel("timestamp (datetime)")
    plt.ylabel("bias")
    plt.grid(True)
    plt.legend()

    # ====== 横轴格式：跟你截图类似 "05 03:15"（日 时:分）======
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %H:%M", tz=mdates.UTC if TZ == "UTC" else None))
    # 若 TZ 不是 UTC，上面 tz 参数不好自动传；更稳的做法是直接不传 tz，
    # 因为我们已经把 long_df["dt"] 转到 TZ 了：
    if TZ != "UTC":
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %H:%M"))

    # 自动选择合适刻度密度
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=6, maxticks=10))
    plt.setp(ax.get_xticklabels(), rotation=0, ha="center")
    # ============================================================

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, f"overlay_bias_distance_{d}.png")
    plt.savefig(out_path, dpi=150)
    plt.close()

print(f"Done. Saved 5 overlay datetime plots to: {os.path.abspath(OUT_DIR)}")