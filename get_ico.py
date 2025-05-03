# coding = utf-8
# Arch   = manyArch
#
# @File name:       get_ico.py
# @brief:           将ico等转换为base64编码，以整合资源到代码中
# @attention:       None
# @TODO:            None
# @Author:          NGC13009
# @History:         2025-05-03		Create

import base64

icon_file = 'favicon.ico'                 # 替换成你的 ico 文件路径
output_variable_name = 'icon_base64_data' # 输出的 Python 变量名

try:
    with open(icon_file, 'rb') as f:
        icon_data = f.read()
        base64_encoded_data = base64.b64encode(icon_data)
        base64_string = base64_encoded_data.decode('utf-8') # 转换为字符串

    # 打印出可以直接复制到代码中的 Python 变量赋值语句
    print(f"{output_variable_name} = '''{base64_string}'''")
    print("\n将上面这行代码复制到你的 Tkinter 程序中。")

except FileNotFoundError:
    print(f"错误：找不到文件 '{icon_file}'。请确保路径正确。")
except Exception as e:
    print(f"发生错误：{e}")
