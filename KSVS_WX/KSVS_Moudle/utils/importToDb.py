from peewee import SqliteDatabase,Model,CharField,IntegerField,TextField,DoubleField
import yaml
settings = yaml.safe_load(open("settings.yaml",encoding="utf8"))
db = SqliteDatabase(settings["db"])

class KSUserData(Model):
    userId = CharField(max_length=50,default='')
    userName = CharField(max_length=50,default='')
    matchedName = CharField(max_length=50,default='') #匹配到的名字，用来检查是否与目标用户相同
    gender = CharField(max_length=10,default='')
    fan = CharField(max_length=10,default='')
    follow = IntegerField(default=0)
    photoPublic = IntegerField(default=0) #发布作品数
    doesIdGet = IntegerField(default=0)
    doesDetailGet = IntegerField(default=0)
    videoCounts = IntegerField(default=0)

    class Meta:

        database = db
        db_table = 'KSUserData'
class KSVideoData(Model):
    videoId = CharField(max_length=50,primary_key=True)
    userId = CharField(max_length=50,default='')
    videoName = CharField(max_length=50,default='')
    videoPath = CharField(max_length=50,default='')
    videoDuration = IntegerField(default=0)
    videoRatio = DoubleField(default=0.0)
    caption = TextField(default='')
    tags = TextField(default='')
    likeCount = CharField(max_length=20,default='')
    realLikeCount = IntegerField(default=0)
    videoDownloadUrl = TextField(default='')
    doesVideoDown = IntegerField(default=0)
    class Meta:
        database = db
        db_table = 'KSVideoData'

def getNameFromUser(field,value):
    data = KSUserData.select().where(field==value)
    return data
def getIdFromUser(field,value):
    data = KSUserData.select().where(field == value and KSUserData.userId != '')
    return data
def getNeededVideo():
    data = KSUserData.select().where(KSUserData.photoPublic>KSUserData.videoCounts)
    return data
def getFromVideo(field,value):
    data = KSVideoData.select().where(field==value)
    return data

def updataUser(field1,value1,field2,value2):
    sql = KSUserData.update({field1:value1}).where(field2==value2)
    sql.execute()
def updataVideo(field1,value1,field2,value2):
    sql = KSVideoData.update({field1:value1}).where(field2==value2)
    sql.execute()
def updataVideoCounts(userId):
    count = KSVideoData.select().where(KSVideoData.userId == userId and KSVideoData.doesVideoDown==1).count()
    sql = KSUserData.update({KSUserData.videoCounts: count}).where(
        KSUserData.userId ==userId)
    sql.execute()
def insertIntoUser(data):
    if not KSUserData.table_exists():
        # KSUserData.drop_table()
        KSUserData.create_table()
        with db.atomic():
            sql = KSUserData.insert_many(data)
            sql.execute()
def insertIntoVideo(data):
    if not db.table_exists(KSVideoData):
        KSVideoData.create_table()
        with db.atomic():
            sql = KSVideoData.insert_many(data)
            sql.execute()

def importUserName2Db(file_path):
    try:
        import pandas as pd
        data = pd.read_excel(file_path)
        username_list = []
        for index, row in data.iterrows():
            username_dict = {}
            username_dict['userName'] = row['昵称'].strip()
            username_list.append(username_dict)
        insertIntoUser(username_list)
        return 1
    except Exception as e:
        print(e)
        return 0
if __name__ == '__main__':
    # KSUserData.drop_table()
    # KSUserData.create_table()
    # KSVideoData.create_table()
    pass

    # data = getFromUser(KSUserData.doesIdGet,0)
    # updataUser(KSUserData.fan,"fan",KSUserData.userId,"")