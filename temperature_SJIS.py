import numpy as np
import datetime
import pymysql
import serial
import socket
from Mariadb_sql_SJIS import *



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~  외부 모듈 (라즈베리파이 열 화상 센서)         ~~~~~~~~~~~~~
# ~~~~~~ 소켓 통신용 코드 포함, 기호에 맞게 주석 시작    ~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
HOST = '192.168.100.25'         # 메인 서버(Server) IP 주소
PORT = 5538                     #  Port

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)     # 소켓 객체 생성(ipv4, Byte Stream)
    # 일반 소켓 레벨 설정, 이미 사용 중인 주소&포트에 대해 바인드 허용
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Socket creation complete!")

try:
    server.bind((HOST, PORT))      # 소켓 바인드
except socket.error:
    print("Bind failed")


server.listen()                                  # 클라이언트 접속 허용
print("Socket waiting for client messages")
(client_socket, addr) = server.accept()         # 클라이언트가 접속하면 새로운 소켓 반환
print(f"client_socket connected = {addr}")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~ 여기까지 주석 ~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#################################################################################################

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~   열 화상 센서 값 호출    ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def Return_Data():
    Send_Message = "Ready"
    client_socket.send(Send_Message.encode())

    Face_Temp = client_socket.recv(1024)          # 클라이언트로부터 데이터 수신
    Face_Temp = Face_Temp.decode()                # 수신한 데이터 디코딩(decode)                # 쉼표(,)를 기준으로 구분하는 리스트 생성
    print("Sensor Data Received " + Face_Temp)    # 예비 출력

    return float(Face_Temp)



# ~~~~~~~~~~~~~~~~~~~~~~~
# ~~   소켓 종료   ~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~
def Close_Socket():
    reply = 'received'
    client_socket.send(reply.encode())
    server.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~    화상 픽셀 수집 함수 (열 화상 센서)   ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def get_pixels():
    # Master -> 센서모듈 신호 전달
    # Start = 0x11, Start Address Hi = 0x00, Start Address Lo = 0x00
    # No. of Data Hi = 0x04, No. of Data Lo = 0x01
    # END = 0x98 
    command_start = b"\x11\x00\x00\x04\x01\x98"
    print("get_pixels Start")
    # 시리얼 통신 객체 생성
    ser = serial.Serial(
        port = '/dev/ttyAMA0',
        baudrate = 115200,
        parity = serial.PARITY_NONE,
        stopbits = serial.STOPBITS_ONE,
        bytesize = serial.EIGHTBITS,
        timeout = 1
    )
    # data = 센서모듈에서 전달받은 데이터 리스트
    data = []
    cnt = 0
    # 센서에 요청 신호를 전달 (센서 작동에 필요)
    ser.write(command_start)
    
    # 인덱스 0 = Start Hi&Lo, 인덱스 1 = 센서 온도
    # 인덱스 2 ~ 1025 (전체 1024) = 대상 픽셀 온도
    # 마지막 인덱스(1026) = End Hi&Lo
    while cnt<1027:
        data.append(bytes_int(ser.read(2)))
        cnt += 1

    # data[2~1025] : pixel data 
    del data[1026], data[1], data[0]
    
    data = np.array(data)
    data = np.reshape(data,(32,32))

    return data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ Binary Data 정수(Integer) 변환 함수   ~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def bytes_int(b):
    # 주어진 바이트 배열로 표현되는 정수를 반환.
    # byteorder는 정수를 나타내는데 사용되는 바이트 순서 결정
    # sys.byteorder로 확인
    # 사람과 친숙한 표현 형태는 big
    i = int.from_bytes(b,'big')
    return i