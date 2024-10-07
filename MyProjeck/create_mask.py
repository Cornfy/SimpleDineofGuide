# create_mask.py

import sys
import os
import netCDF4 as nc
import numpy as np
from netCDF4 import Dataset

def print_help():
    """
    打印脚本的使用方法
    """
    print("该脚本会帮你创建一个仅包含海陆 mask 变量的 NetCDF 文件")
    print("使用方法:")
    print("  python", sys.argv[0], "</path/to/input.nc>        # 创建输入文件的 mask 文件")
    print("  python", sys.argv[0], "--help                     # 显示帮助信息")

def print_available_variables(data_file):
    """
    打印数据文件中可用的变量名称
    """
    variable_names = data_file.variables.keys()
    print("可选的变量名称:")
    for i, var_name in enumerate(variable_names, start=1):
        print(f"  {i}. {var_name}")
    return variable_names

def is_valid_variable(variable_names, target_var):
    """
    检查输入的变量名称是否有效
    """
    return target_var in variable_names or target_var.isdigit() and 0 < int(target_var) <= len(variable_names)

def create_land_mask(input_nc_path, target_var_name):
    """
    创建海陆 mask 变量并保存到 NetCDF 文件中
    """
    try:
        # 打开数据文件
        data_file = Dataset(input_nc_path, 'r')
    except FileNotFoundError:
        print("错误: 未找到数据文件:", input_nc_path)
        return

    # 获取经度和纬度变量名称
    lon_var, lat_var = None, None
    for var_name in data_file.variables.keys():
        var = data_file.variables[var_name]
        if 'units' in var.ncattrs():
            units = var.units
            if units.lower() == 'degrees_east':
                lon_var = var_name
            elif units.lower() == 'degrees_north':
                lat_var = var_name

    if lon_var is None or lat_var is None:
        print("错误: 数据文件中找不到经度或纬度变量。")
        data_file.close()
        return

    # 获取数据
    data = data_file.variables[target_var_name][:]  

    # 创建海陆 mask 数组，初始化为 0（陆地）
    resolution_y, resolution_x = data.shape[-2:]

    mask = np.zeros((resolution_y, resolution_x))

    # 遍历每一个点
    for y in range(resolution_y):
        for x in range(resolution_x):
            # 对于每一个点，遍历时间轴上的每个时间点
            for time_index, time in enumerate(data_file.variables['time'][:]):
                # 在每个时间点上，检查数据是否存在
                if not np.isnan(data[time_index, y, x]): 
                    # 如果数据存在，则将该点标记为海洋（1），并跳出循环
                    mask[y, x] = 1
                    break

    # 获取文件名
    file_name = os.path.basename(input_nc_path)
    file_name_without_ext = os.path.splitext(file_name)[0]

    # 将海陆 mask 写入到 nc 文件中
    output_file_path = "mask_for_" + file_name_without_ext + ".nc"
    output_file = Dataset(output_file_path, 'w', format='NETCDF4')

    # 创建 nc 文件的维度
    output_file.createDimension('lon', resolution_x)
    output_file.createDimension('lat', resolution_y)

    # 根据用户输入创建海陆 mask 变量
    mask_var = output_file.createVariable('mask', 'i', ('lat', 'lon'))

    # 将海陆 mask 数组写入到 nc 文件的变量中
    mask_var[:] = mask

    # 关闭 nc 文件
    output_file.close()

    print("海陆 mask 已写入到文件:", output_file_path)
    return output_file_path

def main():
    """
    主函数，处理命令行参数并调用其他函数
    """
    if len(sys.argv) != 2 or sys.argv[1] == '--help':
        print_help()
        return

    input_nc_path = sys.argv[1]

    try:
        # 打开数据文件
        data_file = Dataset(input_nc_path, 'r')
    except FileNotFoundError:
        print("错误: 未找到数据文件:", input_nc_path)
        return

    # 打印可用的变量名称列表并选择变量名称
    variable_names = print_available_variables(data_file)
    target_var = input("请输入要创建海陆 mask 的待填充变量名称或序号：")
    if not is_valid_variable(variable_names, target_var):
        print("错误: 输入的变量名称或序号不正确。")
        data_file.close()
        return

    if target_var.isdigit():
        target_var = list(variable_names)[int(target_var) - 1]

    try:
        # 创建海陆 mask
        create_land_mask(input_nc_path, target_var)  # 使用选择的变量名称
    except Exception as e:
        print("发生错误:", e)
    finally:
        # 关闭数据文件
        data_file.close()

if __name__ == "__main__":
    main()

