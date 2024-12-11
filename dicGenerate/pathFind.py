from pathlib import Path
import ffmpeg
import json

def list_all_files(directory):
    # 创建一个空列表来存储文件路径
    dic = []
    file_paths = []

    # 使用 Path 对象遍历目录下的所有文件
    for file in Path(directory).rglob('*.wav'):
        if file.is_file():
            file_paths.append(file)
    for file in file_paths:
        name = str(file).split('\\')[-1]
        info = get_info(file)
        dic.append([name, str(file), info])
    return dic
def get_info(file):
    info = ffmpeg.probe(file)
    return info
# 获取用户输入的目录路径
directory = input("Enter the path of the directory: ")
# tag = input("Enter the tag: ")
# tag2 = input("Enter the tag2: ")

# 调用函数并记录所有文件路径
all_files = list_all_files(directory)
json_file_path = Path(".\\dicGenerate\\All.json")

# 在子列表的3索引标注分类
# for i in range(len(all_files)):
#     all_files[i].append(tag)
#     all_files[i].append(tag2)
#     all_files[i].append("")

# 打印所有文件路径
for file_path in all_files:
    print(file_path)


if json_file_path.is_file():
    with open(json_file_path, 'r', encoding='utf-8') as f:
        existing_data = json.load(f)
else:
    existing_data = []

existing_data.extend(all_files)

with open(json_file_path, 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=4)