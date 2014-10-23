#!/usr/bin/python
# -*- coding: utf8 -*-

import sys

from PyQt4 import QtCore, QtGui
from PyKDE4.kdeui import KLineEdit

import os
import shutil

reload(sys)
sys.setdefaultencoding('utf8')

#path_to_iso = os.path.join(os.environ['HOME'], 'ISO')
pcsx2_bin = 'pcsx2'
path_to_pcsx2cfg = os.path.join(os.environ['HOME'], '.config', 'pcsx2', 'inis')
path_to_profiler = os.path.join(os.environ['HOME'], '.config', 'pcsx2profiler')

app = QtGui.QApplication(sys.argv)

class popup_msg(QtGui.QDialog):
    def __init__(self, parent, msg, title="Oops!"):
        QtGui.QDialog.__init__(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setObjectName('message')
        #self.setStyleSheet('#message{border-radius: 5px; border: 1px solid grey;}')
        self.resize(300, 120)

        resolution = parent.geometry()
        self.move(resolution.x() + (resolution.width()/2 - self.geometry().width()/2),
                  resolution.y() + (resolution.height()/2 - self.geometry().height()/2)/3)

        self.mainLayout = QtGui.QVBoxLayout()

        self.groupBox = QtGui.QGroupBox(self)
        self.groupBox.setGeometry(QtCore.QRect(0, 0, 300, 120))

        self.title = QtGui.QLabel(title, self.groupBox)
        self.title.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Maximum)
        self.msg = QtGui.QLabel(msg, self.groupBox)
        self.msg.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.line = QtGui.QFrame(self.groupBox)
        self.line.setGeometry(QtCore.QRect(7, 20, 401, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)

        #self.line = QtGui.QWidget(self)
        #self.line.setStyleSheet('border: 1px solid grey;')
        #self.line.setGeometry(320, 150, 118, 3)
        #self.line.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Maximum)

        self.mainLayout.addWidget(self.title, 1)
        self.mainLayout.addWidget(self.line, 1)
        self.mainLayout.addWidget(self.msg, 1)

        self.setLayout(self.mainLayout)

        self.show()

class MainWindow(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        if not os.path.exists(path_to_profiler):
            os.mkdir(path_to_profiler)

        self.resize(500, 300)
        self.setWindowTitle('PCSX2 Profiler')


        self.mainLayout = QtGui.QVBoxLayout()

        self.line0 = QtGui.QHBoxLayout()

        self.profileName = KLineEdit(self)
        self.profileName.setClearButtonShown(True)
        self.profileName.setClickMessage('Profile name')
        self.line0.addWidget(self.profileName, 1)

        self.btnAddNew = QtGui.QPushButton('Create', self)
        self.line0.addWidget(self.btnAddNew)

        self.list = QtGui.QListWidget(self)

        self.line1 = QtGui.QHBoxLayout()
        self.btnRemove = QtGui.QPushButton('Remove selected', self)
        self.btnActivate = QtGui.QPushButton('Activate selected', self)
        self.btnRun = QtGui.QPushButton('Run PCSX2', self)
        self.line1.addWidget(self.btnActivate)
        self.line1.addWidget(self.btnRun)
        self.line1.addWidget(self.btnRemove)

        self.label = QtGui.QLabel('Create profile from current settings', self)
        self.label.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)

        self.label2 = QtGui.QLabel('Profiles list', self)
        self.label2.setSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)

        self.mainLayout.addWidget(self.label, 1)
        self.mainLayout.addLayout(self.line0, 1)
        self.mainLayout.addWidget(self.label2, 1)
        self.mainLayout.addWidget(self.list, 1)
        self.mainLayout.addLayout(self.line1, 1)

        self.setLayout(self.mainLayout)

        self.btnAddNew.clicked.connect(self.add_new)
        self.btnRemove.clicked.connect(self.remove_selected)
        self.btnActivate.clicked.connect(self.activate_selected)
        self.btnRun.clicked.connect(self.run_selected)

        self.fill_profile_list()

    def clean_profile_name(self, name_string):
        return str(name_string)

    def fill_profile_list(self):
        profiles = os.listdir(path_to_profiler)
        for item in profiles:
            self.list.addItem(item)

    def add_new(self):
        if len(self.profileName.text()) > 0:
            profile_name = self.clean_profile_name(self.profileName.text())
            if not os.path.exists(os.path.join(path_to_profiler, profile_name)):
                self.list.addItem(profile_name)
                new_path = os.path.join(path_to_profiler, profile_name)
                shutil.copytree(path_to_pcsx2cfg, new_path)
                self.profileName.clear()
            else:
                self.msg = popup_msg(self, 'Profile with such name already exists!')
        else:
            self.msg = popup_msg(self, 'Profile name can`t be empty!!!')

    def remove_selected(self):
        if self.list.currentRow() > -1:
            msg = "Remove selected profile?"
            reply = QtGui.QMessageBox.question(self, 'Remove', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                profile_name = str(self.list.currentItem().text())
                path_to = os.path.join(path_to_profiler, profile_name)

                shutil.rmtree(path_to)
                self.list.takeItem(self.list.currentRow())
        else:
            self.msg = popup_msg(self, 'No item selected')

    def activate_selected(self):
        if self.list.currentRow() > -1:
            msg = "Activate selected profile?"
            reply = QtGui.QMessageBox.question(self, 'Activate', msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            if reply == QtGui.QMessageBox.Yes:
                shutil.rmtree(path_to_pcsx2cfg)
                shutil.copytree(os.path.join(path_to_profiler, str(self.list.currentItem().text())), path_to_pcsx2cfg)
            return str(self.list.currentItem().text())
        else:
            self.msg = popup_msg(self, 'No item selected')

    def run_selected(self):
        self.activate_selected()
        QtCore.QProcess.startDetached(pcsx2_bin)

root = MainWindow()
root.show()
sys.exit(app.exec_())
