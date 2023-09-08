import speech_recognition as sr
import sys
r = sr.Recognizer()
 
with sr.AudioFile("sampleJp.wav") as source:
    audio = r.record(source)
 
#事前に設定した探索する単語群(vector<str>)
strSet = ["水筒","リモコン","時計"]
#単語と学習モデルのラベリングのペア
dict = {"水筒":"bottle","リモコン":"remote control","時計":"watch"}
text = r.recognize_google(audio,language = 'ja-JP')
print(text)
print(text[0:4])
print(text[4])
flag = False
cnt = 0
for i in range(len(text)-3):
    if text[i:i+4] =="ドローン":
        flag = True
        locate = i+5
target = "nothing"
if flag == False:
    sys.exit()
for x in strSet:
    if len(text)-locate>=0 and x==text[locate:locate+len(x)]:
        #print(x)
        target=x
        break
print(f'target is{target} ,this label is {dict[target]}')




