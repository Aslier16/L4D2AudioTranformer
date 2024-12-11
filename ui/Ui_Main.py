# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Main.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QScrollArea, QSizePolicy,
    QSpinBox, QTextEdit, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(846, 689)
        self.gridLayout_2 = QGridLayout(Form)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(6)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.filePath = QLineEdit(Form)
        self.filePath.setObjectName(u"filePath")

        self.horizontalLayout_2.addWidget(self.filePath)

        self.fileChooseBtn = QPushButton(Form)
        self.fileChooseBtn.setObjectName(u"fileChooseBtn")
        self.fileChooseBtn.setMinimumSize(QSize(0, 0))
        self.fileChooseBtn.setBaseSize(QSize(0, 0))

        self.horizontalLayout_2.addWidget(self.fileChooseBtn)


        self.gridLayout_2.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.widget = QWidget(Form)
        self.widget.setObjectName(u"widget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(20)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.gridLayout_4 = QGridLayout(self.widget)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.searchBar_target = QLineEdit(self.widget)
        self.searchBar_target.setObjectName(u"searchBar_target")

        self.gridLayout_4.addWidget(self.searchBar_target, 0, 2, 1, 1)

        self.targetSort_ComboBox = QComboBox(self.widget)
        self.targetSort_ComboBox.setObjectName(u"targetSort_ComboBox")

        self.gridLayout_4.addWidget(self.targetSort_ComboBox, 1, 2, 1, 1)

        self.scrollArea = QScrollArea(self.widget)
        self.scrollArea.setObjectName(u"scrollArea")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy1)
        self.scrollArea.setMinimumSize(QSize(0, 0))
        self.scrollArea.setFrameShape(QFrame.Shape.StyledPanel)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 118, 567))
        self.gridLayout = QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_4.addWidget(self.scrollArea, 2, 2, 1, 1)

        self.inputFiles = QListWidget(self.widget)
        self.inputFiles.setObjectName(u"inputFiles")

        self.gridLayout_4.addWidget(self.inputFiles, 2, 0, 1, 1)

        self.searchBar_input = QLineEdit(self.widget)
        self.searchBar_input.setObjectName(u"searchBar_input")
        sizePolicy1.setHeightForWidth(self.searchBar_input.sizePolicy().hasHeightForWidth())
        self.searchBar_input.setSizePolicy(sizePolicy1)

        self.gridLayout_4.addWidget(self.searchBar_input, 0, 0, 2, 1)


        self.horizontalLayout.addWidget(self.widget)

        self.controlPannel = QScrollArea(Form)
        self.controlPannel.setObjectName(u"controlPannel")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.controlPannel.sizePolicy().hasHeightForWidth())
        self.controlPannel.setSizePolicy(sizePolicy2)
        self.controlPannel.setMinimumSize(QSize(300, 0))
        self.controlPannel.setWidgetResizable(True)
        self.controlPannel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.scrollAreaWidgetContents_2 = QWidget()
        self.scrollAreaWidgetContents_2.setObjectName(u"scrollAreaWidgetContents_2")
        self.scrollAreaWidgetContents_2.setGeometry(QRect(0, 0, 430, 636))
        self.verticalLayout_4 = QVBoxLayout(self.scrollAreaWidgetContents_2)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.optionBox = QGroupBox(self.scrollAreaWidgetContents_2)
        self.optionBox.setObjectName(u"optionBox")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.optionBox.sizePolicy().hasHeightForWidth())
        self.optionBox.setSizePolicy(sizePolicy3)
        self.optionBox.setMaximumSize(QSize(16777215, 270))
        self.optionBox.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.optionBox.setCheckable(False)
        self.gridLayout_3 = QGridLayout(self.optionBox)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setSizeConstraint(QLayout.SizeConstraint.SetDefaultConstraint)
        self.timeConsistent = QCheckBox(self.optionBox)
        self.timeConsistent.setObjectName(u"timeConsistent")
        font = QFont()
        font.setPointSize(10)
        self.timeConsistent.setFont(font)
        self.timeConsistent.setChecked(True)

        self.gridLayout_3.addWidget(self.timeConsistent, 0, 0, 1, 1)

        self.ouputPathLineEdit = QTextEdit(self.optionBox)
        self.ouputPathLineEdit.setObjectName(u"ouputPathLineEdit")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.ouputPathLineEdit.sizePolicy().hasHeightForWidth())
        self.ouputPathLineEdit.setSizePolicy(sizePolicy4)
        self.ouputPathLineEdit.setMinimumSize(QSize(0, 0))
        self.ouputPathLineEdit.setMaximumSize(QSize(16777215, 20))

        self.gridLayout_3.addWidget(self.ouputPathLineEdit, 2, 1, 1, 1)

        self.vpkpacking = QGroupBox(self.optionBox)
        self.vpkpacking.setObjectName(u"vpkpacking")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.vpkpacking.sizePolicy().hasHeightForWidth())
        self.vpkpacking.setSizePolicy(sizePolicy5)
        self.vpkpacking.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.vpkpacking.setCheckable(True)
        self.vpkpacking.setChecked(True)
        self.verticalLayout_3 = QVBoxLayout(self.vpkpacking)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_5 = QLabel(self.vpkpacking)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_5.addWidget(self.label_5)

        self.lineEdit = QLineEdit(self.vpkpacking)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout_5.addWidget(self.lineEdit)


        self.verticalLayout_3.addLayout(self.horizontalLayout_5)

        self.ifVpkOnly = QCheckBox(self.vpkpacking)
        self.ifVpkOnly.setObjectName(u"ifVpkOnly")

        self.verticalLayout_3.addWidget(self.ifVpkOnly)


        self.gridLayout_3.addWidget(self.vpkpacking, 6, 0, 1, 2)

        self.fadeInOutOption = QGroupBox(self.optionBox)
        self.fadeInOutOption.setObjectName(u"fadeInOutOption")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.fadeInOutOption.sizePolicy().hasHeightForWidth())
        self.fadeInOutOption.setSizePolicy(sizePolicy6)
        self.fadeInOutOption.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.fadeInOutOption.setCheckable(True)
        self.fadeInOutOption.setChecked(True)
        self.verticalLayout_2 = QVBoxLayout(self.fadeInOutOption)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.fadeInOutOption)
        self.label.setObjectName(u"label")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy7)
        font1 = QFont()
        font1.setPointSize(12)
        self.label.setFont(font1)

        self.horizontalLayout_3.addWidget(self.label)

        self.fadeInTime = QDoubleSpinBox(self.fadeInOutOption)
        self.fadeInTime.setObjectName(u"fadeInTime")

        self.horizontalLayout_3.addWidget(self.fadeInTime)

        self.label_3 = QLabel(self.fadeInOutOption)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font1)

        self.horizontalLayout_3.addWidget(self.label_3)


        self.verticalLayout_2.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.label_2 = QLabel(self.fadeInOutOption)
        self.label_2.setObjectName(u"label_2")
        sizePolicy7.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy7)
        self.label_2.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_2)

        self.fadeOutTime = QDoubleSpinBox(self.fadeInOutOption)
        self.fadeOutTime.setObjectName(u"fadeOutTime")
        sizePolicy3.setHeightForWidth(self.fadeOutTime.sizePolicy().hasHeightForWidth())
        self.fadeOutTime.setSizePolicy(sizePolicy3)

        self.horizontalLayout_4.addWidget(self.fadeOutTime)

        self.label_4 = QLabel(self.fadeInOutOption)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setFont(font1)

        self.horizontalLayout_4.addWidget(self.label_4)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)


        self.gridLayout_3.addWidget(self.fadeInOutOption, 4, 0, 1, 2)

        self.label_6 = QLabel(self.optionBox)
        self.label_6.setObjectName(u"label_6")
        sizePolicy6.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy6)
        self.label_6.setMaximumSize(QSize(16777215, 20))
        self.label_6.setFont(font)

        self.gridLayout_3.addWidget(self.label_6, 2, 0, 1, 1)

        self.Volume_spinBox = QSpinBox(self.optionBox)
        self.Volume_spinBox.setObjectName(u"Volume_spinBox")
        self.Volume_spinBox.setMaximum(1000)
        self.Volume_spinBox.setValue(100)

        self.gridLayout_3.addWidget(self.Volume_spinBox, 1, 1, 1, 1)

        self.label_7 = QLabel(self.optionBox)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setFont(font)

        self.gridLayout_3.addWidget(self.label_7, 1, 0, 1, 1)


        self.verticalLayout_4.addWidget(self.optionBox)

        self.start = QPushButton(self.scrollAreaWidgetContents_2)
        self.start.setObjectName(u"start")
        sizePolicy8 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy8.setHorizontalStretch(0)
        sizePolicy8.setVerticalStretch(0)
        sizePolicy8.setHeightForWidth(self.start.sizePolicy().hasHeightForWidth())
        self.start.setSizePolicy(sizePolicy8)
        self.start.setMaximumSize(QSize(16777215, 380))

        self.verticalLayout_4.addWidget(self.start)

        self.controlPannel.setWidget(self.scrollAreaWidgetContents_2)

        self.horizontalLayout.addWidget(self.controlPannel)


        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"L4D2 \u81ea\u52a8\u97f3\u9891\u8f6c\u6362\u5de5\u5177", None))
        self.filePath.setPlaceholderText(QCoreApplication.translate("Form", u"\u6587\u4ef6\u8def\u5f84", None))
        self.fileChooseBtn.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6587\u4ef6", None))
        self.searchBar_target.setText("")
        self.searchBar_target.setPlaceholderText(QCoreApplication.translate("Form", u"\u8f93\u5165\u97f3\u9891\u540d\u4ee5\u8fdb\u884c\u68c0\u7d22", None))
        self.targetSort_ComboBox.setPlaceholderText(QCoreApplication.translate("Form", u"\u7c7b\u578b", None))
        self.searchBar_input.setPlaceholderText(QCoreApplication.translate("Form", u"\u641c\u7d22", None))
#if QT_CONFIG(whatsthis)
        self.optionBox.setWhatsThis("")
#endif // QT_CONFIG(whatsthis)
        self.optionBox.setTitle(QCoreApplication.translate("Form", u"\u8bbe\u7f6e", None))
        self.timeConsistent.setText(QCoreApplication.translate("Form", u"\u662f\u5426\u63a7\u5236\u65f6\u957f\u76f8\u540c", None))
        self.vpkpacking.setTitle(QCoreApplication.translate("Form", u"\u662f\u5426\u81ea\u52a8\u5c01\u5305\u4e3avpk", None))
        self.label_5.setText(QCoreApplication.translate("Form", u"vpk.exe\u8def\u5f84:", None))
        self.ifVpkOnly.setText(QCoreApplication.translate("Form", u"\u4ec5\u4fdd\u7559vpk\uff1f", None))
        self.fadeInOutOption.setTitle(QCoreApplication.translate("Form", u"\u6de1\u5165\u6de1\u51fa", None))
        self.label.setText(QCoreApplication.translate("Form", u"\u6de1\u5165", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"\u79d2", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"\u6de1\u51fa", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"\u79d2", None))
        self.label_6.setText(QCoreApplication.translate("Form", u"\u8f93\u51fa\u8def\u5f84:", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"\u97f3\u91cf\u767e\u5206\u6bd4", None))
        self.start.setText(QCoreApplication.translate("Form", u"\u6267\u884c", None))
    # retranslateUi

