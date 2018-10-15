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
    timeout = 0
    logging = False
    textWritten_ = QtCore.pyqtSignal(str)

    def __init__(self, timeout_,logging_,parent=None):
        QtCore.QThread.__init__(self, parent)
        self.timeout = timeout_
        self.logging = logging_

    def run(self):
        test_class = Gipfel_Parser('https://gipfel.ru', 'https://gipfel.ru/catalog',
                                   self.timeout, self.logging)
        test_class.textWritten.connect(self.textWritten_)

        test_class.parse_catalog()
        test_class.write_to_txml('result.xml')

class Widget(QtGui.QMainWindow, Ui_MainWindow):
    timeout = 0
    logging = True
    done = QtCore.pyqtSignal()

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
        self.logging = self.radioButton.isChecked()
        self.spinBox.setValue(0)
        self.pushButton.clicked.connect(self.on_btn_clicked)
        self.spinBox.valueChanged.connect(self.spinval_changed)
        self.radioButton.toggled.connect(self.radiobox_changed)

    def radiobox_changed(self,val):
        self.logging = val

    def spinval_changed(self,val):
        self.timeout = val

    def done(self):
        self.pushButton.setEnabled(True)

    def on_btn_clicked(self):
        self.pushButton.setEnabled(False)
        thread = QThread1(timeout_=self.timeout, logging_=self.logging)
        thread.textWritten_.connect(self.normalOutputWritten)
        self.connect(thread, QtCore.SIGNAL("finished()"), self.done)
        thread.start()



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())