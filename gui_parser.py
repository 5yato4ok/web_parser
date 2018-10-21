#!/usr/bin/env python
# -*- coding: utf-8 -*-
from main import Gipfel_Parser
import sys
from PyQt4 import QtGui, uic,QtCore
import time


qtCreatorFile = "gui.ui"
Ui_MainWindow, QtBaseClass= uic.loadUiType(qtCreatorFile)

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

#TODO: run parser in different thread. but get somehow text
class QThread1(QtCore.QThread):
    sig1 = QtCore.pyqtSignal(str)
    timeout = 0
    logging = False
    every_day = False
    textWritten_ = QtCore.pyqtSignal(str)

    def __init__(self, timeout_ = False,logging_=False,every_day_ =False,parent=None):
        QtCore.QThread.__init__(self, parent)
        self.timeout = timeout_
        self.logging = logging_
        self.every_day = every_day_

    def run_parser(self):
        self.textWritten_.emit("Start parsing\n")
        test_class = Gipfel_Parser('https://gipfel.ru', 'https://gipfel.ru/catalog', self.timeout, self.logging)
        test_class.textWritten.connect(self.textWritten_)
        test_class.parse_catalog()
        self.textWritten_.emit("Parsing over\n")
        test_class.write_to_txml('result.xml')
        self.textWritten_.emit("Writing result over\n")

    def run(self):
        self.textWritten_.emit("Start thread\n")
        if self.every_day:
            while True:
                self.run_parser()
                time.sleep(86400) #sleep a day
        else:
            self.run_parser()



class Widget(QtGui.QMainWindow, Ui_MainWindow):
    timeout = 0
    logging = True
    every_day = False
    done = QtCore.pyqtSignal()
    thread = QThread1()

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.plainTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.plainTextEdit.setTextCursor(cursor)
        self.plainTextEdit.ensureCursorVisible()
        self.update()

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.logging = self.checkBox.isChecked()
        self.every_day = self.checkBox_2.isChecked()
        self.spinBox.setValue(0)
        self.pushButton.clicked.connect(self.on_btn_clicked)
        self.spinBox.valueChanged.connect(self.spinval_changed)
        self.checkBox.stateChanged.connect(self.radiobox_changed)
        self.checkBox_2.stateChanged.connect(self.radiobox2_changed)
        

    def radiobox2_changed(self,val):
        self.every_day = self.checkBox_2.isChecked()

    def radiobox_changed(self,val):
        self.logging =  self.checkBox.isChecked()

    def spinval_changed(self,val):
        self.timeout = val

    def done(self):
        self.pushButton.setEnabled(True)
        if self.every_day:
            self.on_btn_clicked()

    def on_btn_clicked(self):
        self.pushButton.setEnabled(False)
        self.thread = QThread1(timeout_=self.timeout, logging_=self.logging, every_day_=self.every_day)
        self.thread.textWritten_.connect(self.normalOutputWritten)
        self.connect(self.thread, QtCore.SIGNAL("finished()"), self.done)
        self.thread.start()




if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())