from tensorflow import keras
import tkinter as tk
from tkinter import ttk
import time
import os
import shutil
from tkinter import Entry, StringVar, messagebox
from trainning_SJIS import *
from capture_SJIS import *        # 촬영 관련
from predict_SJIS import *        # 검증 관련
from Mariadb_sql_SJIS import *

# ---------------------------------------------------------------- #
# <   시작페이지(StartPage)    >        <  관리자페이지(AdminPage)  >
#                                         신규회원등록(NewUserPage)
# 관리자로그인(AdminLoginPage)   ------>   회원삭제(DeletePage)
# 기존회원등록(AddUserImagePage)           학습(TrainingPage)
# 출퇴근체크(CheckPage)                    출근테이블(TablePage)
# ---------------------------------------------------------------- #

# 로고 위치 변수
logoX=220
logoY=450

# 기본 폰트
titleFont='Cambria Math'
contentFont='Ebrima'

# 배경색 코드
bgcode='#003458'
fgcode='white'

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~     초기 페이지 정의    ~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('Access Control')
        container = tk.Frame(self)
        self.geometry('640x540')     #  640x540
        self.resizable(False, False) #페이지 크기 고정
        self._frame = None
        self['bg'] = bgcode
        container.grid(column=0, row=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.switch_frame(StartPage)

    # 페이지 호출 시 이전 페이지 삭제 후 생성
    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.grid()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~     시작 페이지       ~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("Start Page Open")
        self.master = master
        self['bg']=bgcode
        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=5, height=10)\
            .grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="안면 인식 출입 통제 시스템", fg=fgcode, bg=bgcode,
            font=(titleFont, 24, "bold")).grid(row=0,column=1, pady=3)

        # 밑줄
        canvas=tk.Canvas(self, width = 400, height = 30, bg=bgcode, bd = 0, highlightthickness = 0)
        line = canvas.create_line(0, 0, 400, 0, fill="white")
        canvas.place(x=125, y=120)
    
        # 등록 -> 관리자 로그인 페이지로 변경
        tk.Button(self, text="제어판 (관리자)", bg=fgcode, fg=bgcode, font=(contentFont, 14),
                    command=lambda: master.switch_frame(AdminLoginPage), width=50).grid(row=1,column=1, pady=3, ipady=3)

        # 기존유저등록
        tk.Button(self, text="사진 등록 (기존 유저)", bg=fgcode, fg=bgcode, font=(contentFont, 14),
                    command=lambda: master.switch_frame(AddUserImagePage), width=50).grid(row=2, column=1, pady=3, ipady=3)

        # 출퇴근검사
        tk.Button(self, text="출입 인증", bg=fgcode, fg=bgcode, font=(contentFont, 14),
                    command= self.Check_System, width=50).grid(row=3, column=1, pady=3, ipady=3)

        self.Label_text = StringVar()
        tk.Label(self, text="", fg=fgcode, bg=bgcode, font=(contentFont, 14),
            textvariable=self.Label_text).grid(row=4, column=1, pady=15)
    
        tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=5, sticky="nsew") # 로고 보이게 하기 위한 여백    
        
        # 로고
        self.logo=tk.PhotoImage(file="./sejoongW200.png")
        tk.Label(self, image=self.logo, bg=bgcode).place(x=logoX, y=logoY)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~  회원 검증 및 온도 확인  ~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def Check_System(self):
        self.Label_text.set("Start Face Validation")
        In_Time, In_Idx, In_Name, In_Temp = Face_Predict(model)
        Set_Access_Page(In_Time, In_Idx, In_Name, In_Temp)
        


def Set_Access_Page(In_Time, In_Idx, In_Name, In_Temp):
    window = tk.Tk()
    window.title("출입 확인")
    window.geometry("500x500")
    window.resizable(width=False, height=False)
    tk.Frame.configure(window, bg=bgcode)
    Temp = In_Temp + '℃'

    tk.Label(window, text="출입 확인", fg=fgcode, bg=bgcode, font=('System', 24, "bold")).pack(pady=20)
    tk.Label(window, text="출입 시간:", fg=fgcode, bg=bgcode, font=('System', 17, "bold"))\
        .place(width=100, height=40, x=80, y=100)
    tk.Label(window, text=In_Time, fg=fgcode, bg=bgcode, font=('System', 17, "bold"))\
        .place(width=170, height=40, x=140, y=100, relx=0.2)

    tk.Label(window, text="확인 성명:", fg=fgcode, bg=bgcode, font=('System', 17, "bold"))\
        .place(width=100, height=40, x=80, y=150)
    tk.Label(window, text=In_Name, fg=fgcode, bg=bgcode, font=('System', 17, "bold"))\
        .place(width=170, height=40, x=140, y=150, relx=0.2)

    tk.Label(window, text="측정 온도:", fg=fgcode, bg=bgcode, font=('System', 17, "bold"))\
        .place(width=100, height=40, x=80, y=200)
    tk.Label(window, text=Temp, fg=fgcode, bg=bgcode, font=('System', 17, "bold"))\
        .place(width=170, height=40, x=140, y=200, relx=0.2)

    tk.Button(window, text="출입", bg='white', fg='#00498c', font=('Ebrima', 15), width=10,\
        command=lambda:[Access_Save(In_Time, In_Idx, In_Name, In_Temp, "출입"), window.destroy()]).place(width=100, height=40, x=90, y=270)
    tk.Button(window, text="출근", bg='white', fg='#00498c', font=('Ebrima', 17), width=10,\
        command=lambda:[Access_Save(In_Time, In_Idx, In_Name, In_Temp, "출근"), window.destroy()]).place(width=100, height=40, x=200, y=270)
    tk.Button(window, text="퇴근", bg='white', fg='#00498c', font=('Ebrima', 17), width=10,\
        command=lambda:[Access_Save(In_Time, In_Idx, In_Name, In_Temp, "퇴근"), window.destroy()]).place(width=100, height=40, x=310, y=270)

    tk.Button(window, text="다시 인증", bg='white', fg='#00498c', font=('Ebrima', 17), width=10,\
        command=window.destroy).place(width=120, height=40, x=190, y=320)

    logo = tk.PhotoImage(file="./sejoongW200.png", master=window)
    tk.Label(window, image=logo, bg=bgcode).place(width=190, height=60, x=170, y=400)
    window.mainloop()



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~   관리자 로그인 페이지   ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminLoginPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("AdminLogin Page Open")
        self['bg']=bgcode
        self.master = master
        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=22, height=13).grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="관리자 로그인", fg=fgcode, bg=bgcode, font=(titleFont, 24, "bold")).grid(row=0, column=2, pady=5)
        
        # Entry에서 입력 받은 값을 저장
        self.textbar = StringVar()
        self.admin_id_txt = StringVar()
        self.admin_pw_txt = StringVar()

        # 화면 구성 Label
        # ID:
        tk.Label(self, text="ID :", bg=bgcode, fg=fgcode, font=(contentFont, 18)).grid(row=1, column=1, pady=3)
        admin_id = tk.Entry(self, width=30, textvariable=self.admin_id_txt, font=(contentFont, 10),
                ).grid(row=1, column=2, pady=3, ipady=5)
        # PW:
        tk.Label(self, text="PW :", bg=bgcode, fg=fgcode, font=(contentFont, 18)).grid(row=2, column=1, pady=5)
        admin_pw = tk.Entry(self, width=30, textvariable=self.admin_pw_txt, show="*", font=(contentFont, 10),
                ).grid(row=2, column=2, pady=3, ipady=5)

        # 관리자 로그인 버튼
        tk.Button(self, text="로그인", bg=fgcode, fg=bgcode, width=20, font=(contentFont, 14),
            command=self.CheckAdmin).grid(row=3, column=2, pady=5)
    
        # 초기 화면 이동 버튼
        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, width=10, font=(contentFont, 10),
            command=lambda: master.switch_frame(StartPage)).grid(row=5, column=2, pady=5)
        

        tk.Label(self, text="", bg=bgcode, fg=fgcode, textvariable=self.textbar).grid(row=6, column=2, pady=5)

        tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=7, sticky="nsew") # 로고 보이게 하기 위한 여백

        # 로고
        self.logo=tk.PhotoImage(file="./sejoongW200.png")
        tk.Label(self, image=self.logo, bg=bgcode).place(x=logoX, y=logoY)

        self['bg']=bgcode

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~  Admin 계정으로 로그인 되었는지 확인   ~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def CheckAdmin(self):
        # 관리자 ID(admin)와 비밀번호(5538) 값 저장
        id = self.admin_id_txt.get()
        pw = self.admin_pw_txt.get()
        
        # 관리자 ID, 비밀번호 추출
        admin_id_db = "admin"
        if id == admin_id_db:
            sql = 'select 비밀번호 from SejoongInfo where 성명="admin";'
            admin_pw_db = Process_SQL(sql, "select1")
            self.textbar.set("관리자 확인 중...")

            # 최종 확인(id, pw 모두 일치)  --> 영상 촬영 시작
            if pw == admin_pw_db:
                self.textbar.set("확인되었습니다. 잠시만 기다려주세요...")
                time.sleep(1)
                self.master.switch_frame(AdminPage)
            else:
                print("Not Collect Password")
                self.textbar.set("비밀번호가 일치하지 않습니다.")
        else:
            print("Not Collect Admin ID, Retry")
            self.textbar.set("관리자 정보와 일치하지 않습니다. 다시 한번 입력하세요.")



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~      관리자 권한 서비스 페이지       ~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("Admin Page Open")
        self.master = master
        self['bg']=bgcode
        
        tk.Label(self, text="", fg=fgcode, bg=bgcode, width=7, height=5)\
            .grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="제어판", fg=fgcode, bg=bgcode,
            font=(titleFont, 22, "bold")).grid(row=0, column=1, pady=5)
        
        # 밑줄
        canvas=tk.Canvas(self, width = 400, height = 30, bg=bgcode, bd = 0, highlightthickness = 0)
        line = canvas.create_line(0, 0, 400, 0, fill="white")
        canvas.place(x=125, y=120)


        # 신규 등록
        tk.Button(self, text="신규 사용자 등록 및 촬영", bg=fgcode, fg=bgcode, font=(contentFont, 12), width=60,
                command=lambda: master.switch_frame(NewUserPage)).grid(row=1, column=1, pady=5, ipady=3)

        # 회원 삭제
        tk.Button(self, text="사용자 삭제", bg=fgcode, fg=bgcode, font=(contentFont, 12), width=60,
                command=lambda: master.switch_frame(DeletePage)).grid(row=2, column=1, pady=5, ipady=3)

        #얼굴 이미지 학습
        tk.Button(self, text="사용자 사진 학습", bg=fgcode, fg=bgcode, font=(contentFont, 12), width=60,
                command=self.ask_training).grid(row=3, column=1, pady=5, ipady=3)

        # 데이터 테이블
        tk.Button(self, text="출입 기록", bg=fgcode, fg=bgcode, font=(contentFont, 12), width=60,
                command=lambda:master.switch_frame(TablePage)).grid(row=4, column=1, pady=5, ipady=3)


        # 로그인 페이지로 돌아가기
        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, font=(contentFont, 10), width=10,
                command=lambda: master.switch_frame(StartPage)).grid(row=5, column=1, pady=10, ipady=3)

        tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=6, sticky="nsew")

        self.logo=tk.PhotoImage(file="./sejoongW200.png")
        tk.Label(self, image=self.logo, bg=bgcode).place(x=logoX, y=logoY)


    # 학습 시작 질의
    def ask_training(self):
        MsgBox=tk.messagebox.askokcancel("Training", "학습을 시작합니다.\n(확인 버튼 클릭 시 시작)")
        if MsgBox==True:
            try:
                Training_Start()
            except:
                self.re_training()
        else:
            tk.messagebox.showinfo("Cancel", "취소되었습니다.")

    # 사진 학습 에러 처리
    def re_training(self):
        MsgBox=tk.messagebox.askretrycancel("ERROR","사진파일 확인 후 다시 시도 하십시오.")
        if MsgBox==True:
            self.ask_training()
        else:
            tk.messagebox.showinfo("Cancel", "취소되었습니다.")



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~  신규 사용자 등록 페이지    ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NewUserPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("NewUser Page Open")
        self.master = master
        self['bg']=bgcode
        # 신규 사용자 ID, PW 저장
        self.newid = StringVar()
        self.newpw = StringVar()
        self.infotext = StringVar()

        tk.Label(self, text="", bg=bgcode, fg=bgcode, width=15)\
            .grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="신규 유저 등록", bg=bgcode, fg=fgcode,
            font=(titleFont, 24, "bold")).grid(row=0, column=2, pady=5)

        # tk.Label(self, text="", width=5, height=13).grid(row=1,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        # New ID:
        tk.Label(self, text="New ID :", bg=bgcode, fg=fgcode, font=(contentFont, 18))\
            .grid(row=1, column=1, pady=3)
        user_id = tk.Entry(self, width=30, textvariable=self.newid, font=(contentFont, 10))\
            .grid(row=1, column=2, pady=2, ipady=5)
        
        # New PW:
        tk.Label(self, text="New PW :", bg=bgcode, fg=fgcode, font=(contentFont, 18))\
            .grid(row=2, column=1, pady=5)
        user_pw = tk.Entry(self, width=30, textvariable=self.newpw, show="*", font=(contentFont, 10))\
            .grid(row=2, column=2, pady=3, ipady=5)


        tk.Button(self, text="등록 및 촬영", bg=fgcode, fg=bgcode, width=20, font=(contentFont, 14),
            command=self.SignUp).grid(row=3, column=2, pady=5)
        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, width=10, font=(contentFont, 10),
            command=lambda: master.switch_frame(AdminPage)).grid(row=5, column=2, pady=5)

        tk.Label(self, text="", bg=bgcode, fg=bgcode, textvariable=self.infotext).grid(row=6, column=2, pady=3)       
        tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=7, sticky="nsew") # 로고 보이게 하기 위한 여백

        # 로고
        self.logo=tk.PhotoImage(file="./sejoongW200.png")
        tk.Label(self, image=self.logo, bg=bgcode).place(x=logoX, y=logoY)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~   사용자 계정 등록 및 촬영 진행   ~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SignUp(self):
        id = self.newid.get()
        pw = self.newpw.get()
        # ID, PW가 일치하는 기존 사용자가 있는지 검사
        sql1='select 고유번호 from SejoongInfo where 성명="' + id + '" and 비밀번호="' + pw + '";'
        try:
            sql1_result = Process_SQL(sql1, "select1")
            print("User Already Exists.")
            self.infotext.set("User Already Exists.")
        except:
            sql2 = 'insert into SejoongInfo(성명, 비밀번호) values("' + id + '","' + pw + '");'
            sql3 = 'set @CNT=0;'   # id count 초기화
            sql4 = 'update SejoongInfo set SejoongInfo.고유번호 = @CNT:=@CNT+1;'  # id 고유번호 재정렬
            Process_SQL(sql2, "commit")
            Process_SQL(sql3, "commit")
            Process_SQL(sql4, "commit")
            sql1_result = Process_SQL(sql1, "select1")

            # 신규 사용자 이미지 저장 폴더 생성 후 캡처 진행
            Image_Route = "./Sejoong_Image/" + str(sql1_result)
            try:
                if not os.path.exists(Image_Route):
                    os.makedirs(Image_Route)
            except OSError:
                print("Error Making Image Folder!")

            self.infotext.set("등록되었습니다. 촬영이 시작됩니다...")
            print("New User Is Saved")

            # 얼굴 촬영 함수 시작
            Face_Capture(sql1_result)



# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~       회원 삭제 페이지        ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class DeletePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("Delete Page Open")
        self.master = master
        self['bg']=bgcode
        self.textbar = StringVar()
        self.userid = StringVar()
        self.userpw = StringVar()

        tk.Label(self, text="", bg=bgcode, fg=bgcode, width=15, height=13)\
            .grid(row=0, column=0) # 가운데 정렬용
        tk.Label(self, text="유저 정보 삭제", bg=bgcode, fg=fgcode,
            font=(titleFont, 24, "bold")).grid(row=0, column=2)
        

        # 회원 조회
        tk.Label(self, text="User ID :", bg=bgcode, fg=fgcode, font=(contentFont, 18)).grid(row=1, column=1, pady=5)
        tk.Label(self, text="User PW :", bg=bgcode, fg=fgcode, font=(contentFont, 18)).grid(row=2, column=1, pady=5)

        user_id = tk.Entry(self, width=30, textvariable=self.userid, font=(contentFont, 10)).grid(row=1, column=2, pady=3, ipady=5)
        user_pw = tk.Entry(self, width=30, textvariable=self.userpw, show="*", font=(contentFont, 10)).grid(row=2, column=2, pady=3, ipady=5)

        tk.Button(self, text="삭제", bg=fgcode, fg=bgcode, width=20, font=(contentFont, 14),
            command=self.delete).grid(row=3, column=2, pady=5, ipady=2)
        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, width=10, font=(contentFont, 10),
            command=lambda: master.switch_frame(AdminPage)).grid(row=5, column=2, pady=5)

        tk.Label(self, text="", bg=bgcode, fg=bgcode, textvariable=self.textbar).grid(row=6, column=2, pady=3)
        tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=7, sticky="nsew") # 로고 보이게 하기 위한 여백
        
        # 로고
        self.logo=tk.PhotoImage(file="./sejoongW200.png")
        tk.Label(self, image=self.logo, bg=bgcode).place(x=logoX, y=logoY)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~       회원 삭제 함수          ~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def delete(self):
        path = './Sejoong_Image'
        id = self.userid.get()
        pw = self.userpw.get()
        sql = 'select 고유번호 from SejoongInfo where 성명="' + id + '" and 비밀번호="' + pw + '";'
        sql2 = 'select max(고유번호) from SejoongInfo;'
        # 등록된 사용자인지 확인 후 고유 번호 획득 --> 삭제 진행
        try:
            start_id = Process_SQL(sql, "select1")   # 고유번호 (id)
            end_id = Process_SQL(sql2, "select1")
            self.textbar.set("조회되었습니다. 삭제합니다...")
            print(start_id)

            # 계정 삭제
            Dsql = "delete from SejoongInfo where 고유번호=" + str(start_id) + ";"
            sql3 = 'set @CNT=0;'   # id count 초기화
            sql4 = 'update SejoongInfo set SejoongInfo.고유번호 = @CNT:=@CNT+1;'  # id 고유번호 재정렬
            Process_SQL(Dsql, "commit")
            Process_SQL(sql3, "commit")
            Process_SQL(sql4, "commit")
            print("User Delete Complete !")

            # 파일명 변경
            for i in range(start_id+1, end_id+1):
                ImageDir = path + '/' + str(i)
                print(f"ImageDir = {ImageDir}")

                files = os.listdir(ImageDir)
    
                
                for file in files:
                    name = file
                    num = file.split('_')[1]
                    change_text = '_' + num + '_'
                    new_name = file.replace(change_text, '_' + str(i-1) + '_')

                    name = os.path.join(ImageDir, name)
                    new_name = os.path.join(ImageDir, new_name)
                    os.rename(name, new_name)

            Image_Route = './Sejoong_Image/' + str(start_id)
            shutil.rmtree(Image_Route)

            # 디렉터리명 변경
            directories = os.listdir(path)
            for directory in directories:
                if int(directory) > start_id:
                    name = directory
                    new_name = name.replace(str(directory), str(int(directory)-1))
                    name = os.path.join(path, name)
                    new_name = os.path.join(path, new_name)
                    print(f" name = {name}  new name = {new_name}")
                    os.rename(name, new_name)

            print("Image Folder Deleted!!")
        except:
            print("Not Collect User ..!")
            self.textbar.set("아이디 또는 비밀번호가 일치하지 않습니다.")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~       근태 관리 테이블        ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TablePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("Table Page Open")
        self.master = master
        self['bg']=bgcode

        tk.Label(self, text="", bg=bgcode, fg=fgcode, width=5, height=5)\
            .grid(row=0, column=0) # 가운데 정렬용
        tk.Label(self, text="출입 기록", bg=bgcode, fg=fgcode,
            font=(titleFont, 24, "bold")).grid(row=0, column=1)

        canvas=tk.Canvas(self, width = 400, height = 30, bg=bgcode, bd = 0, highlightthickness = 0)
        line = canvas.create_line(0, 0, 400, 0, fill="white")
        canvas.place(x=125, y=120)

        tk.Button(self, text="Back", bg='lightgray', fg=bgcode, font=(contentFont, 12),
                command=lambda: master.switch_frame(AdminPage), width=10).grid(row=3, column=1, pady=10)


        tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=5, sticky="nsew") # 로고 보이게 하기 위한 여백    
        
        # 로고
        self.logo=tk.PhotoImage(file="./sejoongW200.png")
        tk.Label(self, image=self.logo, bg=bgcode).place(x=logoX, y=logoY)
        
        # 테이블
        self.tree = ttk.Treeview(self, columns=(1, 2, 3, 4, 5), show="headings", height=9)
        self.tree.grid(row=1, column=1, sticky="nsew")

        # 필드명
        self.tree.heading(1, text="시간")    # 고유번호
        self.tree.heading(2, text="ID")  # 이름
        self.tree.heading(3, text="이름")  # 시간
        self.tree.heading(4, text="온도") # 열
        self.tree.heading(5, text="근태상황")  # 출퇴근

        col=87
        # 기본 너비
        self.tree.column(1, width=col+100)
        self.tree.column(2, width=col)
        self.tree.column(3, width=col+20)
        self.tree.column(4, width=col)
        self.tree.column(5, width=col)

        # 테이블 스크롤바 표시
        scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scroll.grid(row=1, column=1, sticky="nse")
        self.tree.configure(yscrollcommand=scroll.set)

        # 기본 데이터 추가
        # test용으로 Accessinfo 사용 
        sql = "SELECT * FROM AccessInfo"
        Access_Data = Process_SQL(sql, "select2")
        for i in Access_Data:
            self.tree.insert('', 'end', values=(i[0], i[1], i[2], i[3], i[4]))



    # def Access_Update(self):
    #     table_data = self.tree.get_children()
    #     for i in table_data:
    #         print(f"data i = {i}")
    #         self.tree.delete(i)

    #     sql = "SELECT * FROM AccessInfo"
    #     Access_Data = Process_SQL(sql, "select2")
    #     for i in Access_Data:
    #         print(f"insert data = {i}")
    #         self.tree.insert('', 'end', values=(i[0], i[1], i[2], i[3], i[4]))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~   회원 이미지 추가 페이지      ~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AddUserImagePage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        print("추가 사진 등록")
        self.master = master

        tk.Label(self, text="", bg=bgcode, fg=fgcode, width=15, height=13).grid(row=0,column=0) # (추가)가운데 정렬을 위한 빈 라벨
        tk.Label(self, text="회원 조회", bg=bgcode, fg=fgcode, font=(titleFont, 24, "bold")).grid(row=0, column=2, pady=5)
        tk.Label(self, text="User ID :", bg=bgcode, fg=fgcode, font=(contentFont, 18)).grid(row=1, column=1, pady=5)
        tk.Label(self, text="User PW :", bg=bgcode, fg=fgcode, font=(contentFont, 18)).grid(row=2, column=1, pady=5)
        
        self.textbar = StringVar()
        self.userid = StringVar()
        self.userpw = StringVar()

        user_id = tk.Entry(self, width=30, textvariable=self.userid, font=(contentFont, 10)).grid(row=1, column=2, pady=3, ipady=3)
        user_pw = tk.Entry(self, width=30, textvariable=self.userpw, show="*", font=(contentFont, 10)).grid(row=2, column=2, pady=3, ipady=3)

        tk.Button(self, text="조회 및 촬영", bg=fgcode, fg=bgcode, width=20, font=(contentFont, 14),
            command=self.SignIn).grid(row=3, column=2, pady=5, ipady=2)
        tk.Button(self, text="Go Back", bg='lightgray', fg=fgcode, width=10, font=(contentFont, 10),
            command=lambda: master.switch_frame(StartPage)).grid(row=5, column=2, pady=5) 

        tk.Label(self, text="", bg=bgcode, fg=fgcode, textvariable=self.textbar).grid(row=6, column=2, pady=3)     
        self['bg']=bgcode

        tk.Label(self, text="", fg=fgcode, bg=bgcode, height=20).grid(row=7, sticky="nsew") # 로고 보이게 하기 위한 여백

        # 로고
        self.logo=tk.PhotoImage(file="./sejoongW200.png")
        tk.Label(self, image=self.logo, bg=bgcode).place(x=logoX, y=logoY)


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~   사용자 로그인 후 사진 추가 작업   ~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def SignIn(self):
        id = self.userid.get()
        pw = self.userpw.get()
        sql = 'select 고유번호 from SejoongInfo where 성명="' + id + '" and 비밀번호="' + pw + '";'
        
        # 등록된 사용자인지 확인 후 고유 번호 획득 --> 촬영 진행
        try:
            sql_result = Process_SQL(sql, "select1")
            self.textbar.set("조회되었습니다. 촬영을 시작합니다...")
            print(sql_result)
            Face_Capture(sql_result)
        except:
            print("Not Collect User Access..!")
            self.textbar.set("아이디 또는 비밀번호가 일치하지 않습니다.")




if __name__ == "__main__":
    model = keras.models.load_model('./trainer/Save_model')
    print("Page is Open")
    app = SampleApp()
    app.mainloop()