import sys
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTabWidget,QApplication

from KSVS_Moudle.tabs.GetUserDetailTab import getUserDetailTab
from KSVS_Moudle.tabs.DownVideoTab import downVideoTab


class KSVSWidget(QWidget):
    def __init__(self):
        super(KSVSWidget, self).__init__()
        # self.resize(800,500)
        self.initUI()
        # self.topBar()
    def initUI(self):
        main_layout = QHBoxLayout(self)
        self.tab_widget = QTabWidget(self)
        self.get_user_detail_tab = getUserDetailTab()
        self.down_video_tab = downVideoTab()
        self.tab_widget.addTab(self.get_user_detail_tab, "获取用户信息")
        self.tab_widget.addTab(self.down_video_tab, "下载视频")
        main_layout.addWidget(self.tab_widget)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainView = KSVSWidget()
    mainView.show()
    sys.exit(app.exec_())

