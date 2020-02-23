import random
from flask import Flask, request, abort
from imgurpython import ImgurClient

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import tempfile, os
from config import client_id, client_secret, album_id, access_token, refresh_token, line_channel_access_token, \
    line_channel_secret

from object_detection.evaluate import YoloTest
YoloTest = YoloTest()

# import speech_recognition as sr
import requests
import json

app = Flask(__name__)

line_bot_api = LineBotApi(line_channel_access_token)
handler = WebhookHandler(line_channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'images')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'


@handler.add(MessageEvent, message=(ImageMessage, TextMessage))
def handle_message(event):
    user_id = event.source.user_id
    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
        message_content = line_bot_api.get_message_content(event.message.id)

        static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'images', user_id)
        if not os.path.exists(static_tmp_path): os.mkdir(static_tmp_path)
        # os.mkdir(static_tmp_path)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name
            print("tempfile_path",tempfile_path)
        dist_path = tempfile_path + '.' + ext
        print("dist_path",dist_path)
        dist_name = os.path.basename(dist_path)
        print("dist_name",dist_name)
        # with open(f'{static_tmp_path}/images/{dist_name}', 'wb') as fi:
        #     for chunk in message_content.iter_content():
        #         fi.write(chunk)
        os.rename(tempfile_path, dist_path)
        try:
            client = ImgurClient(client_id, client_secret, access_token, refresh_token)
            config = {
                'album': album_id,
                'name': 'Catastrophe!',
                'title': 'Catastrophe!',
                'description': 'Cute kitten being cute on '
            }
            # path = os.path.join('static', 'images',user_id, dist_name)
            # client.upload_from_path(path, config=config, anon=False)
            # os.remove(path)
            # print(path)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f'上傳成功'))
            print("user_id =", user_id)
            print("dist_name = ",dist_name)
            YoloTest.evaluate(user_id,dist_name)
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='上傳失敗'))
        return 0

    elif isinstance(event.message, VideoMessage):
        ext = 'mp4'
    elif isinstance(event.message, AudioMessage):
        ext = 'm4a'
    elif isinstance(event.message, TextMessage):
        if not os.path.exists(f"./object_detection/mAP/predicted/{user_id}/123.txt"): 
            line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text='請先上傳圖片')
            ])
            return 0
        response = requests.get(
        url=f'https://westus.api.cognitive.microsoft.com/luis/v2.0/apps/47fdbcf4-00cb-4e9a-a55c-df61cef1a102?verbose=true&timezoneOffset=0&subscription-key=7e25519a1e41462e8561a0bd60f5ddc2&q={event.message.text}'
        )
        if response.status_code != 200:
            print(f'status is not 200 ({response.status_code})')
            # return
        data = json.loads(response.text)
        intent = data['topScoringIntent']['intent']
        print("intent = ",intent)
        keyword = []
        keywordnumber = []
        for i in range(len(data['entities'])):
            if 'resolution' not in (data['entities'][i]):
                keyword.append(data['entities'][i]['entity'])
            if 'resolution' in (data['entities'][i]):
                keywordnumber.append(data['entities'][i]['resolution']['value'])
        print("keyword = ",keyword)
        print("keywordnumber = ",keywordnumber)
        a = []
        b = []
        with open('./object_detection/data/classes/111.txt','r') as f :
            for i in f.readlines():
                a.append(i.replace('\n',''))
        with open('./object_detection/data/classes/coco.names','r') as f :
            for i in f.readlines():
                b.append(i.replace('\n',''))
        if intent == "正面":
            object_list = []
            object_index =[]
            img_message = []
            img_no = []
            url = []
            
            with open(f"./object_detection/mAP/predicted/{user_id}/123.txt","r") as all_image:
                client = ImgurClient(client_id, client_secret, access_token, refresh_token)
                config = {
                'album': album_id,
                'name': 'Catastrophe!',
                'title': 'Catastrophe!',
                'description': 'Cute kitten being cute on '
                }
                for index,i in enumerate(all_image.readlines()):
                    if index % 2 == 0:
                        print(i)
                        dict_ = eval(i)
                        print("dict_ = ",dict_)
                        val = list(dict_.keys())
                        print("val = " ,val)
                        for indexkey,key in enumerate(keyword):
                            if key not in a:
                                line_bot_api.reply_message(
                                    event.reply_token, [
                                TextSendMessage(text='沒有該項目，請重新搜尋')
                                ])
                                return 0
                            print('key = ',key)
                            engindex = a.index(key)
                            print("engindex",engindex)
                            eng_key = b[engindex]
                            print("eng_key",eng_key)
                            if len(keywordnumber) and len(dict_) != 0:
                                # print("val = ",val)
                                # print("keywordnumber = ",keywordnumber)  
                                # print("indexkey = ",indexkey)
                                # print("dict_[eng_key] = ",dict_[eng_key])
                                # print("keywordnumber[indexkey] = ",keywordnumber[indexkey])
                                if (eng_key in val) and (dict_[eng_key] == int(keywordnumber[indexkey])):
                                    img_no.append(index+1)
                            elif eng_key in val:
                                img_no.append(index+1)
                        print("img_no = ",img_no)
                    object_list.append(i.replace('\n',''))
                img_no = list(set(img_no))
                print("img_no = ",img_no)
                for show in img_no:
                    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
                    client.upload_from_path(object_list[show], config=config, anon=False)
                    images = client.get_album_images(album_id)
                    index = (len(images)-1)
                    url.append(images[index].link)
                    print("url = ",url)
                    print(object_list[show])
            image_list=[]
            if len(url) !=0:
                for item in url:
                    image_list.append(ImageSendMessage(
                        original_content_url=item,
                        preview_image_url=item
                    ))
                line_bot_api.reply_message(event.reply_token, image_list)
                return 0
            else:
                line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='沒有該項目，請重新搜尋')
                ])
                return 0
        
        if intent =="負面":
            object_list = []
            object_index =[]
            img_message = []
            img_no = []
            url = []
            with open(f"./object_detection/mAP/predicted/{user_id}/123.txt","r") as all_image:
                client = ImgurClient(client_id, client_secret, access_token, refresh_token)
                config = {
                'album': album_id,
                'name': 'Catastrophe!',
                'title': 'Catastrophe!',
                'description': 'Cute kitten being cute on '
                }
                for index,i in enumerate(all_image.readlines()):
                    if index % 2 == 0:
                        print(i)
                        dict_ = eval(i)
                        val = list(dict_.keys())
                        print("val = " ,val)
                        for key in keyword:
                            if key not in a:
                                line_bot_api.reply_message(
                                    event.reply_token, [
                                TextSendMessage(text='沒有該項目，請重新搜尋')
                                ])
                                return 0
                            print('key = ',key)
                            engindex = a.index(key)
                            print("engindex",engindex)
                            eng_key = b[engindex]
                            print("eng_key",eng_key)
                        #     if eng_key not in val:
                        #         img_no.append(index+1)
                        # print("img_no = ",img_no)
                            if eng_key in val:
                                img_no.append(index+1)
                    else:            
                        object_index.append(index)
                    object_list.append(i.replace('\n',''))
                    print("object_list = ",object_list)
                print("object_index",object_index)
                print("img_no = ",img_no)
                img_no = list(set(object_index)-set(img_no))
                print("img_no = ",img_no)
                for show in img_no:
                    client = ImgurClient(client_id, client_secret, access_token, refresh_token)
                    client.upload_from_path(object_list[show], config=config, anon=False)
                    images = client.get_album_images(album_id)
                    index = (len(images)-1)
                    url.append(images[index].link)
                    print("url = ",url)
                    print(object_list[show])
            image_list=[]
            if len(url) !=0:
                for item in url:
                    image_list.append( ImageSendMessage(
                        original_content_url=item,
                        preview_image_url=item
                    ))
                line_bot_api.reply_message(event.reply_token, image_list)
                return 0
            else:
                line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='沒有該項目，請重新搜尋')
                ])
                return 0
        # elif event.message.text == "看看大家都傳了什麼圖片":
        #     client = ImgurClient(client_id, client_secret)
        #     images = client.get_album_images(album_id)
        #     index = random.randint(0, len(images) - 1)
        #     url = images[index].link
        #     image_message = ImageSendMessage(
        #         original_content_url=url,
        #         preview_image_url=url
        #     )
        #     line_bot_api.reply_message(
        #         event.reply_token, image_message)
        #     return 0
        else:
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='沒有該項目，請重新搜尋')
                ])
            return 0


if __name__ == '__main__':
    app.run()
