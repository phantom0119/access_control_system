import pymysql
import os

connect_maria = pymysql.connect(host='192.168.100.25', user='CamTeam',\
    password='5538', db='CamProject', charset='utf8' )

# SQL에 사용할 커서
cur = connect_maria.cursor()


def Process_SQL(sql, type):
    cur.execute(sql)

    if type == "select1":
        Return_Data = cur.fetchone()[0]
        return Return_Data
    elif type == "select2":
        Return_Data = cur.fetchall()
        return Return_Data
    elif type == "commit":
        connect_maria.commit()
    else:
        Return_Data = cur.fetchone()
        return Return_Data



# def Saved_Change(id_num):
#     print("Folder Change Start")
#     path = './Sejoong_Image'
#     sql = 'select max(고유번호) from SejoongInfo;'
#     start_id = id_num
#     end_id = Process_SQL(sql, 'select1')

#     for i in range(start_id+1, end_id+1):
#         ImageDir = path + '/' + str(i)
#         files = [os.path.join(ImageDir,f) for f in os.listdir(ImageDir)]

#         for file in files:
#             file_index = file.split('_')
#             print(f"file = {file}")
#             os.rename = (file, ImageDir + '/User_' + str(i-1) + '_' + file_index[3] + '.jpg')

#         os.rename = (ImageDir, path + '/' + str(i-1))
