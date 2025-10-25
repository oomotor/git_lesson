import os
import datetime
import requests
from flask import Flask, request, abort

# 新しいv3のimport
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent

app = Flask(__name__)

# 設定
configuration = Configuration(access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

def get_weather_info(api_key, city_name="東京"):
    """都市名から天気情報を取得"""
    # 都市名のマッピング
    city_ids = {
        "東京": "1850147",
        "大阪": "1853909",
        "名古屋": "1856057"
    }

    city_id = city_ids.get(city_name, "1850147")  # デフォルトは東京

    URL = f'https://api.openweathermap.org/data/2.5/weather?id={city_id}&appid={api_key}&units=metric&lang=ja'

    try:
        res = requests.get(URL)
        if res.status_code == 200:
            data = res.json()
            return f"📍{data['name']}の天気\n🌤️ {data['weather'][0]['description']}\n🌡️ 気温: {data['main']['temp']}°C"
        else:
            return "申し訳ありません。天気情報の取得に失敗しました。"
    except:
        return "天気情報の取得中にエラーが発生しました。"


def get_time_based_greeting():
    """現在時刻に応じた挨拶を返す"""
    now = datetime.datetime.now()
    hour = now.hour

    if 5 <= hour < 12:
        return "おはようございます"
    elif 12 <= hour < 17:
        return "こんにちは"
    elif 17 <= hour < 22:
        return "こんばんは"
    else:
        return "夜更かしですね"


def get_reply(user_message):
    """ユーザーメッセージに応じた返答を生成"""
    message = user_message.lower()
    greeting = get_time_based_greeting()  # 時間に応じた挨拶を取得

    # 天気に関するキーワードをチェック
    if "天気" in message:
        api_key = "f9f31998445b7eae562dd0666b8cc528"
        if "大阪" in message:
            return get_weather_info(api_key, "大阪")
        elif "名古屋" in message:
            return get_weather_info(api_key, "名古屋")
        else:
            return get_weather_info(api_key, "東京")

    elif "こんにちは" in message or "おはよう" in message or "こんばんは" in message:
        return f"{greeting}！今日も一日頑張りましょう！"
    elif "ありがとう" in message:
        return "どういたしまして！また何かあれば声をかけてくださいね。"
    elif "疲れた" in message:
        return f"{greeting}！お疲れ様です。少し休憩してくださいね。"
    elif "バカ" in message:
        return f"{greeting}！馬と鹿と書いてバカと読みます！"
    elif "宿題" in message:
        return f"{greeting}！宿題は言われなくても早くやって下さい！または諦めてズーンをくらって下さい！"
    elif "ママ" in message:
        return f"{greeting}！ママのいう事は聞いて下さい。ワガママばかり言ってはいけないよ！"
    elif "パパ" in message:
        return f"{greeting}！パパを見習って宿題は早く終わらせるよう頑張って下さい！パパに文句ばかり言ってはいけないよ！"
    else:
        return f"{greeting}！すみません、よく分かりませんでした。他に何かお聞きしたいことはありますか？"


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_message = event.message.text
    reply_text = get_reply(user_message)  # 新しい関数を呼び出し

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=reply_text)]
            )
        )


if __name__ == "__main__":
    port = 5001
    app.run(host="0.0.0.0", port=port)