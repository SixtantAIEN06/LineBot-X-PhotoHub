import speech_recognition as sr
import requests
import json

# # 錄音
# recognizer = sr.Recognizer()
# microphone = sr.Microphone()
# with microphone as source:
#     print('輸入語音關鍵字:')
#     recognizer.adjust_for_ambient_noise(source)
#     audio = recognizer.listen(source)

# # 語音辨識    
# # pip install SpeechRecognition
# # pip install pyaudio
# try:
#     text=recognizer.recognize_google(audio, language='zh-tw')
#     print(text)
# except:
#     pass

text = input('輸入搜尋關鍵字:')

def input_X_PhotoHub(text):
    response = requests.get(
        url=f'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/9ec72d9e-f4e9-448d-9fae-1da78139f5f0?verbose=true&timezoneOffset=0&subscription-key=f00dc26709a54cc3ad9ee162285e0a16&q={text}'
    )
    if response.status_code != 200:
        print(f'status is not 200 ({response.status_code})')
        return
    # p = requests.Session()
    data = json.loads(response.text)
    print(text)
    intent = data['topScoringIntent']['intent']
    keyword = []
    aaa = len(data['entities'])
    for i in range(len(data['entities'])):
        keyword.append(data['entities'][i]['entity'])
    print(intent,keyword,aaa)

if __name__ == '__main__':
    input_X_PhotoHub(text)
