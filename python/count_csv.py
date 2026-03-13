import pandas as pd

FILE_PATH = "D:\\uid03859\\Desktop\\python\\bias_log_2026_02_25_11_17_30.txt"   # 改成你的路径也行
OUT_CSV = "gaps_over_200ms.csv"
THRESH_NS = 200_000_000  # 0.2s

# 读入
df = pd.read_csv(FILE_PATH)

# 取第一列为时间戳(ns)
ts_ns = df.iloc[:, 0].astype("int64")

# 计算“后面一列 - 当前列”的差值：delta[i] = ts[i+1] - ts[i]
delta_ns = ts_ns.shift(-1) - ts_ns

# 筛选超过阈值的行（最后一行 shift(-1) 会是 NaN，会自动被过滤掉）
mask = delta_ns > THRESH_NS

# 将当前时间戳转成 datetime（UTC），再格式化为 时:分:秒.毫秒
dt = pd.to_datetime(ts_ns[mask], unit="ns", utc=True)

# 如果你想用本地时间（比如中国）：取消下一行注释
# dt = dt.dt.tz_convert("Asia/Shanghai")

time_str = dt.dt.strftime("%H:%M:%S.%f").str.slice(0, 12)  # 保留到毫秒：HH:MM:SS.mmm

out_df = pd.DataFrame({
    "timestamp_hms": time_str,          # 第一列：当前时间戳(时分秒)
    "delta_ns": delta_ns[mask].astype("int64")  # 第二列：后面一列 - 当前列 的差值(ns)
})

# 保存并打印
out_df.to_csv(OUT_CSV, index=False, encoding="utf-8-sig")
print(out_df.to_csv(index=False))

print(f"\n已保存到: {OUT_CSV}")
print(f"超过 {THRESH_NS} ns 的条数: {len(out_df)}")