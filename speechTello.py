import tello
from PIL import Image
import socket
import io
import pickle
import math
import time
from PIL import Image,ImageTk
import tkinter as tk
import torch
import numpy as np
import cv2
import sys
import speech_recognition as sr
#事前に設定した探索する単語群(vector<str>)
strSet = ["水筒","リモコン","時計"]
#単語と学習モデルのラベリングのペア
dict = {"水筒":"bottle","リモコン":"remote control","時計":"watch","nothing":"nothing","bottle":"bottle"}

fov = math.radians(41)#視野角
tan_value = math.tan(fov)

#進む距離
x=1
y=0.8
#flag == true の時move_foward
flag = True
receptionFlag=False
moveX_cnt = 0
moveY_cnt = 0
#探索範囲
ROOMX =5
ROOMY =5
#false=左、True = 右   
LRflag=False
#初めて対象を見つけた時のピクセルすう
A=0
B=0

def isolate_word(text):
    flag = False
    cnt = 0
    for i in range(len(text)-3):
        if text[i:i+4] =="ドローン":
            flag = True
            locate = i+5
    target = "nothing"
    if not flag:
        print(text)
        print("not drone call\n")
        return target
    for x in strSet:
        if len(text)-locate>=0 and x==text[locate:locate+len(x)]:
            #print(x)
            target=x
            break
    print(f'target is{target} ,this label is {dict[target]}\n')
    target=dict[target]
    return target
#実験用の.wavファイルのカウント変数

def speech_reception():
    #wavCnt=1#音声ファイル１〜連続で入力するようのカウント変数
    while True:
            r = sr.Recognizer()

            ###
            #実験用ファイルナンバリング
            """
            if wavCnt ==9:
                sys.exit()
            wavStr=str(wavCnt)
            #.wav実験用
            wavFailName="sample"+wavStr+".wav"
            print(f'{wavFailName}\n')
            wavCnt+=1
            with sr.AudioFile(wavFailName) as source:
                audio = r.record(source)
            """
            ###

            print("\n")
            cnt = 0
            with sr.Microphone() as source:
                print("Say something!")
                audio = r.listen(source)
            
            text = r.recognize_google(audio,language="ja-JP")
            try:
                print("Google Speech Recognition thinks you said " + text)
                lenText = len(text)
                for i in range(int(lenText/2)):
                    if (text[i]=='ス' or text[lenText-1-i]=='プ'):
                        if text[i:i+4]=="ストップ" or text[lenText-4-i:lenText-i-1+1]=="ストップ":
                            print("ストップを検知しました。システムを終了します\n")
                            sys.exit()

                target = isolate_word(text)
                if target == "nothing":
                    print("Could not request results")
                    continue

                #テキスト音声ファイルでの実験時はリターンなしで全ファイルを試してみる
                return target


            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

def move (target):
    #print(target)
    print("move呼び出し")
    time.sleep(0.5)
    exist = False
    frame=drone.read()
    if frame is None or frame.size == 0:
        print("frame is None")
        return exist
    result = model(frame)
    result.render()
    result.show()
    global moveX_cnt
    moveX_cnt +=1 

    #drone.move_forward(x)
    #obj に推論の結果の集合を代入
    obj = result.pandas().xyxy[0]
    #推論の結果のバウンディングボックスのクラスネームと座標を出力
    dic = {}
    for i in range(len(obj)):
      name = obj.name[i]
      xmin = obj.xmin[i]
      ymin = obj.ymin[i]
      xmax = obj.xmax[i]
      ymax = obj.ymax[i]
      # 元の物体の高さ（ピくセル）を　A、後をBに
      if name == target :
        A = float(ymax-ymin)
        exist = True
        return exist
    print("見つからず、動いて次ループへ")
    time.sleep(5)
    drone.move_forward(x)    
    return exist
def analyDistance(A,B):
    #print(f"A is {A},B is {B}")
    dis = B/(B-A)*x
    dis = float(dis)
    print(dis,type(dis))
    return dis
def final_move(A):
   time.sleep(3)
   print("もう少し")
   drone.move_forward(x)
   time.sleep(5)
   drone.move_down(x*tan_value)
   time.sleep(5)
   frame = drone.read()
   drone.move_up(x*tan_value)
   result = model(frame)
   result.render()
   result.show()
   #drone.move_forward(x)
   #obj に推論の結果の集合を代入
   obj = result.pandas().xyxy[0]
   #推論の結果のバウンディングボックスのクラスネームと座標を出力
   dic = {}
   B=0
   for i in range(len(obj)):
     name = obj.name[i]
     xmin = obj.xmin[i]
     ymin = obj.ymin[i]
     xmax = obj.xmax[i]
     ymax = obj.ymax[i]
     # 元の物体の高さ（ピくセル）を　A、後をBに
     if name == target :
       B= ymax-ymin
   if B==0:
      print("見失いました,近辺にある...ってこと？")
      drone.land()
      sys.exit()
   time.sleep(5)
   drone.move_forward(analyDistance(A,B))
   print("見つけました？、システムを終了します")
   drone.land()
   return 0

#システム本体
#drone接続
drone = tello.Tello('', 8889)
time.sleep(0.5)

#model の読み込み
model = torch.hub.load('ultralytics/yolov5','yolov5s')
time.sleep(0.5)
target="a"
#print(speech_reception())
#音声認識受付部分　
while True:
    try:
        target = speech_reception()
        print(f"target is {target}")
        break 

    except KeyboardInterrupt:
        print("\n-------input ~c------\n")
        del drone
        sys.exit()

drone.takeoff()
time.sleep(5)
drone.move_up(0.5)
time.sleep(5)

while True:
    try:
        #探索範囲を超えていないかを最初に確認
        print(f"moveX_cnt is {moveX_cnt}")
        if moveX_cnt*x>ROOMX:
         moveX_cnt=0
         moveY_cnt+=1
         if flag:
            time.sleep(5)
            drone.move_right(y)
            time.sleep(5)
         else:
            drone.move_left(y)
            time.sleep(5)
         drone.rotate_cw(180)
         time.sleep(5)
         flag ^=1
        if moveY_cnt*y > ROOMY:
           print("見つかりませんでした")
           drone.land()
           sys.exit()

        if move(target):
           print("とりあえず見つけた")
           time.sleep(3)
           drone.move_forward(x)
           time.sleep(3)
           drone.move_down(x*tan_value)
           time.sleep(3)
           frame = drone.read()
           result = model(frame)
           result.render()
           result.show()
           moveX_cnt+=1
           #drone.move_forward(x)
           #obj に推論の結果の集合を代入
           obj = result.pandas().xyxy[0]
           #推論の結果のバウンディングボックスのクラスネームと座標を出力
           dic = {}
           for i in range(len(obj)):
             name = obj.name[i]
             xmin = obj.xmin[i]
             ymin = obj.ymin[i]
             xmax = obj.xmax[i]
             ymax = obj.ymax[i]
             # 元の物体の高さ（ピくセル）を　A、後をBに
             if name =="bottle" :
               result.show()
               B= float (ymax-ymin)
               if xmin<2592/2:
                  LRflag=True
                  
               break
           if B==0:
              print("見失いました,近辺にあるはず")
              drone.land()
              sys.exit()
           else:
              distanse = analyDistance(A,B)
              print(f"distanse is {distanse}")
              drone.move_forward(distanse)
              break
        else:
           continue

    except KeyboardInterrupt:
        print("\n-------input ~c------\n")
        drone.land()
        del drone
        sys.exit()

print("while抜けました")
time.sleep(3)
drone.rotate_cw(90)
time.sleep(3)
frame = drone.read()
result = model(frame)
result.render()
#result.show()
moveX_cnt+=1
#drone.move_forward(x)
#obj に推論の結果の集合を代入
obj = result.pandas().xyxy[0]
#推論の結果のバウンディングボックスのクラスネームと座標を出力
dic = {}
flag2 = False
for i in range(len(obj)):
  name = obj.name[i]
  xmin = obj.xmin[i]
  ymin = obj.ymin[i]
  xmax = obj.xmax[i]
  ymax = obj.ymax[i]
  # 元の物体の高さ（ピくセル）を　A、後をBに
  if name =="bottle" :#あとで
     A = ymax-ymin
     flag2 = True
if flag2 :
   final_move(A)
else:
   drone.rotate_cw(180)
   for i in range(len(obj)):
    name = obj.name[i]
    xmin = obj.xmin[i]
    ymin = obj.ymin[i]
    xmax = obj.xmax[i]
    ymax = obj.ymax[i]
    # 元の物体の高さ（ピくセル）をA、後をBに
    if name =="bottle" :#
       A = ymax-ymin
       flag2 = True
       final_move(A)
#見失った後左右どっちにあるか前の写真で判断してそっちにより再度確認して待たなかった場合は諦める

if flag==False:
   print("見失いました")
   drone.land()


