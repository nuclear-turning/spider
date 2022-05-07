import os
import sys

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QEventLoop, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QCheckBox, \
    QFileDialog, QMessageBox, QGroupBox, QApplication
from KSVS_Moudle.utils.KSVS import runGetUserDetail,runGetUserId
from KSVS_Moudle.utils.DataGrid import DataGrid

class UserDetailThread(QThread):
    user_detail_signal = pyqtSignal(str)
    def __init__(self,data=None, parent=None):
        super(UserDetailThread, self).__init__(parent)
        self.data = data

    def write(self, text):
        self.user_detail_signal.emit(str(text))  # 发射信号

    def run(self):
        runGetUserId()
        print("userID抓取完成，开始抓取用户信息")
        runGetUserDetail()
        print("用户信息抓取完成")
        self.exit(0)  # 关闭线程
    def stop(self):
        os._exit(0)
class getUserDetailTab(QWidget):
    def __init__(self):
        super(getUserDetailTab, self).__init__()
        self.resize(500,300)
        self.initUI()

    def initUI(self):
        self.processBar()
        self.process = QTextEdit(self, readOnly=True)
        self.process.ensureCursorVisible()
        self.process.setLineWrapColumnOrWidth(1000)
        self.process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.process_layout)
        main_layout.addWidget(self.process)
        self.setLayout(main_layout)
    def dataBox(self):
        self.data_box = QGroupBox("数据",self)
        self.data_box.setFlat(True)
        data_layout = QVBoxLayout()
        self.show_file_layout = QHBoxLayout()
        self.process_file_layout = QHBoxLayout()
        self.filePathlineEdit = QLineEdit(self)
        self.filePathlineEdit.setObjectName("filePathlineEdit")
        self.open_file_button = QPushButton("导入数据", self)
        self.open_file_button.clicked.connect(self.openFile)
        self.check_import_box = QCheckBox(self)
        from KSVS_Moudle.utils.importToDb import KSUserData
        if KSUserData.table_exists():
            self.check_import_box.setChecked(True)
            self.open_file_button.setDisabled(True)
        else:
            self.check_import_box.setChecked(False)
            self.open_file_button.setDisabled(False)
        self.check_import_box.setDisabled(True)
        self.show_file_layout.addWidget(self.filePathlineEdit)
        self.show_file_layout.addWidget(self.check_import_box)
        clean_db_button = QPushButton("清空数据",self)
        clean_db_button.clicked.connect(self.cleanFile)
        self.process_file_layout.addWidget(self.open_file_button)
        self.process_file_layout.addWidget(clean_db_button)
        self.process_file_layout.addStretch(0.1)
        self.process_file_layout.setSpacing(20)

        data_layout.addLayout(self.show_file_layout)
        data_layout.addLayout(self.process_file_layout)
        data_layout.setSpacing(10)
        self.data_box.setLayout(data_layout)

    def runBox(self):
        run_layout = QVBoxLayout()
        self.run_box = QGroupBox("运行",self)
        self.run_box.setFlat(True)
        show_user_detail_button = QPushButton("查看用户信息", self)
        show_user_detail_button.clicked.connect(self.showUserDetail)
        get_user_detail_button = QPushButton("开始抓取", self)
        get_user_detail_button.clicked.connect(self.crawlUserDetail)
        run_layout.addWidget(self.data_box)
        run_layout.addWidget(get_user_detail_button)
        run_layout.addWidget(show_user_detail_button)
        # self.top_layout.addWidget(stop_user_detail_button)
        run_layout.setSpacing(10)
        self.run_box.setLayout(run_layout)
    def processBar(self):
        self.dataBox()
        self.runBox()
        self.process_layout = QHBoxLayout()
        self.process_layout.addWidget(self.data_box)
        self.process_layout.addWidget(self.run_box)
        self.process_layout.setStretch(0,3)
        self.process_layout.setStretch(1,1)
    def openFile(self):
        # self.filePathlineEdit.setText(str(get_directory_path))
        self.get_filename_path, ok = QFileDialog.getOpenFileName(self,
                                                            "选取单个文件",
                                                            "../basicdata",
                                                            "All Files (*);;Text Files (*.txt)")
        if ok:
            self.filePathlineEdit.setText(str(self.get_filename_path))
            from KSVS_Moudle.utils.importToDb import importUserName2Db
            import_success = importUserName2Db(str(self.get_filename_path))
            if import_success:
                QMessageBox.information(self,"提示","成功导入数据！",QMessageBox.Ok)
                self.check_import_box.setChecked(True)
            else:
                QMessageBox.information(self, "提示", "导入失败，请检查数据！",QMessageBox.Ok)
                self.check_import_box.setChecked(False)
    def cleanFile(self):
        from KSVS_Moudle.utils.importToDb import db,KSUserData,KSVideoData
        db.drop_tables((KSUserData,KSVideoData))
        if not db.table_exists(KSUserData) and not db.table_exists(KSVideoData):
            QMessageBox.information(self, "提示", "数据已清空!")
            self.check_import_box.setChecked(False)
            self.open_file_button.setDisabled(False)
    def onUpdateUserDetailText(self, text):
        cursor = self.process.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()

    def crawlUserDetail(self):
        try:
            self.user_detail_th = UserDetailThread()
            self.user_detail_th.user_detail_signal.connect(self.onUpdateUserDetailText)
            sys.stdout = self.user_detail_th
            self.user_detail_th.start()
        except Exception as e:
            raise e
        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec_()
    def showUserDetail(self):
        self.dg = DataGrid("用户信息","KSUserData")
        self.dg.show()
    def stopCrawlUserDetail(self):
        # self.user_detail_th.stop()
        os._exit(0)
    def changeEvent(self, a0: QtCore.QEvent) -> None:
        pass
    # def closeEvent(self, event):
    #     """Shuts down application on close."""
    #     # Return stdout to defaults.
    #     sys.stdout = sys.__stdout__
    #     super().closeEvent(event)