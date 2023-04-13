# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'detect.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(982, 746)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(320, 5, 71, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(320, 355, 71, 31))
        self.label_2.setObjectName("label_2")
        self.graphicsView = QtWidgets.QGraphicsView(Form)
        self.graphicsView.setGeometry(QtCore.QRect(62, 32, 611, 321))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView_2 = QtWidgets.QGraphicsView(Form)
        self.graphicsView_2.setGeometry(QtCore.QRect(60, 390, 611, 321))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(700, 130, 231, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(700, 170, 231, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(700, 230, 131, 51))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(700, 300, 131, 51))
        self.pushButton_2.setObjectName("pushButton_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "速度监测系统"))
        self.label.setText(_translate("Form", "动态监测"))
        self.label_2.setText(_translate("Form", "二值化视角"))
        self.lineEdit.setPlaceholderText(_translate("Form", "请输入速度上限"))
        self.lineEdit_2.setPlaceholderText(_translate("Form", "请输入速度下限"))
        self.pushButton.setText(_translate("Form", "导入视频"))
        self.pushButton_2.setText(_translate("Form", "开始监测"))

