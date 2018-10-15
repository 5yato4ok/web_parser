#!/usr/bin/env python
# -*- coding: utf-8 -*-
from main import Gipfel_Parser
import sys
from PyQt4 import QtGui, uic,QtCore

qtCreatorFile = "gui.ui"
Ui_MainWindow, QtBaseClass= uic.loadUiType(qtCreatorFile)

class EmittingStream(QtCore.QObject):
    textWritten = QtCore.pyqtSignal(str)
    def write(self, text):
        self.textWritten.emit(str(text))

#TODO: run parser in different thread. but get somehow text
class QThread1(QtCore.QThread):
    sig1 = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

class Widget(QtGui.QMainWindow, Ui_MainWindow):
    timeout = 0
    logging = True

    def normalOutputWritten(self, text):
        """Append text to the QTextEdit."""
        # Maybe QTextEdit.append() works as well, but this is how I do it:
        cursor = self.plainTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.plainTextEdit.setTextCursor(cursor)
        self.plainTextEdit.ensureCursorVisible()
        self.MainWindow.update()

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.setupUi(self)
        self.logging = self.radioButton.isChecked()
        self.spinBox.setValue(0)
        self.pushButton.clicked.connect(self.on_btn_clicked)
        self.spinBox.valueChanged.connect(self.spinval_changed)
        self.radioButton.toggled.connect(self.radiobox_changed)


    def __del__(self):
        # Restore sys.stdout
        sys.stdout = sys.__stdout__

    def radiobox_changed(self,val):
        self.logging = val

    def spinval_changed(self,val):
        self.timeout = val

    def on_btn_clicked(self):
        smth = 2
        test_class = Gipfel_Parser('https://gipfel.ru','https://gipfel.ru/catalog',self.timeout,self.logging)
        test_class.parse_catalog()
        test_class.write_to_txml('result.xml')

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())