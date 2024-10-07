# 使用 dineof 填充缺失值的步骤：

#### 0、前言

- 本文默认读者拥有基础的 Linux 和 Shell 知识，例如： 
  - 一般使用美元符号加大写字母来表示变量，如： `$USER` 代表当前用户。 
  - 一般使用 `~/` 来代表当前用户的家目录： `/home/$USER/` 。
  - 一般用 `./` 代表当前目录，用 `../` 代表上一级目录。
  - 一般来说，用户的默认工作目录为家目录，即： `/home/$USER/` 。
  - 一般来说，运行程序的方法就是在之间输入该程序所在的路径。若将该程序所在的目录添加到系统环境变量中，即可直接输入程序名称来执行，例如：
    - 运行家目录中的 `~/示例脚本.sh` 脚本，可直接执行：`~/示例脚本.sh`
    - 运行系统 `/bin` 目录中的 `/bin/示例程序` ，可直接执行：`示例程序`
    - Linux 系统中，一般对文件的后缀名不敏感，比如将 `示例脚本.sh` 重命名为 `示例脚本`，也一样可以正常运行 。

- 本文默认使用 Vim 编辑器，你也可以使用其他文本编辑器（如 nano、gedit）或开发环境（如 vscode）来修改文本文件。Vim 编辑器的基础用法如下（快捷键需在英文模式下才有效）：

  ```shell
  # 按 i 进入编辑模式
  i
  
  # 按 ESC 返回常规模式
  Esc
  
  # 常规模式下，按 : 进入命令模式，输入 wq 保存退出（w 保存，q推出）
  :wq
  
  # 常规模式下，按大写 V 即可按行进行选择
  shift + v
  
  # 常规模式下，按 u 撤销当前操作。
  u
  # 也可使用命令来撤销：
  :undo
  
  # 常规模式下，按 Ctrl + r 重做当前操作。
  Ctrl + r
  # 也可使用命令来重做：
  :redo
  
  # 常规模式下，按 : 进入命令模式，输入 q！ 不保存并强制退出
  :q！
  ```

- 复制、移动文件，可以用文件管理器来进行，不必拘泥于敲命令。
  - 如果不方便使用图形界面（例如服务器上操作），可以使用终端下的文件管理器，例如：ranger
  - 简单介绍一下 ranger 的操作：
    - ranger 中有三列，中间是当前位置，左边是上级目录，右边是预览窗格；
    - 用方向键控制光标的移动；
    - 按 `yy` 复制，会复制光标覆盖的文件到剪切板；
    - 按 `pp` 粘贴，会将剪切板中的文件粘贴到光标所在的文件夹；
    - 按 `a` 重命名光标覆盖的文件，回车确认。
    - 按 `空格` 可进行多选，按小写 `v` 可全选。

- 本文将仅讨论 arch 系列的 Linux 发行版的情况，原因是：
  - 基本步骤相同，相同软件用法也相同。
  - 不同 Linux 发行版中，安装软件的命令、需要安装的包名可能不同，而发行版众多，无法一一列举。会有这些差异是因为，不同发行版用来安装软件的 **包管理工具** 不同，同一软件在各发行版所维护的 **软件仓库** 中的名称也可能不同。
  
- 为便于说明，本文以示例文件 input.nc 和待填充变量 chlor_a 为例。大致流程通用，个别案例可能需要自己进行 NetCDF 文件的预处理。



#### 1、安装 dineof 的依赖

所谓依赖，就是主要软件的一些功能需要依赖其他软件来实现，这些被需要的软件就是主软件的依赖。

- 对于 arch 系列的发行版（如 archlinux 、manjaro 等），可执行如下命令：

  ```shell
  # 更新系统
  sudo pacman -Syyu

  # 安装依赖
  sudo pacman -S base-devel git gcc-fortran arpack netcdf netcdf-fortran
  ```

- 如果找不到软件包，请编辑 /etc/pacman.conf 文件，**启用 multilib 仓库，再更新系统**即可：

  ```shell
  # 将 /etc/pacman.conf 文件复制到 /etc/pacman.conf_bak ，对于新手这有备无患
  sudo cp /etc/pacman.conf /etc/pacman.conf_bak

  # 编辑 pacman 配置文件来启用 multilib 仓库
  sudo vim /etc/pacman.conf
  ```

- 启用 multilib 仓库，一般去掉 /etc/pacman.conf 文件中相关条目的注释（开头的 # 号）即可：

  ```shell
  [multilib]
  Include = /etc/pacman.d/mirrorlist
  ```

- /etc/pacman.conf 文件是系统中的重要配置文件，如果出现意外，用刚才备份的 /etc/pacman.conf_bak 文件来覆盖 /etc/pacman.conf 文件，即可恢复。

  ```shell
  # 复制备份的 /etc/pacman.conf_bak 文件到 /etc/pacman.conf
  sudo cp -f /etc/pacman.conf_bak /etc/pacman.conf
  ## cp 参数解释：
  ##  -f:		强制
  ```


#### 2、编译源码

- 使用 git 工具，从远程仓库克隆项目源码到本地，然后编译源码，得到可执行的二进制文件（程序）：
  ```shell
  # 切换到家目录（这是确保我们开始的目录一致）
  # 如果你熟悉你的 Linux 目录结构，也可以从其他你喜欢的目录开始
  cd ~
  
  # 拉取源码，保存到当前目录下的 DINEOF 文件夹
  git clone https://github.com/Aida-Alvera/DINEOF.git ./DINEOF
  
  # 进入 DINEOF 文件夹
  cd ./DINEOF
  
  # 将配置文件模板 config.mk.template 复制一份作为配置文件 config.mk
  cp config.mk.template config.mk
  
  # 编译 dineof 二进制文件
  make
  ```

- 至此，会看到如下文件结构：

  ```txt
  ~/
  |-- DINEOF/					# 本地的源码文件夹
  	|-- config.mk.template	# 配置文件模板
  	|-- config.mk			# 配置文件
  	|-- dineof				# 编译好的二进制文件（可运行的程序）
  	|-- SmallExample/		# 自带的示例项目
  		|-- ...
  	|-- ...
  ```

- 如果编译失败，先确认依赖项是否全部正常安装或依赖的版本是否符合要求，再重新编译。如果仍然编译失败，可能需要根据需求尝试修改 config.mk 配置文件。



#### 3、尝试运行示例，以检查 `dineof` 程序是否正常工作：

- 进入 `~/DINEOF/SmallExample`文件夹：

  ```shell
  # 进入示例文件的目录
  cd ~/DINEOF/SmallExample/

  # 查看当前目录内容
  ls -la --color=auto
  ## ls 参数解释：
  ## -l：				以列表显示
  ## -a：				显示隐藏文件
  ## --color=auto：	显示颜色
  ```

- 我们可以看到 SmallExample 文件夹的内容如下，要记得此时我们的 dineof 二进制文件在 SmallExample 文件夹的在上级目录 `../` 中。

  ```txt
  ~/
  |-- DINEOF/							# 本地的源码文件夹
  	|-- dineof						# 二进制文件
  	|-- ...
  	|-- SmallExample/				# 自带的示例项目文件夹
  		|-- alboranSST_small.nc		# NetCDF 文件
  		|-- dineof.init				# init 文件
  		|-- Output/					# dineof 处理后的输出文件夹
  		|-- ...
  ```

- 已经有一个 NetCDF 文件和一个 init 文件了,可以直接运行。我们运行试试看：

  ```shell
  # 直接运行 dineof 即可查看用法
  ../dineof
  
  # 使用 cat 命令检查 init 文件
  cat ./dineof.init
  
  # 我们将当前目录的 init 文件作为参数传入，试运行该项目
  ../dineof ./dineof.init
  ```

- 至此，可以看到终端上的输出信息，最后显示 ` ...done!` 则表示运行成功。运行后输出的文件位于 `./Output` 中。



#### 4、运行自己的项目

- 返回 DINEOF 文件夹，创建一个新的文件夹用于存放自己的项目，比如我创建一个 MyProjeck 文件夹:

  ```shell
  # 创建 MyProject 文件夹
  mkdir -p ~/DINEOF/MyProjeck/
  ## mkdir 参数解释：
  ## -p：	即使中间文件夹不存在，也以递归的方式创建最终的文件夹
  
  # 进入 MyProjeck 文件夹
  cd ~/DINEOF/MyProjeck/
  
  # 创建一个 Output 文件夹，之后要用到
  mkdir ./Output/
  
  # 将你的 NetCDF 文件拷贝到 MyProjeck 文件夹中来
  cp /path/to/your/<NetCDF.nc> ./input.nc
  ## 注意，你应该填写你自己的文件所在的位置、名称，不要直接复制!!
  
  # 使用 vim 编辑器，按需修改 mydineof.init 文件
  vim ./mydineof.init
  ## 也可以使用其他你喜欢的编辑器，如：nano、micro
  ## 甚至可以使用图形化的编辑器、开发环境等
  ```

- mydineof.init 文件的具体内容**需要根据自己的要求编写**，如有疑问建议咨询GPT。可以从示例项目中复制一份作为参考，再进行修改。

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 复制示例项目的 init 文件到自己的项目文件夹中
  cp ../SmallExample/dineof.init ./mydineof.init
  
  # 修改 init 文件
  vim ./mydineof.init
  ```

- 编辑好 mydineof.init 文件后，即可像运行示例项目一样运行。运行后的文件会根据 mydineof.init 文件中的配置，存放到指定目录。

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 运行
  ../dineof ./mydineof.init
  ```

- 对于可直接处理的 NetCDF 文件，以上步骤即可运行 dineof 进行填充。



#### 5、关于补全 input.nc 缺失的 mask 变量的处理方法

#### 5.1、查看 input.nc 文件的信息，确定创建 mask 变量的方法

- 准备 Python 及其包管理工具。
- 这里以 arch 系发行版为例，其他发行版可能需要使用 python 自己的包管理工具（如 pip）进行安装。

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 安装 python 及后续会用到的函数库
  sudo pacman -S python python-netcdf4 python-numpy
  
  ## python-xarray 包不再需要，如果你本来就用不到这个包，可以移除
  sudo pacman -Rsnc python-xarray
  
  # 创建一个 Python 脚本来检查 input.nc 文件的结构、变量 chlor_a 的缺失值
  vim ./check.py
  ```

- 编辑 `check.py` 的内容如下：

  ```python
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
  
  
  ```

- 执行 Python 脚本，检查 input.nc 文件结构。也顺便检查 Python 环境是否可用。

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 授予 check.py 脚本执行权限
  chmod +x ./check.py
  
  # 用 Python 执行 check.py 脚本，查看该脚本用法
  python ./check.py
  
  # 用 Python 执行 check.py 脚本，查看 input.nc 文件结构
  python ./check.py ./input.nc
  ```

- 也使用 ncdump 命令进行查看：

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 查看 input.nc 文件中开头部分的变量（如 chlor_a）的信息
  ncdump -v chlor_a ./input.nc | head
  
  # 查看 input.nc 文件开头部分的完整信息
  ncdump -h ./input.nc
  ```

#### 5.2、根据输出结果，创建纯 mask 变量的 NetCDF 文件

- 根据输出结果，我们将待填充变量（例如 chlor_a）缺失值的地方 mask 标记为 1（我们关心的区域），否则为 0（我们不关心的区域）。

- 现在同样编写一个脚本 create_mask.py 并运行它，该脚本读取 input.nc 文件，输出一个纯 mask 变量的 NetCDF 文件 mask_for_intup.nc 。

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 使用 vim 创建 create_mask.py 文件
  vim ./create_mask.py
  ```

- 编辑 create_mask.py 的内容如下：

  ```python
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
  
  
  ```

- 授予 create_mask.py 执行权限，运行脚本创建 mask_for_input.nc 文件：

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 授予 create_mask.py 脚本执行权限
  chmod +x ./create_mask.py
  
  # 执行 create_mask.py 脚本查看用法
  python ./create_mask.py
  
  # 执行 create_mask.py 脚本来创建 mask 文件
  python create_mask.py ./input.nc
  ```

- 根据脚本提示操作。例如：
  可选的变量名称:
    1. chlor_a
    2. time
    3. lat
    4. lon

  请输入要创建海陆 mask 的待填充变量名称或序号：1
  海陆 mask 已写入到文件: mask_for_input.nc
  
- 然后，我们需要编写一份 mydineof.init 文件：

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 创建 mydineof.init 文件
  vim ./mydineof.init
  ```

- 编辑 mydineof.init 内容如下：

  ```txt
  ! mydineof.init
  ! 文件中的具体参数的值和 dineof 程序的填充方式有关，需要的话咨询 GPT 。
  
  ! INPUT File for DINEOF 3.0
  ! Lines starting with a ! or # are comments
  
  ! data、time 填写待处理的 NetCDF 文件，及对应变量名；mask 填写我们自己创建的 mask 文件和 mask 变量。
  data = ['input.nc#chlor_a']
  mask = ['mask_for_input.nc#mask']
  time = 'input.nc#time'
  
  alpha = 0.01
  numit = 3
  nev = 5
  neini = 1
  ncv = 10
  tol = 1.0e-8
  nitemax = 300
  toliter = 1.0e-3
  rec = 1
  eof = 1
  norm = 0
  seed = 243435
  
  ! 这里是输出文件夹、输出文件路径及变量等
  Output = 'Output/'
  results = ['Output/filled.nc#chlor_a']
  
  EOF.U = ['Output/eof.nc#U']
  EOF.V = 'Output/eof.nc#V'
  EOF.Sigma = 'Output/eof.nc#Sigma'
  
  ```



#### 6、大功告成可以填充数据了！

- 我们需要的文件已经都有了：

  ```txt
  ~/
  |-- DINEOF/							# 本地的源码文件夹
  	|-- dineof						# 二进制文件
  	|-- ...
  	|-- MyProjeck/					# 我们的项目文件夹
  		|-- input.nc				# NetCDF 文件
  		|-- mask_for_input.nc		# 纯 mask 变量的 NetCDF 文件
  		|-- mydineof.init			# init 文件
  		|-- Output/					# dineof 处理后的输出文件夹
  		|-- ...
  ```

- 运行并等待结果即可：

  ```shell
  # 进入目录
  cd ~/DINEOF/MyProjeck/
  
  # 执行 dineof 并传入我们的 mydineof.init 作为参数
  ../dineof ./mydineof.init
  ```

- 如果你没有报错，那么大功告成，输出的文件在 mydineof.init 所指定的输出目录中。
- 默认应该是 `~/DINEOF/MyProjeck/Output/filled.nc` 。
