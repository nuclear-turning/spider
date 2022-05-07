import os
import sys
from PyQt5.QtWidgets import QMainWindow, QPushButton, QWidget, QApplication, QDesktopWidget, QVBoxLayout, \
    QHBoxLayout,QStackedWidget
from KSVS_Moudle.MainPage import KSVSWidget
from KSVS_Moudle.utils.ScanLogin import LoginCookieView

class SpiderMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("数据抓取界面（author by：Turning）")
        self.resize(800,500)
        self.center()

        self.login_button = QPushButton("登录", self)
        self.login_button.clicked.connect(self.showLoginView)
        self.ks_button = QPushButton('快手抓取', self)
        self.ks_button.clicked.connect(self.goToKSVS)
        # self.gzh_button = QPushButton('公众号抓取', self)
        # self.gzh_button.clicked.connect(self.goToGZH)

        self.setLeftPanel() #侧面板
        self.setMainPanel() #主面板
        self.login_view = LoginCookieView()


    def setMainPanel(self):
        self.right_widget = QStackedWidget()
        self.right_widget.setObjectName("mainTab")

        self.right_widget.addWidget(KSVSWidget()) #添加快手抓取界面
        # self.right_widget.addWidget(QWidget()) #添加公众号抓取界面

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.left_widget)
        main_layout.addWidget(self.right_widget)
        main_layout.setStretch(0, 40)
        main_layout.setStretch(1, 200)
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def setLeftPanel(self):
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.login_button)
        left_layout.addWidget(self.ks_button)
        # left_layout.addWidget(self.gzh_button)
        left_layout.addStretch(5)
        left_layout.setSpacing(20)
        self.left_widget = QWidget()
        self.left_widget.setLayout(left_layout)

    def goToKSVS(self):
        self.right_widget.setCurrentIndex(0)
    # def goToGZH(self):
    #     self.right_widget.setCurrentIndex(1)

    def showLoginView(self):
        self.login_view.open("http://www.kuaishou.com")

    def center(self):  # 定义一个函数使得窗口居中显示
        # 获取屏幕坐标系
        screen = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        size = self.geometry()
        newLeft = (screen.width() - size.width()) / 2
        newTop = (screen.height() - size.height()) / 2
        self.move(int(newLeft), int(newTop))

    def closeEvent(self, event): #主窗口退出全部退出
        sys.stdout = sys.__stdout__
        os._exit(0)
        sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.aboutToQuit.connect(app.deleteLater)
    mainView = SpiderMain()
    mainView.show()
    sys.exit(app.exec_())