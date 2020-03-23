# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals
import re
import json
import requests
import errno
import os
import sys
import tempfile
from argparse import ArgumentParser

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
#channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
#channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
channel_secret = 'channel_secret'
channel_access_token = 'channel_access_token'
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')


# function for create tmp dir for download content
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            raise


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

    if text == '我的資料':
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            line_bot_api.reply_message(
                event.reply_token, [
                    TextSendMessage(text='Display name: ' + profile.display_name),
                    TextSendMessage(text='Status message: ' + profile.status_message)
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="Bot can't use profile API without user ID"))
    elif text == '購物車':
        #讀取json檔案
        with open('cart.json' , 'r') as reader:
            cart = json.loads(reader.read())
        profile = line_bot_api.get_profile(event.source.user_id)
        cuser = 0
        for i3 in cart['user']:
            if i3['name'][0] == profile.display_name:
                break
            else:
                cuser = cuser + 1

        product_confirm = ConfirmTemplate(text='喜歡嗎？', actions=[
            PostbackAction(label='清除全部',data='清除購物車'),
            PostbackAction(label='結帳',data='結帳')
        ])
        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text='你購物車裡面現在有：'+'\n'+'\n'.join(cart['user'][cuser]['productname'])),
            TemplateSendMessage(alt_text='購買確認', template=product_confirm)
        ])
    elif text == '結帳':
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='nothing'))
    else:
        word = text
        url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results?q="+ word +"&page=1&sort=rnk/dc"
        res = requests.get(url)
        data = json.loads(res.text)
        if 'prods' not in data:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='沒有你打的搜尋結果'))
        elif len(data['prods']) == 1:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) == 2:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) == 3:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][2]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][2]['price'])+'元',data=data['prods'][2]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) == 4:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][2]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][2]['price'])+'元',data=data['prods'][2]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][3]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][3]['price'])+'元',data=data['prods'][3]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) == 5:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][2]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][2]['price'])+'元',data=data['prods'][2]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][3]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][3]['price'])+'元',data=data['prods'][3]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][4]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][4]['price'])+'元',data=data['prods'][4]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) == 6:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][2]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][2]['price'])+'元',data=data['prods'][2]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][3]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][3]['price'])+'元',data=data['prods'][3]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][4]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][4]['price'])+'元',data=data['prods'][4]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][5]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][5]['price'])+'元',data=data['prods'][5]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) == 7:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][2]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][2]['price'])+'元',data=data['prods'][2]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][3]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][3]['price'])+'元',data=data['prods'][3]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][4]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][4]['price'])+'元',data=data['prods'][4]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][5]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][5]['price'])+'元',data=data['prods'][5]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][6]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][6]['price'])+'元',data=data['prods'][6]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) == 8:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][2]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][2]['price'])+'元',data=data['prods'][2]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][3]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][3]['price'])+'元',data=data['prods'][3]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][4]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][4]['price'])+'元',data=data['prods'][4]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][5]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][5]['price'])+'元',data=data['prods'][5]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][6]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][6]['price'])+'元',data=data['prods'][6]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][7]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][7]['price'])+'元',data=data['prods'][7]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) == 9:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][2]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][2]['price'])+'元',data=data['prods'][2]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][3]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][3]['price'])+'元',data=data['prods'][3]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][4]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][4]['price'])+'元',data=data['prods'][4]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][5]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][5]['price'])+'元',data=data['prods'][5]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][6]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][6]['price'])+'元',data=data['prods'][6]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][7]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][7]['price'])+'元',data=data['prods'][7]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][8]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][8]['price'])+'元',data=data['prods'][8]['name']))
                ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])
        elif len(data['prods']) >= 10:
            image_carousel_template = ImageCarouselTemplate(columns=[
                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][0]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][0]['price'])+'元',data=data['prods'][0]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][1]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][1]['price'])+'元',data=data['prods'][1]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][2]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][2]['price'])+'元',data=data['prods'][2]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][3]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][3]['price'])+'元',data=data['prods'][3]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][4]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][4]['price'])+'元',data=data['prods'][4]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][5]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][5]['price'])+'元',data=data['prods'][5]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][6]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][6]['price'])+'元',data=data['prods'][6]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][7]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][7]['price'])+'元',data=data['prods'][7]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][8]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][8]['price'])+'元',data=data['prods'][8]['name'])),

                ImageCarouselColumn(image_url="https://b.ecimg.tw"+data['prods'][9]['picS'],
                                    action=PostbackAction(label='價格：'+str(data['prods'][9]['price'])+'元',data=data['prods'][9]['name']))
            ])
            product_images = TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
            line_bot_api.reply_message(event.reply_token, [
                TemplateSendMessage(alt_text=word+'搜尋結果', template=image_carousel_template)
                ])


@handler.add(PostbackEvent)
def handle_postback(event):
    if ("cart-" in event.postback.data):
        #讀取json檔案
        with open('cart.json' , 'r') as reader:
            cart = json.loads(reader.read())
        #調整cart.json內容
        word = event.postback.data[6:100]
        url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results?q="+ word +"&page=1&sort=rnk/dc"
        res = requests.get(url)
        data = json.loads(res.text)
        profile = line_bot_api.get_profile(event.source.user_id)
        cname = 'notfound'
        cuser = len(cart['user'])
        fvalue = 0
        for i2 in cart['user']:
            if i2['name'][0] == profile.display_name:
                i2['productname'].append(data['prods'][0]['name'])
                i2['productid'].append(data['prods'][0]['Id'])
                i2['count'].append(1)
                break
            else:
                fvalue = fvalue + 1
        if cuser == fvalue:
            cart['user'].append({'name':[profile.display_name],'productid':[data['prods'][0]['Id']],'count':[1],'productname':[data['prods'][0]['name']]})
        #輸出json檔案
        with open('cart.json', 'w') as outfile:
            json.dump(cart,outfile, sort_keys = True, indent = 4, separators=(',', ': '))
        profile = line_bot_api.get_profile(event.source.user_id)

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='把'+data['prods'][0]['name']+'加到購物車了！'))
    elif ("nolike" in event.postback.data):
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='不喜歡就算了！哼～'))
    elif event.postback.data == '清除購物車':
        #讀取json檔案
        with open('cart.json' , 'r') as reader:
            cart = json.loads(reader.read())
        profile = line_bot_api.get_profile(event.source.user_id)
        i3 = 0
        for i2 in cart['user']:
            if i2['name'][0] == profile.display_name:
                del cart['user'][i3]
                break
            i3 = i3 + 1
            #輸出json檔案
        with open('cart.json', 'w') as outfile:
            json.dump(cart,outfile, sort_keys = True, indent = 4, separators=(',', ': '))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='清除購物車裡的東西了'))
    else :
        word = event.postback.data
        url = "https://ecshweb.pchome.com.tw/search/v3.3/all/results?q="+word+"&page=1&sort=rnk/dc"
        res = requests.get(url)
        data = json.loads(res.text)
        product_confirm = ConfirmTemplate(text='喜歡嗎？', actions=[
            PostbackAction(label='加購物車',data='cart-'+event.postback.data),
            PostbackAction(label='不喜歡',data='nolike')
        ])
        line_bot_api.reply_message(
            event.reply_token, [
            TextSendMessage(text='商品名稱：'+data['prods'][0]['name']+'\n'+'商品價格：'+str(data['prods'][0]['price'])+'元'),
            TextSendMessage(text='商品描述：'+data['prods'][0]['describe']),
            TemplateSendMessage(alt_text='購買確認', template=product_confirm)
            ])




@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='不要傳貼圖給我！')
        )



@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(text='Got follow event'))


@handler.add(UnfollowEvent)
def handle_unfollow():
    app.logger.info("Got Unfollow event")


@handler.add(JoinEvent)
def handle_join(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text='Joined this ' + event.source.type))


@handler.add(LeaveEvent)
def handle_leave():
    app.logger.info("Got leave event")



if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=5000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    # create tmp dir for download content
    make_static_tmp_dir()

    
    #app.run(host='0.0.0.0',debug=options.debug, port=options.port,ssl_context='adhoc')
    app.run()


