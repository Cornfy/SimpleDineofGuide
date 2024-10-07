# check.py

import sys
import os
import netCDF4 as nc
import numpy as np
from datetime import datetime, timedelta
import warnings

def display_help():
    """
    显示脚本的使用帮助信息。
    """
    print("使用方法:")
    print("  python", sys.argv[0], "</path/to/input.nc>        # 显示文件结构")
    print("  python", sys.argv[0], "--help                     # 显示帮助信息")

def print_file_structure(filename):
    """
    打印 netCDF 文件的结构，包括变量及其详细信息，并从每个变量中显示一些数据样本。
    """
    try:
        with nc.Dataset(filename, 'r') as ds:
            print(f"文件：{filename} 包含以下变量：")
            for var_name in ds.variables:
                var = ds.variables[var_name]
                print(f"\n变量名：{var_name}")
                print(f"    维    度：{var.dimensions}")
                print(f"    数据类型：{var.dtype}")
                print(f"    单    位：{var.units if 'units' in var.ncattrs() else '无单位信息'}")
                data = var[:]
                if var_name == 'mask':
                    mask_ones = np.sum(data == 1)
                    mask_zeros = np.sum(data == 0)
                    print(f"    总 数 量：{var.size}")
                    print(f"    缺失数量：{np.sum(np.isnan(data))}")
                    print(f"    样本统计 ——  1 的数量：{mask_ones}，0 的数量：{mask_zeros}")
                elif var_name == 'time':
                    print(f"    总 数 量：{var.size}")
                    print(f"    缺失数量：{np.sum(np.isnan(data))}")
                    min_time = int(np.min(data))
                    max_time = int(np.max(data))
                    start_date = datetime(1970, 1, 1)
                    min_date = start_date + timedelta(days=min_time)
                    max_date = start_date + timedelta(days=max_time)
                    print(f"    样本统计 ——  最早时间: {min_date.strftime('%Y-%m-%d')}, 最晚时间: {max_date.strftime('%Y-%m-%d')}")
                else:
                    missing_count = np.sum(np.isnan(data))
                    total_count = data.size
                    print(f"    总 数 量：{total_count}")
                    print(f"    缺失数量：{missing_count}")
                    valid_data = data[~np.isnan(data)]  # 过滤出非 NaN 的数据
                    if valid_data.size > 0:
                        print(f"    样本统计 ——  最小值: {np.nanmin(valid_data):.4g}, 最大值: {np.nanmax(valid_data):.4g}, 平均值: {np.nanmean(valid_data):.4g}, 标准差: {np.nanstd(valid_data):.4g}")
                    else:
                        print("    无有效数据可用。")
    except FileNotFoundError:
        print(f"错误：文件 '{filename}' 不存在。")

def main():
    """
    主函数，用于处理命令行参数并根据输入调用其他函数。
    """
    # 忽略 RuntimeWarning
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    if len(sys.argv) == 1 or sys.argv[1] == '--help':
        display_help()
        return
    
    if len(sys.argv) == 2:
        if not os.path.exists(sys.argv[1]):
            print(f"错误：文件 '{sys.argv[1]}' 不存在。")
            return
        print_file_structure(sys.argv[1])
    else:
        print("提供的参数无效。使用 'python check.py --help' 查看正确的使用方法。")

if __name__ == "__main__":
    main()

