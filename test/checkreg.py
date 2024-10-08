import os
import json
import re

class TableEntry:
    def __init__(self, reg_name, values, action_name, is_default_entry):
        self.reg_name = reg_name
        self.values = values
        self.action_name = action_name
        self.is_default_entry = is_default_entry

def parse_line(line):
    # 使用正则表达式提取大括号内的内容
    match = re.search(r"\{(.*?)\}", line)
    if match:
        content = "{" + match.group(1) + "}"
        # 将提取的字符串转换为字典
        data_dict = json.loads(content.replace("'", '"').replace("None", 'null').replace("True", 'true').replace("False", 'false'))
        return TableEntry(
            reg_name=list(data_dict.keys())[0],
            values=data_dict[list(data_dict.keys())[0]],
            action_name=data_dict['action_name'],
            is_default_entry=data_dict['is_default_entry']
        )
    return None

def read_files(folder_path):
    all_entries = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                entries = []
                for line in file:
                    entry = parse_line(line)
                    if entry:
                        entries.append(entry)
                all_entries[filename] = entries
    return all_entries

# 使用示例
folder_path = 'tableEntries'  # 文件夹路径
all_entries = read_files(folder_path)
i=0
for filename, entries in all_entries.items():
    if entries[1].values[1] != 0 and entries[5].values[1] == 4:
        print(f"Entries in {filename}:")
        i = i+1
        # for entry in entries:
        #     print(f"Reg Name: {entry.reg_name}")
        #     print(f"Values: {entry.values}")
        #     print()
print(i)