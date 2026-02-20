from PySide6.QtWidgets import QFileDialog, QCheckBox, QWidget, QGridLayout, QVBoxLayout, QButtonGroup, QLineEdit, QListWidget, QListWidgetItem, QTreeView
from PySide6.QtWidgets import QDialog, QLabel
from PySide6.QtWidgets import QPushButton, QHBoxLayout
from PySide6.QtGui import QColor, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt
from os import path
import os
import re
import html
import json
import ffmpeg
from pathlib import Path
import subprocess
import sqlite3
import threading
import sys
import wave


def _ffmpeg_executable() -> str:
    """返回可用的 ffmpeg 可执行文件路径。

    打包(onefile)时二进制会被解压到 _MEIPASS 下，这里优先使用 resource_path('ffmpeg.exe')。
    源码运行时则尝试项目根目录的 ffmpeg-file/ffmpeg.exe，最后回退到系统 PATH 上的 ffmpeg。
    """
    try:
        candidate = resource_path("ffmpeg.exe")
        if Path(candidate).exists():
            return str(candidate)
    except Exception:
        pass

    try:
        project_root = Path(__file__).resolve().parent.parent
        candidate = project_root / "ffmpeg-file" / "ffmpeg.exe"
        if candidate.exists():
            return str(candidate)
    except Exception:
        pass

    return "ffmpeg"


_DURATION_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")


def _duration_seconds(file_path: str) -> float:
    """获取音频时长(秒)。

    - 对 wav：用 wave 直接读 header（快且不依赖 ffprobe）
    - 其它格式：调用 ffmpeg.exe -i 解析输出中的 Duration（只依赖 ffmpeg.exe）
    """
    p = str(file_path)
    if p.lower().endswith(".wav"):
        try:
            return float(get_audio_duration(p))
        except Exception:
            # wav header 异常时回退到 ffmpeg
            pass

    cmd = [_ffmpeg_executable(), "-hide_banner", "-i", p]
    # ffmpeg 在未指定 output 时会返回非 0，但 stderr 中包含 Duration
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    blob = (proc.stderr or "") + "\n" + (proc.stdout or "")
    m = _DURATION_RE.search(blob)
    if not m:
        raise RuntimeError(f"无法获取时长: {file_path}")
    hh = int(m.group(1))
    mm = int(m.group(2))
    ss = float(m.group(3))
    return hh * 3600 + mm * 60 + ss

class SrcAudio:
    """源音频文件属性类"""
    def __init__(self, path, target=[], volume=100):
        self.path = path
        self.target = target
        self.volume = volume
        # 加速 UI 勾选同步：记录被选中的目标索引集合
        self.selected_targets = set()


def _ensure_target_info_loaded(self, target_index: int) -> dict:
    """按需解析 targets[target_index][3] 的 JSON。

    之前是在 generateCheckbox 时对所有条目 json.loads，数量大时会导致启动卡顿。
    这里改为：只有真正需要转换时，才解析并缓存。
    """
    info = self.targets[target_index][3]
    if isinstance(info, str):
        info = json.loads(info)
        self.targets[target_index][3] = info
    return info


def _path_parts_after_sound(p: str) -> list[str]:
    """返回路径中第一个 'sound' 之后的 parts（不包含 sound）。

    - 若包含 sound：E:\\...\\sound\\a\\b.wav -> ['a', 'b.wav']
    - 若不包含 sound：保持原样切分（相对路径时也能工作）
    """
    # 兼容 Windows 路径 '\\' 与可能出现的 '/'
    parts = [x for x in re.split(r"[\\/]+", str(p)) if x]
    lower_parts = [x.lower() for x in parts]
    if "sound" in lower_parts:
        idx = lower_parts.index("sound")
        return parts[idx + 1 :]
    return parts


def _clean_user_path(text: str) -> str:
    """清洗用户输入的路径字符串：去空白、去成对引号。"""
    if text is None:
        return ""
    t = str(text).strip()
    # 处理用户粘贴时带的引号
    if len(t) >= 2 and ((t[0] == '"' and t[-1] == '"') or (t[0] == "'" and t[-1] == "'")):
        t = t[1:-1].strip()
    return t


def _range_tags_from_target_path(target_path: str) -> set[str]:
    """从目标 path 提取“范围标签”。

    规则：
    - 路径中包含 sound：
      - sound 前一个分段作为包名标签（如 left4dead2_dlc1 / update）
      - sound 后面到文件名之前的每一层文件夹作为标签（跳过 sound 本身）
    - 不包含 sound：
      - 取第一个分段作为包名标签（若存在）
      - 其余到文件名之前作为标签

    注意：不添加 sound 标签，不添加文件名。
    """
    parts = [x for x in re.split(r"[\\/]+", str(target_path)) if x]
    if not parts:
        return set()

    lower_parts = [p.lower() for p in parts]
    tags: set[str] = set()

    if "sound" in lower_parts:
        sidx = lower_parts.index("sound")
        if sidx - 1 >= 0:
            tags.add(parts[sidx - 1])
        # sound 后的文件夹层级（不含文件名）
        for p in parts[sidx + 1 : -1]:
            if p and p.lower() != "sound":
                tags.add(p)
    else:
        # 没有 sound：尽量保守处理
        tags.add(parts[0])
        for p in parts[1:-1]:
            if p and p.lower() != "sound":
                tags.add(p)

    return tags


def _apply_target_list_filters(self, *, search_text: str | None = None, range_tag: str | None = None) -> None:
    """应用目标列表过滤：搜索框 + 范围下拉框，二者同时生效。"""
    if not hasattr(self, "targetListWidget"):
        return

    st = (search_text or "").strip().lower()
    rt = (range_tag or "").strip()
    if rt in ("", "全部"):
        rt = ""

    self.targetListWidget.setUpdatesEnabled(False)
    try:
        for i in range(self.targetListWidget.count()):
            item = self.targetListWidget.item(i)
            target_index = item.data(Qt.UserRole)
            if target_index is None:
                continue

            visible = True
            if st:
                visible = st in self._target_search_haystack[target_index]
            if visible and rt:
                tags = self._target_range_tags[target_index] if hasattr(self, "_target_range_tags") else set()
                visible = rt in tags

            item.setHidden(not visible)
    finally:
        self.targetListWidget.setUpdatesEnabled(True)


def _format_target_info_text(self, target_index: int) -> str:
    """把目标的音频信息格式化为 UI 可读文本。"""
    try:
        tid, name, tpath, _ = self.targets[target_index]
    except Exception:
        return "目标信息不可用"

    def row(k: str, v) -> str:
        return f"<b>{html.escape(str(k))}</b> {html.escape(str(v))}"

    lines = [
        row("name:", name),
        row("path:", tpath),
    ]

    try:
        info = _ensure_target_info_loaded(self, target_index)
    except Exception as e:
        lines.append(row("info:", f"解析失败 ({e})"))
        return "<br>".join(lines)

    if isinstance(info, dict) and "error" in info:
        lines.append(row("info:", info.get("error")))
        return "<br>".join(lines)

    try:
        fmt = info.get("format", {}) if isinstance(info, dict) else {}
        streams = info.get("streams", []) if isinstance(info, dict) else []
        s0 = streams[0] if streams else {}

        lines.append(row("format:", fmt.get("format_name", "")))
        lines.append(row("codec:", s0.get("codec_name", "")))
        lines.append(row("channels:", s0.get("channels", "")))
        lines.append(row("sample_rate:", s0.get("sample_rate", "")))
        lines.append(row("bit_rate:", fmt.get("bit_rate", "")))
        lines.append(row("duration:", fmt.get("duration", "")))
    except Exception as e:
        lines.append(row("info:", f"展示失败 ({e})"))

    return "<br>".join(lines)


def updateCurrentTargetInfoDisplay(self, item: QListWidgetItem | None) -> None:
    """更新右侧控制面板中的“目标音频信息”显示。"""
    if not hasattr(self, "targetInfoLabel") or self.targetInfoLabel is None:
        return

    if item is None:
        self.targetInfoLabel.setText("未选择目标")
        return

    idx = item.data(Qt.UserRole)
    if idx is None:
        self.targetInfoLabel.setText("未选择目标")
        return

    try:
        text = _format_target_info_text(self, int(idx))
    except Exception:
        text = "目标信息不可用"
    self.targetInfoLabel.setText(text)


def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(".").resolve() / relative_path


def openFileDialog(self, LineEdit: QLineEdit):
    """打开文件对话框，将选择的文件路径写入LineEdit

    Args:
        LineEdit (QLineEdit): 文件路径将被写入的LineEdit

    Returns:
        str: 返回选择的文件路径
    """
    #打开文件对话框
    file_dialog = QFileDialog(self)
    # 常见音频 + 容器格式（ffmpeg 可读取并抽取音轨）；保留 All Files 兜底
    media_filter = (
        "媒体文件 ("
        "*.wav *.mp3 *.ogg *.flac *.aac *.m4a *.wma *.aiff *.aif *.opus "
        "*.mp4 *.m4v *.mkv *.webm *.mov *.avi *.flv *.wmv *.mpg *.mpeg *.3gp *.ts *.m2ts"
        ");;All Files (*)"
    )
    file_path, _ = file_dialog.getOpenFileNames(self, "选择文件", "", media_filter)
    if file_path:
        # 自动为路径加引号，避免空格等导致用户复制/编辑出错
        LineEdit.setText(";".join([f'"{p}"' for p in file_path]))
    return file_path


def openDirDialog(self, LineEdit: QLineEdit):
    """打开目录选择对话框，将选择的目录路径写入LineEdit"""
    directory = QFileDialog.getExistingDirectory(self, "选择输出目录", "")
    if directory:
        # 自动加引号，保持与 filePath 一致
        LineEdit.setText(f'"{directory}"')
    return directory


def updateListWidget(self, LineEdit: QLineEdit, ListWidget: QListWidget):
    """将LineEdit中的文件路径依据";"同步到ListWidget中

    Args:
        LineEdit (QLineEdit): 文件路径来源
        ListWidget (QListWidget): 被同步的ListWidget
    """
    ListWidget.clear()
    file_path = [p for p in LineEdit.text().split(";") if p]
    for fpath in file_path: #检测文件是否存在，存在则添加到ListWidget
        cleaned = _clean_user_path(fpath)
        if cleaned and path.exists(cleaned):
            ListWidget.addItem(cleaned)


def generateCheckbox(self, db_path: str):
    """读取数据库，生成复选框

    Args:
        db_path (str): 数据库路径，一般为resource_path("dicGenerate/Audio.db")
    """
    # 使用 QListWidget 替代海量 QCheckBox widgets：加载更快，搜索过滤也更轻量
    self.targetListWidget = QListWidget()
    self.targetListWidget.setUniformItemSizes(True)
    self.targetListWidget.setAlternatingRowColors(False)
    self.targetListWidget.itemChanged.connect(lambda item: _on_target_item_changed(self, item))
    self.scrollArea.setWidget(self.targetListWidget)

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM targets")
        rows = cur.fetchall()
    finally:
        conn.close()

    # targets 结构: [id, name, path, info]，其中 info 初始保持为 JSON 字符串（按需解析）
    self.targets = [list(row) for row in rows]

    # 预构建搜索用的 haystack，避免每次搜索重复 lower/split
    self._target_search_haystack = []
    # 预构建范围筛选用的 tags：target_index -> set[str]
    self._target_range_tags = []
    # target_index -> QListWidgetItem，便于差量更新勾选状态
    self._target_items_by_index = [None] * len(self.targets)
    self._ui_checked_targets = set()

    self.targetListWidget.blockSignals(True)
    try:
        self.targetListWidget.clear()
        for index in range(len(self.targets)):
            name = self.targets[index][1]
            tpath = self.targets[index][2]
            lpath = _path_parts_after_sound(tpath)
            tooltip = "\\".join(lpath)

            item = QListWidgetItem(str(name))
            item.setToolTip(tooltip)
            item.setData(Qt.UserRole, index)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            # 初始不隐藏（兼容原逻辑中 searchState/columnState 的默认可见）
            item.setHidden(False)
            self.targetListWidget.addItem(item)

            self._target_search_haystack.append((str(name) + " " + str(tpath)).lower())
            self._target_range_tags.append(_range_tags_from_target_path(tpath))
            self._target_items_by_index[index] = item
    finally:
        self.targetListWidget.blockSignals(False)

    # 兼容旧变量（其他函数会读取）
    self.checkboxes = []
    self.searchState = [1] * len(self.targets)
    self.columnState = [1] * len(self.targets)


def initTargetRangeComboBox(self) -> None:
    """初始化 targetSort_ComboBox：按路径生成“范围”筛选项。"""
    if not hasattr(self, "targetSort_ComboBox"):
        return
    if not hasattr(self, "_target_range_tags"):
        return

    # 汇总所有标签
    all_tags: set[str] = set()
    for tags in self._target_range_tags:
        all_tags.update(tags)

    # 包名优先按常见顺序展示，其余按字母排序
    pkg_order = ["left4dead2", "update", "left4dead2_dlc1", "left4dead2_dlc2", "left4dead2_dlc3"]
    pkgs = [p for p in pkg_order if p in all_tags]
    rest = sorted([t for t in all_tags if t not in set(pkgs)], key=lambda s: s.lower())
    items = ["全部"] + pkgs + rest

    self.targetSort_ComboBox.blockSignals(True)
    try:
        self.targetSort_ComboBox.clear()
        self.targetSort_ComboBox.addItems(items)
        # 默认“全部”
        self._target_range_filter_tag = ""
        self.targetSort_ComboBox.setCurrentIndex(0)
    finally:
        self.targetSort_ComboBox.blockSignals(False)


def onTargetRangeChanged(self, text: str) -> None:
    """范围下拉框变化：刷新目标列表显示。"""
    self._target_range_filter_tag = text or ""
    # 合并当前搜索条件
    current_search = ""
    if hasattr(self, "searchBar_target") and self.searchBar_target is not None:
        try:
            current_search = self.searchBar_target.text()
        except Exception:
            current_search = ""
    _apply_target_list_filters(self, search_text=current_search, range_tag=self._target_range_filter_tag)


def _on_target_item_changed(self, item: QListWidgetItem) -> None:
    """处理目标列表勾选变更，同步到当前计划。"""
    if not hasattr(self, "plans") or not self.plans:
        return
    if not hasattr(self, "activePlan"):
        return
    idx = item.data(Qt.UserRole)
    if idx is None:
        return
    checked = item.checkState() == Qt.Checked
    self.plans[self.activePlan].target[idx] = 2 if checked else 0
    if checked:
        self.plans[self.activePlan].selected_targets.add(idx)
        if hasattr(self, "_ui_checked_targets"):
            self._ui_checked_targets.add(idx)
    else:
        self.plans[self.activePlan].selected_targets.discard(idx)
        if hasattr(self, "_ui_checked_targets"):
            self._ui_checked_targets.discard(idx)


# def addTree(self,path: list):
#     for i in range(6,len(path)-1):
#         item = QStandardItem(path[i])
#         if item not in self.subroot:
#             for j in range(len(self.subroot)):
#                 if path[i-1] == self.subroot[j].text():
#                     break
#             parrent = self.subroot[j]
#             parrent.appendRow(item)
#             self.subroot.append(item)


def createPlan(self, ListWidget: QListWidget):
    """根据ListWidget中的文件路径生成计划(self.plans)

    Args:
        ListWidget (QListWidget): 输入音频文件路径的ListWidget
    """
    self.file_path = getListWidgetItems(ListWidget)
    self.plans = [None] * ListWidget.count()
    for index in range(ListWidget.count()):
        self.plans[index] = SrcAudio(self.file_path[index], [0] * len(self.targets), 100)
    print(self.plans)
    setCheckbox(self)


def setCheckbox(self):
    """根据当前计划的target设置复选框的状态"""
    if not hasattr(self, "targetListWidget"):
        return
    # 差量更新：只更新发生变化的勾选项，避免每次切换计划都遍历几万条
    new_checked = getattr(self.plans[self.activePlan], "selected_targets", None)
    if new_checked is None:
        # 兜底：从 target 数组计算（会慢，但不影响功能）
        new_checked = {i for i, v in enumerate(self.plans[self.activePlan].target) if v == 2}
        self.plans[self.activePlan].selected_targets = set(new_checked)

    old_checked = getattr(self, "_ui_checked_targets", set())
    to_uncheck = old_checked - new_checked
    to_check = new_checked - old_checked

    self.targetListWidget.blockSignals(True)
    try:
        for idx in to_uncheck:
            item = self._target_items_by_index[idx] if hasattr(self, "_target_items_by_index") else None
            if item is not None:
                item.setCheckState(Qt.Unchecked)
        for idx in to_check:
            item = self._target_items_by_index[idx] if hasattr(self, "_target_items_by_index") else None
            if item is not None:
                item.setCheckState(Qt.Checked)
        self._ui_checked_targets = set(new_checked)
    finally:
        self.targetListWidget.blockSignals(False)


def getListWidgetItems(ListWidget: QListWidget) -> list:
    """获取ListWidget中的所有内容

    Args:
        ListWidget (QListWidget): 要获取内容的ListWidget

    Returns:
        list: 返回ListWidget中的所有内容
    """
    items = []
    for i in range(ListWidget.count()):
        items.append(ListWidget.item(i).text())
    return items


def changePlan(self, item: int):
    """更改当前计划

    Args:
        item (int): 被点击的ListWidget中的item的索引
    """
    self.activePlan = self.inputFiles.row(item)
    print(self.activePlan)
    print(self.plans[self.activePlan].path, self.plans[self.activePlan].target)
    setCheckbox(self)
    self.Volume_spinBox.setValue(self.plans[self.activePlan].volume)


# def readPlan(self):
#     for checkbox in self.checkboxes:
#         checkbox.setCheckState(self.plans[self.activePlan].target[self.checkboxes.index()])


def makePlan(self, id: int, checked: bool):
    """更改计划(self.plans)中的目标

    Args:
        id (int): 被更改的目标在targets中的索引
        checked (bool): 是否被选中
    """
    if checked:
        self.plans[self.activePlan].target[id] = 2
    else:
        self.plans[self.activePlan].target[id] = 0
    print(self.plans[self.activePlan].target)


# def readJson(jpath):
#     # path = Path(jpath)
#     with open(jpath, 'r', encoding='utf-8') as f:
#         targets = json.load(f)
#     return targets


def doPlan(self):
    """执行计划"""
    successCount = 0
    totalCount = 0
    inflict = checkPlan(self)
    output_root = getOutputRoot(self)
    if inflict:
        finishWindow = FinishWindow(self, successCount, totalCount, inflict, output_root)
        finishWindow.show()        
    else:
        for index in range(len(self.plans)):
            path = self.plans[index].path
            for j in range(len(self.plans[index].target)):
                if self.plans[index].target[j] == 2:
                    s, t = transAudio(self, path, j, index)
                    successCount += s
                    totalCount += t
        finishWindow = FinishWindow(self, successCount, totalCount, inflict, output_root)
        finishWindow.show()


def getOutputRoot(self) -> str:
    """获取输出根目录：与 creatFolder 使用同一套规则。"""
    base_output = "./output"
    if hasattr(self, "outputPath") and self.outputPath is not None:
        try:
            text = _clean_user_path(self.outputPath.text())
            if text:
                base_output = text
        except Exception:
            pass
    elif hasattr(self, "ouputPathLineEdit") and self.ouputPathLineEdit is not None:
        try:
            text = self.ouputPathLineEdit.toPlainText().strip().strip('"')
            if text:
                base_output = text
        except Exception:
            pass
    return base_output


def openOutputPath(self) -> None:
    """打开当前输出根目录。"""
    base_output = getOutputRoot(self)
    try:
        out_dir = Path(base_output).expanduser().resolve()
    except Exception:
        out_dir = Path("./output").resolve()

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass

    try:
        os.startfile(str(out_dir))
    except Exception:
        try:
            subprocess.Popen(["explorer", str(out_dir)])
        except Exception:
            return


def checkPlan(self):
    """检查所有计划中是否存在重复选择的目标"""
    AllTargets = [[] for _ in range(len(self.targets))]
    for index in range(len(self.plans)):
        for j in range(len(self.plans[index].target)):
            if self.plans[index].target[j] == 2:
                AllTargets[j].append(index)
    inflict = 0

    print(AllTargets)
    for i in range(len(AllTargets)):
        if len(AllTargets[i]) > 1:
            for j in range(len(AllTargets[i])):
                self.inputFiles.item(AllTargets[i][j]).setBackground(QColor(255, 0, 0))
            inflict = 1
    return inflict


# def getSystemLanguage(self):
#     system_locale = QLocale.system()
#     self.language = system_locale.name()


def transAudio(self, source: str , targetIndex: int, index: int) -> tuple:
    """使用ffmpeg执行音频转换任务

    Args:
        source (str): 将被转换的音频文件路径，用于ffmpeg的input
        targetIndex (int): 正在执行的转换任务在targets(ListWidget)中的索引
        index (int): 正在执行的转换任务在inputFiles(ListWidget)中的索引

    Returns:
        tuple: 返回成功转换的数量(0)和总数量(1)
    """
    successCount = 0
    totalCount = 0
    try:
        outputPath = str(creatFolder(self, targetIndex))
        original = Path(outputPath + "/" + str(self.targets[targetIndex][1].split("\\")[-1]))
        tmp = Path(outputPath + "/tmp.wav")
        tmp = Path(outputPath + "/tmp.wav")        
        # 获取参考文件的格式信息（按需解析/缓存）
        info = _ensure_target_info_loaded(self, targetIndex)
        format_name = info['format']['format_name']
        codec_name = info['streams'][0]['codec_name']
        channels = info['streams'][0]['channels']
        sample_rate = info['streams'][0]['sample_rate']
        bit_rate = info['format']['bit_rate']
        duration = info['format']['duration']
        volume_target = self.plans[index].volume/100

        if self.fadeInOutOption.isChecked():
            fade_in_duration = self.fadeInTime.value()
            fade_out_duration = self.fadeOutTime.value()
        else:
            fade_in_duration = fade_out_duration = 0

        # 使用 ffmpeg 将源文件转换为相同格式的目标文件
        if self.fadeInOutOption.isChecked() and (fade_in_duration != 0 or fade_out_duration != 0):
            if fade_in_duration == 0 and fade_out_duration != 0:
                fade_in_duration = 0.001
            if not self.timeConsistent.isChecked():
                source_duration = _duration_seconds(source)
                fade_out_start = max(0.0, float(source_duration) - float(fade_out_duration))
                ffmpeg_cmd = (
                    ffmpeg
                    .input(source)
                    .filter('afade', t='in', st=0, d=fade_in_duration)  # 淡入
                    .filter('afade', t='out', st=fade_out_start, d=fade_out_duration)  # 淡出
                    .filter('volume', volume=volume_target)
                    .output(
                        str(original),
                        format=format_name,
                        acodec=codec_name,
                        ac=channels,
                        ar=sample_rate,
                        bitrate=bit_rate,
                        y=None,
                        map_metadata=-1
                    )
                )
            else:
                ffmpeg_cmd = (
                    ffmpeg
                    .input(source)
                    .filter('afade', t='in', st=0, d=fade_in_duration)  # 淡入
                    .filter('afade', t='out', st=float(duration) - fade_out_duration, d=fade_out_duration)  # 淡出
                    .filter('volume', volume=volume_target)
                    .output(
                        str(original),
                        format=format_name,
                        acodec=codec_name,
                        ac=channels,
                        ar=sample_rate,
                        bitrate=bit_rate,
                        t=duration,
                        y=None,
                        map_metadata=-1
                    )
                )
        else:
            if not self.timeConsistent.isChecked():
                ffmpeg_cmd = (
                    ffmpeg
                    .input(source)
                    .output(
                        str(original),
                        format=format_name,
                        acodec=codec_name,
                        ac=channels,
                        ar=sample_rate,
                        bitrate=bit_rate,
                        y=None,
                        map_metadata=-1
                    )
                )
            else:
                ffmpeg_cmd = (
                    ffmpeg
                    .input(source)
                    .output(
                        str(original),
                        format=format_name,
                        acodec=codec_name,
                        ac=channels,
                        ar=sample_rate,
                        bitrate=bit_rate,
                        t=duration,
                        y=None,
                        map_metadata=-1
                    )
                )
            
        ffmpeg_cmd.run(cmd=_ffmpeg_executable())
        silence = resource_path("./blank_audio.wav")
        Concat_count = 0

        if self.timeConsistent.isChecked() and float(_duration_seconds(str(original))) < float(duration):
            while float(_duration_seconds(str(original))) < float(duration):

                if tmp.exists():
                    tmp.unlink()            
                original.rename(tmp)

                (
                    ffmpeg
                        .concat(ffmpeg.input(str(tmp)), ffmpeg.input(silence), v=0, a=1)
                        .output(str(original), format=format_name, acodec=codec_name, ac=channels, ar=sample_rate, bitrate=bit_rate, y=None)
                ).run(cmd=_ffmpeg_executable())
                Concat_count += 1
                if tmp.exists():
                    tmp.unlink()
            if tmp.exists():
                tmp.unlink()                    
            original.rename(tmp)
            ffmpeg.input(str(tmp)).output(str(original), format=format_name, acodec=codec_name, ac=channels, ar=sample_rate, bitrate=bit_rate,t=duration, y=None,map_metadata=-1).run(cmd=_ffmpeg_executable())
            if tmp.exists():
                tmp.unlink()            
        print(f"Concat {Concat_count} times")

        if tmp.exists():
            tmp.unlink()
        original.rename(tmp)
        with wave.open(str(tmp), 'rb') as infile:
            params = infile.getparams()
            frames = infile.readframes(params.nframes)
        with wave.open(str(original), 'wb') as outfile:
            outfile.setparams(params)
            outfile.writeframes(frames)
        tmp.unlink()                

            
        self.inputFiles.item(index).setBackground(QColor(170, 255, 127))
        successCount += 1
        totalCount += 1

    except ffmpeg.Error as e:
        print("Err")
        self.inputFiles.item(index).setBackground(QColor(221, 72, 42))
        totalCount += 1
    
    return successCount, totalCount


# def displayOptions(self, object, on):
#     for child in object.findChildren(QWidget):
#         child.setVisible(on)


def creatFolder(self, targetIndex: int) -> Path:
    """创建输出文件夹供ffmepg输出

    Args:
        targetIndex (int): 目标在targets中的索引

    Returns:
        Path: 返回创建的文件夹路径
    """
    base_output = getOutputRoot(self)

    parts_after_sound = _path_parts_after_sound(self.targets[targetIndex][2])
    folder_parts = parts_after_sound[:-1] if len(parts_after_sound) >= 2 else []
    out_path = Path(base_output).joinpath(*folder_parts)
    try:
        out_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        # 用户可能手动删坏/输入非法路径；回退到默认输出目录，避免任务整体失败
        out_path = Path("./output").joinpath(*folder_parts)
        out_path.mkdir(parents=True, exist_ok=True)
    print(out_path)
    return out_path


def searchInput(self, serachbar: QLineEdit, listWidget: QListWidget):
    """源音频文件搜索框

    Args:
        serachbar (QLineEdit): 搜索框
        listWidget (QListWidget): 要搜索的ListWidget
    """
    search = serachbar.text()
    if search != "":
        for i in range(listWidget.count()):
            listWidget.item(i).setHidden(search not in listWidget.item(i).text())
    else:
        for i in range(listWidget.count()):
            listWidget.item(i).setHidden(False)


def searchCheckBtn(self, serachbar: QLineEdit):
    """搜索复选框

    Args:
        serachbar (QLineEdit): 搜索框
    """
    text = serachbar.text().strip().lower()
    range_tag = getattr(self, "_target_range_filter_tag", "")
    _apply_target_list_filters(self, search_text=text, range_tag=range_tag)


def searchFilter(self):
    """根据搜索结果显示复选框"""
    # 旧实现基于 QCheckBox widgets；现在已切换为 QListWidget 过滤，保留空实现以兼容调用
    return


class FinishWindow(QDialog):
    """完成窗口"""
    def __init__(self, parent=None, successCount=0, totalCount=0, inflict=False, output_root: str = "./output"):
        super().__init__(parent)
        self.setWindowTitle("运行完毕")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self._output_root = output_root

        title = QLabel(self)
        title.setText("<b>转换完成</b>" if not inflict else "<b>存在冲突</b>")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px;")
        layout.addWidget(title)

        msg = QLabel(self)
        msg.setWordWrap(True)
        msg.setTextInteractionFlags(Qt.TextSelectableByMouse)
        if inflict:
            msg.setText("存在目标音频被重复选择，请检查红色标记的源文件。")
        else:
            failed = totalCount - successCount
            msg.setText(f"共有 {totalCount} 个任务，失败 {failed} 个。")
        layout.addWidget(msg)

        out = QLabel(self)
        out.setWordWrap(True)
        out.setTextInteractionFlags(Qt.TextSelectableByMouse)
        try:
            out_abs = str(Path(_clean_user_path(output_root)).expanduser().resolve())
        except Exception:
            out_abs = str(Path("./output").resolve())
        out.setText(f"<b>输出路径：</b><br>{html.escape(out_abs)}")
        layout.addWidget(out)

        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        btn_row.setSpacing(8)
        btn_row.addStretch(1)

        open_btn = QPushButton(self)
        open_btn.setText("打开输出路径")
        open_btn.clicked.connect(lambda: self._open_output_path())
        btn_row.addWidget(open_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

        # 初始最紧凑尺寸，但允许用户调整大小
        self.adjustSize()
        self.setMinimumSize(self.sizeHint())
        try:
            self.setSizeGripEnabled(True)
        except Exception:
            pass


    def _open_output_path(self) -> None:
        base_output = self._output_root or "./output"
        try:
            out_dir = Path(_clean_user_path(base_output)).expanduser().resolve()
        except Exception:
            out_dir = Path("./output").resolve()
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        try:
            os.startfile(str(out_dir))
        except Exception:
            try:
                subprocess.Popen(["explorer", str(out_dir)])
            except Exception:
                return


def updateVolume(self, i: int):
    """更新音量

    Args:
        i (int): 音量值
    """
    self.plans[self.activePlan].volume = i


def get_audio_duration(file_path):
    with wave.open(file_path, 'rb') as wave_file:
        frames = wave_file.getnframes()
        rate = wave_file.getframerate()
        duration = frames / float(rate)
        return duration



# def generateCombobox(self):
#     self.Path_treeView = QTreeView()
#     self.Path_itemModel = QStandardItemModel()
#     self.Path_itemModel.setHorizontalHeaderLabels(['路径'])

#     root = self.Path_itemModel.invisibleRootItem() 
#     # item0 = QStandardItem('left4dead2')
#     # item1 = QStandardItem('left4dead2_dlc1')
#     # item2 = QStandardItem('left4dead2_dlc2')
#     # item3 = QStandardItem('left4dead2_dlc3')
#     self.subroot = [QStandardItem('left4dead2'),QStandardItem('left4dead2_dlc1'),QStandardItem('left4dead2_dlc2'),QStandardItem('left4dead2_dlc3')]
#     # root.appendRow([item0])
#     # root.appendRow([item1])
#     # root.appendRow([item2])
#     # root.appendRow([item3])
#     root.appendRows(self.subroot)

#     self.Path_treeView.setModel(self.Path_itemModel)

#     self.targetSort_ComboBox.setView(self.Path_treeView)
#     self.targetSort_ComboBox.setModel(self.Path_itemModel)
