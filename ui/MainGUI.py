from PySide6.QtWidgets import QWidget, QApplication, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QFont
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from pathlib import Path
from func import *
from Ui_Main import Ui_Form


class MyWindow(QWidget, Ui_Form):
    def _quote_path(self, p: str) -> str:
        p = str(p).strip()
        if not p:
            return p
        # 避免重复加引号
        if len(p) >= 2 and p[0] == '"' and p[-1] == '"':
            return p
        return f'"{p}"'

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 加大“执行”按钮字体
        try:
            f = QFont(self.start.font())
            f.setPointSize(max(14, f.pointSize() + 4))
            self.start.setFont(f)
        except Exception:
            pass
        # 初始化变量
        self.targets = []
        self.plans = []
        self.searchState = []
        self.columnState = []
        self.activePlan = 0
        self.checkboxes = []
        self.existedPath = []
        self.subroot = []

        # 隐藏未实现控件
        # 输出路径：改为顶栏统一设置（与文件选择同一层级）
        self.label_6.hide()
        self.ouputPathLineEdit.hide()
        self.vpkpacking.hide()
        # getSystemLanguage(self)
        # self.targetSort_ComboBox.hide() 
        self.searchBar_input.setText("")
        self.searchBar_target.setText("")

        # 启用拖拽导入文件
        self.setAcceptDrops(True)
        self.filePath.setAcceptDrops(True)
        self.inputFiles.setAcceptDrops(True)
        self.filePath.installEventFilter(self)
        self.inputFiles.installEventFilter(self)

        db_path = resource_path("dicGenerate/Audio.db")
        # generateCombobox(self)
        generateCheckbox(self, db_path) # 生成复选框
        initTargetRangeComboBox(self)

        # 在“设置(optionBox)”上方显示当前选中目标的音频信息
        self.targetInfoBox = QGroupBox(self.scrollAreaWidgetContents_2)
        self.targetInfoBox.setTitle("目标音频信息")
        targetInfoLayout = QVBoxLayout(self.targetInfoBox)
        targetInfoLayout.setContentsMargins(6, 6, 6, 6)
        targetInfoLayout.setSpacing(4)
        self.targetInfoLabel = QLabel(self.targetInfoBox)
        self.targetInfoLabel.setWordWrap(True)
        self.targetInfoLabel.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.targetInfoLabel.setTextFormat(Qt.RichText)
        self.targetInfoLabel.setText("未选择目标")
        targetInfoLayout.addWidget(self.targetInfoLabel)

        try:
            # 插到 optionBox 之前（同一栏上方）
            self.verticalLayout_4.insertWidget(0, self.targetInfoBox)
        except Exception:
            pass

        # 绑定：点击/切换目标时更新信息
        if hasattr(self, "targetListWidget") and self.targetListWidget is not None:
            self.targetListWidget.currentItemChanged.connect(
                lambda cur, prev: updateCurrentTargetInfoDisplay(self, cur)
            )
            self.targetListWidget.itemClicked.connect(
                lambda item: updateCurrentTargetInfoDisplay(self, item)
            )

        # 顶栏改为纵向两行：
        # 1) 文件路径 + 选择文件
        # 2) 输出路径 + 选择输出路径
        self.outputPath = QLineEdit(self)
        self.outputPath.setPlaceholderText("输出路径")
        self.outputPath.setText("./output")
        self.outputChooseBtn = QPushButton(self)
        self.outputChooseBtn.setText("选择输出路径")
        self.outputOpenBtn = QPushButton(self)
        self.outputOpenBtn.setText("打开输出路径")

        # 把原 horizontalLayout_2 替换成 topBarWidget(QVBoxLayout)
        topBarWidget = QWidget(self)
        topBarLayout = QVBoxLayout(topBarWidget)
        topBarLayout.setContentsMargins(0, 0, 0, 0)
        topBarLayout.setSpacing(6)

        fileRow = QHBoxLayout()
        fileRow.setSpacing(6)
        outputRow = QHBoxLayout()
        outputRow.setSpacing(6)

        # 从旧布局中移除并重新加入（避免一个控件同时属于多个 layout）
        try:
            self.horizontalLayout_2.removeWidget(self.filePath)
            self.horizontalLayout_2.removeWidget(self.fileChooseBtn)
        except Exception:
            pass

        fileRow.addWidget(self.filePath)
        fileRow.addWidget(self.fileChooseBtn)
        outputRow.addWidget(self.outputPath)
        outputRow.addWidget(self.outputChooseBtn)
        outputRow.addWidget(self.outputOpenBtn)

        topBarLayout.addLayout(fileRow)
        topBarLayout.addLayout(outputRow)

        # 替换 gridLayout_2 的第 0 行布局
        try:
            self.gridLayout_2.removeItem(self.horizontalLayout_2)
        except Exception:
            pass
        self.gridLayout_2.addWidget(topBarWidget, 0, 0, 1, 1)
        
        # self.targetSort_ComboBox.addItem("按文件名排序")
        # 选择文件按钮绑定事件 更新LineEdit：filePath，用textChanged事件更新ListWidget：inputFiles
        self.fileChooseBtn.clicked.connect(lambda:openFileDialog(self,self.filePath)) 
        self.outputChooseBtn.clicked.connect(lambda: openDirDialog(self, self.outputPath))
        self.outputOpenBtn.clicked.connect(lambda: openOutputPath(self))
        self.filePath.textChanged.connect(lambda: updateListWidget(self, self.filePath, self.inputFiles))
        self.filePath.textChanged.connect(lambda: createPlan(self,self.inputFiles))
        self.inputFiles.itemClicked.connect(lambda item: changePlan(self, item))
        self.start.clicked.connect(lambda:doPlan(self))
        self.Volume_spinBox.valueChanged.connect(lambda i: updateVolume(self,i))                                                                                                                                                                                   

        # 隐藏子可选项
        self.fadeInOutOption.toggled.connect(lambda on:displayOptions(self,self.fadeInOutOption,on))
        self.vpkpacking.toggled.connect(lambda on:displayOptions(self,self.vpkpacking,on))
        # 搜索框绑定事件
        self.searchBar_input.textChanged.connect(lambda:searchInput(self,self.searchBar_input,self.inputFiles))
        self.searchBar_target.returnPressed.connect(lambda:searchCheckBtn(self,self.searchBar_target))
        self.targetSort_ComboBox.currentTextChanged.connect(lambda t: onTargetRangeChanged(self, t))

    def _merge_paths_to_filePath(self, new_paths: list[str]) -> None:
        """把拖入/选择的新路径合并进 filePath（; 分隔，去重，保序）。"""
        existing = [p for p in self.filePath.text().split(";") if p]
        seen = set(existing)
        merged = list(existing)
        for p in new_paths:
            qp = self._quote_path(p)
            if qp not in seen:
                merged.append(qp)
                seen.add(qp)
        self.filePath.setText(";".join(merged))


    def _paths_from_drop(self, event) -> list[str]:
        """从 drop event 中提取本地音频文件路径；目录会展开为其中的音频文件。"""
        mime = event.mimeData()
        result: list[str] = []

        # 常见可被 ffmpeg 读取的音频格式（按需可再加）
        audio_exts = {
            ".wav",
            ".mp3",
            ".ogg",
            ".flac",
            ".aac",
            ".m4a",
            ".wma",
            ".aiff",
            ".aif",
            ".opus",
            # 容器格式（ffmpeg 会抽取音轨）
            ".mp4",
            ".m4v",
            ".mkv",
            ".webm",
            ".mov",
            ".avi",
            ".flv",
            ".wmv",
            ".mpg",
            ".mpeg",
            ".3gp",
            ".ts",
            ".m2ts",
        }

        if mime is None:
            return result

        # Explorer 拖入通常是 urls
        if mime.hasUrls():
            for url in mime.urls():
                local = url.toLocalFile()
                if not local:
                    continue
                p = Path(local)
                if p.is_dir():
                    for f in p.rglob("*"):
                        if f.is_file() and f.suffix.lower() in audio_exts:
                            result.append(str(f))
                else:
                    if p.suffix.lower() in audio_exts:
                        result.append(str(p))

        # 兼容部分情况下以纯文本给路径
        elif mime.hasText():
            text = mime.text().strip().strip('"')
            if text:
                parts = [t.strip().strip('"') for t in text.splitlines() if t.strip()]
                for part in parts:
                    p = Path(part)
                    if p.exists() and p.is_dir():
                        for f in p.rglob("*"):
                            if f.is_file() and f.suffix.lower() in audio_exts:
                                result.append(str(f))
                    elif p.exists() and p.suffix.lower() in audio_exts:
                        result.append(str(p))

        return result


    def eventFilter(self, obj, event):
        # 仅拦截 filePath / inputFiles 的拖拽
        if obj in (self.filePath, self.inputFiles):
            if event.type() == QEvent.DragEnter:
                drag_event: QDragEnterEvent = event
                if drag_event.mimeData() and (drag_event.mimeData().hasUrls() or drag_event.mimeData().hasText()):
                    drag_event.acceptProposedAction()
                    return True
            if event.type() == QEvent.Drop:
                drop_event: QDropEvent = event
                paths = self._paths_from_drop(drop_event)
                if paths:
                    self._merge_paths_to_filePath(paths)
                drop_event.acceptProposedAction()
                return True
        return super().eventFilter(obj, event)


    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData() and (event.mimeData().hasUrls() or event.mimeData().hasText()):
            event.acceptProposedAction()


    def dropEvent(self, event: QDropEvent):
        paths = self._paths_from_drop(event)
        if paths:
            self._merge_paths_to_filePath(paths)
        event.acceptProposedAction()

        

if __name__ == "__main__":
    app = QApplication()
    window = MyWindow()
    # n = window.targets[0][2].split("\\")
    # window.targetSort_ComboBox.addItems(n)
    window.show()
    app.exec()

print("end")