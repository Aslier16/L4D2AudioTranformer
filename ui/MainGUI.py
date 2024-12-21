from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt
from func import *
from Ui_Main import Ui_Form


class MyWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # 初始化变量
        self.targets = []
        self.plans = []
        self.searchState = []
        self.columnState = []
        self.activePlan = 0
        self.checkboxes = []
        # 隐藏未实现控件
        self.label_6.hide()
        self.ouputPathLineEdit.hide()
        self.vpkpacking.hide()
        # getSystemLanguage(self)
        self.targetSort_ComboBox.hide() 
        self.searchBar_input.setText("")
        self.searchBar_target.setText("")

        db_path = resource_path("dicGenerate/Audio.db")
        generateCheckbox(self, db_path) # 生成复选框

        # 选择文件按钮绑定事件 更新LineEdit：filePath，用textChanged事件更新ListWidget：inputFiles
        self.fileChooseBtn.clicked.connect(lambda:openFileDialog(self,self.filePath)) 
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
  

if __name__ == "__main__":
    app = QApplication()
    window = MyWindow()
    window.show()
    app.exec()
