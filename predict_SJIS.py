from tensorflow import keras
import cv2
import cvlib as cv
import socket
import time
import numpy as np
from temperature_SJIS import *
from Mariadb_sql_SJIS import *

# DB에서 1번은 관리자로 지정함
sql = 'select 성명 from SejoongInfo where 고유번호>1;'
sql2 = 'select 영문성명 from SejoongInfo where 고유번호>1;'
sql_result = Process_SQL(sql, "select2")
sql2_result = Process_SQL(sql2, "select2")

# ['Unknown', '사용자1', '사용자2', '사용자3', ...] 리스트 저장

English_list = ['Unknown']
for name in sql2_result:
    English_list.append(name[0])

def Change_Image(img):
    size = (68, 68)
    frame = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    Face_Image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_numpy = np.array(Face_Image, 'uint8') / 255.0  # 소수점 값 배열
    img_numpy = np.array(img_numpy).reshape(-1, 68, 68, 1)
    return img_numpy


# 얼굴 검증 함수
def Face_Predict(model):
    id = 0  
    cap_cnt = 0
    cap_index = []
    temp_index = []
    In_Time = ''
    In_Name = ''
    In_Temp = ''

    # ---------------------------
    #    set3, 4 = 사진 사이즈    
    #     디스플레이에 맞게 조정   
    # ---------------------------
    cam = cv2.VideoCapture(0)
    cam.set(3, 1080) # set video widht
    cam.set(4, 720) # set video height
    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        time_set = time.strftime("%y-%m-%d %H:%M:%S")
        status, frame =cam.read()
            # face = 얼굴 검출 좌표, confidence = 얼굴 확률
        face, confidence = cv.detect_face(frame)

        if not status:
            print("Cam is not working")
            break

        for idx, f in enumerate(face):
            (startX, startY) = f[0], f[1]
            (endX, endY) = f[2], f[3]

            cv2.rectangle(frame, (startX, startY), (endX, endY), (0,255,0), 2)


            # 얼굴 추출 부분 np 배열로 복사
            # 검증 진행하고 그 결과 인덱스를 id_val, 확률을 confidence에 저장
            Face_Temp = Return_Data()
            Frame_Image = frame[startY:endY, startX:endX]
            Face_Image = Change_Image(Frame_Image)
            preds = model.predict(Face_Image)
            
            confidence = np.trunc(np.max(preds) *100)
            id_val = np.argmax(preds)-1

                # Check if confidence is less them 100 ==> "0" is perfect match
                # 확률이 90% 미만이라면
            if (confidence < 80):
                id = English_list[0]
                confidence_label = "  {0}%".format(confidence)
                cap_cnt += 1
                cap_index.append(0)
                temp_index.append(Face_Temp)
                print(f"Unknown, temp = {temp_index} Checking Time = {time_set} ")
                print(f"Unknown, Checking Time = {time_set} ")
                if cap_cnt == 20:
                    In_Time, In_Idx, In_Name, In_Temp = Access_Insert(cap_index, temp_index)
                    break
            else:
                id = English_list[id_val]
                confidence_label = "  {0}%".format(confidence)
                cap_cnt += 1
                cap_index.append(id_val)
                temp_index.append(Face_Temp) 
                print(f"User Checking, id={cap_index}, temp = {temp_index} Checking Time = {time_set}")
                if cap_cnt == 20:
                    In_Time, In_Idx, In_Name, In_Temp = Access_Insert(cap_index, temp_index)
                    break

            if cap_cnt % 5  == 0:                     
                face_in_img = frame[startY:endY, startX:endX]
                cv2.imwrite('Access_Image/' + str(id) + '_' + str(time_set) + '.jpg', face_in_img)
                print("Access User Capture")

                # 이름 출력
            cv2.putText(frame, str(id), (startX+5,startY-5), font, 1, (255,255,255), 2)
                # 테두리 안, 아래 중앙에 표시, 확률과 온도 출력
            cv2.putText(frame, str(confidence_label), (startX+5,endY-5), font, 1, (255,255,0), 1)
            if Face_Temp > 37.2: 
                cv2.putText(frame, str(Face_Temp), (endX-5, endY-5), font, 1, (0, 0, 255), 2)
            elif Face_Temp < 35:
                text_info = "Contact Close"
                cv2.putText(frame, text_info, (endX+5, endY+5), font, 1, (255,255,127), 2)
            else:
                cv2.putText(frame, str(Face_Temp), (endX-5, endY-5), font, 1, (255, 255, 127), 2)

        if cap_cnt == 20:
            cam.release()
            cv2.destroyAllWindows()
            return In_Time, In_Idx, In_Name, In_Temp
                
        cv2.imshow('camera',frame) 
        
        k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
        if k == 27:
                # Do a bit of cleanup
            print("\n [INFO] Exiting Program and cleanup stuff")
            cam.release()
            cv2.destroyAllWindows()
            return In_Time, In_Idx, In_Name, In_Temp





def Access_Insert(cap_list, temp_list):
    cap_set = set(cap_list)
    sql = "select max(고유번호) from SejoongInfo;"
    cnt = Process_SQL(sql, "select1")
    cap_index = [0] * cnt

    for i in range(len(cap_list)):
        value = cap_list[i]
        cap_index[value] += 1
    
    cap_idx = str(cap_index.index(max(cap_index))+1)

    temp_list = np.array(temp_list)
    avgTemp = str(round(np.mean(temp_list),1))

    sql1 = 'select 성명 from SejoongInfo where 고유번호="' + cap_idx + '";'
    sql1_result = Process_SQL(sql1, "select1")   # 출입 확인 성명
    Access_Time = datetime.datetime.now()        # 출입 확인 시간
    In_Time = Access_Time.strftime("%Y-%m-%d %H:%M:%S")

    if sql1_result == "admin":
        sql1_result = "Unknown"


    return In_Time, cap_idx, sql1_result, avgTemp




def Access_Save(In_Time, In_Idx, In_Name, In_Temp, type_text):
    sql = 'insert into AccessInfo(time, id, name, bodyheat, inandout) values("'\
        + In_Time + '","' + In_Idx + '","' + In_Name + '","' + In_Temp + '","' + type_text + '");'

    Process_SQL(sql, "commit")
    print(f"Access Save Function Clear")
