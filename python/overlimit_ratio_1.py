import os
import glob
import pandas as pd

# ====== 你的 7 个分段文件所在目录 ======
IN_DIR = r"D:\uid03859\Desktop\python\split_ranges"
# 输出 CSV 的目录（可改；默认同目录下建一个 stats 子目录）
OUT_DIR = os.path.join(IN_DIR, "stats_csv")
os.makedirs(OUT_DIR, exist_ok=True)

# 距离与阈值映射：0/10/20/30/40 对应 9/9/11/14/16
THRESH = {0: 9, 10: 9, 20: 11, 30: 14, 40: 16}
DISTANCES = [0, 10, 20, 30, 40]

def parse_pipe_list(s: str, cast=float):
    s = str(s).strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    if s == "":
        return []
    return [cast(x) for x in s.split("|")]

def load_long_bias(file_path: str) -> pd.DataFrame:
    """
    展开为 long：timestamp, distance, bias
    - 同一 timestamp 的重复行保留第一个（文件顺序）
    - 只保留 validty==1
    - 展开后同一 (timestamp, distance) 重复保留第一个
    """
    df = pd.read_csv(file_path)

    # timestamp 重复保留第一个（按文件顺序）
    df = df.drop_duplicates(subset=["timestamp"], keep="first").reset_index(drop=True)

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
                    "timestamp": ts,
                    "distance": int(d),
                    "bias": float(b),
                })

    long_df = pd.DataFrame(records)
    if long_df.empty:
        return long_df

    # 展开后：同一 (timestamp, distance) 重复保留第一个
    long_df = (long_df
               .sort_values(["timestamp", "row_no"])
               .drop_duplicates(subset=["timestamp", "distance"], keep="first")
               .reset_index(drop=True))
    return long_df

def compute_exceed_stats(long_df: pd.DataFrame) -> pd.DataFrame:
    """
    每个 distance 统计：
      total_valid_cnt: valid==1 的总数
      exceed_cnt: abs(bias) > threshold 的数量
      exceed_pct: exceed_cnt / total_valid_cnt
    """
    rows = []
    for d in DISTANCES:
        sub = long_df[long_df["distance"] == d] if not long_df.empty else long_df
        total = int(len(sub))
        thr = THRESH[d]
        if total == 0:
            exceed = 0
            pct = 0.0
        else:
            exceed = int((sub["bias"].abs() > thr).sum())
            pct = exceed / total
        rows.append({
            "distance": d,
            "threshold": thr,
            "total_valid_cnt": total,
            "exceed_cnt": exceed,
            "exceed_pct": pct,
        })
    return pd.DataFrame(rows)

def main():
    files = sorted(glob.glob(os.path.join(IN_DIR, "table_*.txt")))
    if not files:
        raise FileNotFoundError(f"在目录里没找到 table_*.txt: {IN_DIR}")

    for fp in files:
        long_df = load_long_bias(fp)
        stats_df = compute_exceed_stats(long_df)

        base = os.path.splitext(os.path.basename(fp))[0]
        out_csv = os.path.join(OUT_DIR, f"{base}_exceed_stats.csv")
        stats_df.to_csv(out_csv, index=False, encoding="utf-8-sig")

        print(f"[OK] {fp} -> {out_csv}")

if __name__ == "__main__":
    main()