"""Import generated JSON target lists into SQLite.

JSON 格式仍为：
    [name, path, info]

其中 info 会以 JSON 字符串形式存入 targets.info，供 UI 侧 json.loads 使用。

默认会导入 pathFind.py 自动生成的 5 个文件：
    left4dead2.json / update.json / left4dead2_dlc1.json / left4dead2_dlc2.json / left4dead2_dlc3.json
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path


def load_json_list(json_path: Path) -> list:
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, list):
        raise ValueError(f"Invalid JSON root (expect list): {json_path}")
    return data


def ensure_schema(cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            path TEXT,
            info TEXT
        )
        """
    )


def import_targets(cursor: sqlite3.Cursor, data: list, source: str) -> int:
    inserted = 0
    for item in data:
        if not (isinstance(item, list) and len(item) >= 3):
            continue
        name, path, info = item[0], item[1], item[2]
        cursor.execute(
            "INSERT INTO targets (name, path, info) VALUES (?, ?, ?)",
            (name, path, json.dumps(info, ensure_ascii=False)),
        )
        inserted += 1
    print(f"[ok] {source}: inserted {inserted}")
    return inserted


def main() -> None:
    base_dir = Path("./dicGenerate")
    default_files = [
        "left4dead2.json",
        "update.json",
        "left4dead2_dlc1.json",
        "left4dead2_dlc2.json",
        "left4dead2_dlc3.json",
    ]

    # 支持：python json2sql.py a.json b.json ...
    json_files = [Path(p) for p in sys.argv[1:]]
    if not json_files:
        json_files = [base_dir / name for name in default_files]

    db_path = base_dir / "Audio.db"
    conn = sqlite3.connect(str(db_path))
    try:
        cursor = conn.cursor()
        ensure_schema(cursor)

        total = 0
        for json_path in json_files:
            if not json_path.exists():
                print(f"[skip] not found: {json_path}")
                continue
            data = load_json_list(json_path)
            total += import_targets(cursor, data, source=str(json_path))

        conn.commit()
        print(f"Done! Total inserted: {total}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()