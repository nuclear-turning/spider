import json
import sys
import time
import os
import requests
import yaml
from PyQt5.QtCore import QThread, pyqtSignal, QEventLoop, QTimer
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QCheckBox, QLineEdit, \
    QFileDialog, QMessageBox

from KSVS_Moudle.utils.DataGrid import DataGrid
from KSVS_Moudle.utils.DownProcessBar import PercentProgressBar
from KSVS_Moudle.utils.importToDb import KSVideoData, getNeededVideo, insertIntoVideo, updataVideoCounts, updataVideo


class downloadThread(QThread):
    get_url_signal = pyqtSignal(str)  # 创建信号
    download_proess_signal = pyqtSignal(int) #创建信号
    start_down_signal = pyqtSignal(str)
    video_id_signal = pyqtSignal(str)

    def __init__(self,down_dir):
        super(downloadThread, self).__init__()
        self.down_dir = down_dir
    def write(self, text):
        self.get_url_signal.emit(str(text))  # 发射信号
    def down(self,videoId,url,filepath,chunk_size):
        try:
            start = time.time()
            response = requests.get(url, stream=True)                #流下载模式
            offset = 0
            content_size = int(response.headers['content-length'])
            if response.status_code == 200:
                start_down_message = 'Start download,[File size]:{size:.2f} MB'.format(size=content_size / chunk_size / 1024)
                self.start_down_signal.emit(str(start_down_message))
                with open(filepath, 'wb') as file:
                    for data in response.iter_content(chunk_size=chunk_size):
                        if not data: break
                        file.seek(offset)
                        file.write(data)
                        offset = offset + len(data)
                        proess = offset / int(content_size) * 100
                        self.download_proess_signal.emit(int(proess))  # 发送信号
                end = time.time()
                stop_down_message = videoId+'下载完成!,times: %.2f秒' % (end - start)
                print(stop_down_message)
        except Exception as e:
            raise e
    def getVideoDetail(self,userId,feeds):
        details = []
        for feed in feeds:
            detail = {}
            detail["userId"] = userId
            detail["videoId"] = feed["photo"]["id"]
            detail["videoName"] = feed["photo"]["id"]
            detail["videoPath"] = "ks_video/" + detail["userId"] + "/" + feed["photo"]["id"] + '.mp4'
            detail["videoDuration"] = feed["photo"]["duration"]
            detail["videoRatio"] = feed["photo"]["videoRatio"]
            detail["caption"] = feed["photo"]["caption"]
            detail["likeCount"] = feed["photo"]["likeCount"]
            detail["realLikeCount"] = feed["photo"]["realLikeCount"]
            detail["videoDownloadUrl"] = feed["photo"]["photoUrl"]
            if feed.get("tags", 0):
                tags = []
                for tag in feed["tags"]:
                    tags.append(tag["name"])
                detail["tags"] = "###".join(tags)
            details.append(detail)
        return details
    def getVideo(self,userId):
        self.pcursor = ""
        while True:
            data = '{"operationName":"visionProfilePhotoList","variables":{"userId":"%s","pcursor":"%s","page":"profile"},"query":"%s"}'%(userId,self.pcursor,self.video_query)
            self.headers['Referer'] = 'https://www.kuaishou.com/profile/' + userId
            response = requests.post('https://www.kuaishou.com/graphql', headers=self.headers, cookies=self.cookies,
                                     data=data)
            result = response.json()
            if result:
                if result.get("data", 0):
                    if result["data"].get("visionProfilePhotoList", 0):
                        if result["data"]["visionProfilePhotoList"].get("feeds", 0):
                            # print(result["data"]["visionProfilePhotoList"]["feeds"])
                            details = self.getVideoDetail(userId, result["data"]["visionProfilePhotoList"]["feeds"])
                            new_details = []
                            for detail in details:
                                if KSVideoData.table_exists():
                                    if KSVideoData.select().where(KSVideoData.videoId == detail["videoId"]
                                                                  and KSVideoData.doesVideoDown == 1).first():
                                        print(detail["videoId"], "已存在")
                                    else:
                                        down_video_url = detail["videoDownloadUrl"]
                                        video_path = os.path.join(self.down_dir, detail["videoPath"])
                                        if os.path.exists(video_path):
                                            print(detail["videoName"] + "已存在,跳过")
                                            updataVideo(KSVideoData.doesVideoDown, 1, KSVideoData.videoId,
                                                        detail["videoId"])
                                        else:
                                            self.video_id_signal.emit(str(detail['videoId']))
                                            self.down(str(detail['videoId']), down_video_url, video_path, 10240)
                                            updataVideo(KSVideoData.doesVideoDown, 1, KSVideoData.videoId,
                                                        detail["videoId"])
                                        if not KSVideoData.select().where(
                                                KSVideoData.videoId == detail["videoId"]).first():
                                            new_details.append(detail)
                                else:
                                    new_details = details
                            insertIntoVideo(new_details)
                            updataVideoCounts(userId)
                            if len(result["data"]["visionProfilePhotoList"]["feeds"]) == 0:
                                break
                        else:
                            break
                        if result["data"]["visionProfilePhotoList"].get("pcursor", 0):
                            self.pcursor = result["data"]["visionProfilePhotoList"]["pcursor"]
                    else:
                        break
                else:
                    break
            time.sleep(5)
    def run(self):
        userData = getNeededVideo()  # 从数据库中读取信息
        for row in userData:
            settings = yaml.safe_load(open('settings.yaml', encoding='utf8'))
            self.cookies = settings['cookies']
            self.headers = settings['headers']
            self.video_query = settings['video_query']
            userId = row.userId.strip()
            userName = row.userName.strip()
            print(f"正在下载{userName}:{userId}的视频")
            if not os.path.exists(os.path.join(self.down_dir,"ks_video",userId)):os.makedirs(os.path.join(self.down_dir,"ks_video",userId))
            self.getVideo(userId)
            time.sleep(5)
        print("下载完成")
        self.exit(0)  # 关闭线程
    def stop(self):
        os._exit(0)
class downVideoTab(QWidget):
    def __init__(self):
        super(downVideoTab, self).__init__()
        self.get_directory_path=''
        self.initUI()

    def initUI(self):
        self.dirBar()
        self.downArea()
        self.process = QTextEdit(self, readOnly=True)
        self.process.ensureCursorVisible()
        self.process.setLineWrapColumnOrWidth(1000)
        self.process.setLineWrapMode(QTextEdit.FixedPixelWidth)
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.choose_dir_layout)
        main_layout.addWidget(self.process)
        main_layout.addLayout(self.down_layout)
        self.setLayout(main_layout)


    def dirBar(self):
        self.choose_dir_layout = QHBoxLayout()
        self.dirPathlineEdit = QLineEdit(self)
        self.dirPathlineEdit.setObjectName("dirPathlineEdit")
        open_dir_button = QPushButton("选择下载路径", self)
        open_dir_button.clicked.connect(self.openDir)
        self.check_dir_box = QCheckBox(self)
        self.check_dir_box.setDisabled(True)
        self.settings = yaml.safe_load(open('settings.yaml', encoding='utf8'))
        if self.settings.get('get_directory_path'):
            if os.path.exists(self.settings.get('get_directory_path')):
                self.get_directory_path = self.settings["get_directory_path"]
                self.dirPathlineEdit.setText(self.settings["get_directory_path"])
                self.check_dir_box.setChecked(True)
            else:
                self.get_directory_path = ""
                self.check_dir_box.setChecked(False)
        else:
            self.check_dir_box.setChecked(False)
        show_video_detail_button = QPushButton("查看视频信息",self)
        show_video_detail_button.clicked.connect(self.showVideoDetail)
        down_video_button = QPushButton("开始下载",self)
        down_video_button.clicked.connect(self.downVideo)
        self.choose_dir_layout.addWidget(self.dirPathlineEdit)
        self.choose_dir_layout.addWidget(open_dir_button)
        self.choose_dir_layout.addWidget(self.check_dir_box)
        self.choose_dir_layout.addStretch(0.05)
        self.choose_dir_layout.addWidget(down_video_button)
        self.choose_dir_layout.addWidget(show_video_detail_button)

        self.choose_dir_layout.setSpacing(10)

    def downArea(self):
        self.down_layout = QHBoxLayout()
        self.label_layout = QVBoxLayout()
        self.processbar_widget = PercentProgressBar(self, showFreeArea=True)
        self.video_id_label = QLabel()
        self.process_label = QLabel()
        self.process_label.setObjectName("process_label")
        self.video_id_label.setObjectName("video_id_label")
        self.label_layout.addWidget(self.video_id_label)
        self.label_layout.addWidget(self.process_label)
        self.down_layout.addStretch(1)
        self.down_layout.addLayout(self.label_layout)
        self.down_layout.addStretch(1)
        self.down_layout.addWidget(self.processbar_widget)

    def openDir(self):
        self.get_directory_path = QFileDialog.getExistingDirectory(self,
                                                      "选取文件夹",
                                                      "./")
        if self.get_directory_path:
            self.dirPathlineEdit.setText(str(self.get_directory_path))
            self.check_dir_box.setChecked(True)
            self.settings['get_directory_path'] = self.get_directory_path
            yaml.safe_dump(self.settings,open('settings.yaml','w', encoding='utf8'))
        else:
            self.check_dir_box.setChecked(False)
            self.dirPathlineEdit.setText("")
    def onUpdateVideoText(self, text):
        cursor = self.process.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.process.setTextCursor(cursor)
        self.process.ensureCursorVisible()
    def onUpdateProcessLabel(self,text):
        self.process_label.setText(text)
    def onUpdateVideoIdLabel(self,text):
        self.video_id_label.setText("正在下载"+text)
    def downVideo(self):
        try:
            if self.get_directory_path:
                self.down_video_th = downloadThread(str(self.get_directory_path))
                self.down_video_th.download_proess_signal.connect(self.set_progressbar_value)
                self.down_video_th.get_url_signal.connect(self.onUpdateVideoText)
                self.down_video_th.start_down_signal.connect(self.onUpdateProcessLabel)
                self.down_video_th.video_id_signal.connect(self.onUpdateVideoIdLabel)
                sys.stdout = self.down_video_th
                self.down_video_th.start()
            else:
                QMessageBox.information(self,"提示","请选择下载目录")
        except Exception as e:
            raise e
        loop = QEventLoop()
        QTimer.singleShot(2000, loop.quit)
        loop.exec_()
    def showVideoDetail(self):
        self.dg = DataGrid("视频信息","KSVideoData")
        self.dg.show()
    # 设置进度条
    def set_progressbar_value(self, value):
        self.processbar_widget.setValue(value)
        if value == 100:
            return
