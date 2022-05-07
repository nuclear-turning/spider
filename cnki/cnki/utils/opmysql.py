import re

import scrapy.utils.project

import pymysql
settings = scrapy.utils.project.get_project_settings()

def table_exists(con,table_name):        #这个函数用来判断表是否存在
    sql = "show tables;"
    con.execute(sql)
    tables = [con.fetchall()]
    table_list = re.findall('(\'.*?\')',str(tables))
    table_list = [re.sub("'",'',each) for each in table_list]
    if table_name in table_list:
        return 1        #存在返回1
    else:
        return 0        #不存在返回0
def import_data(txt_path):
    conn = pymysql.connect(host=settings['MYSQL_HOST'], port=settings['MYSQL_POST'], user=settings['MYSQL_USER'],
                           passwd=settings['MYSQL_PASSWORD'], db=settings['MYSQL_DB'])
    cursor = conn.cursor()
    if not table_exists(cursor,'cnki_status'):
        with open(txt_path,encoding='utf8') as f:
            journals = f.read().splitlines()
        index = 1
        create_table_sql = 'CREATE TABLE cnki_status(id INT PRIMARY KEY,journal_name VARCHAR(100),is_searched INT DEFAULT 0,searched_page INT DEFAULT 0,pages INT DEFAULT 2)'
        try:
            cursor.execute(create_table_sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
        for journal in journals:
            journal = journal.strip()
            sql = 'INSERT INTO %s(id,journal_name,is_searched,searched_page,pages) VALUES ("%s","%s",0,0,1)' % ('cnki_status',index,journal)
            try:
                cursor.execute(sql)
                conn.commit()
                index += 1
            except Exception as e:
                print(e)
                conn.rollback()
        cursor.close()
        conn.close()


def get_item(journal_name):
    conn = pymysql.connect(host=settings['MYSQL_HOST'], port=settings['MYSQL_POST'], user=settings['MYSQL_USER'],
                           passwd=settings['MYSQL_PASSWORD'], db=settings['MYSQL_DB'])
    cursor = conn.cursor()
    sql = 'select searched_page,pages from cnki_status where journal_name like "%s"'%journal_name
    cursor.execute(sql)
    result = cursor.fetchone()
    return result
def get_data():
    conn = pymysql.connect(host=settings['MYSQL_HOST'], port=settings['MYSQL_POST'], user=settings['MYSQL_USER'],
                           passwd=settings['MYSQL_PASSWORD'], db=settings['MYSQL_DB'])
    cursor = conn.cursor()
    sql = 'select * from cnki_status where searched_page < pages'
    cursor.execute(sql)
    results = cursor.fetchall()
    datas = []
    for row in results:
        datas.append([int(row[0]), row[1].strip(),int(row[2]),int(row[3]),int(row[4])])
    return datas

def update_data(journal_name,mark,searched_page,pages):
    conn = pymysql.connect(host=settings['MYSQL_HOST'], port=settings['MYSQL_POST'], user=settings['MYSQL_USER'],
                           passwd=settings['MYSQL_PASSWORD'], db=settings['MYSQL_DB'])
    cursor = conn.cursor()
    sql = 'update cnki_status set is_searched=%s,searched_page=%s,pages = %s where journal_name like "%s"'%(mark,searched_page,pages,journal_name)
    # print(sql)
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    import_data()
    # r = get_item('财经研究')
    # print(r)
    # r = get_data()
    # print(r)