from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage,TemplateSendMessage,ButtonsTemplate,PostbackTemplateAction,PostbackEvent
)
import os
from craw_lotto import craw_lotto_info


#======================parameter==================
search_type_kind = ['lotto','superlotto']
session_dict = {}

#=================================================
app = Flask(__name__)


# Channel Access Token
line_bot_api = LineBotApi(os.environ['lineToken'])
# Channel Secret
handler = WebhookHandler(os.environ['lineSecret'])

# 監聽所有來自 /callback 的 Post Request
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
    except InvalidSignatureError:
        abort(400)

    return 'OK'
@handler.add(PostbackEvent, message=None)
def handle_Postback(event):
    print("Now event in handle_Postback handle")
    user_id = event.source.user_id
    if(event.postback.data == 'kind = lotto'):
        message = TextSendMessage(text="請輸入6個獎號 範例: 5,8,12,18,24,37")
        session_dict[user_id].append("大樂透")
        push_message(event,message)
    elif (event.postback.data == 'kind = superlotto'):
        session_dict[user_id].append("威力彩")
        message = TextSendMessage(text="請輸入第一區6個獎號 範例: 5,8,12,18,24,37")   
        push_message(event,message)
    elif(event.postback.data == 'is_correct = true'): 
        if(session_dict[user_id][0] == "大樂透"):
            mychoice_number = session_dict[user_id][1].split(",")
            correct_award(event,mychoice_number)
        elif(session_dict[user_id][0] == "威力彩"):
            if(len(session_dict[user_id]) >= 3 ):
                mychoice_number_1 = session_dict[user_id][1].split(",")
                mychoice_number_2 = session_dict[user_id][2].split(",")
                if(len(mychoice_number_2) == 1):
                    correct_award(event,mychoice_number_1,mychoice_number_2)
            else:    
                message = TextSendMessage(text="請輸入第2區獎號 範例: 1")   
                push_message(event,message)
    elif (event.postback.data == 'is_correct = false'):  
        if(len(session_dict[user_id]) >= 2):
            session_dict[user_id][1] = ""
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print(event)
    user_id = event.source.user_id
    if (user_id  not in session_dict) :
        session_dict[user_id] = []
        if("大樂透" == event.message.text):
            message = TextSendMessage(text="大樂透 查詢中")
            replay_message(event,message)
            search_TW_lotto(event,search_type_kind[0],"大樂透") 
        elif("威力彩" == event.message.text):
            message = TextSendMessage(text="威力彩 查詢中")
            replay_message(event,message)
            search_TW_lotto(event,search_type_kind[1],"威力彩")
        elif("對獎" in event.message.text):
            message = TextSendMessage(text="請選擇兌獎彩券種類")
            replay_message(event,message)
            lotto_kind_button(event)
        else:    
            message = TextSendMessage(text="抱歉我聽不懂你在說甚麼，目前僅提供查詢大樂透、威力彩")
            replay_message(event,message)
    elif(user_id in session_dict) :
        if(len(session_dict[user_id]) >= 1):
            if(session_dict[user_id][0] == "大樂透"):
                winings = event.message.text
                if(len(winings.split(",")) == 6):
                    text_string = "你輸入的獎號是:"+winings
                    message = TextSendMessage(text=text_string)
                    replay_message(event,message)
                    session_dict[user_id].append(winings)
                    is_correct(event,winings)
                else:
                    message = TextSendMessage(text="獎號格式錯誤，請重新輸入\n 範例:5,8,12,18,24,37")
            elif(session_dict[user_id][0] == "威力彩")  :
                winings = event.message.text
                if(len(winings.split(",")) == 6):
                    text_string = "你輸入的獎號是:"+winings
                    message = TextSendMessage(text=text_string)
                    replay_message(event,message)
                    session_dict[user_id].append(winings)
                    is_correct(event,winings)
                elif(len(winings.split(",")) == 1):
                    text_string = "你輸入的獎號是:"+winings
                    message = TextSendMessage(text=text_string)
                    replay_message(event,message)
                    session_dict[user_id].append(winings)
                    is_correct(event,winings)
                else:
                    message = TextSendMessage(text="獎號格是錯誤，請重新輸入\n 範例:5,8,12,18,24,37")
        elif("重新輸入" in event.message.text):
            session_dict[user_id] = []
            message = TextSendMessage(text="請重新選擇兌獎彩券種類")
            replay_message(event,message)
            lotto_kind_button(event)
        else:
            if("大樂透" == event.message.text):
                message = TextSendMessage(text="大樂透 查詢中")
                replay_message(event,message)
                search_TW_lotto(event,search_type_kind[0],"大樂透") 
            elif("威力彩" == event.message.text):
                message = TextSendMessage(text="威力彩 查詢中")
                replay_message(event,message)
                search_TW_lotto(event,search_type_kind[1],"威力彩")
            elif("對獎" in event.message.text):
                message = TextSendMessage(text="請選擇兌獎彩券種類")
                replay_message(event,message)
                lotto_kind_button(event)
            else:    
                message = TextSendMessage(text="抱歉我聽不懂你在說甚麼，目前僅提供查詢大樂透、威力彩")
                replay_message(event,message)
def search_TW_lotto(event,search_type_kind,type_name):
    header_Info_Dict,winning_Numbers_Dict = craw_lotto_info(search_type_kind) 
    keys_list = header_Info_Dict.keys()
    keys_list_sort= sorted(list(keys_list),reverse=True)
    print(keys_list_sort)
    result_string = ""+type_name + "最新開獎結果"+"\n"
    result_string +="=============" +"\n"
    result_string += "期別: "+keys_list_sort[0]+"\n"
    result_string += "開獎日期: "+header_Info_Dict[keys_list_sort[0]][1]+"\n"
    result_string += "兌獎截止日: "+header_Info_Dict[keys_list_sort[0]][2]+"\n" 
    result_string += "開獎獎號: "+str(winning_Numbers_Dict[keys_list_sort[0]][0])+", "+winning_Numbers_Dict[keys_list_sort[0]][1]+", "+winning_Numbers_Dict[keys_list_sort[0]][2]+", "+winning_Numbers_Dict[keys_list_sort[0]][3]+", "+winning_Numbers_Dict[keys_list_sort[0]][4]+", "+winning_Numbers_Dict[keys_list_sort[0]][5]+"\n" 
    result_string += "特別號: "+winning_Numbers_Dict[keys_list_sort[0]][6]+"\n"
    result_string +="============="  
    message = TextSendMessage(text=result_string)
    push_message(event,message)
    print(winning_Numbers_Dict)
    print(header_Info_Dict)

def lotto_kind_button(event):
    buttons_template_message = TemplateSendMessage(
        alt_text='詢問式按鈕',
        template=ButtonsTemplate(
            title="台彩大樂透",
            text="目前提供大樂透、威力彩兌獎",
            actions=[
                PostbackTemplateAction(
                    label='大樂透',
                    data='kind = lotto'
                ),
                PostbackTemplateAction(
                    label='威力彩',
                    data='kind = superlotto'
                )               
            ]
        )
    )  
    push_message(event,buttons_template_message)
def correct_award(event,winings_number,mychoice_number_2 = '0'):
    user_id = event.source.user_id
    if(session_dict[user_id][0] == "大樂透"):
        header_Info_Dict,winning_Numbers_Dict = craw_lotto_info(search_type_kind[0])
    elif(session_dict[user_id][0] == "威力彩"):    
        header_Info_Dict,winning_Numbers_Dict = craw_lotto_info(search_type_kind[1])
    keys_list = header_Info_Dict.keys() 
    keys_list_sort= sorted(list(keys_list),reverse=True)
    winnings_number = "中獎號碼:"
    winnings_number_count = 0
    winnings_number_special = "特別號中獎號碼:"
    winnings_number_count_special = 0
    for item in winings_number:
        if item in winning_Numbers_Dict[keys_list_sort[0]][0:6]:
            winnings_number += str(item)+","
            winnings_number_count+=1
        if item in winning_Numbers_Dict[keys_list_sort[0]][-1]:
            winnings_number_special = "特別號中獎號碼:"+str(item)
            winnings_number_count_special+=1    
    winnings_number += "\n中獎數:"+str(winnings_number_count)+"\n"
    if(winnings_number_count_special == 0):
        winnings_number += "沒中特別號"
    else:
        winnings_number += winnings_number_special
    message = TextSendMessage(text=winnings_number)
    push_message(event,message)
    session_dict[user_id] = []    
def is_correct(event,winings):
    buttons_template_message = TemplateSendMessage(
        alt_text='詢問式按鈕',
        template=ButtonsTemplate(
            title="輸入的獎號是否正確",
            text=winings,
            actions=[
                PostbackTemplateAction(
                    label='正確',
                    data='is_correct = true'
                ),
                PostbackTemplateAction(
                    label='不正確',
                    text = "重新輸入",
                    data='is_correct = false'
                )               
            ]
        )
    )
    push_message(event,buttons_template_message)    
def replay_message(event,text):
    line_bot_api.reply_message(
        event.reply_token,
        text)
        
def push_message(event,text):
    line_bot_api.push_message(
        event.source.user_id,
        text)        
       
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
