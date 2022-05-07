import sys

import pyperclip
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QStandardItem
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel, QSqlQueryModel
import re
import yaml
from PyQt5.QtWidgets import QWidget, QMenu, QHBoxLayout, QPushButton, QLineEdit, QLabel, QSplitter, QTableView, \
    QHeaderView, QVBoxLayout, QMessageBox, QApplication, QMainWindow, QFileDialog

settings = yaml.safe_load(open('settings.yaml'))

class DataGrid(QWidget):
    def __init__(self,title_name,table_name,parent=None):
        super(DataGrid, self).__init__(parent=parent)
        self.setWindowTitle(title_name)
        self.table_name = table_name
        self.resize(750, 410)
        self.initializedModel()
        self.initUI()

    def initializedModel(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(settings['db'])
        if not self.db.open():
            return False
        # 当前页
        self.currentPage = 0
        # 总页数
        self.totalPage = 0
        # 总记录数
        self.totalRecrodCount = 0
        # 每页显示记录数
        self.PageRecordCount = 10
    def initUI(self):
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # 创建QMenu信号事件
        self.customContextMenuRequested.connect(self.showMenu)
        self.contextMenu = QMenu(self)
        self.CP = self.contextMenu.addAction('复制')
        self.CP.triggered.connect(self.copy)

        # 创建窗口
        self.createWindow()
        # 设置表格
        self.setTableView()
        # 信号槽连接
        self.prevButton.clicked.connect(self.onPrevButtonClick)
        self.nextButton.clicked.connect(self.onNextButtonClick)
        self.switchPageButton.clicked.connect(self.onSwitchPageButtonClick)
        self.exportButton.clicked.connect(self.openExportDir)



    def createWindow(self):
        # 操作布局
        operatorLayout = QHBoxLayout()
        self.prevButton = QPushButton("前一页")
        self.nextButton = QPushButton("后一页")
        self.switchPageButton = QPushButton("Go")
        self.switchPageLineEdit = QLineEdit()
        self.switchPageLineEdit.setFixedWidth(40)
        self.exportButton = QPushButton("导出")


        switchPage = QLabel("转到第")
        page = QLabel("页")
        operatorLayout.addWidget(self.prevButton)
        operatorLayout.addWidget(self.nextButton)
        operatorLayout.addWidget(switchPage)
        operatorLayout.addWidget(self.switchPageLineEdit)
        operatorLayout.addWidget(page)
        operatorLayout.addWidget(self.switchPageButton)
        operatorLayout.addWidget(QSplitter())
        operatorLayout.addStretch(1)
        operatorLayout.addWidget(self.exportButton)

        # 状态布局
        statusLayout = QHBoxLayout()
        self.totalPageLabel = QLabel()
        self.totalPageLabel.setFixedWidth(70)
        self.currentPageLabel = QLabel()
        self.currentPageLabel.setFixedWidth(70)

        self.totalRecordLabel = QLabel()
        self.totalRecordLabel.setFixedWidth(70)

        statusLayout.addWidget(self.totalPageLabel)
        statusLayout.addWidget(self.currentPageLabel)
        statusLayout.addWidget(QSplitter())
        statusLayout.addWidget(self.totalRecordLabel)

        # 设置表格属性
        self.tableView = QTableView()
        # 表格宽度的自适应调整
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 创建界面
        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(operatorLayout)
        mainLayout.addWidget(self.tableView)
        mainLayout.addLayout(statusLayout)
        self.setLayout(mainLayout)

    def setTableView(self):
        # 声明查询模型
        self.queryModel = QSqlQueryModel(self)
        # 设置模型
        self.tableView.setModel(self.queryModel)
        # 设置当前页
        self.currentPage = 1
        # 得到总记录数
        self.totalRecrodCount = self.getTotalRecordCount()
        # 得到总页数
        self.totalPage = self.getPageCount()
        # 刷新状态
        self.updateStatus()
        # 设置总页数文本
        self.setTotalPageLabel()
        # 设置总记录数
        self.setTotalRecordLabel()
        # 查询第一页
        self.recordQuery(0)

    # 得到记录数
    def getTotalRecordCount(self):
        self.queryModel.setQuery("select * from %s"%self.table_name,self.db)
        rowCount = self.queryModel.rowCount()
        return rowCount
    # 记录查询
    def recordQuery(self, limitIndex):
        szQuery = ("select * from %s limit %d,%d" % (self.table_name
                                                     ,limitIndex, self.PageRecordCount))
        self.queryModel.setQuery(szQuery,self.db)
    # 设置总数页文本

    def setTotalPageLabel(self):
        szPageCountText = ("总共%d页" % self.totalPage)
        self.totalPageLabel.setText(szPageCountText)

    # 设置总记录数
    # 得到页数
    def getPageCount(self):
        if self.totalRecrodCount % self.PageRecordCount == 0:
            return (self.totalRecrodCount / self.PageRecordCount)
        else:
            return (self.totalRecrodCount // self.PageRecordCount + 1)
    def setTotalRecordLabel(self):
        szTotalRecordText = ("共%d条" % self.totalRecrodCount)
        self.totalRecordLabel.setText(szTotalRecordText)

    # 刷新状态
    def updateStatus(self):
        # 设置按钮是否可用
        if self.currentPage == 1:
            self.prevButton.setEnabled(False)
            self.nextButton.setEnabled(True)
        elif self.currentPage == self.totalPage:
            self.prevButton.setEnabled(True)
            self.nextButton.setEnabled(False)
        else:
            self.prevButton.setEnabled(True)
            self.nextButton.setEnabled(True)
        szCurrentText = ("当前第%d页" % self.currentPage)
        self.currentPageLabel.setText(szCurrentText)



    # 前一页按钮按下
    def onPrevButtonClick(self):
        limitIndex = (self.currentPage - 2) * self.PageRecordCount
        self.recordQuery(limitIndex)
        self.currentPage -= 1
        self.updateStatus()

        # 后一页按钮按下

    def onNextButtonClick(self):
        limitIndex = self.currentPage * self.PageRecordCount
        self.recordQuery(limitIndex)
        self.currentPage += 1
        self.updateStatus()

    # 转到页按钮按下

    def onSwitchPageButtonClick(self):
        # 得到输入字符串
        szText = self.switchPageLineEdit.text()

        # 得到页数
        pageIndex = int(szText)
        # 判断是否有指定页
        if pageIndex > self.totalPage or pageIndex < 1:
            QMessageBox.information(self, "提示", "没有指定的页面，请重新输入")
            return

        # 得到查询起始行号
        limitIndex = (pageIndex - 1) * self.PageRecordCount

        # 记录查询
        self.recordQuery(limitIndex)
        # 设置当前页
        self.currentPage = pageIndex
        # 刷新状态
        self.updateStatus()

    def exportToCsv(self):
        from sqlalchemy import create_engine
        import pandas as pd
        import os
        # 参数字段 sqlite:///<database path>
        engine = create_engine('sqlite:///'+settings['db'])
        data = pd.read_sql(self.table_name,engine)
        data.to_csv(os.path.join(self.export_directory_path,self.table_name+'.csv'))
    def openExportDir(self):
        self.export_directory_path = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      "./")
        if self.export_directory_path:
            self.exportToCsv()
            QMessageBox.information(self,"提示","导出成功")

    def selected_tb_text(self):
        try:
            indexes = self.tableView.selectedIndexes()  # 获取表格对象中被选中的数据索引列表
            indexes_dict = {}
            for index in indexes:  # 遍历每个单元格
                row, column = index.row(), index.column()  # 获取单元格的行号，列号
                if row in indexes_dict.keys():
                    indexes_dict[row].append(column)
                else:
                    indexes_dict[row] = [column]
            # 将数据表数据用制表符(\t)和换行符(\n)连接，使其可以复制到excel文件中
            text = []
            for row, columns in indexes_dict.items():
                row_data = []
                for column in columns:
                    data = self.tableView.model().data(self.tableView.model().index(row, column))
                    row_data.append(str(data))
                text.append('\t'.join(row_data))
            return '\n'.join(text)
        except BaseException as e:
            print(e)
            return e

    def copy(self):
        text = self.selected_tb_text()  # 获取当前表格选中的数据
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            # pyperclip.copy(text) # 复制数据到粘贴板


    def showMenu(self, pos):
        # pos 鼠标位置
        # 菜单显示前,将它移动到鼠标点击的位置
        self.contextMenu.exec_(QCursor.pos())  # 在鼠标位置显示

    def keyPressEvent(self, event):  # 重写键盘监听事件
        # 监听 CTRL+C 组合键，实现复制数据到粘贴板
        if (event.key() == Qt.Key_C) and QApplication.keyboardModifiers() == Qt.ControlModifier:
            self.copy()  # 获取当前表格选中的数据
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        # 关闭数据库
        self.db.close()

        # 创建窗口



if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 创建窗口
    example = DataGrid("快手用户信息","KSUserData")
    # 显示窗口
    example.show()
    sys.exit(app.exec_())