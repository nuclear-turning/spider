# -*- coding: utf-8 -*-
# @Author: turning
# @Date  :  2021/12/23
import json
import sys

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMessageBox, QApplication

class LoginCookieView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        super(LoginCookieView, self).__init__(*args, **kwargs)
        self.page().profile().cookieStore().deleteAllCookies()
        QWebEngineView.__init__(self) #初始化WebEngine
        self.ua = ""
        self.cookies = {}

        self.page().profile().cookieStore().cookieAdded.connect(self.onCookieAdd) #获取cookie
        # self.loadFinished.connect(self.getCookie)settings = yaml.safe_load(open('settings.yaml', encoding='utf8'))
        self.setWindowTitle('登录快手') #设置窗口标题
        self.resize(1300, 700) #设置窗口大小


    def open(self,url):
        self.load(QUrl(url))
        self.show()

    def onCookieAdd(self,cookie):
        name = cookie.name().data().decode('utf-8')
        value = cookie.value().data().decode('utf-8')
        self.cookies[name] = value


    def closeEvent(self, event):  # 主窗口退出全部退出
        if self.cookies.get("userId",0):
            import yaml
            settings = yaml.safe_load(open('settings.yaml', encoding='utf8'))
            settings['cookies'] = self.cookies
            # settings['headers']['User-Agent'] = str(self.ua.random)
            yaml.safe_dump(settings,open('settings.yaml','w',encoding='utf8'),encoding="utf8")
            QMessageBox.information(self, "登录提示", "登录成功!")
        else:
            QMessageBox.information(self, "登录提示", "请扫码二维码登录!", QMessageBox.Ok)
            # event.ignore()
# 程序入口
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 创建主窗口
    view = LoginCookieView()
    view.open("http://www.kuaishou.com")
    # 运行应用，并监听事件
    sys.exit(app.exec_())
