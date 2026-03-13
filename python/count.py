import pandas as pd

FILE_PATH = "D:\\uid03859\\Desktop\\python\\bias_log_2026_02_25_13_06_52.txt"  # 或改成你本地路径
THRESH_NS = 200_000_000  # 0.2s = 200,000,000ns

# 读入：默认第一列就是时间戳；如果你的文件有表头，会自动用表头名
df = pd.read_csv(FILE_PATH)

# 取第一列作为时间戳（兼容第一列列名不确定的情况）
ts = df.iloc[:, 0].astype("int64")

# 相邻差值（后一列减前一列）
diff_ns = ts.diff()

# 统计大于阈值的个数（diff 的第一个是 NaN，会自动排除）
count = (diff_ns > THRESH_NS).sum()

print("相邻时间戳差值 > 0.2s 的次数 =", int(count))