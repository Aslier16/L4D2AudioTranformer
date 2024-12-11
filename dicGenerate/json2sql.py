#transport json file to sql database

import json
import sqlite3

# 读取 JSON 文件
with open('.\dicGenerate\left4dead2_dlc3.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 连接到 SQLite 数据库（如果数据库不存在，则会创建一个新的）
conn = sqlite3.connect('dicGenerate\Audio.db')
cursor = conn.cursor()

# 创建表（假设 JSON 数据是一个包含多个字典的列表）
cursor.execute('''
CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    path TEXT,
    info TEXT
)
''')

# 插入数据
for item in data:
    cursor.execute('''INSERT INTO targets (name, path, info) VALUES (?, ?, ?)''', (item[0], item[1], json.dumps(item[2])))

# 提交事务并关闭连接
conn.commit()
conn.close()
print("Done!")