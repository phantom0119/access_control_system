import socket                            # socket Connect
import time                             # 시간 제어 관련.
import pymysql
import serial
import numpy as np

def get_pixels():
    command_start = b"\x11\x00\x00\x04\x01\x98"
    print("get_pixels Start")
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
    MiddleData =  data[8:25, 8:25]
    data = np.max(MiddleData)
    #print(f"dataTemp = {MiddleData}")        
    return data


def bytes_int(b):
    i = int.from_bytes(b,'big')
    return i


#connect_maria = pymysql.connect(host='127.0.0.1', user='camTeam',\
    #password='9876', db='CamProject', charset='utf8' )
HOST = '192.168.100.25'         #  메인 서버 IP
PORT = 5538                    # 메인 서버 개방 포트
server = socket.socket(socket .AF_INET, socket.SOCK_STREAM)   # 소켓 객체 생성(ipv4, Byte Stream)
server.connect((HOST,PORT))                                     # 서버에 연결 시도

if __name__ == "__main__":
    while True:
        reply = server.recv(2048)
        
        if reply.decode() == 'Ready':
            data = get_pixels()
            data = str(round(data * 0.1,1))
            server.send(data.encode())   # 인코딩(encode) 작업 후 서버로 전달
            
        if reply.decode() == 'received':     # 서버로부터 전달받은 내용이 “received”라면
            print("data sending success!")
            server.close()
