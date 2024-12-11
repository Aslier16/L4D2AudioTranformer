from PySide6.QtWidgets import QFileDialog, QCheckBox, QWidget, QGridLayout, QVBoxLayout, QButtonGroup
from PySide6.QtWidgets import QDialog, QLabel
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QLocale
from os import path
import json
import ffmpeg
from pathlib import Path
# import subprocess
import sqlite3
import threading
import sys
import wave

class SrcAudio:
    def __init__(self, path, target=[], volume=100):
        self.path = path
        self.target = target
        self.volume = volume


def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    if hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / relative_path
    return Path(".").resolve() / relative_path


def openFileDialog(self, LineEdit):
    #打开文件对话框
    file_dialog = QFileDialog(self)
    file_path, _ = file_dialog.getOpenFileNames(self, "选择文件", "", "All Files (*)")
    if file_path:
        LineEdit.setText(";".join(file_path))
    return file_path


def updateListWidget(self, LineEdit, ListWidget):
    ListWidget.clear()
    file_path = LineEdit.text().split(";")
    for fpath in file_path: #检测文件是否存在，存在则添加到ListWidget
        if path.exists(fpath):
            ListWidget.addItem(fpath)


def generateCheckbox(self, db_path):
    #设定滚动区域布局
    self.scrollAreaWidget = QWidget()
    self.scrollArea.setWidget(self.scrollAreaWidget)
    self.scrollAreaLayout = QVBoxLayout()
    self.scrollAreaWidget.setLayout(self.scrollAreaLayout)

    self.checkboxTargets = QButtonGroup(self)
    self.checkboxTargets.setExclusive(False)
    self.checkboxTargets.idToggled.connect(lambda id,cheked:makePlan(self, id, cheked))

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT * FROM targets")
    self.targets = cur.fetchall()

    modified_targets = []
    for index in range(len(self.targets)):
        target_list = list(self.targets[index])
        target_list[3] = json.loads(target_list[3])
        modified_targets.append(tuple(target_list))
    self.targets = modified_targets

    #根据Targets列表生成选项
    for index in range(len(self.targets)):
        checkbox = QCheckBox(self.targets[index][1])
        checkbox = QCheckBox(self.targets[index][1])
        checkbox.setToolTip("\\".join(self.targets[index][2].split("\\")[5:]))
        checkbox.hide()
        self.checkboxTargets.addButton(checkbox, index)
        self.scrollAreaLayout.addWidget(checkbox)
        self.checkboxes = self.checkboxTargets.buttons()
        print(f"Checkbox {self.targets[index][1]} created")

    self.searchState = [1]*len(self.checkboxes)
    self.columnState = [1]*len(self.checkboxes)


def createPlan(self, ListWidget):
    self.file_path = getListWidgetItems(ListWidget)
    self.plans = [None] * ListWidget.count()
    for index in range(ListWidget.count()):
        self.plans[index] = SrcAudio(self.file_path[index], [0] * len(self.targets), 100)
    print(self.plans)
    setCheckbox(self)


def setCheckbox(self):
    for index in range(len(self.checkboxes)):
        if self.plans[self.activePlan].target[index] == 0:
            self.checkboxes[index].setCheckState(Qt.Unchecked)
        if self.plans[self.activePlan].target[index] == 2:
            self.checkboxes[index].setCheckState(Qt.Checked)


def getListWidgetItems(ListWidget):
    items = []
    for i in range(ListWidget.count()):
        items.append(ListWidget.item(i).text())
    return items


def changePlan(self, item):
    self.activePlan = self.inputFiles.row(item)
    print(self.activePlan)
    print(self.plans[self.activePlan].path, self.plans[self.activePlan].target)
    setCheckbox(self)
    self.Volume_spinBox.setValue(self.plans[self.activePlan].volume)


def readPlan(self):
    for checkbox in self.checkboxes:
        checkbox.setCheckState(self.plans[self.activePlan].target[self.checkboxes.index()])


def makePlan(self, id, checked):
    if checked:
        self.plans[self.activePlan].target[id] = 2
    else:
        self.plans[self.activePlan].target[id] = 0
    print(self.plans[self.activePlan].target)


def readJson(jpath):
    # path = Path(jpath)
    with open(jpath, 'r', encoding='utf-8') as f:
        targets = json.load(f)
    return targets


def doPlan(self):
    successCount = 0
    totalCount = 0
    inflict = checkPlan(self)
    if inflict:
        finishWindow = FinishWindow(self, successCount, totalCount, inflict)
        finishWindow.show()        
    else:
        for index in range(len(self.plans)):
            path = self.plans[index].path
            for j in range(len(self.plans[index].target)):
                if self.plans[index].target[j] == 2:
                    successCount += transAudio(self, path, j, index)[0]
                    totalCount += transAudio(self, path, j, index)[1]
        finishWindow = FinishWindow(self, successCount, totalCount, inflict)
        finishWindow.show()


def checkPlan(self):
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


def getSystemLanguage(self):
    system_locale = QLocale.system()
    self.language = system_locale.name()


def transAudio(self, source, targetIndex, index):
    successCount = 0
    totalCount = 0
    try:
        outputPath = str(creatFolder(self, targetIndex))
        original = Path(outputPath + "/" + str(self.targets[targetIndex][1].split("\\")[-1]))
        tmp = Path(outputPath + "/tmp.wav")
        tmp = Path(outputPath + "/tmp.wav")        
        # 获取参考文件的格式信息
        format_name = self.targets[targetIndex][3]['format']['format_name']
        codec_name = self.targets[targetIndex][3]['streams'][0]['codec_name']
        channels = self.targets[targetIndex][3]['streams'][0]['channels']
        sample_rate = self.targets[targetIndex][3]['streams'][0]['sample_rate']
        bit_rate = self.targets[targetIndex][3]['format']['bit_rate']
        duration = self.targets[targetIndex][3]['format']['duration']
        volume_target = self.plans[index].volume/100

        # exception = ["Jukebox", "Concert"]

        if self.fadeInOutOption.isChecked():
            fade_in_duration = self.fadeInTime.value()
            fade_out_duration = self.fadeOutTime.value()
        else:
            fade_in_duration, fade_out_duration = 0
        # 使用 ffmpeg 将源文件转换为相同格式的目标文件

        if not self.timeConsistent.isChecked():
            ffmpeg_cmd = (
                ffmpeg
                .input(source)
                .filter('afade', t='in', st=0, d=fade_in_duration)  # 淡入
                .filter('afade', t='out', st=float(ffmpeg.probe(source)['format']['duration']) - fade_out_duration, d=fade_out_duration)  # 淡出
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

        ffmpeg_cmd.run()
        silence = resource_path("./blank_audio.wav")
        Concat_count = 0

        if self.timeConsistent.isChecked() and float(ffmpeg.probe(original)['format']['duration']) < float(duration):
            while float(ffmpeg.probe(original)['format']['duration']) < float(duration):

                if tmp.exists():
                    tmp.unlink()            
                original.rename(tmp)

                (
                    ffmpeg
                        .concat(ffmpeg.input(str(tmp)), ffmpeg.input(silence), v=0, a=1)
                        .output(str(original), format=format_name, acodec=codec_name, ac=channels, ar=sample_rate, bitrate=bit_rate, y=None)
                ).run()
                Concat_count += 1
                if tmp.exists():
                    tmp.unlink()
            if tmp.exists():
                tmp.unlink()                    
            original.rename(tmp)
            ffmpeg.input(str(tmp)).output(str(original), format=format_name, acodec=codec_name, ac=channels, ar=sample_rate, bitrate=bit_rate,t=duration, y=None,map_metadata=-1).run()
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


def displayOptions(self, object, on):
    for child in object.findChildren(QWidget):
        child.setVisible(on)


def creatFolder(self, targetIndex):
    temp = "./output/" + "/".join(self.targets[targetIndex][2].split("\\")[6:-1])
    path = Path(temp)
    path.mkdir(parents=True, exist_ok=True)
    print(path)
    return path


def searchInput(self, serachbar, listWidget):
    search = serachbar.text()
    if search != "":
        for i in range(listWidget.count()):
            listWidget.item(i).setHidden(search not in listWidget.item(i).text())
    else:
        for i in range(listWidget.count()):
            listWidget.item(i).setHidden(False)


def searchCheckBtn(self, serachbar):
    text = serachbar.text()

    def searchText(self, text, rangeAssembled):
        if text != "":
            for i in rangeAssembled:
                if text in self.targets[i][2]:
                    self.searchState[i] = 1
                else:
                    self.searchState[i] = 0
        else:
            for i in range(len(self.searchState)):
                self.searchState[i] = 0
    
    sliceSize = 12800
    threadNum = len(self.checkboxes) // sliceSize + 1
    tlock = threading.Lock()
    threads = []
    for i in range(threadNum):
        if i != threadNum - 1:
            t = threading.Thread(target=searchText, args=(self, text, range(i*sliceSize, (i+1)*sliceSize)))
        else:
            t = threading.Thread(target=searchText, args=(self, text, range(i*sliceSize, len(self.checkboxes))))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    searchFilter(self)


def searchFilter(self):
    for i in range(len(self.checkboxes)):
        if self.searchState[i] == 0 or self.columnState[i] == 0:
            self.checkboxes[i].hide()
        else:
            self.checkboxes[i].show()


class FinishWindow(QDialog):
    def __init__(self, parent=None, successCount=0, totalCount=0, inflict=False):
        super().__init__(parent)
        self.setWindowTitle("运行完毕")
        self.setGeometry(50, 50, 300, 200)
        layout = QGridLayout()

        if inflict:
            self.label = QLabel("存在目标音频被重复选择", self)
            layout.addWidget(self.label)
        else:
            self.label = QLabel(f"转换完毕，共有{totalCount}个任务，{totalCount - successCount}个失败\n查看程序根目录以找到转换后的音频", self)
            layout.addWidget(self.label)

        self.label.setStyleSheet("font-size: 18px;")
        self.label.setAlignment(Qt.AlignCenter)

        self.setLayout(layout)


def updateVolume(self, i):
    self.plans[self.activePlan].volume = i