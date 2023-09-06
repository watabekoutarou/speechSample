#.wavファイルを変換する（日本語）
#　サイト Pythonで音声からテキストへ変換【SpeechRecognition】　を参考
import speech_recognition as sr

r = sr.Recognizer()
 
with sr.AudioFile("sample.wav") as source:
    audio = r.record(source)
 
text = r.recognize_google(audio, language='ja-JP')
print(text)
