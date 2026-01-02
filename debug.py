import pandas as pd
import numpy as np
if __name__ == "__main__":
    red = "\033[31m"
    yellow = "\033[33m"
    bright_white = "\033[1;37m"
    print(f"{red}%%%%%%%%%%%%%%%%%%%{yellow}-------{red}%%%%%%%%%%%%%%%{yellow}-----{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%{yellow}------{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(f"%%%%%%%%%%%%%%%%%%%{yellow}-------{red}%%%%%%%%%%%%%%%{yellow}-----{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%{yellow}------{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(f"%%%%%%%%%%%%%%%%%%%%%%%{yellow}--{red}%%%%%%%%%%%%%%%%%%%{yellow}----{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(f"%%%%%%%%%%%%%%%%%%%%%%%%%{yellow}---------------------{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%{yellow}-------{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(f"%%%%%%%%%%%%%%%%%%%%%%{yellow}-----{red}%%%%%%%%%%%%%%%%%{yellow}----{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%{yellow}----{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(f"%%%%%%%%%%%%%%%%%%%%%%%%%{yellow}---------{red}%%%%%%%%%%%{yellow}-----{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%{yellow}-----{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print(f"%%%%%%%%%%%%%%%%%%%%{yellow}-------{red}%%%%%%%%%%%%%%%%%%%%{yellow}----------{red}%%%%%%%%%%%%%%%%%%%%%%%{yellow}-----{red}%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%{bright_white}")


    def remove_empty_columns(path):
        """
        删除Excel文件中第一行和第二行都为空的列（空白列），
        并将结果保存回原文件。

        参数:
            path (str): Excel文件路径（.xlsx）
        """
        # 读取Excel，保留原始索引，不把第一行当作列名
        df = pd.read_excel(path, header=None, dtype=str)

        # 确保至少有两行，否则无法判断
        if df.shape[0] < 2:
            print("警告：Excel文件少于两行，无法判断空白列。")
            return

        # 将空字符串转为 NaN，便于统一判断
        df = df.replace(r'^\s*$', np.nan, regex=True).infer_objects(copy=False)

        # 获取所有列索引
        cols_to_drop = []
        for col in df.columns:
            # 检查第0行和第1行是否都为空（NaN）
            val1 = df.iloc[0, col]
            val2 = df.iloc[1, col]
            if pd.isna(val1) and pd.isna(val2):
                cols_to_drop.append(col)

        # 删除空白列
        df_cleaned = df.drop(columns=cols_to_drop).reset_index(drop=True)

        # 保存回原文件（覆盖）
        df_cleaned.to_excel(path, index=False, header=False)

        print(f"已删除 {len(cols_to_drop)} 个空白列，文件已更新：{path}")
    remove_empty_columns("test.xlsx")







