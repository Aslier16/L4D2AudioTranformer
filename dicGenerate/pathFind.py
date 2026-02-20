from pathlib import Path
import ffmpeg
import json
import sys


def simplify_game_root_path(file_path: Path | str) -> str:
    """简化音频路径：舍弃 `...\\Left 4 Dead 2\\` 之前的部分。

    例如：
    - E:\\SteamLibrary\\steamapps\\common\\Left 4 Dead 2\\update\\sound\\a.wav
      -> update\\sound\\a.wav

    若路径中找不到 `Left 4 Dead 2` 目录，则返回完整路径。
    """
    p = Path(file_path)
    parts = list(p.parts)
    lower_parts = [str(x).lower() for x in parts]
    marker = "left 4 dead 2"
    if marker in lower_parts:
        idx = lower_parts.index(marker)
        if idx + 1 < len(parts):
            return "\\".join(str(x) for x in parts[idx + 1 :])
    return str(p)

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
        dic.append([name, simplify_game_root_path(file), info])
    return dic
def get_info(file):
    """提取转换所需的最小音频元数据。

    该项目的转换逻辑（见 ui/func.py: transAudio）只依赖：
    - format.format_name
    - streams[0].codec_name
    - streams[0].channels
    - streams[0].sample_rate
    - format.bit_rate
    - format.duration

    为了避免 update.json 体积过大，这里剔除 ffprobe 的其他字段。
    """
    try:
        probe = ffmpeg.probe(str(file))
    except Exception as e:
        # 保持 JSON 可序列化；上层可以据此排查失败文件
        return {"error": str(e)}

    fmt = probe.get("format", {}) if isinstance(probe, dict) else {}
    streams = probe.get("streams", []) if isinstance(probe, dict) else []
    first_audio = streams[0] if streams else {}

    slim = {
        "streams": [
            {
                "codec_name": first_audio.get("codec_name"),
                "channels": first_audio.get("channels"),
                "sample_rate": first_audio.get("sample_rate"),
            }
        ],
        "format": {
            "format_name": fmt.get("format_name"),
            "bit_rate": fmt.get("bit_rate"),
            "duration": fmt.get("duration"),
        },
    }
    return slim


def generate_json_for_sound_folder(sound_dir: Path, out_json: Path) -> None:
    """扫描一个 sound 目录并输出 JSON（覆盖写入）。"""
    if not sound_dir.exists():
        print(f"[skip] not found: {sound_dir}")
        return
    if not sound_dir.is_dir():
        print(f"[skip] not a dir: {sound_dir}")
        return

    all_files = list_all_files(sound_dir)
    print(f"[ok] {sound_dir} -> {out_json} ({len(all_files)} wav)")

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(all_files, f, ensure_ascii=False, indent=4)


def main() -> None:
    """从 Left 4 Dead 2 根目录自动生成各子包 JSON。"""
    # 用法：python pathFind.py "E:\\...\\Left 4 Dead 2"
    if len(sys.argv) >= 2:
        game_root = Path(sys.argv[1])
    else:
        game_root = Path(input("Enter 'Left 4 Dead 2' root path: ").strip('"'))

    # 目标目录名 -> 输出 JSON 文件名
    packages = [
        ("left4dead2", "left4dead2.json"),
        ("update", "update.json"),
        ("left4dead2_dlc1", "left4dead2_dlc1.json"),
        ("left4dead2_dlc2", "left4dead2_dlc2.json"),
        ("left4dead2_dlc3", "left4dead2_dlc3.json"),
    ]

    out_dir = Path("./dicGenerate")
    for folder_name, out_name in packages:
        sound_dir = game_root / folder_name / "sound"
        out_json = out_dir / out_name
        generate_json_for_sound_folder(sound_dir, out_json)


if __name__ == "__main__":
    main()