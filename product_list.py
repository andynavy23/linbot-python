# coding=utf-8
import json
import random
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




with open('product.json' , 'r') as reader:
    jf = json.loads(reader.read())

number = [random.randint(0,29) for _ in range(10)]





image_carousel_template = ImageCarouselTemplate(columns=[
    ImageCarouselColumn(image_url=jf['values'][number[0]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[0]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[1]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[1]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[2]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[2]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[3]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[3]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[4]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[4]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[5]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[5]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[6]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[6]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[7]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[7]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[8]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[8]]['productid'][0]))),

    ImageCarouselColumn(image_url=jf['values'][number[9]]['imageurl'][0],
                        action=PostbackAction(data='detail-productid='+str(jf['values'][number[9]]['productid'][0])))

])
product_images = TemplateSendMessage(
    alt_text='ImageCarousel alt text', template=image_carousel_template)

